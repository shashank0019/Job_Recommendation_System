import os
import json
import time
from typing import List, Dict, Any

import requests
from flask import Blueprint, request, jsonify

problems_bp = Blueprint("problems", __name__)

# Support both 'data/problems' and 'data/Problems' (Windows/macOS case differences)
def _get_problems_path() -> str | None:
    base_dir = os.path.dirname(__file__)
    candidates = [
        os.path.join(base_dir, "data", "problems", "problems.json"),
        os.path.join(base_dir, "data", "Problems", "problems.json"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None

# Judge0 configuration (set in .env or environment)
JUDGE0_URL = os.getenv("JUDGE0_URL", "https://judge0-ce.p.rapidapi.com")
JUDGE0_KEY = os.getenv("JUDGE0_KEY")
JUDGE0_HOST = os.getenv("JUDGE0_HOST")  # Some providers need X-RapidAPI-Host

# Language map: update IDs to your Judge0 instance versions if needed
LANGUAGE_ID_MAP = {
    # Python 3.x
    "python": 71,  # Python (3.8.1)
    "py": 71,
    # JavaScript (Node.js)
    "javascript": 63,  # Node.js (12.14.0)
    "js": 63,
    # C++
    "cpp": 54,  # GCC 9.2.0 (C++ 17)
    # Java
    "java": 62,  # Java (OpenJDK 13.0.1)
}

_cached_problems: List[Dict[str, Any]] | None = None

def _load_problems() -> List[Dict[str, Any]]:
    global _cached_problems
    if _cached_problems is not None:
        return _cached_problems
    path = _get_problems_path()
    if not path or not os.path.exists(path):
        # Print a hint once to help diagnose missing dataset
        print("⚠️ problems_api: problems.json not found under data/problems or data/Problems")
        _cached_problems = []
        return _cached_problems
    try:
        with open(path, "r", encoding="utf-8") as f:
            _cached_problems = json.load(f)
            return _cached_problems
    except Exception as e:
        print(f"❌ problems_api: failed to load problems.json: {e}")
        _cached_problems = []
        return _cached_problems


def _filter_problems(items: List[Dict[str, Any]], q: str | None, difficulty: str | None, topic: str | None) -> List[Dict[str, Any]]:
    res = items
    if difficulty:
        d = difficulty.strip().lower()
        res = [p for p in res if ((p.get("difficulty", "") or "").strip().lower() == d)]
    if topic:
        t = topic.strip().lower()
        res = [p for p in res if any(t in (x or "").lower() for x in p.get("topics", []))]
    if q:
        needle = q.strip().lower()
        res = [p for p in res if (needle in (p.get("title", "").lower()) or needle in (p.get("id", "").lower()))]
    return res


@problems_bp.get("/problems")
def list_problems():
    items = _load_problems()
    q = request.args.get("search")
    difficulty = request.args.get("difficulty")
    topic = request.args.get("topic")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 1000))

    filtered = _filter_problems(items, q, difficulty, topic)
    start = (page - 1) * limit
    end = start + limit
    page_items = filtered[start:end]

    return jsonify({
        "success": True,
        "total": len(filtered),
        "page": page,
        "limit": limit,
        "items": [
            {
                "id": p.get("id"),
                "title": p.get("title"),
                "difficulty": p.get("difficulty"),
                "topics": p.get("topics", [])
            } for p in page_items
        ]
    })


@problems_bp.get("/problems/<pid>")
def get_problem(pid: str):
    items = _load_problems()
    for p in items:
        if str(p.get("id")) == str(pid):
            # Do not expose hidden tests
            data = dict(p)
            tests = dict(data.get("tests", {}))
            tests.pop("hidden", None)
            data["tests"] = tests
            return jsonify({"success": True, "problem": data})
    return jsonify({"success": False, "error": "Problem not found"}), 404


def _judge0_headers():
    headers = {"Content-Type": "application/json"}
    if JUDGE0_KEY:
        headers["X-RapidAPI-Key"] = JUDGE0_KEY
    if JUDGE0_HOST:
        headers["X-RapidAPI-Host"] = JUDGE0_HOST
    return headers


