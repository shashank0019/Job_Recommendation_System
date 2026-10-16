import os
import json
import re
from typing import Dict, List, Any, Optional

try:
    import pandas as pd
except Exception:  # Pandas is already in requirements
    pd = None


def _normalize_role(value: Optional[str]) -> str:
    if not value or not isinstance(value, str):
        return "general"
    v = value.strip().lower()
    v = re.sub(r"[^a-z0-9]+", "_", v)
    v = re.sub(r"_+", "_", v).strip("_")
    return v or "general"


def _normalize_level(value: Optional[str]) -> str:
    if value is None:
        return "any"
    if isinstance(value, (int, float)):
        try:
            n = int(value)
            if n <= 1:
                return "junior"
            if n == 2:
                return "mid"
            return "senior"
        except Exception:
            return "any"
    v = str(value).strip().lower()
    if any(k in v for k in ["junior", "entry", "beginner", "fresh"]):
        return "junior"
    if any(k in v for k in ["mid", "intermediate", "middle"]):
        return "mid"
    if any(k in v for k in ["senior", "lead", "principal", "staff"]):
        return "senior"
    if any(k in v for k in ["all", "any", "mixed"]):
        return "any"
    # Map by numeric difficulty inside strings if present
    m = re.search(r"\b(\d)\b", v)
    if m:
        return _normalize_level(int(m.group(1)))
    return "any"


def _first_existing(columns: List[str], candidates: List[str]) -> Optional[str]:
    lower_cols = {c.lower(): c for c in columns}
    for cand in candidates:
        if cand.lower() in lower_cols:
            return lower_cols[cand.lower()]
    return None


