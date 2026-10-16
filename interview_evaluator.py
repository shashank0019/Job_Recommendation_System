import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

# Reuse dataset loader
from interview_data import load_interview_datasets, _normalize_role


class InterviewEvaluator:
    """Unsupervised evaluator that scores answers based on role-specific
    keyphrase coverage plus basic communication heuristics.
    """

    def __init__(self):
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.role_to_keywords: Dict[str, List[str]] = {}
        self.global_keywords: List[str] = []

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        text = (text or "").lower()
        # Keep words and simple bigrams via whitespace split; punctuation removed
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        tokens = [t for t in text.split() if t]
        return tokens

    def _extract_top_terms(self, texts: List[str], top_k: int = 50) -> List[str]:
        if not texts:
            return []
        if self.vectorizer is None:
            # Fit a vectorizer on supplied texts to get vocabulary
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words="english",
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.95,
            )
            X = self.vectorizer.fit_transform(texts)
        else:
            X = self.vectorizer.transform(texts)

        # Average tf-idf across documents
        import numpy as np
        mean_vec = X.mean(axis=0)
        mean_arr = np.asarray(mean_vec).ravel()
        feature_names = self.vectorizer.get_feature_names_out()
        ranked = sorted(zip(feature_names, mean_arr), key=lambda x: x[1], reverse=True)
        keywords = [w for w, _ in ranked[: top_k * 3]]  # initial pool

        # Filter out overly generic tokens
        generic = {"you", "use", "using", "like", "know", "think", "work", "good", "best"}
        pruned = [w for w in keywords if len(w) > 2 and w not in generic]
        # Deduplicate while preserving order
        seen = set()
        uniq: List[str] = []
        for w in pruned:
            if w not in seen:
                seen.add(w)
                uniq.append(w)
        return uniq[:top_k]

    def train_from_directory(self, base_dir: str = "data/interview", json_sample_limit: int = 20000) -> Dict[str, Any]:
        """Build role-specific keyword banks by analyzing question texts."""
        by_role = load_interview_datasets(base_dir=base_dir, json_sample_limit=json_sample_limit)
        role_texts: Dict[str, List[str]] = {r: [q["text"] for q in qs if q.get("text")] for r, qs in by_role.items()}

        # Fit vectorizer on all texts combined to get a coherent vocabulary
        all_texts: List[str] = []
        for texts in role_texts.values():
            all_texts.extend(texts)
        if not all_texts:
            raise ValueError("No interview texts found to train evaluator")

        # Fit vectorizer once
        self.vectorizer = TfidfVectorizer(
            max_features=8000,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.97,
        )
        self.vectorizer.fit(all_texts)

        # Extract top terms per role and globally
        self.role_to_keywords = {}
        for role, texts in role_texts.items():
            self.role_to_keywords[role] = self._extract_top_terms(texts, top_k=60)

        self.global_keywords = self._extract_top_terms(all_texts, top_k=80)

        return {
            "roles": list(self.role_to_keywords.keys()),
            "total_questions": sum(len(v) for v in by_role.values()),
            "global_keywords": len(self.global_keywords),
        }

    def save(self, model_path: str = "data/interview_evaluator.joblib", keywords_path: str = "data/interview_keywords.json") -> None:
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump({
            "vectorizer": self.vectorizer,
            "role_to_keywords": self.role_to_keywords,
            "global_keywords": self.global_keywords,
        }, model_path)
        with open(keywords_path, "w", encoding="utf-8") as f:
            json.dump({
                "role_to_keywords": self.role_to_keywords,
                "global_keywords": self.global_keywords,
            }, f, ensure_ascii=False, indent=2)

    def load(self, model_path: str = "data/interview_evaluator.joblib") -> bool:
        if not os.path.exists(model_path):
            return False
        data = joblib.load(model_path)
        self.vectorizer = data.get("vectorizer")
        self.role_to_keywords = data.get("role_to_keywords", {})
        self.global_keywords = data.get("global_keywords", [])
        return self.vectorizer is not None

    def score_and_feedback(self, answer: str, role_hint: str = "", question_text: str = "") -> Dict[str, Any]:
        role = _normalize_role(role_hint)
        tokens = set(self._tokenize(answer))

        # Build target keyword set
        role_keys = self.role_to_keywords.get(role) or []
        if not role_keys:
            role_keys = self.global_keywords[:60]

        # Count coverage by keywords (allow space-separated phrases)
        answer_lc = (answer or "").lower()
        matched: List[str] = []
        for kw in role_keys:
            if kw in answer_lc:
                matched.append(kw)

        coverage = len(matched) / max(1, len(role_keys))

        # Communication heuristics
        length_words = len(tokens)
        has_example = ("for example" in answer_lc) or ("e.g." in answer_lc) or bool(re.search(r"\bexample\b", answer_lc))
        has_metrics = bool(re.search(r"\b(\d+%?|\d+\.\d+%?)\b", answer_lc))
        has_outcome = any(w in answer_lc for w in ["result", "impact", "reduced", "improved", "increased"])
        structure_cues = sum(1 for w in ["first", "then", "finally", "because"] if w in answer_lc)

        # Scores
        keyword_score = min(1.0, coverage * 3.0)  # len(role_keys) is large; scale up
        length_score = min(1.0, length_words / 120.0)  # ~120+ words saturates
        comm_score = 0.0
        comm_score += 0.35 if has_example else 0.0
        comm_score += 0.25 if has_metrics else 0.0
        comm_score += 0.25 if has_outcome else 0.0
        comm_score += min(0.15, 0.05 * structure_cues)

        total = 0.55 * keyword_score + 0.20 * length_score + 0.25 * comm_score
        total_pct = round(total * 100.0, 1)

        # Feedback
        strengths: List[str] = []
        improvements: List[str] = []
        if has_example:
            strengths.append("Provided concrete example(s)")
        else:
            improvements.append("Add a concrete example to demonstrate application")
        if has_metrics:
            strengths.append("Used numbers/metrics")
        else:
            improvements.append("Quantify impact with metrics (%, time saved, etc.)")
        if has_outcome:
            strengths.append("Explained outcome/impact")
        else:
            improvements.append("State the outcome/impact of your approach")
        if length_words >= 100:
            strengths.append("Sufficient level of detail")
        else:
            improvements.append("Expand with more details (context → actions → results)")

        # Keyword-based suggestions: show top missing 5
        missing = [kw for kw in role_keys if kw not in matched][:5]
        if missing:
            improvements.append("Mention key topics: " + ", ".join(missing))

        return {
            "score": total_pct,
            "strengths": strengths[:3],
            "improvements": improvements[:4],
            "matched_keywords": matched[:10],
            "missing_keywords": missing,
        }