def _submit_to_judge0(language: str, source_code: str, stdin: str | None = None) -> Dict[str, Any]:
    lang_id = LANGUAGE_ID_MAP.get(language.lower())
    if not lang_id:
        raise ValueError(f"Unsupported language: {language}")
    payload = {
        "language_id": lang_id,
        "source_code": source_code,
    }
    if stdin is not None:
        payload["stdin"] = stdin

    r = requests.post(f"{JUDGE0_URL}/submissions?base64_encoded=false&wait=true", headers=_judge0_headers(), data=json.dumps(payload), timeout=30)
    r.raise_for_status()
    return r.json()


def _format_run_result(j: Dict[str, Any]) -> Dict[str, Any]:
    status = (j.get("status") or {}).get("description")
    return {
        "status": status,
        "stdout": j.get("stdout"),
        "stderr": j.get("stderr"),
        "time": j.get("time"),
        "memory": j.get("memory"),
        "compile_output": j.get("compile_output"),
        "message": j.get("message"),
    }


@problems_bp.post("/submissions")
def submit_solution():
    """
    Synchronous MVP: runs immediately and returns aggregate per-test results.
    Body: { problem_id, language, source_code, mode: "run"|"submit" }
    """
    if not JUDGE0_URL:
        return jsonify({"success": False, "error": "Judge0 not configured"}), 400

    data = request.get_json(force=True) or {}
    problem_id = data.get("problem_id")
    language = data.get("language", "python")
    source_code = data.get("source_code", "")
    mode = (data.get("mode") or "run").lower()

    if not problem_id or not source_code:
        return jsonify({"success": False, "error": "problem_id and source_code are required"}), 400

    # locate problem
    items = _load_problems()
    problem = next((p for p in items if str(p.get("id")) == str(problem_id)), None)
    if not problem:
        return jsonify({"success": False, "error": "Problem not found"}), 404

    tests = problem.get("tests", {})
    public_tests = tests.get("public", [])
    hidden_tests = tests.get("hidden", []) if mode == "submit" else []

    # Build stdin per test as JSON
    def to_stdin(t: Dict[str, Any]) -> str:
        # You can adjust harness to expected format your solution reads.
        # For MVP, we pass a JSON with input and expected output; user prints just the answer.
        return json.dumps({"input": t.get("input"), "expected": t.get("output")})

    results = []
    passed = 0
    total = len(public_tests) + len(hidden_tests)

    # If no tests provided, run once without stdin (so users can debug)
    tests_to_run = public_tests + hidden_tests
    if total == 0:
        try:
            j = _submit_to_judge0(language, source_code)
            fr = _format_run_result(j)
            return jsonify({"success": True, "total": 0, "passed": 0, "results": [fr], "note": "No tests configured for this problem yet."})
        except requests.exceptions.RequestException as e:
            # Bubble up a clear error instead of a 500
            return jsonify({"success": False, "error": f"Judge0 request failed: {str(e)}"}), 502
        except Exception as e:
            return jsonify({"success": False, "error": f"Execution failed: {str(e)}"}), 502

    for i, t in enumerate(tests_to_run):
        try:
            j = _submit_to_judge0(language, source_code, to_stdin(t))
        except requests.exceptions.RequestException as e:
            return jsonify({"success": False, "error": f"Judge0 request failed: {str(e)}"}), 502
        except Exception as e:
            return jsonify({"success": False, "error": f"Execution failed: {str(e)}"}), 502
        fr = _format_run_result(j)
        # Very simple correctness check: compare stdout stripped with expected (stringified)
        expected = t.get("output")
        out = (fr.get("stdout") or "").strip()
        ok = False
        if expected is None:
            ok = (fr.get("status") == "Accepted") and (fr.get("stderr") in (None, ""))
        else:
            ok = out == json.dumps(expected) or out == str(expected)
        if ok:
            passed += 1
        # hide hidden test details in run mode response
        is_hidden = (i >= len(public_tests))
        if is_hidden and mode != "run":
            results.append({"status": "hidden", "passed": ok})
        else:
            fr.update({"passed": ok, "hidden": is_hidden})
            results.append(fr)

    status_overall = "passed" if passed == total else "failed"
    return jsonify({
        "success": True,
        "status": status_overall,
        "passed": passed,
        "total": total,
        "results": results,
        "time_ms": None,
    })