def _split_tags(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    text = str(value)
    if "|" in text:
        parts = text.split("|")
    elif "," in text:
        parts = text.split(",")
    else:
        parts = text.split()
    return [p.strip().lower() for p in parts if p and p.strip()]


def _row_to_question(row: Dict[str, Any], file_hint: str = "") -> Optional[Dict[str, Any]]:
    columns = list(row.keys())
    q_col = _first_existing(columns, [
        "question", "question_text", "text", "prompt", "Title", "Question"
    ])
    if not q_col:
        return None

    role_col = _first_existing(columns, [
        "role", "category", "topic", "domain", "track", "Job Role"
    ])
    level_col = _first_existing(columns, [
        "level", "difficulty", "seniority", "experience_level"
    ])
    tags_col = _first_existing(columns, [
        "tags", "keywords", "key_points", "skills"
    ])

    q_text = str(row.get(q_col, "")).strip()
    if not q_text:
        return None

    role = _normalize_role(row.get(role_col)) if role_col else "general"
    level = _normalize_level(row.get(level_col)) if level_col else "any"
    tags = _split_tags(row.get(tags_col)) if tags_col else []

    # Generate a deterministic id
    base = f"{file_hint}:{role}:{level}:{abs(hash(q_text)) % (10**9)}"
    return {
        "id": base,
        "text": q_text,
        "role": role,
        "level": level,
        "tags": tags,
    }


def _load_csv(path: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    if pd is None:
        return items
    try:
        # Use chunking for big CSVs
        first_pass = True
        for chunk in pd.read_csv(path, chunksize=10000, low_memory=False):
            # Convert rows
            for _, r in chunk.iterrows():
                q = _row_to_question(r.to_dict(), file_hint=os.path.basename(path))
                if q:
                    items.append(q)
            if limit and len(items) >= limit:
                return items[:limit]
            # If no recognizable columns after first chunk, bail
            if first_pass and not items:
                break
            first_pass = False
    except Exception:
        return items
    return items


def _load_json_stream(path: str, limit: int = 10000) -> List[Dict[str, Any]]:
    """Stream a massive JSON to extract plausible Q&A fields.
    Supports NDJSON or a top-level array. We only sample up to `limit` items.
    """
    items: List[Dict[str, Any]] = []
    try:
        # Try NDJSON first
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    obj = None
                if not obj:
                    # If first lines fail, this may not be NDJSON
                    if i < 3:
                        continue
                    break
                q = _row_to_question(obj, file_hint=os.path.basename(path))
                if q:
                    items.append(q)
                if len(items) >= limit:
                    return items
        if items:
            return items

        # Fallback: top-level array (careful with memory)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
            if isinstance(data, list):
                for obj in data[:limit]:
                    if isinstance(obj, dict):
                        q = _row_to_question(obj, file_hint=os.path.basename(path))
                        if q:
                            items.append(q)
                            if len(items) >= limit:
                                break
    except Exception:
        return items
    return items


def load_interview_datasets(base_dir: str = "data/interview", json_sample_limit: int = 20000) -> Dict[str, List[Dict[str, Any]]]:
    """Load questions from CSV/JSON files into a dict keyed by normalized role.
    Only extracts fields needed to ask questions. For giant JSON files we sample.
    """
    questions_by_role: Dict[str, List[Dict[str, Any]]] = {}

    if not os.path.isdir(base_dir):
        return questions_by_role

    for name in os.listdir(base_dir):
        path = os.path.join(base_dir, name)
        if not os.path.isfile(path):
            continue
        lower = name.lower()
        # Prioritize likely files
        is_candidate = any(k in lower for k in ["question", "interview", "software", "qa"])
        if not is_candidate and not lower.endswith((".csv", ".json", ".ndjson")):
            continue

        loaded: List[Dict[str, Any]] = []
        if lower.endswith(".csv"):
            loaded = _load_csv(path, limit=None)
        elif lower.endswith(".json") or lower.endswith(".ndjson"):
            # Avoid loading 1.1GB fully; sample
            loaded = _load_json_stream(path, limit=json_sample_limit)

        for q in loaded:
            role = q.get("role", "general")
            questions_by_role.setdefault(role, []).append(q)

    # Deduplicate by id within each role
    for role, items in questions_by_role.items():
        seen = set()
        uniq: List[Dict[str, Any]] = []
        for it in items:
            qid = it.get("id")
            if qid in seen:
                continue
            seen.add(qid)
            uniq.append(it)
        questions_by_role[role] = uniq

    return questions_by_role


def choose_questions_for_interview(questions_by_role: Dict[str, List[Dict[str, Any]]], role: str = "", level: str = "any", skills: Optional[List[str]] = None, num_questions: int = 6, time_limit_sec: int = 90) -> List[Dict[str, Any]]:
    import random

    if not questions_by_role:
        return []

    role_norm = _normalize_role(role)
    level_norm = _normalize_level(level)
    pool: List[Dict[str, Any]] = []

    # 1) Exact role match
    if role_norm in questions_by_role:
        pool.extend(questions_by_role[role_norm])
    # 2) Fallback general
    if "general" in questions_by_role:
        pool.extend(questions_by_role["general"])

    if not pool:
        # Use any role's questions
        for items in questions_by_role.values():
            pool.extend(items)

    # Filter by level when possible
    if level_norm != "any":
        filtered = [q for q in pool if _normalize_level(q.get("level")) in (level_norm, "any")]
        if filtered:
            pool = filtered

    # Light personalization: prefer questions with tags that intersect skills
    skills_set = set([s.lower() for s in (skills or [])])
    if skills_set:
        tagged = [q for q in pool if set(q.get("tags", [])) & skills_set]
        # Mix tagged and others
        if tagged:
            random.shuffle(tagged)
            random.shuffle(pool)
            pool = (tagged[: max(2, num_questions // 2)] + pool)  # bias towards tagged

    random.shuffle(pool)
    selected = pool[:num_questions]
    # Normalize output
    return [{"id": q.get("id"), "text": q.get("text"), "time_limit_sec": time_limit_sec} for q in selected if q.get("text")]


