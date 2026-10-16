import os
import json
import re
import sys
import pandas as pd
from typing import List, Dict, Any

# Usage:
#   python scripts/import_problems_from_leetcode_csv.py "data/Problems/leetcode_dataset - lc.csv" \
#          --out data/problems/problems.json --limit 200
# If args omitted, uses defaults above.

DEFAULT_IN = os.path.join("data", "Problems", "leetcode_dataset - lc.csv")
DEFAULT_OUT = os.path.join("data", "problems", "problems.json")

EXAMPLE_BLOCK_RE = re.compile(r"Example\s*\d*\s*:?(.*?)Constraints:|Example\s*\d*\s*:?(.*)$", re.S | re.I)
INPUT_LINE_RE = re.compile(r"Input\s*:\s*(.*)")
OUTPUT_LINE_RE = re.compile(r"Output\s*:\s*(.*)")
EXPLANATION_LINE_RE = re.compile(r"Explanation\s*:\s*(.*)")

SUPPORTED_LANGS = ["python", "javascript", "cpp", "java"]


def parse_samples(description: str) -> List[Dict[str, Any]]:
    if not description:
        return []
    text = description.replace("\r", "")
    samples: List[Dict[str, Any]] = []
    # Split by 'Example' heuristically
    parts = re.split(r"\n\s*Example\s*\d*\s*:|\n\s*Example:\s*", text, flags=re.I)
    for part in parts[1:]:
        # Stop at next blank line block of constraints or end
        block = part.strip()
        # Extract Input/Output/Explanation lines
        inp_m = INPUT_LINE_RE.search(block)
        out_m = OUTPUT_LINE_RE.search(block)
        exp_m = EXPLANATION_LINE_RE.search(block)
        sample = {}
        if inp_m:
            sample["input_raw"] = inp_m.group(1).strip()
        if out_m:
            sample["output_raw"] = out_m.group(1).strip()
        if exp_m:
            sample["explanation"] = exp_m.group(1).strip()
        if sample:
            samples.append(sample)
    return samples


def normalize_topics(s: str | None) -> List[str]:
    if not s:
        return []
    parts = [p.strip() for p in str(s).split(',') if p.strip()]
    # Some csv have topics like "Array,Hash Table" or with extra spaces
    return parts


def to_problem_row(row: pd.Series) -> Dict[str, Any]:
    pid = str(row.get('id'))
    title = str(row.get('title') or '').strip()
    difficulty = str(row.get('difficulty') or '').strip()
    topics = normalize_topics(row.get('related_topics'))
    url = str(row.get('url') or '').strip()
    description = str(row.get('description') or '').strip()
    samples = parse_samples(description)

    # Convert crude samples into simple structures; keep raw strings for MVP
    structured_samples = []
    for s in samples[:3]:
        structured_samples.append({
            "input": s.get("input_raw"),
            "output": s.get("output_raw"),
            "explanation": s.get("explanation")
        })

    return {
        "id": pid,
        "title": title,
        "difficulty": difficulty or "Unknown",
        "topics": topics,
        "languages": SUPPORTED_LANGS,
        "statement": {
            "description": description,
            "input_spec": "",
            "output_spec": "",
            "samples": structured_samples,
        },
        "tests": {
            # Public tests left empty initially; authors can add precise IO later
            "public": [],
            "hidden": [],
            "constraints": {"time_limit_ms": 2000, "memory_mb": 256}
        },
        "meta": {"source_url": url}
    }


def main():
    csv_in = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_IN
    out = DEFAULT_OUT
    limit = None
    # parse optional args
    for i, a in enumerate(sys.argv):
        if a == '--out' and i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
        if a == '--limit' and i + 1 < len(sys.argv):
            try:
                limit = int(sys.argv[i + 1])
            except Exception:
                limit = None

    os.makedirs(os.path.dirname(out), exist_ok=True)

    df = pd.read_csv(csv_in)
    if limit:
        df = df.head(limit)

    problems: List[Dict[str, Any]] = []
    for _, row in df.iterrows():
        try:
            problems.append(to_problem_row(row))
        except Exception as e:
            # skip malformed rows, but continue
            print(f"Skipping row due to error: {e}")
            continue

    with open(out, 'w', encoding='utf-8') as f:
        json.dump(problems, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(problems)} problems to {out}")


if __name__ == '__main__':
    main()
