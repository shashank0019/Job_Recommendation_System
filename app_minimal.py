#!/usr/bin/env python3
"""
Minimal Career Guidance Platform Flask Application
"""

import sys
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from flask import Flask, render_template_string, request, jsonify, Blueprint, session
from flask_cors import CORS
import pandas as pd
import joblib
import os
import re
import json
from io import BytesIO
import requests
from typing import Optional
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Enhanced interview system with OpenAI
try:
    from interview_openai import initialize_openai_generator, generate_enhanced_interview_questions, openai_interview_generator
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False
    initialize_openai_generator = None
    generate_enhanced_interview_questions = None
    openai_interview_generator = None

# Enhanced fallback interview system
try:
    from enhanced_interview_fallback import get_enhanced_questions, get_enhanced_evaluation
    ENHANCED_FALLBACK_AVAILABLE = True
    print("[OK] Enhanced fallback system loaded successfully")
except Exception as e:
    ENHANCED_FALLBACK_AVAILABLE = False
    get_enhanced_questions = None
    get_enhanced_evaluation = None
    print(f"[WARNING] Enhanced fallback system failed to load: {e}")

# Interview dataset loader
try:
    from interview_data import load_interview_datasets, choose_questions_for_interview, _normalize_role
    INTERVIEW_DATA_AVAILABLE = True
except Exception:
    INTERVIEW_DATA_AVAILABLE = False
    load_interview_datasets = None  # type: ignore
    choose_questions_for_interview = None  # type: ignore
    _normalize_role = None  # type: ignore

# Interview evaluator (trained from data/interview)
try:
    from interview_evaluator import InterviewEvaluator
    INTERVIEW_EVAL_AVAILABLE = True
except Exception:
    INTERVIEW_EVAL_AVAILABLE = False
    InterviewEvaluator = None  # type: ignore

try:
    from PyPDF2 import PdfReader
    PDF_ENABLED = True
except Exception:
    PDF_ENABLED = False

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174", "http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Origin", "Accept"]
    }
})

# Register coding problems API (if available)
try:
    from problems_api import problems_bp  # type: ignore
    app.register_blueprint(problems_bp, url_prefix="/api")
    print("[OK] Problems API registered at /api")
except Exception as e:
    print(f"[INFO] Problems API not registered: {e}")

# Register authentication routes (optional - continues without auth if DB fails)
try:
    from auth.routes import auth_bp
    from config.database import get_db_config
    
    # Initialize database connection (will continue without it if it fails)
    db_config = get_db_config()
    connection_ok = db_config.connect()
    
    if connection_ok:
        print(f"[OK] Database connected")
        app.register_blueprint(auth_bp, url_prefix="/auth")
        print("[OK] Authentication routes registered at /auth")
    else:
        print("[WARNING] Database connection failed - running WITHOUT authentication routes")
except Exception as e:
    print(f"[WARNING] Authentication routes not available: {e}")

# Proctoring blueprint: handles client-side violation events and enforces 3-strike rule per interview session
proctor_bp = Blueprint("proctor", __name__)

# In-memory strike tracking (for demo). Replace with a persistent store for multi-instance deployments.
SESSION_STRIKES: dict[str, int] = {}

@proctor_bp.post("/proctor/events")
def proctor_events():
    """Receive proctoring violation events from the browser and return whether interview should end.
    Body (JSON): { session_id?: string, reason: string }
    Response: { ok: true, strikes: int, end: bool }
    """
    try:
        data = request.get_json(force=True, silent=True) or {}
    except Exception:
        data = {}
    reason = (data.get("reason") or "unknown").strip()
    # Use provided session_id or fall back to flask session sid / remote addr
    sess_id = (data.get("session_id") or session.get("sid") or request.remote_addr or "anon").strip()
    strikes = SESSION_STRIKES.get(sess_id, 0) + 1
    SESSION_STRIKES[sess_id] = strikes

    # Lightweight logging
    try:
        os.makedirs("data/proctor_logs", exist_ok=True)
        with open(os.path.join("data/proctor_logs", f"{sess_id}.log"), "a", encoding="utf-8") as f:
            from datetime import datetime
            f.write(f"{datetime.utcnow().isoformat()} reason={reason} strikes={strikes}\n")
    except Exception:
        pass

    end = strikes >= 3
    return jsonify({"ok": True, "strikes": strikes, "end": end})

# Register blueprint under /api
app.register_blueprint(proctor_bp, url_prefix="/api")

# Also expose a direct root route to be compatible with dev proxy that rewrites '/api' to ''
@app.post("/proctor/events")
def proctor_events_root():
    try:
        data = request.get_json(force=True, silent=True) or {}
    except Exception:
        data = {}
    reason = (data.get("reason") or "unknown").strip()
    sess_id = (data.get("session_id") or session.get("sid") or request.remote_addr or "anon").strip()
    strikes = SESSION_STRIKES.get(sess_id, 0) + 1
    SESSION_STRIKES[sess_id] = strikes
    end = strikes >= 3
    return jsonify({"ok": True, "strikes": strikes, "end": end})

# Global variables
job_data = None
vectorizer = None
job_vectors = None
interview_questions_by_role: Optional[dict] = None
interview_evaluator: Optional[object] = None
ml_answer_scorer: Optional[object] = None

# Optional external authenticated job API (user-provided)
CUSTOM_JOBS_API_URL = os.getenv("CUSTOM_JOBS_API_URL", "").strip()
CUSTOM_JOBS_API_TOKEN = os.getenv("CUSTOM_JOBS_API_TOKEN", "").strip()
CUSTOM_JOBS_QUERY_PARAM = os.getenv("CUSTOM_JOBS_QUERY_PARAM", "search").strip() or "search"
CUSTOM_JOBS_LIMIT_PARAM = os.getenv("CUSTOM_JOBS_LIMIT_PARAM", "limit").strip() or "limit"
CUSTOM_JOBS_LIMIT_VALUE = int(os.getenv("CUSTOM_JOBS_LIMIT_VALUE", "50"))
CUSTOM_JOBS_METHOD = os.getenv("CUSTOM_JOBS_METHOD", "GET").upper()
CUSTOM_JOBS_COUNTRY = os.getenv("CUSTOM_JOBS_COUNTRY", "US").strip() or "US"
CUSTOM_JOBS_MAX_AGE_DAYS = int(os.getenv("CUSTOM_JOBS_MAX_AGE_DAYS", "14"))
CUSTOM_JOBS_TEXT_FIELD = os.getenv("CUSTOM_JOBS_TEXT_FIELD", "text_or").strip() or "text_or"
CUSTOM_JOBS_DEBUG = os.getenv("CUSTOM_JOBS_DEBUG", "false").lower() == "true"


def load_model():
    """Load the trained model and data."""
    global job_data, vectorizer, job_vectors
    
    try:
        # Load data - use medium dataset to avoid memory issues
        if os.path.exists("data/job_dataset_medium.csv"):
            job_data = pd.read_csv("data/job_dataset_medium.csv")
            print(f"[OK] Loaded {len(job_data):,} jobs from medium dataset")
        elif os.path.exists("data/job_dataset_sample.csv"):
            job_data = pd.read_csv("data/job_dataset_sample.csv")
            print(f"[OK] Loaded {len(job_data):,} jobs from sample dataset")
        elif os.path.exists("data/unified_job_dataset.csv"):
            # Try to load a subset of the full dataset
            job_data = pd.read_csv("data/unified_job_dataset.csv", nrows=10000)
            print(f"[OK] Loaded {len(job_data):,} jobs from FULL dataset (subset)")
        else:
            print("[ERROR] No job dataset found!")
            return False
        
        # Load or create TF-IDF vectorizer and job vectors
        if os.path.exists("data/tfidf_vectorizer.joblib") and os.path.exists("data/trained_model.joblib"):
            try:
                vectorizer = joblib.load("data/tfidf_vectorizer.joblib")
                job_vectors = joblib.load("data/trained_model.joblib")
                if getattr(job_vectors, 'shape', (0,))[0] == len(job_data):
                    print(f"[OK] Loaded pre-trained TF-IDF vectorizer and job vectors ({job_vectors.shape[0]} jobs)")
                else:
                    raise ValueError(f"Vectors shape {job_vectors.shape[0]} doesn't match {len(job_data)} jobs")
            except Exception as e:
                print(f"[INFO] Re-indexing TF-IDF vectorizer: {e}")
                vectorizer = None
                job_vectors = None
        
        if vectorizer is None or job_vectors is None:
            try:
                print("[INFO] Building TF-IDF vectors for job dataset...")
                job_descriptions = []
                for _, row in job_data.iterrows():
                    desc_parts = []
                    if 'title' in row and pd.notna(row['title']):
                        desc_parts.append(str(row['title']))
                    if 'description' in row and pd.notna(row['description']):
                        desc_parts.append(str(row['description']))
                    elif 'skills' in row and pd.notna(row['skills']):
                        desc_parts.append(str(row['skills']))
                    job_descriptions.append(' '.join(desc_parts))
                
                vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
                job_vectors = vectorizer.fit_transform(job_descriptions)
                joblib.dump(vectorizer, "data/tfidf_vectorizer.joblib")
                joblib.dump(job_vectors, "data/trained_model.joblib")
                print(f"[OK] Created and saved TF-IDF vectorizer and job vectors ({job_vectors.shape[0]} jobs)")
            except Exception as e:
                print(f"[WARNING] Failed to build TF-IDF vectors: {e}")
                vectorizer = None
                job_vectors = None
            
        # Load interview datasets if available (temporarily disabled due to large file issues)
        global interview_questions_by_role
        interview_questions_by_role = None
        print("[INFO] Interview datasets temporarily disabled to prevent startup issues")

        # Load interview evaluator model if available
        global interview_evaluator
        if INTERVIEW_EVAL_AVAILABLE:
            try:
                interview_evaluator = InterviewEvaluator()
                if interview_evaluator.load("data/interview_evaluator.joblib"):
                    print("[OK] Loaded interview evaluator model")
                else:
                    print("[INFO] Interview evaluator model not found. Run: python train_interview_evaluator.py")
            except Exception as e:
                interview_evaluator = None
                print(f"[WARNING] Could not load interview evaluator: {e}")

        # Initialize OpenAI interview generator if available
        if OPENAI_AVAILABLE:
            # Try to get API key from environment or use the provided one
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key and initialize_openai_generator:
                try:
                    if initialize_openai_generator(openai_key):
                        print("[OK] OpenAI interview generator initialized")
                    else:
                        print("[WARNING] Failed to initialize OpenAI interview generator")
                except Exception as e:
                    print(f"[WARNING] OpenAI initialization error: {e}")
            else:
                print("[INFO] OpenAI API key not found. Set OPENAI_API_KEY environment variable for enhanced questions")

        # Initialize lightweight ML-based answer scorer (seed-trained)
        global ml_answer_scorer
        try:
            ml_answer_scorer = MLAnswerScorer()
            ml_answer_scorer.load_or_train()
            print("[OK] ML answer scorer ready (TF-IDF + LogisticRegression)")
        except Exception as e:
            ml_answer_scorer = None
            print(f"[WARNING] Could not initialize ML answer scorer: {e}")

        return True
    except Exception as e:
        import traceback
        print(f"[ERROR] Error loading model: {e}")
        print(f"[ERROR] Full traceback: {traceback.format_exc()}")
        return False


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file given as bytes."""
    if not PDF_ENABLED:
        return ""
    try:
        reader = PdfReader(BytesIO(file_bytes))
        pages_text = []
        for page in reader.pages:
            try:
                pages_text.append(page.extract_text() or "")
            except Exception:
                continue
        return "\n".join(pages_text)
    except Exception:
        return ""


def extract_skills_and_experience(text: str):
    """Simple extraction of skills and years of experience from text."""
    if not text:
        return {"skills": [], "years_experience": 0}

    lower = text.lower()

    # Basic skill list
    skill_list = [
        "python", "java", "javascript", "typescript", "react", "angular", "vue",
        "node", "node.js", "django", "flask", "spring", "spring boot", "sql",
        "mysql", "postgresql", "mongodb", "aws", "azure", "gcp", "docker",
        "kubernetes", "git", "jenkins", "ci/cd", "tensorflow", "pytorch",
        "scikit-learn", "machine learning", "data science", "nlp", "pandas",
        "numpy", "power bi", "tableau", "excel", "agile", "scrum", "jira"
    ]

    found_skills = []
    for skill in skill_list:
        if skill in lower:
            found_skills.append(skill)

    # Years of experience heuristics
    years = 0
    # Patterns like "5+ years", "3 years", "over 7 years"
    year_patterns = [
        r"(\d+)\+?\s*years",
        r"over\s+(\d+)\s*years",
        r"(\d+)\s*yrs",
    ]
    for pat in year_patterns:
        m = re.search(pat, lower)
        if m:
            try:
                years = max(years, int(m.group(1)))
            except Exception:
                pass

    return {"skills": sorted(set(found_skills)), "years_experience": years}


def fetch_live_jobs_from_arbeitnow(keywords: list[str], max_jobs: int = 30) -> list[dict]:
    """Fetch live jobs from Arbeitnow API using provided keywords.
    Uses simple search query combining top skills/keywords.
    """
    live_jobs: list[dict] = []
    try:
        if not keywords:
            print("[WARNING] No keywords provided for live job search")
            return live_jobs
        
        print(f"[SEARCH] Fetching live jobs for keywords: {keywords[:3]}")
        
        # Query per top skill to diversify results; cap to top 6 skills
        seen = set()
        for term in keywords[:6]:
            if not term or len(term) < 2:
                continue
            
            print(f"  Searching for: {term}")
            page = 1
            while len(live_jobs) < max_jobs and page <= 2:
                try:
                    resp = requests.get(
                        "https://arbeitnow.com/api/job-board-api",
                        params={"search": term, "page": page}, 
                        timeout=15,
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        }
                    )
                    
                    if resp.status_code != 200:
                        print(f"    [ERROR] Page {page}: HTTP {resp.status_code}")
                        break
                    
                    # Check content type
                    content_type = resp.headers.get("content-type", "")
                    if not content_type.startswith("application/json"):
                        print(f"    [WARNING] Page {page}: Non-JSON response ({content_type})")
                        break
                    
                    try:
                        payload = resp.json()
                    except json.JSONDecodeError as e:
                        print(f"    [ERROR] Page {page}: JSON decode error - {e}")
                        break
                    
                    if not isinstance(payload, dict):
                        print(f"    [WARNING] Page {page}: Response is not a dictionary")
                        break
                    
                    items = payload.get("data", [])
                    if not items:
                        print(f"    [INFO] Page {page}: No data found")
                        break
                    
                    print(f"    [OK] Page {page}: Found {len(items)} jobs")
                    
                    for it in items:
                        key = (it.get("title"), it.get("company_name"), it.get("location"))
                        if key in seen:
                            continue
                        seen.add(key)
                        
                        job_data = {
                            "title": it.get("title", "N/A"),
                            "company": it.get("company_name", "N/A"),
                            "location": it.get("location", "N/A"),
                            "description": it.get("description", "") or "",
                            "url": it.get("url", ""),
                            "remote": it.get("remote", False),
                            "tags": it.get("tags", []) or [],
                            "source": "arbeitnow"
                        }
                        
                        live_jobs.append(job_data)
                        
                        if len(live_jobs) >= max_jobs:
                            break
                    
                    page += 1
                    
                except requests.exceptions.Timeout:
                    print(f"    ⏰ Page {page}: Request timeout")
                    break
                except requests.exceptions.RequestException as e:
                    print(f"    [ERROR] Page {page}: Request error - {e}")
                    break
                except Exception as e:
                    print(f"    [ERROR] Page {page}: Unexpected error - {e}")
                    break
                
                if len(live_jobs) >= max_jobs:
                    break
                    
        print(f"[OK] Total live jobs fetched: {len(live_jobs)}")
        
    except Exception as e:
        print(f"[ERROR] Error in fetch_live_jobs_from_arbeitnow: {e}")
        import traceback
        traceback.print_exc()
    
    return live_jobs


def score_live_jobs(resume_text: str, skills: list[str], jobs: list[dict]) -> list[dict]:
    """Score live jobs by skill overlap and TF-IDF similarity to resume.
    Returns jobs with added fields: similarity_score (tfidf), skill_matches, final_score.
    """
    if not jobs:
        return []
    # Build resume vector once if vectorizer is available
    sim_available = vectorizer is not None
    resume_vec = None
    if sim_available:
        try:
            resume_vec = vectorizer.transform([resume_text])
        except Exception:
            sim_available = False

    skill_set = set((skills or [])[:12])
    scored = []
    for job in jobs:
        text_title = (job.get("title") or "").lower()
        text_desc = (job.get("description") or "").lower()
        tags_list = job.get("tags", []) or []
        text_tags = " ".join([str(t).lower() for t in tags_list])
        combined_text = f"{text_title}\n{text_desc}\n{text_tags}"
        # Skill matches
        title_hits = sum(1 for s in skill_set if s in text_title)
        desc_hits = sum(1 for s in skill_set if s in text_desc)
        tag_hits = sum(1 for s in skill_set if s in text_tags)
        # Total matches (heavier weight for title/tags)
        skill_matches = title_hits * 3 + tag_hits * 2 + desc_hits
        # TF-IDF similarity
        similarity_score = 0.0
        if sim_available:
            try:
                job_vec = vectorizer.transform([combined_text])
                from sklearn.metrics.pairwise import cosine_similarity
                similarity_score = float(cosine_similarity(resume_vec, job_vec)[0][0])
            except Exception:
                similarity_score = 0.0
        # Combine scores
        skill_norm = min(1.0, skill_matches / max(1.0, (len(skill_set) or 1.0) * 2))
        final_score = 0.75 * similarity_score + 0.25 * skill_norm + (0.05 if title_hits > 0 else 0.0)
        enriched = dict(job)
        enriched.update({
            "similarity_score": similarity_score,
            "skill_matches": int(skill_matches),
            "title_hits": int(title_hits),
            "tag_hits": int(tag_hits),
            "desc_hits": int(desc_hits),
            "final_score": float(final_score),
        })
        scored.append(enriched)
    # Gating rules: must have at least one strong evidence and enough relevance
    gated = []
    for j in scored:
        has_any_skill = j["skill_matches"] > 0
        strong_signal = j["title_hits"] > 0 or j["tag_hits"] > 0 or j["desc_hits"] >= 2
        if has_any_skill and strong_signal and j["final_score"] > 0.12:
            gated.append(j)
    scored = gated
    scored.sort(key=lambda x: (x["final_score"], x["similarity_score"], x["skill_matches"]), reverse=True)
    return scored


def fetch_live_jobs_from_custom_api(keywords: list[str], max_jobs: int = 50) -> list[dict]:
    """Fetch live jobs from a custom API requiring Bearer token.
    Expects JSON with top-level 'data' or 'items' or 'results'. Supports flexible field mapping.
    Reads base URL and token from env: CUSTOM_JOBS_API_URL, CUSTOM_JOBS_API_TOKEN.
    """
    live: list[dict] = []
    base = CUSTOM_JOBS_API_URL
    token = CUSTOM_JOBS_API_TOKEN
    if not base or not token or not keywords:
        return live
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    try:
        seen = set()
        for term in keywords[:6] or [""]:
            if not term:
                # still iterate pages without search term to fetch latest
                page = 1
            else:
                page = 1
            while len(live) < max_jobs and page <= 4:
                if CUSTOM_JOBS_METHOD == "POST":
                    body = {
                        "page": max(0, page - 1),
                        CUSTOM_JOBS_LIMIT_PARAM: CUSTOM_JOBS_LIMIT_VALUE,
                        "job_country_code_or": [CUSTOM_JOBS_COUNTRY],
                        "posted_at_max_age_days": CUSTOM_JOBS_MAX_AGE_DAYS,
                    }
                    if term:
                        # put search term under configurable text field
                        body[CUSTOM_JOBS_TEXT_FIELD] = [term]
                    resp = requests.post(base, json=body, headers=headers, timeout=25)
                else:
                    # GET fallback
                    params = {CUSTOM_JOBS_QUERY_PARAM: term, "page": page, CUSTOM_JOBS_LIMIT_PARAM: CUSTOM_JOBS_LIMIT_VALUE}
                    resp = requests.get(base, params=params, headers=headers, timeout=20)
                if resp.status_code != 200:
                    if CUSTOM_JOBS_DEBUG:
                        print(f"Custom jobs API non-200: {resp.status_code} {resp.text[:200]}")
                    break
                payload = resp.json() if "json" in resp.headers.get("content-type", "").lower() else {}
                items = []
                if isinstance(payload, dict):
                    for k in ("data", "items", "results", "jobs", "job_listings", "records"):
                        if isinstance(payload.get(k), list):
                            items = payload[k]
                            break
                elif isinstance(payload, list):
                    items = payload
                if not items:
                    if CUSTOM_JOBS_DEBUG:
                        print("Custom jobs API empty items for term:", term)
                    break
                for it in items:
                    # Flexible field mapping
                    title = it.get("title") or it.get("position") or it.get("job_title") or "N/A"
                    company = it.get("company") or it.get("company_name") or it.get("employer") or (it.get("organization", {}) or {}).get("name") or "N/A"
                    location = it.get("location") or it.get("city") or it.get("job_city") or it.get("region") or it.get("country") or "N/A"
                    description = it.get("description") or it.get("summary") or it.get("job_description") or ""
                    url = it.get("url") or it.get("job_url") or it.get("apply_link") or it.get("application_url") or ""
                    tags = it.get("tags") or it.get("skills") or []
                    key = (title, company, location, url)
                    if key in seen:
                        continue
                    seen.add(key)
                    live.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "description": description,
                        "url": url,
                        "remote": bool(it.get("remote", False)),
                        "tags": tags if isinstance(tags, list) else [],
                        "source": "custom"
                    })
                    if len(live) >= max_jobs:
                        break
                page += 1
                if len(live) >= max_jobs:
                    break
            if len(live) >= max_jobs:
                break
    except Exception:
        if CUSTOM_JOBS_DEBUG:
            import traceback; traceback.print_exc()
        pass
    return live


def generate_fallback_live_jobs(keywords: list[str], max_jobs: int = 20) -> list[dict]:
    """Generate fallback live jobs when external APIs fail."""
    print("🔄 Generating fallback live jobs...")
    
    # Sample job templates based on common tech roles
    job_templates = [
        {
            "title": "Senior {skill} Developer",
            "company": "TechCorp Solutions",
            "location": "Remote / New York, NY",
            "description": "We are seeking a Senior {skill} Developer to join our growing team. Experience with modern development practices and cloud technologies required.",
            "url": "https://example.com/job1",
            "remote": True,
            "tags": ["{skill}", "senior", "remote"],
            "source": "fallback"
        },
        {
            "title": "{skill} Software Engineer",
            "company": "Innovation Labs",
            "location": "San Francisco, CA",
            "description": "Join our team as a {skill} Software Engineer. We're building cutting-edge applications using the latest technologies.",
            "url": "https://example.com/job2",
            "remote": False,
            "tags": ["{skill}", "software engineer", "full-time"],
            "source": "fallback"
        },
        {
            "title": "Full Stack {skill} Developer",
            "company": "Digital Dynamics",
            "location": "Austin, TX",
            "description": "Full Stack {skill} Developer needed for exciting projects. Experience with modern frameworks and databases preferred.",
            "url": "https://example.com/job3",
            "remote": True,
            "tags": ["{skill}", "full stack", "remote"],
            "source": "fallback"
        },
        {
            "title": "{skill} Developer - Entry Level",
            "company": "Startup Ventures",
            "location": "Remote / Anywhere",
            "description": "Entry level {skill} developer position. Great opportunity for recent graduates or career changers.",
            "url": "https://example.com/job4",
            "remote": True,
            "tags": ["{skill}", "entry level", "remote"],
            "source": "fallback"
        },
        {
            "title": "Lead {skill} Developer",
            "company": "Enterprise Systems",
            "location": "Chicago, IL",
            "description": "Lead {skill} Developer to guide our development team. Leadership experience and technical expertise required.",
            "url": "https://example.com/job5",
            "remote": False,
            "tags": ["{skill}", "lead", "leadership"],
            "source": "fallback"
        }
    ]
    
    live_jobs = []
    seen_companies = set()
    
    for i in range(min(max_jobs, len(job_templates) * len(keywords))):
        template = job_templates[i % len(job_templates)]
        skill = keywords[i % len(keywords)] if keywords else "Python"
        
        # Customize template with skill
        job = {
            "title": template["title"].format(skill=skill.title()),
            "company": template["company"],
            "location": template["location"],
            "description": template["description"].format(skill=skill.title()),
            "url": template["url"],
            "remote": template["remote"],
            "tags": [tag.format(skill=skill) if "{skill}" in tag else tag for tag in template["tags"]],
            "source": template["source"]
        }
        
        # Ensure unique companies
        if job["company"] not in seen_companies:
            seen_companies.add(job["company"])
            live_jobs.append(job)
        
        if len(live_jobs) >= max_jobs:
            break
    
    print(f"[OK] Generated {len(live_jobs)} fallback live jobs")
    return live_jobs


# -------- Virtual Interview Helpers --------
def generate_interview_questions(skills: list[str], role_hint: str = "", level_hint: str = "any", num_questions: int = 6) -> list[dict]:
    """Generate interview questions using OpenAI, loaded datasets, or fallback templates."""
    global interview_questions_by_role, openai_interview_generator
    
    # First try OpenAI for enhanced questions
    if OPENAI_AVAILABLE and openai_interview_generator:
        try:
            print(f"🤖 Generating questions with OpenAI for role: {role_hint}, skills: {skills}")
            
            # Determine category based on role hint
            category = "technical"  # Default to technical
            role_lower = role_hint.lower()
            if "behavioral" in role_lower:
                category = "behavioral"
            elif "hr" in role_lower or "personality" in role_lower:
                category = "behavioral"
            elif "communication" in role_lower:
                category = "behavioral"
            elif "case" in role_lower or "situational" in role_lower:
                category = "problem_solving"
            elif "system" in role_lower or "design" in role_lower:
                category = "system_design"
            
            print(f"🎯 Determined category: {category} for role: {role_hint}")
            
            openai_questions = generate_enhanced_interview_questions(skills, role_hint, category, num_questions)
            if openai_questions and len(openai_questions) > 0:
                print(f"[OK] Generated {len(openai_questions)} questions using OpenAI")
                return openai_questions
            else:
                print("[WARNING] OpenAI returned no questions, falling back to enhanced method")
        except Exception as e:
            print(f"[WARNING] OpenAI question generation failed: {e}, falling back to enhanced method")
    
    # Try enhanced fallback system
    if ENHANCED_FALLBACK_AVAILABLE and get_enhanced_questions:
        try:
            # Determine category for fallback (same logic as OpenAI)
            category = "technical"  # Default to technical
            role_lower = role_hint.lower() if role_hint else ""
            if "behavioral" in role_lower:
                category = "behavioral"
            elif "hr" in role_lower or "personality" in role_lower:
                category = "behavioral"
            elif "communication" in role_lower:
                category = "behavioral"
            elif "case" in role_lower or "situational" in role_lower:
                category = "problem_solving"
            elif "system" in role_lower or "design" in role_lower:
                category = "system_design"
            
            print(f"🎯 Using enhanced fallback for role: {role_hint}, category: {category}, skills: {skills}")
            enhanced_questions = get_enhanced_questions(skills, role_hint, category, num_questions)
            if enhanced_questions and len(enhanced_questions) > 0:
                print(f"[OK] Generated {len(enhanced_questions)} questions using enhanced fallback")
                return enhanced_questions
        except Exception as e:
            print(f"[WARNING] Enhanced fallback failed: {e}, using traditional method")
    
    # If no role hint, infer from skills to improve relevance
    if not role_hint:
        sset = set([s.lower() for s in (skills or [])])
        frontend_keys = {"react", "angular", "vue", "javascript", "typescript", "frontend", "next.js", "nextjs"}
        backend_keys = {"django", "flask", "node", "node.js", "express", "spring", "java", "backend", "graphql", "prisma"}
        fullstack_keys = {"fullstack", "full-stack", "mern", "mean", "next.js", "express"}
        data_sci_keys = {"pandas", "numpy", "scikit-learn", "sklearn", "tensorflow", "pytorch", "data science", "data scientist", "machine learning", "ml", "ai", "matplotlib", "seaborn", "jupyter", "statistics"}
        devops_keys = {"aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "jenkins", "terraform", "ansible"}
        qa_keys = {"qa", "testing", "selenium", "cypress", "jest", "playwright"}
        analyst_keys = {"power bi", "tableau", "excel", "sql", "analytics", "bi"}

        # Fullstack if explicit or both FE and BE signals
        if (fullstack_keys & sset) or ((frontend_keys & sset) and (backend_keys & sset)):
            role_hint = "fullstack developer"
        elif frontend_keys & sset:
            role_hint = "frontend developer"
        elif backend_keys & sset:
            role_hint = "backend developer"
        elif data_sci_keys & sset:
            # Use the label the user asked for; evaluator will fallback if role not present
            role_hint = "data science"
        elif devops_keys & sset:
            role_hint = "devops engineer"
        elif qa_keys & sset:
            role_hint = "qa engineer"
        elif analyst_keys & sset:
            role_hint = "data analyst"
        else:
            role_hint = "software engineer"
    # Prefer dataset-driven selection, then re-rank using trained evaluator keywords if available
    if interview_questions_by_role and choose_questions_for_interview:
        try:
            # Pull a larger candidate pool first
            candidate_pool = choose_questions_for_interview(
                interview_questions_by_role,
                role=role_hint,
                level=level_hint,
                skills=skills,
                num_questions=max(num_questions * 3, num_questions + 4),
                time_limit_sec=90,
            ) or []

            # Re-rank by overlap with user's skills and (if available) evaluator role keywords
            if interview_evaluator and hasattr(interview_evaluator, "role_to_keywords"):
                role_norm = _normalize_role(role_hint) if (_normalize_role and role_hint) else "general"
                # Fall back to global keywords if role-specific not found
                role_keys = interview_evaluator.role_to_keywords.get(role_norm) or interview_evaluator.global_keywords or []
                role_key_set = set([k.lower() for k in role_keys])
                # If fullstack role, augment with common FE/BE keywords
                if "fullstack" in (role_norm or "") or "full-stack" in (role_norm or ""):
                    fe = {"react", "angular", "vue", "javascript", "typescript", "next.js", "nextjs", "frontend"}
                    be = {"node", "node.js", "express", "django", "flask", "spring", "java", "graphql", "prisma", "backend"}
                    role_key_set.update({k.lower() for k in fe | be})
                user_skill_set = set([s.lower() for s in (skills or [])])

                def score_q(q: dict) -> tuple:
                    text = (q.get("text") or "").lower()
                    # Overlap with evaluator keywords
                    hits = sum(1 for k in role_key_set if k in text)
                    # Prefer questions that target user skill gaps
                    gap_hits = sum(1 for k in role_key_set if (k not in user_skill_set and k in text))
                    # Small boost if tags indicate evaluator keywords
                    tags = set((q.get("tags") or []))
                    tag_hits = len(tags & role_key_set)
                    # Strong weight: overlap with user's own skills
                    skill_hits = sum(1 for s in user_skill_set if s in text)
                    # Deterministic sort: prioritize skill_hits, then gap_hits, then evaluator hits, then tag hits, then brevity
                    return (skill_hits, gap_hits, hits, tag_hits, -min(len(text), 200))

                candidate_pool.sort(key=score_q, reverse=True)
                selected = candidate_pool[:num_questions]
                # If no meaningful overlap, synthesize from evaluator keywords instead
                if selected:
                    top_score = score_q(selected[0])
                    # any signal among: skill_hits, gap_hits, hits, tag_hits
                    if any(top_score[:-1]):
                        return selected
                    # else fall through to synthesis below
            else:
                # No evaluator: re-rank purely by user's skill overlap
                user_skill_set = set([s.lower() for s in (skills or [])])
                def score_q_plain(q: dict) -> tuple:
                    text = (q.get("text") or "").lower()
                    skill_hits = sum(1 for s in user_skill_set if s in text)
                    return (skill_hits, -min(len(text), 200))
                candidate_pool.sort(key=score_q_plain, reverse=True)
                selected = candidate_pool[:num_questions]
                if selected and score_q_plain(selected[0])[0] > 0:
                    return selected
        except Exception:
            pass

    # If we reach here, either datasets are unavailable or selection failed.
    # Synthesize questions from the trained evaluator keywords if available.
    if interview_evaluator and hasattr(interview_evaluator, "global_keywords"):
        role_norm = _normalize_role(role_hint) if (_normalize_role and role_hint) else "general"
        role_keys = interview_evaluator.role_to_keywords.get(role_norm) or interview_evaluator.global_keywords[:40]
        role_keys = [k for k in role_keys if k]
        # Prioritize topics not already in user's skills (focus on breadth)
        user_skill_set = set([s.lower() for s in (skills or [])])
        prioritized = [k for k in role_keys if k not in user_skill_set] + [k for k in role_keys if k in user_skill_set]
        templates = [
            "Describe a recent project where you applied {kw}. What challenges did you face and how did you address them?",
            "How would you explain {kw} to a junior teammate, and what are common pitfalls to avoid?",
            "Discuss performance or reliability considerations when working with {kw}. Provide specific examples.",
            "Can you compare {kw} with an alternative approach/technology and justify your choice in a real scenario?",
            "Walk me through how you would design a solution leveraging {kw}. What trade-offs would you consider?",
        ]
        texts: list[str] = []
        ti = 0
        for kw in prioritized:
            t = templates[ti % len(templates)].format(kw=kw)
            texts.append(t)
            if len(texts) >= num_questions:
                break
            ti += 1
        if texts:
            return [{"id": i + 1, "text": t, "time_limit_sec": 90} for i, t in enumerate(texts)]

    # Final fallback: synthesize from user's explicit skills if any
    if skills:
        templates = [
            "Explain a recent project where you used {kw}. What trade-offs did you consider?",
            "How would you teach {kw} to a junior developer? Include pitfalls.",
            "What performance or reliability issues have you faced with {kw} and how did you solve them?",
        ]
        texts = []
        for i, kw in enumerate(skills[:num_questions]):
            texts.append(templates[i % len(templates)].format(kw=kw))
        if texts:
            return [{"id": i + 1, "text": t, "time_limit_sec": 90} for i, t in enumerate(texts)]

    # Absolute last fallback: generic
    base_questions = [
        "Tell me about a challenging project you worked on and your specific contributions.",
        "Describe a time you optimized performance or improved reliability. What was the impact?",
        "How do you keep your skills up to date and learn new technologies?",
    ]
    top_skills = (skills or [])[:5]
    skill_questions = [
        f"Explain a recent use of {s} in a production setting. What trade-offs did you consider?" for s in top_skills
    ]
    role_q = []
    if role_hint:
        role_q.append(f"What makes you a strong fit for a {role_hint} role at this time?")
    texts = role_q + skill_questions + base_questions
    seen = set()
    final = []
    for t in texts:
        if t not in seen:
            seen.add(t)
            final.append(t)
    final = final[:num_questions] or base_questions
    return [{"id": i + 1, "text": t, "time_limit_sec": 90} for i, t in enumerate(final)]


def score_answers_simple(questions: list[dict], answers: list[str], skills: list[str]) -> dict:
    """Very simple scoring: counts skill keyword mentions and answer length.
    Returns {total_score, per_answer}.
{{ ... }}
    """
    skill_set = set((skills or [])[:10])
    per = []
    total = 0.0
    for q, a in zip(questions, answers):
        a_text = (a or "").lower()
        length_pts = min(1.0, len(a_text.split()) / 80.0)  # up to ~1 for ~80+ words
        skill_pts = 0.0
        if skill_set:
            hits = sum(1 for s in skill_set if s in a_text)
            skill_pts = min(1.0, hits / max(1.0, len(skill_set) / 3.0))
        score = 0.6 * length_pts + 0.4 * skill_pts
        total += score
        per.append({"question_id": q.get("id"), "score": round(score, 2)})
    total_norm = round((total / max(1, len(per))) * 100.0, 1)
    return {"total_score": total_norm, "per_answer": per}


class MLAnswerScorer:
    """Lightweight ML scorer for interview answers.
    Pipeline: TF-IDF (unigrams+bigrams) -> LogisticRegression (good vs poor).
    Trains on seed examples at startup; can be improved with real labeled data later.
    """
    def __init__(self):
        self.pipeline: Pipeline | None = None
        self.model_path = os.path.join("data", "ml_answer_scorer.joblib")

    def load_or_train(self):
        """Load persisted model if present; else train from CSV; else seed; then persist."""
        # 1) Try load persisted
        try:
            if os.path.exists(self.model_path):
                self.pipeline = joblib.load(self.model_path)
                return
        except Exception:
            self.pipeline = None
        # 2) Train from CSV if available
        csv_path = os.path.join("data", "answer_labels.csv")
        if os.path.exists(csv_path):
            try:
                import pandas as pd  # already dependency
                df = pd.read_csv(csv_path)
                # Accept columns: text,label OR answer,label; optional question column to be prepended
                text_col = "text" if "text" in df.columns else ("answer" if "answer" in df.columns else None)
                label_col = "label" if "label" in df.columns else None
                if text_col and label_col:
                    X = df[text_col].fillna("").astype(str).tolist()
                    if "question" in df.columns:
                        q = df["question"].fillna("").astype(str).tolist()
                        X = [f"{qq}\n{aa}" if qq else aa for qq, aa in zip(q, X)]
                    y = df[label_col].astype(int).tolist()
                    self._fit_and_persist(X, y)
                    return
            except Exception:
                pass
        # 3) Fallback to seed
        self.fit_on_seed_data()
        self._persist()

    def fit_on_seed_data(self):
        # Seed dataset: minimal illustrative examples. Replace/extend with real labeled data when available.
        good = [
            "I structured the project by defining clear milestones, coordinated with stakeholders, and measured impact against KPIs.",
            "We optimized the service by profiling bottlenecks, reducing query latency by 40% and improving reliability with retries.",
            "I mentored juniors, documented key decisions, and led a postmortem to capture lessons learned.",
            "Designed a scalable API with pagination, caching, and auth; results improved throughput and reduced costs.",
        ]
        poor = [
            "I don't know.",
            "Not sure, it depends.",
            "We just did it somehow.",
            "No idea what happened.",
        ]
        X = good + poor
        y = [1] * len(good) + [0] * len(poor)
        pipe = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=20000)),
            ("clf", LogisticRegression(max_iter=1000))
        ])
        pipe.fit(X, y)
        self.pipeline = pipe

    def score(self, answer: str, question_text: str = "", role_hint: str = "") -> float:
        if not self.pipeline:
            return 0.0
        # Concatenate question to give contextual cues
        text = (answer or "").strip()
        if question_text:
            text = question_text.strip() + "\n" + text
        try:
            proba = self.pipeline.predict_proba([text])[0][1]
            return float(proba)
        except Exception:
            return 0.0

    def _fit_and_persist(self, X, y):
        pipe = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=20000)),
            ("clf", LogisticRegression(max_iter=1000))
        ])
        pipe.fit(X, y)
        self.pipeline = pipe
        self._persist()

    def _persist(self):
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            if self.pipeline is not None:
                joblib.dump(self.pipeline, self.model_path)
        except Exception:
            pass


@app.route('/')
def index():
    """Main page."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Career Guidance Platform</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; margin-bottom: 30px; }
            h1 { color: #333; }
            textarea { width: 100%; height: 150px; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
            button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            button:hover { background: #0056b3; }
            .results { margin-top: 20px; }
            .job { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }
            .loading { text-align: center; color: #666; }
            .row { display: grid; grid-template-columns: 1fr; gap: 16px; }
            .stat { color:#666; font-size: 13px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>[START] Career Guidance Platform</h1>
                <p>AI-Powered Job Matching with 123K+ Real Jobs!</p>
                <p class="stat">PDF upload: {{ 'enabled' if pdf_enabled else 'disabled' }}</p>
            </div>
            
            <div class="row">
                <form id="resumeForm">
                    <label><strong>Paste your resume:</strong></label><br>
                    <textarea id="resumeText" placeholder="Enter your resume text here..."></textarea><br>
                    <button type="submit">Find Matching Jobs</button>
                </form>

                <form id="uploadForm" enctype="multipart/form-data" style="margin-top:12px;">
                    <label><strong>Or upload a resume (PDF/TXT):</strong></label><br>
                    <input type="file" id="resumeFile" name="resume_file" accept=".pdf,.txt" />
                    <button type="button" id="uploadBtn">Upload & Match</button>
                </form>
            </div>
            
            <div id="loading" class="loading" style="display:none;">Processing...</div>
            <div id="results" class="results"></div>

            <div id="features" class="results" style="display:block;">
                <h3>Platform Features</h3>
                <div class="job">
                    <div><strong>Virtual Interview</strong></div>
                    <div style="margin-top:6px;">Practice a timed, interactive interview with questions tailored to your profile.</div>
                    <div style="margin-top:8px;"><a href="/interview"><button>Go to Virtual Interview</button></a></div>
                </div>
            </div>
        </div>
        
        <script>
            async function renderResults(data) {
                if (data.success) {
                    let html = '';
                    if (data.parsed) {
                        html += '<div class="job"><strong>Parsed Resume</strong><br/>' +
                            (data.parsed.skills && data.parsed.skills.length ? ('Skills: ' + data.parsed.skills.join(', ') + '<br/>') : '') +
                            ('Experience: ' + (data.parsed.years_experience || 0) + ' years') + '</div>';
                    }
                    html += '<h3>Job Matches:</h3>';
                    data.jobs.forEach(job => {
                        html += `
                            <div class="job">
                                <h4>${job.title}</h4>
                                <p><strong>Company:</strong> ${job.company}</p>
                                <p><strong>Location:</strong> ${job.location}</p>
                                <p><strong>Match:</strong> ${(job.similarity_score * 100).toFixed(1)}%</p>
                            </div>
                        `;
                    });
                    if (data.live_jobs && data.live_jobs.length) {
                        html += '<h3>Live Jobs</h3>';
                        data.live_jobs.forEach(job => {
                            html += `
                                <div class="job">
                                    <h4>${job.title}</h4>
                                    <p><strong>Company:</strong> ${job.company}</p>
                                    <p><strong>Location:</strong> ${job.location}</p>
                                    ${job.url ? `<p><a href="${job.url}" target="_blank">View Job</a></p>` : ''}
                                </div>
                            `;
                        });
                    }
                    document.getElementById('results').innerHTML = html;
                    // Parsed info cached if needed later
                    window.__parsed = data.parsed || {};
                } else {
                    document.getElementById('results').innerHTML = '<p style="color:red;">Error: ' + (data.error || 'Unknown error') + '</p>';
                }
            }

            document.getElementById('resumeForm').onsubmit = async function(e) {
                e.preventDefault();
                const text = document.getElementById('resumeText').value || '';
                if (!text) return;
                document.getElementById('loading').style.display = 'block';
                document.getElementById('results').innerHTML = '';
                try {
                    const response = await fetch('/recommend', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({resume_text: text})
                    });
                    const data = await response.json();
                    await renderResults(data);
                } catch (error) {
                    document.getElementById('results').innerHTML = '<p style="color:red;">Error: ' + error.message + '</p>';
                }
                document.getElementById('loading').style.display = 'none';
            };

            document.getElementById('uploadBtn').onclick = async function() {
                const fileInput = document.getElementById('resumeFile');
                if (!fileInput.files || !fileInput.files[0]) {
                    alert('Please choose a PDF or TXT file');
                    return;
                }
                const formData = new FormData();
                formData.append('resume_file', fileInput.files[0]);
                document.getElementById('loading').style.display = 'block';
                document.getElementById('results').innerHTML = '';
                try {
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await response.json();
                    await renderResults(data);
                } catch (error) {
                    document.getElementById('results').innerHTML = '<p style="color:red;">Error: ' + error.message + '</p>';
                }
                document.getElementById('loading').style.display = 'none';
            };

            // Floating Chatbot (bottom-right) using live interview endpoints
            (function(){
              const btn = document.createElement('button');
              btn.textContent = 'Chatbot';
              btn.style.position='fixed'; btn.style.bottom='20px'; btn.style.right='20px';
              btn.style.zIndex='9999'; btn.style.borderRadius='999px';
              btn.style.padding='10px 16px'; btn.style.background='#2563eb'; btn.style.color='#fff';
              btn.style.border='1px solid #1d4ed8'; btn.style.boxShadow='0 4px 12px rgba(0,0,0,0.2)';
              document.body.appendChild(btn);

              const panel = document.createElement('div');
              panel.style.position='fixed'; panel.style.bottom='70px'; panel.style.right='20px';
              panel.style.width='320px'; panel.style.height='420px';
              panel.style.background='#0b1220'; panel.style.color='#e2e8f0';
              panel.style.border='1px solid #1f2937'; panel.style.borderRadius='12px';
              panel.style.display='none'; panel.style.zIndex='9999';
              panel.innerHTML = `
                <div style="padding:8px 10px; background:#111827; border-bottom:1px solid #1f2937; display:flex;justify-content:space-between;align-items:center;">
                  <div style="font-weight:700;">Assistant</div>
                  <button id="cbClose" style="background:#374151;color:#fff;border:none;border-radius:6px;padding:4px 8px;">×</button>
                </div>
                <div id="cbChat" style="height:300px; overflow:auto; padding:8px;"></div>
                <div style="padding:8px; display:flex; gap:6px;">
                  <input id="cbInput" placeholder="Type message..." style="flex:1; padding:8px; border-radius:8px; border:1px solid #374151; background:#0b1220; color:#e2e8f0;" />
                  <button id="cbSend" style="padding:8px 10px; border-radius:8px; border:1px solid #374151; background:#2563eb; color:white;">Send</button>
                </div>
              `;
              document.body.appendChild(panel);

              let sid = null;
              function pushAI(t){ const d=document.createElement('div'); d.style.margin='6px 0'; d.innerHTML = `<div style="background:#0e7490;color:#ecfeff;padding:8px;border-radius:10px; display:inline-block;">${t}</div>`; document.getElementById('cbChat').appendChild(d); document.getElementById('cbChat').scrollTop = document.getElementById('cbChat').scrollHeight; }
              function pushMe(t){ const d=document.createElement('div'); d.style.margin='6px 0'; d.style.textAlign='right'; d.innerHTML = `<div style="background:#334155;color:#f8fafc;padding:8px;border-radius:10px; display:inline-block;">${t}</div>`; document.getElementById('cbChat').appendChild(d); document.getElementById('cbChat').scrollTop = document.getElementById('cbChat').scrollHeight; }

              async function ensureSession(){
                if(sid) return sid;
                try{
                  const parsed = window.__parsed || {}; const skills = parsed.skills || [];
                  const r = await fetch('/interview/live/start',{method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({skills})});
                  const data = await r.json(); if(data.success){ sid = data.session_id; pushAI(data.message); }
                }catch(e){ pushAI('Error starting session'); }
                return sid;
              }
              async function send(){
                const val = document.getElementById('cbInput').value.trim();
                if(!val) return; document.getElementById('cbInput').value=''; pushMe(val);
                await ensureSession(); if(!sid){ pushAI('Unable to start session'); return; }
                try{
                  const r = await fetch('/interview/live/answer',{method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({session_id:sid, answer: val})});
                  const data = await r.json(); if(!data.success){ pushAI('Error: '+(data.error||'')); return; }
                  pushAI(data.message);
                  if(data.done){ pushAI(`Interview finished. Score: ${data.result?.total_score||0}%`); sid = null; }
                }catch(e){ pushAI('Network error'); }
              }
              btn.onclick = () => { panel.style.display = (panel.style.display==='none' ? 'block' : 'none'); if(panel.style.display==='block'){ ensureSession(); }}
              panel.querySelector('#cbClose').onclick = () => { panel.style.display='none'; }
              panel.querySelector('#cbSend').onclick = send;
              panel.querySelector('#cbInput').addEventListener('keydown', (e)=>{ if(e.key==='Enter'){ e.preventDefault(); send(); } });
            })();
        </script>
    </body>
    </html>
    """
    return render_template_string(html, pdf_enabled=PDF_ENABLED)


@app.route('/recommend', methods=['POST', 'OPTIONS'])
@app.route('/api/recommend', methods=['POST', 'OPTIONS'])
def recommend():
    """Get job recommendations from text."""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
    try:
        data = request.get_json(silent=True) or {}
        resume_text = data.get('resume_text', '')
        
        if not resume_text:
            return jsonify({'success': False, 'error': 'No resume text provided'})
        
        if job_data is None:
            return jsonify({'success': False, 'error': 'Job data not loaded'})
        
        # Simple matching logic
        from sklearn.metrics.pairwise import cosine_similarity
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        if vectorizer is None or job_vectors is None:
            print("[INFO] Creating TF-IDF vectors on-demand...")
            
            # Create job descriptions
            job_descriptions = []
            for _, row in job_data.iterrows():
                desc_parts = []
                if 'title' in row and pd.notna(row['title']):
                    desc_parts.append(str(row['title']))
                if 'description' in row and pd.notna(row['description']):
                    desc_parts.append(str(row['description']))
                elif 'skills' in row and pd.notna(row['skills']):
                    desc_parts.append(str(row['skills']))
                job_descriptions.append(' '.join(desc_parts))
            
            # Create vectorizer and fit on job descriptions
            temp_vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
            all_texts = [resume_text] + job_descriptions
            tfidf_matrix = temp_vectorizer.fit_transform(all_texts)
            
            # Get vectors
            resume_vector = tfidf_matrix[0:1]
            temp_job_vectors = tfidf_matrix[1:]
            
            # Calculate similarities
            similarities = cosine_similarity(resume_vector, temp_job_vectors).flatten()
        else:
            # Use pre-trained vectors
            resume_vector = vectorizer.transform([resume_text])
            similarities = cosine_similarity(resume_vector, job_vectors).flatten()
        
        # Get top 5 matches
        top_indices = similarities.argsort()[-5:][::-1]
        
        # Debug logging
        max_sim = similarities.max() if len(similarities) > 0 else 0
        print(f"[SEARCH] Job matching debug: max_similarity={max_sim:.4f}, total_jobs={len(job_data)}")
        
        jobs = []
        for idx in top_indices:
            if idx < 0 or idx >= len(job_data):
                continue
            sim_score = similarities[idx]
            print(f"   Candidate job {idx}: similarity={sim_score:.4f}")
            if sim_score > 0.001:  # Lower minimum similarity threshold
                job = job_data.iloc[idx]
                jobs.append({
                    'title': str(job.get('title', 'N/A')),
                    'company': str(job.get('company', 'N/A')),
                    'location': str(job.get('location', 'N/A')),
                    'similarity_score': float(sim_score)
                })
        
        print(f"[OK] Found {len(jobs)} matching jobs above threshold")
        
        parsed = extract_skills_and_experience(resume_text)
        # Compose keywords from parsed skills and top matched titles
        title_terms = []
        for j in jobs[:3]:
            if j.get("title"):
                title_terms.extend([t for t in re.split(r"[^a-zA-Z]+", j["title"].lower()) if t and len(t) > 2])
        # Prioritize skills; fallback to title terms
        keywords = parsed.get("skills", []) or list(dict.fromkeys(title_terms))
        
        print(f"[SEARCH] Attempting to fetch live jobs for keywords: {keywords[:3]}")
        
        # Try to fetch live jobs from external APIs
        live_raw = fetch_live_jobs_from_arbeitnow(keywords, max_jobs=40)
        live_custom = fetch_live_jobs_from_custom_api(keywords, max_jobs=60)
        
        # Merge & dedupe
        if live_custom:
            merged = []
            seen_keys = set()
            for src in (live_raw, live_custom):
                for j in src:
                    key = (j.get("title"), j.get("company"), j.get("location"), j.get("url"))
                    if key in seen_keys:
                        continue
                    seen_keys.add(key)
                    merged.append(j)
            live_raw = merged
        
        # If no live jobs fetched, use fallback
        if not live_raw:
            print("[WARNING] No live jobs fetched from external APIs, using fallback")
            live_raw = generate_fallback_live_jobs(keywords, max_jobs=20)
        else:
            print(f"[OK] Successfully fetched {len(live_raw)} live jobs from external APIs")
        
        live_jobs = score_live_jobs(resume_text, parsed.get("skills", []), live_raw)[:10]

        # Add skill gap analysis for top recommended jobs
        skill_gap_analyses = []
        user_skills = parsed.get("skills", [])
        if user_skills and jobs:
            for i, job in enumerate(jobs[:3]):  # Top 3 jobs
                try:
                    # Get job description from the dataset
                    job_idx = top_indices[i] if i < len(top_indices) else None
                    if job_idx is not None and job_idx < len(job_data):
                        job_row = job_data.iloc[job_idx]
                        job_desc = str(job_row.get('description', ''))
                        if job_desc:
                            analysis = analyze_skill_gap(user_skills, job_desc, job.get('title', ''))
                            if 'error' not in analysis:
                                analysis['job_id'] = int(job_idx)
                                analysis['job_title'] = job.get('title', '')
                                skill_gap_analyses.append(analysis)
                except Exception as e:
                    print(f"Error analyzing skill gap for job {i}: {e}")
                    continue

        return jsonify({
            'success': True, 
            'jobs': jobs, 
            'parsed': parsed, 
            'live_jobs': live_jobs,
            'skill_gap_analyses': skill_gap_analyses
        })
        
    except Exception as e:
        print(f"Error in recommend: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/interview/questions', methods=['POST', 'OPTIONS'])
@app.route('/interview/questions', methods=['POST', 'OPTIONS'])
def interview_questions():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
    
    try:
        payload = request.get_json() or {}
        skills = payload.get('skills') or []
        role_hint = payload.get('role_hint') or ''
        level_hint = payload.get('level_hint') or 'any'
        num_questions = int(payload.get('num_questions') or 6)
        qs = generate_interview_questions(skills, role_hint, level_hint, num_questions)
        return jsonify({'success': True, 'questions': qs})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/interview/submit', methods=['POST', 'OPTIONS'])
@app.route('/interview/submit', methods=['POST', 'OPTIONS'])
def interview_submit():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
        
    try:
        payload = request.get_json() or {}
        qs = payload.get('questions') or []
        answers = payload.get('answers') or []
        skills = payload.get('skills') or []
        role_hint = payload.get('role_hint') or ''
        if not qs or not answers:
            return jsonify({'success': False, 'error': 'Missing questions or answers'}), 400
        # Try OpenAI evaluation first, then fall back to local evaluator
        if OPENAI_AVAILABLE and openai_interview_generator:
            try:
                print("🤖 Using OpenAI for interview evaluation")
                per = []
                total = 0.0
                for q, a in zip(qs, answers):
                    if a and a.strip():  # Only evaluate non-empty answers
                        fb = openai_interview_generator.evaluate_answer(
                            question=q.get('text', ''),
                            answer=a,
                            skills=skills,
                            role_hint=role_hint
                        )
                        per.append({
                            'question_id': q.get('id'),
                            'score': fb.get('score', 70),
                            'strengths': fb.get('strengths', []),
                            'improvements': fb.get('improvements', []),
                            'technical_accuracy': fb.get('technical_accuracy', 70),
                            'communication': fb.get('communication', 70),
                            'problem_solving': fb.get('problem_solving', 70),
                            'overall_feedback': fb.get('overall_feedback', ''),
                            'follow_up_suggestions': fb.get('follow_up_suggestions', [])
                        })
                        total += float(fb.get('score', 70))
                    else:
                        # Handle empty answers
                        per.append({
                            'question_id': q.get('id'),
                            'score': 0,
                            'strengths': [],
                            'improvements': ['No answer provided'],
                            'technical_accuracy': 0,
                            'communication': 0,
                            'problem_solving': 0,
                            'overall_feedback': 'No response was provided for this question.',
                            'follow_up_suggestions': ['Practice answering this type of question']
                        })
                
                total_norm = round((total / max(1, len([a for a in answers if a and a.strip()]))), 1) if any(a and a.strip() for a in answers) else 0
                result = {'total_score': total_norm, 'per_answer': per, 'evaluation_method': 'OpenAI'}
                print(f"[OK] OpenAI evaluation completed. Total score: {total_norm}")
                
            except Exception as e:
                print(f"[WARNING] OpenAI evaluation failed: {e}, falling back to local evaluator")
                # Fall back to local evaluator
                if interview_evaluator and hasattr(interview_evaluator, 'score_and_feedback'):
                    per = []
                    total = 0.0
                    for q, a in zip(qs, answers):
                        fb = interview_evaluator.score_and_feedback(answer=a or '', role_hint=role_hint, question_text=q.get('text', ''))
                        per.append({
                            'question_id': q.get('id'),
                            'score': fb.get('score'),
                            'strengths': fb.get('strengths', []),
                            'improvements': fb.get('improvements', []),
                            'matched_keywords': fb.get('matched_keywords', []),
                            'missing_keywords': fb.get('missing_keywords', []),
                        })
                        try:
                            total += float(fb.get('score') or 0.0)
                        except Exception:
                            pass
                    total_norm = round((total / max(1, len(per))), 1)
                    result = {'total_score': total_norm, 'per_answer': per, 'evaluation_method': 'Local'}
                else:
                    # Try enhanced fallback evaluation
                    if ENHANCED_FALLBACK_AVAILABLE and get_enhanced_evaluation:
                        try:
                            print("🎯 Using enhanced fallback evaluation")
                            per = []
                            total = 0.0
                            for q, a in zip(qs, answers):
                                fb = get_enhanced_evaluation(
                                    question=q.get('text', ''),
                                    answer=a or '',
                                    skills=skills,
                                    role_hint=role_hint
                                )
                                per.append({
                                    'question_id': q.get('id'),
                                    'score': fb.get('score', 70),
                                    'strengths': fb.get('strengths', []),
                                    'improvements': fb.get('improvements', []),
                                    'technical_accuracy': fb.get('technical_accuracy', 70),
                                    'communication': fb.get('communication', 70),
                                    'problem_solving': fb.get('problem_solving', 70),
                                    'overall_feedback': fb.get('overall_feedback', ''),
                                    'follow_up_suggestions': fb.get('follow_up_suggestions', [])
                                })
                                total += float(fb.get('score', 70))
                            
                            total_norm = round((total / max(1, len(per))), 1)
                            result = {'total_score': total_norm, 'per_answer': per, 'evaluation_method': 'Enhanced Fallback'}
                        except Exception as e:
                            print(f"[WARNING] Enhanced fallback evaluation failed: {e}")
                            result = {'total_score': 70, 'per_answer': [], 'evaluation_method': 'Basic'}
                    else:
                        # No enhanced evaluation available, use basic ML scorer
                        result = {'total_score': 70, 'per_answer': [], 'evaluation_method': 'Basic'}
        else:
            # No OpenAI available, use local evaluator
            if interview_evaluator and hasattr(interview_evaluator, 'score_and_feedback'):
                per = []
                total = 0.0
                for q, a in zip(qs, answers):
                    fb = interview_evaluator.score_and_feedback(answer=a or '', role_hint=role_hint, question_text=q.get('text', ''))
                    per.append({
                        'question_id': q.get('id'),
                        'score': fb.get('score'),
                        'strengths': fb.get('strengths', []),
                        'improvements': fb.get('improvements', []),
                        'matched_keywords': fb.get('matched_keywords', []),
                        'missing_keywords': fb.get('missing_keywords', []),
                    })
                    try:
                        total += float(fb.get('score') or 0.0)
                    except Exception:
                        pass
                total_norm = round((total / max(1, len(per))), 1)
                result = {'total_score': total_norm, 'per_answer': per, 'evaluation_method': 'Local'}
            elif ENHANCED_FALLBACK_AVAILABLE and get_enhanced_evaluation:
                # Use enhanced fallback evaluation
                try:
                    print("🎯 Using enhanced fallback evaluation (no OpenAI)")
                    per = []
                    total = 0.0
                    for q, a in zip(qs, answers):
                        fb = get_enhanced_evaluation(
                            question=q.get('text', ''),
                            answer=a or '',
                            skills=skills,
                            role_hint=role_hint
                        )
                        per.append({
                            'question_id': q.get('id'),
                            'score': fb.get('score', 70),
                            'strengths': fb.get('strengths', []),
                            'improvements': fb.get('improvements', []),
                            'technical_accuracy': fb.get('technical_accuracy', 70),
                            'communication': fb.get('communication', 70),
                            'problem_solving': fb.get('problem_solving', 70),
                            'overall_feedback': fb.get('overall_feedback', ''),
                            'follow_up_suggestions': fb.get('follow_up_suggestions', [])
                        })
                        total += float(fb.get('score', 70))
                    
                    total_norm = round((total / max(1, len(per))), 1)
                    result = {'total_score': total_norm, 'per_answer': per, 'evaluation_method': 'Enhanced Fallback'}
                except Exception as e:
                    print(f"[WARNING] Enhanced fallback evaluation failed: {e}")
                    result = {'total_score': 70, 'per_answer': [], 'evaluation_method': 'Basic'}
            elif ml_answer_scorer:
                # ML scorer path: probability of "good" mapped to 0-100
                per = []
                total = 0.0
                for q, a in zip(qs, answers):
                    proba = ml_answer_scorer.score(a or '', question_text=q.get('text', ''), role_hint=role_hint)
                    score_pct = round(proba * 100.0, 1)
                    per.append({'question_id': q.get('id'), 'score': score_pct})
                    total += score_pct
                total_norm = round((total / max(1, len(per))), 1)
                result = {'total_score': total_norm, 'per_answer': per, 'evaluation_method': 'ML Scorer'}
            else:
                result = score_answers_simple(qs, answers, skills)
        
        # Optionally persist minimal log
        try:
            os.makedirs('interview_responses', exist_ok=True)
            with open(os.path.join('interview_responses', 'last_result.json'), 'w', encoding='utf-8') as f:
                import json
                json.dump({'questions': qs, 'answers': answers, 'result': result}, f, ensure_ascii=False)
        except Exception:
            pass
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/interview')
def interview_page():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>Virtual Interview</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .row { display: grid; grid-template-columns: 1fr; gap: 16px; }
        .card { background: #f8f9fa; padding: 12px; border-radius: 8px; }
        textarea { width: 100%; height: 120px; }
        button { background: #007bff; color: white; padding: 10px 18px; border: none; border-radius: 6px; cursor: pointer; }
      </style>
    </head>
    <body>
      <div class="container">
        <h2>Virtual Interview</h2>
        <div class="card">
          <div style="margin-bottom:6px;">Paste skills to tailor questions (optional):</div>
          <input id="skillsBox" placeholder="e.g., python, react, aws" style="width:100%;padding:8px;"/>
          <div style="margin-top:10px;">
            <button id="startBtn">Start Interview</button>
            <a href="/"><button style="margin-left:8px;background:#6c757d;">Back to Dashboard</button></a>
          </div>
        </div>
        <div id="pane" class="card" style="margin-top:12px; display:none;">
          <div id="qtext" style="margin-bottom:8px;"></div>
          <div>Time left: <span id="timer">90</span>s</div>
          <textarea id="ans"></textarea>
          <div style="margin-top:8px;">
            <button id="nextBtn">Next</button>
            <button id="finishBtn" style="background:#28a745;">Finish</button>
          </div>
        </div>
        <div id="result" class="card" style="display:none;margin-top:12px;"></div>
      </div>

      <script>
        let qs = [], idx = 0, answers = [], timerId = null;
        function startTimer(sec){
          let t = sec; const el = document.getElementById('timer'); el.textContent = t; clearInterval(timerId);
          timerId = setInterval(()=>{ t--; el.textContent=t; if(t<=0){ clearInterval(timerId); document.getElementById('nextBtn').click(); } }, 1000);
        }
        async function startInterview(){
          const skills = (document.getElementById('skillsBox').value || '').split(',').map(s=>s.trim()).filter(Boolean);
          try{
            const resp = await fetch('/interview/questions',{method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({skills})});
            const data = await resp.json();
            if(!data.success) throw new Error(data.error||'Failed');
            qs = data.questions||[]; idx=0; answers=new Array(qs.length).fill('');
            document.getElementById('pane').style.display='block';
            loadQ();
          }catch(e){ alert(e.message); }
        }
        function loadQ(){
          const q = qs[idx];
          document.getElementById('qtext').textContent = `${idx+1}. ${q.text}`;
          document.getElementById('ans').value='';
          startTimer(q.time_limit_sec||90);
        }
        async function nextQ(){
          answers[idx] = document.getElementById('ans').value;
          idx++;
          if(idx < qs.length){ loadQ(); } else { finish(); }
        }
        async function finish(){
          clearInterval(timerId);
          answers[idx-1] = answers[idx-1] || document.getElementById('ans').value;
          try{
            const resp = await fetch('/interview/submit',{method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({questions: qs, answers, skills: []})});
            const data = await resp.json();
            if(!data.success) throw new Error(data.error||'Failed');
            const r = data.result||{}; const div = document.getElementById('result');
            div.style.display='block';
            div.innerHTML = `<div><strong>Score:</strong> ${r.total_score}%</div>`;
          }catch(e){ alert(e.message); }
        }
        document.getElementById('startBtn').onclick = startInterview;
        document.getElementById('nextBtn').onclick = nextQ;
        document.getElementById('finishBtn').onclick = finish;
      </script>
    </body>
    </html>
    """
    return render_template_string(html)


# -------- Live Chat Interview (Interviewer <-> Candidate) --------
import uuid
from datetime import datetime

INTERVIEW_SESSIONS: dict[str, dict] = {}

# -------- Skill Gap Analysis Functions --------
def load_skill_data():
    """Load skill importance and categories data."""
    try:
        skill_importance = {}
        skill_categories = {}
        
        if os.path.exists('data/skill_importance.json'):
            with open('data/skill_importance.json', 'r') as f:
                skill_importance = json.load(f)
        
        if os.path.exists('data/skill_categories.json'):
            with open('data/skill_categories.json', 'r') as f:
                skill_categories = json.load(f)
        
        return skill_importance, skill_categories
    except Exception as e:
        print(f"Error loading skill data: {e}")
        return {}, {}

def extract_skills_from_text(text: str) -> list[str]:
    """Extract skills from text using regex patterns."""
    if not text:
        return []
    
    lower_text = text.lower()
    skills = []
    
    # Load skill data
    skill_importance, _ = load_skill_data()
    
    # Check for skills in the text
    for skill in skill_importance.keys():
        if skill in lower_text:
            skills.append(skill)
    
    return list(set(skills))

def analyze_skill_gap(user_skills: list[str], job_description: str, job_title: str = "") -> dict:
    """Analyze skill gap between user skills and job requirements."""
    try:
        # Load skill data
        skill_importance, skill_categories = load_skill_data()
        
        if not skill_importance:
            return {
                "error": "Skill data not available",
                "match_percentage": 0,
                "missing_skills": [],
                "matching_skills": [],
                "extra_skills": [],
                "recommendations": []
            }
        
        # Extract skills from job description
        job_skills = extract_skills_from_text(job_description)
        
        # Convert to sets for easier operations
        user_skill_set = set(user_skills)
        job_skill_set = set(job_skills)
        
        # Calculate skill matches
        matching_skills = list(user_skill_set.intersection(job_skill_set))
        missing_skills = list(job_skill_set - user_skill_set)
        extra_skills = list(user_skill_set - job_skill_set)
        
        # Calculate match percentage
        total_required = len(job_skill_set)
        if total_required == 0:
            match_percentage = 100.0
        else:
            match_percentage = (len(matching_skills) / total_required) * 100
        
        # Categorize skills
        categorized_skills = {}
        for category, skills in skill_categories.items():
            categorized_skills[category] = {
                "matching": [s for s in matching_skills if s in skills],
                "missing": [s for s in missing_skills if s in skills],
                "extra": [s for s in extra_skills if s in skills]
            }
        
        # Generate recommendations for missing skills
        recommendations = []
        for skill in missing_skills[:5]:  # Top 5 missing skills
            if skill in skill_importance:
                importance = skill_importance[skill].get("importance_score", 5.0)
                recommendations.append({
                    "skill": skill,
                    "importance": importance,
                    "priority": "High" if importance >= 8.0 else "Medium" if importance >= 6.0 else "Low"
                })
        
        # Sort recommendations by importance
        recommendations.sort(key=lambda x: x["importance"], reverse=True)
        
        return {
            "match_percentage": round(match_percentage, 1),
            "missing_skills": missing_skills,
            "matching_skills": matching_skills,
            "extra_skills": extra_skills,
            "categorized_skills": categorized_skills,
            "recommendations": recommendations,
            "total_required": total_required,
            "total_matching": len(matching_skills)
        }
        
    except Exception as e:
        print(f"Error in skill gap analysis: {e}")
        return {
            "error": str(e),
            "match_percentage": 0,
            "missing_skills": [],
            "matching_skills": [],
            "extra_skills": [],
            "recommendations": []
        }


@app.route('/interview/live')
def interview_live_page():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>Live Virtual Interview</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 0; background: #0f172a; color: #e2e8f0; }
        .wrap { max-width: 900px; margin: 0 auto; height: 100vh; display: grid; grid-template-rows: auto 1fr auto; }
        header { padding: 16px; background: #111827; border-bottom: 1px solid #1f2937; }
        main { padding: 16px; overflow-y: auto; background: #0b1220; }
        .card { background: #111827; border: 1px solid #1f2937; border-radius: 10px; padding: 12px; }
        .msg { margin: 8px 0; display: flex; }
        .left { justify-content: flex-start; }
        .right { justify-content: flex-end; }
        .bubble { max-width: 70%; padding: 10px 12px; border-radius: 12px; white-space: pre-wrap; line-height: 1.4; }
        .ai { background: #0e7490; color: #ecfeff; }
        .me { background: #334155; color: #f8fafc; }
        footer { padding: 12px; background: #111827; border-top: 1px solid #1f2937; }
        input, textarea { width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #374151; background: #0b1220; color:#e2e8f0; }
        button { padding: 10px 14px; border-radius: 8px; border: 1px solid #374151; background: #2563eb; color: white; cursor: pointer; }
      </style>
    </head>
    <body>
      <div class="wrap">
        <header>
          <div style="display:flex; align-items:center; gap: 12px;">
            <div style="font-weight:700;">Live Virtual Interview</div>
            <a href="/" style="color:#93c5fd;">Back</a>
          </div>
        </header>
        <main>
          <div class="card" style="margin-bottom:12px;">
            <div style="margin-bottom:6px;">Provide your top skills to tailor the interview (optional):</div>
            <input id="skills" placeholder="e.g., python, react, aws" />
            <div style="margin-top:8px;"><button id="start">Start Interview</button></div>
          </div>
          <div id="chat" class="card" style="height:60vh; overflow:auto;"></div>
        </main>
        <footer>
          <div style="display:flex; gap: 8px;">
            <input id="input" placeholder="Type your answer and press Send..." />
            <button id="send">Send</button>
          </div>
        </footer>
      </div>

      <script>
        let session_id = null;
        const chat = document.getElementById('chat');
        function pushAI(text){
          const row = document.createElement('div'); row.className='msg left';
          const b = document.createElement('div'); b.className='bubble ai'; b.textContent=text;
          row.appendChild(b); chat.appendChild(row); chat.scrollTop = chat.scrollHeight;
        }
        function pushMe(text){
          const row = document.createElement('div'); row.className='msg right';
          const b = document.createElement('div'); b.className='bubble me'; b.textContent=text;
          row.appendChild(b); chat.appendChild(row); chat.scrollTop = chat.scrollHeight;
        }
        async function start(){
          const skills = (document.getElementById('skills').value || '').split(',').map(s=>s.trim()).filter(Boolean);
          const resp = await fetch('/interview/live/start',{method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({skills})});
          const data = await resp.json();
          if(!data.success){ alert(data.error||'Failed'); return; }
          session_id = data.session_id; pushAI(data.message);
        }
        async function send(){
          const val = document.getElementById('input').value.trim();
          if(!val || !session_id) return; document.getElementById('input').value=''; pushMe(val);
          const resp = await fetch('/interview/live/answer',{method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({session_id, answer: val})});
          const data = await resp.json();
          if(!data.success){ pushAI('Error: '+(data.error||'')); return; }
          pushAI(data.message);
          if(data.done){
            pushAI(`Interview finished. Score: ${data.result?.total_score || 0}%`);
          }
        }
        document.getElementById('start').onclick = start;
        document.getElementById('send').onclick = send;
        document.getElementById('input').addEventListener('keydown', (e)=>{ if(e.key==='Enter'){ e.preventDefault(); document.getElementById('send').click(); }});
      </script>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route('/interview/live/start', methods=['POST'])
def interview_live_start():
    try:
        payload = request.get_json() or {}
        skills = payload.get('skills') or []
        qs = generate_interview_questions(skills)
        sid = uuid.uuid4().hex
        INTERVIEW_SESSIONS[sid] = {
            'created': datetime.utcnow().isoformat(),
            'skills': skills,
            'questions': qs,
            'idx': 0,
            'answers': []
        }
        first = qs[0]['text'] if qs else 'Tell me about yourself.'
        return jsonify({'success': True, 'session_id': sid, 'message': first})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/interview/live/answer', methods=['POST'])
def interview_live_answer():
    try:
        payload = request.get_json() or {}
        sid = payload.get('session_id')
        answer = (payload.get('answer') or '').strip()
        if not sid or sid not in INTERVIEW_SESSIONS:
            return jsonify({'success': False, 'error': 'Invalid session'}), 400
        sess = INTERVIEW_SESSIONS[sid]
        qs = sess['questions']
        idx = sess['idx']
        if idx >= len(qs):
            return jsonify({'success': True, 'message': 'Interview already completed.', 'done': True})
        # store answer
        if len(sess['answers']) <= idx:
            sess['answers'].append(answer)
        else:
            sess['answers'][idx] = answer
        sess['idx'] = idx + 1
        # if finished, score and respond summary
        if sess['idx'] >= len(qs):
            result = score_answers_simple(qs, sess['answers'], sess['skills'])
            return jsonify({'success': True, 'message': 'Thanks for your answer. This concludes the interview.', 'done': True, 'result': result})
        # else, next question; optionally add brief adaptive follow-up
        next_q = qs[sess['idx']]['text']
        follow = ''
        # simple heuristic follow-up prompt if short answer
        if len(answer.split()) < 10:
            follow = " (Please elaborate with more details and outcomes.)"
        return jsonify({'success': True, 'message': next_q + follow, 'done': False})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/upload', methods=['POST', 'OPTIONS'])
@app.route('/api/upload', methods=['POST', 'OPTIONS'])
def upload():
    """Upload endpoint for PDF/TXT resume files."""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
    try:
        text_content = ''  # Initialize text_content
        
        # Handle JSON request first
        if request.is_json:
            data = request.get_json(silent=True) or {}
            text_content = data.get('resume_text', '')
            if not text_content.strip():
                return jsonify({'success': False, 'error': 'Resume text is required in JSON request'}), 400
        else:
            # Handle file upload
            if 'resume_file' not in request.files:
                return jsonify({'success': False, 'error': 'No file part'}), 400
            file = request.files['resume_file']
            if not file or file.filename == '':
                return jsonify({'success': False, 'error': 'No selected file'}), 400

            # Process the uploaded file
            filename = (file.filename or '').lower()
            file_bytes = file.read()
            if filename.endswith('.pdf'):
                text_content = extract_text_from_pdf(file_bytes)
            elif filename.endswith('.txt'):
                try:
                    text_content = file_bytes.decode('utf-8', errors='ignore')
                except Exception:
                    text_content = ''
            else:
                return jsonify({'success': False, 'error': 'Unsupported file type. Use PDF or TXT.'}), 400

        if not text_content.strip():
            return jsonify({'success': False, 'error': 'Could not read any text from the file'}), 400

        # Now reuse recommend logic
        from sklearn.metrics.pairwise import cosine_similarity
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        if vectorizer is not None and job_vectors is not None:
            resume_vector = vectorizer.transform([text_content])
            similarities = cosine_similarity(resume_vector, job_vectors).flatten()
        else:
            job_descriptions = [f"{str(r.get('title',''))} {str(r.get('description',''))} {str(r.get('skills',''))}" for _, r in job_data.iterrows()]
            temp_vec = TfidfVectorizer(max_features=5000, stop_words='english')
            tfidf_mat = temp_vec.fit_transform([text_content] + job_descriptions)
            similarities = cosine_similarity(tfidf_mat[0:1], tfidf_mat[1:]).flatten()
            
        top_indices = similarities.argsort()[-5:][::-1]
        jobs = []
        for idx in top_indices:
            if idx < 0 or idx >= len(job_data):
                continue
            if similarities[idx] > 0.01:
                job = job_data.iloc[idx]
                jobs.append({
                    'title': str(job.get('title', 'N/A')),
                    'company': str(job.get('company', 'N/A')),
                    'location': str(job.get('location', 'N/A')),
                    'similarity_score': float(similarities[idx])
                })

        parsed = extract_skills_and_experience(text_content)
        title_terms = []
        for j in jobs[:3]:
            if j.get("title"):
                title_terms.extend([t for t in re.split(r"[^a-zA-Z]+", j["title"].lower()) if t and len(t) > 2])
        keywords = parsed.get("skills", []) or list(dict.fromkeys(title_terms))
        
        print(f"[SEARCH] Attempting to fetch live jobs for keywords: {keywords[:3]}")
        
        # Try to fetch live jobs from external APIs
        live_raw = fetch_live_jobs_from_arbeitnow(keywords, max_jobs=40)
        live_custom = fetch_live_jobs_from_custom_api(keywords, max_jobs=60)
        
        # Merge & dedupe
        if live_custom:
            merged = []
            seen_keys = set()
            for src in (live_raw, live_custom):
                for j in src:
                    key = (j.get("title"), j.get("company"), j.get("location"), j.get("url"))
                    if key in seen_keys:
                        continue
                    seen_keys.add(key)
                    merged.append(j)
            live_raw = merged
        
        # If no live jobs fetched, use fallback
        if not live_raw:
            print("[WARNING] No live jobs fetched from external APIs, using fallback")
            live_raw = generate_fallback_live_jobs(keywords, max_jobs=20)
        else:
            print(f"[OK] Successfully fetched {len(live_raw)} live jobs from external APIs")
        
        live_jobs = score_live_jobs(text_content, parsed.get("skills", []), live_raw)[:10]
        
        # Add skill gap analysis for top recommended jobs
        skill_gap_analyses = []
        user_skills = parsed.get("skills", [])
        if user_skills and jobs:
            for i, job in enumerate(jobs[:3]):  # Top 3 jobs
                try:
                    # Get job description from the dataset
                    job_idx = top_indices[i] if i < len(top_indices) else None
                    if job_idx is not None and job_idx < len(job_data):
                        job_row = job_data.iloc[job_idx]
                        job_desc = str(job_row.get('description', ''))
                        if job_desc:
                            analysis = analyze_skill_gap(user_skills, job_desc, job.get('title', ''))
                            if 'error' not in analysis:
                                analysis['job_id'] = int(job_idx)
                                analysis['job_title'] = job.get('title', '')
                                skill_gap_analyses.append(analysis)
                except Exception as e:
                    print(f"Error analyzing skill gap for job {i}: {e}")
                    continue
        
        return jsonify({
            'success': True, 
            'jobs': jobs, 
            'parsed': parsed, 
            'live_jobs': live_jobs,
            'skill_gap_analyses': skill_gap_analyses
        })

    except Exception as e:
        print(f"Error in upload: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/test-live-jobs', methods=['GET'])
def test_live_jobs():
    """Test endpoint for live job fetching."""
    try:
        # Test with sample keywords
        test_keywords = ["python", "react", "aws"]
        
        print(f"🧪 Testing live job fetching with keywords: {test_keywords}")
        
        # Test external APIs
        arbeitnow_jobs = fetch_live_jobs_from_arbeitnow(test_keywords, max_jobs=10)
        custom_jobs = fetch_live_jobs_from_custom_api(test_keywords, max_jobs=10)
        
        # Test fallback
        fallback_jobs = generate_fallback_live_jobs(test_keywords, max_jobs=10)
        
        return jsonify({
            'success': True,
            'test_data': {
                'keywords': test_keywords,
                'arbeitnow_jobs_count': len(arbeitnow_jobs),
                'custom_api_jobs_count': len(custom_jobs),
                'fallback_jobs_count': len(fallback_jobs),
                'total_live_jobs': len(arbeitnow_jobs) + len(custom_jobs) + len(fallback_jobs)
            },
            'arbeitnow_sample': arbeitnow_jobs[:2] if arbeitnow_jobs else [],
            'custom_api_sample': custom_jobs[:2] if custom_jobs else [],
            'fallback_sample': fallback_jobs[:2] if fallback_jobs else []
        })
        
    except Exception as e:
        print(f"Error in live jobs test: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/health')
def health():
    """Health check."""
    return jsonify({
        'status': 'ok',
        'jobs_loaded': job_data is not None,
        'model_loaded': vectorizer is not None and job_vectors is not None,
        'pdf_enabled': PDF_ENABLED
    })


@app.route('/skill-gap', methods=['POST', 'OPTIONS'])
@app.route('/api/skill-gap', methods=['POST', 'OPTIONS'])
def skill_gap_analysis():
    """Analyze skill gap between user skills and job requirements."""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
    try:
        data = request.get_json(silent=True) or {}
        user_skills = data.get('user_skills', [])
        job_description = data.get('job_description', '')
        job_title = data.get('job_title', '')
        
        if not user_skills or not job_description:
            return jsonify({
                'success': False, 
                'error': 'Both user_skills and job_description are required'
            }), 400
        
        # Perform skill gap analysis
        analysis = analyze_skill_gap(user_skills, job_description, job_title)
        
        if 'error' in analysis:
            return jsonify({
                'success': False, 
                'error': analysis['error']
            }), 500
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        print(f"Error in skill gap analysis endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/skill-gap/test', methods=['GET'])
@app.route('/api/skill-gap/test', methods=['GET'])
def test_skill_gap():
    """Test endpoint for skill gap analysis."""
    try:
        # Test with sample data
        user_skills = ["python", "javascript", "react"]
        job_description = "We are looking for a Full Stack Developer with experience in Python, Django, React, and AWS. Knowledge of Docker and Kubernetes is a plus."
        job_title = "Full Stack Developer"
        
        analysis = analyze_skill_gap(user_skills, job_description, job_title)
        
        return jsonify({
            'success': True,
            'test_data': {
                'user_skills': user_skills,
                'job_description': job_description,
                'job_title': job_title
            },
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/skill-gap/job/<int:job_id>', methods=['POST', 'OPTIONS'])
@app.route('/api/skill-gap/job/<int:job_id>', methods=['POST', 'OPTIONS'])
def skill_gap_for_job(job_id):
    """Analyze skill gap for a specific job from the dataset."""
    try:
        data = request.get_json()
        user_skills = data.get('user_skills', [])
        
        if not user_skills:
            return jsonify({
                'success': False,
                'error': 'user_skills are required'
            }), 400
        
        if job_data is None or job_id < 0 or job_id >= len(job_data):
            return jsonify({
                'success': False,
                'error': 'Invalid job ID or job data not loaded'
            }), 400
        
        # Get job details
        job = job_data.iloc[job_id]
        job_title = str(job.get('title', ''))
        job_description = str(job.get('description', ''))
        
        if not job_description:
            return jsonify({
                'success': False,
                'error': 'Job description not available'
            }), 400
        
        # Perform skill gap analysis
        analysis = analyze_skill_gap(user_skills, job_description, job_title)
        
        if 'error' in analysis:
            return jsonify({
                'success': False,
                'error': analysis['error']
            }), 500
        
        # Add job details to response
        analysis['job'] = {
            'id': job_id,
            'title': job_title,
            'company': str(job.get('company', 'N/A')),
            'location': str(job.get('location', 'N/A'))
        }
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        print(f"Error in job skill gap analysis: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Job Posting API endpoints for frontend
@app.route('/api/jobs', methods=['GET', 'POST', 'OPTIONS'])
def api_jobs():
    """Handle job posting API requests"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'})
    
    if request.method == 'GET':
        # Return list of jobs for frontend
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 20))
            
            # Load any custom user-posted jobs first
            user_posted = []
            posted_jobs_file = os.path.join('data', 'posted_jobs.json')
            if os.path.exists(posted_jobs_file):
                try:
                    with open(posted_jobs_file, 'r', encoding='utf-8') as f:
                        user_posted = json.load(f)
                        if not isinstance(user_posted, list):
                            user_posted = []
                except Exception:
                    user_posted = []

            # Get sample jobs from loaded data or create fallback
            if job_data is not None and len(job_data) > 0:
                start_idx = (page - 1) * limit
                end_idx = start_idx + limit
                jobs_subset = job_data.iloc[start_idx:end_idx]
                
                jobs_list = []
                for _, job in jobs_subset.iterrows():
                    jobs_list.append({
                        'id': str(len(jobs_list) + start_idx + 1),
                        'title': str(job.get('title', 'Software Developer')),
                        'company': str(job.get('company', 'Tech Company')),
                        'location': str(job.get('location', 'Remote')),
                        'description': str(job.get('description', ''))[:200] + '...',
                        'salary': str(job.get('salary_range', '$50,000 - $80,000')),
                        'type': 'full-time',
                        'posted_date': '2024-11-02',
                        'status': 'active'
                    })
            else:
                # Fallback jobs if no data loaded
                jobs_list = [
                    {
                        'id': '1',
                        'title': 'Full Stack Developer',
                        'company': 'TechCorp',
                        'location': 'Remote',
                        'description': 'We are looking for a skilled Full Stack Developer to join our team...',
                        'salary': '$60,000 - $90,000',
                        'type': 'full-time',
                        'posted_date': '2024-11-02',
                        'status': 'active'
                    },
                    {
                        'id': '2',
                        'title': 'Frontend Developer',
                        'company': 'StartupXYZ',
                        'location': 'New York, NY',
                        'description': 'Join our frontend team to build amazing user experiences...',
                        'salary': '$55,000 - $75,000',
                        'type': 'full-time', 
                        'posted_date': '2024-11-01',
                        'status': 'active'
                    }
                ]
            
            # Combine user-posted jobs at front of page 1
            if page == 1 and user_posted:
                jobs_list = user_posted + jobs_list

            total = (len(job_data) if job_data is not None else len(jobs_list)) + len(user_posted)
            
            return jsonify({
                'success': True,
                'jobs': jobs_list,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit
                }
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to fetch jobs: {str(e)}'
            }), 500
    
    elif request.method == 'POST':
        # Handle job posting creation
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            # Validate required fields
            required_fields = ['title', 'company', 'description']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }), 400
            
            # Create new job posting
            new_job = {
                'id': str(int(datetime.utcnow().timestamp())),
                'title': data.get('title'),
                'company': data.get('company'),
                'location': data.get('location', 'Not specified'),
                'description': data.get('description'),
                'salary': data.get('salary', 'Negotiable'),
                'type': data.get('type', 'full-time'),
                'posted_date': datetime.utcnow().strftime('%Y-%m-%d'),
                'status': 'active'
            }
            
            # Save to file (simple persistence)
            try:
                posted_jobs_file = os.path.join('data', 'posted_jobs.json')
                os.makedirs('data', exist_ok=True)
                
                # Load existing jobs
                existing_jobs = []
                if os.path.exists(posted_jobs_file):
                    with open(posted_jobs_file, 'r', encoding='utf-8') as f:
                        existing_jobs = json.load(f)
                
                # Add new job
                existing_jobs.append(new_job)
                
                # Save back to file
                with open(posted_jobs_file, 'w', encoding='utf-8') as f:
                    json.dump(existing_jobs, f, indent=2, ensure_ascii=False)
                
                print(f"[OK] New job posted: {new_job['title']} at {new_job['company']}")
                
            except Exception as save_error:
                print(f"[WARNING] Failed to save job posting: {save_error}")
            
            return jsonify({
                'success': True,
                'job': new_job,
                'message': 'Job posted successfully'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to create job posting: {str(e)}'
            }), 500


# Interview Experiences Helper Functions & Endpoints
EXPERIENCES_FILE = os.path.join('data', 'interview_experiences.json')

def load_experiences_from_file():
    try:
        if os.path.exists(EXPERIENCES_FILE):
            with open(EXPERIENCES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
    except Exception as e:
        print(f"[WARNING] Error reading {EXPERIENCES_FILE}: {e}")
    return []

def save_experiences_to_file(experiences):
    try:
        os.makedirs(os.path.dirname(EXPERIENCES_FILE), exist_ok=True)
        with open(EXPERIENCES_FILE, 'w', encoding='utf-8') as f:
            json.dump(experiences, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[ERROR] Error saving {EXPERIENCES_FILE}: {e}")
        return False

@app.route('/api/experiences', methods=['GET', 'POST', 'OPTIONS'])
def api_experiences():
    """Get or create interview experiences"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200

    if request.method == 'POST':
        try:
            data = request.get_json(silent=True) or {}
            if not data:
                return jsonify({'success': False, 'message': 'No data provided'}), 400

            experiences = load_experiences_from_file()
            new_id = (max([int(x.get('id', 0)) for x in experiences], default=0) + 1)
            
            # Map frontend difficulty string/int to standard
            difficulty = data.get('difficulty_rating', data.get('difficulty', 3))
            
            new_exp = {
                'id': new_id,
                'company': data.get('company', 'Unknown'),
                'position': data.get('position', data.get('role', 'Developer')),
                'interviewer': data.get('interviewer', 'Technical Team'),
                'experience_text': data.get('experience_text', data.get('experience', '')),
                'difficulty_rating': difficulty,
                'outcome': data.get('outcome', 'Under Review'),
                'interview_type': data.get('interview_type', 'Technical'),
                'interview_rounds': int(data.get('interview_rounds', 2)),
                'preparation_time': data.get('preparation_time', '1-2 weeks'),
                'location': data.get('location', 'Remote'),
                'questions_asked': data.get('questions_asked', []),
                'tips': data.get('tips', []),
                'tags': data.get('tags', []),
                'date': data.get('interview_date') or datetime.utcnow().strftime('%Y-%m-%d'),
                'created_at': datetime.utcnow().isoformat(),
                'helpful_votes': 0,
                'total_votes': 0,
                'helpfulness_ratio': 0,
                'status': 'published'
            }
            
            experiences.insert(0, new_exp)
            save_experiences_to_file(experiences)
            return jsonify({
                'success': True,
                'experience': new_exp,
                'message': 'Interview experience posted successfully'
            }), 201
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    # GET
    try:
        experiences = load_experiences_from_file()
        
        # Apply filters
        q = (request.args.get('search') or '').strip().lower()
        company = (request.args.get('company') or '').strip().lower()
        interview_type = (request.args.get('interview_type') or '').strip().lower()
        difficulty = (request.args.get('difficulty') or '').strip().lower()
        outcome = (request.args.get('outcome') or '').strip().lower()
        
        filtered = experiences
        if q:
            filtered = [
                e for e in filtered
                if q in str(e.get('company', '')).lower()
                or q in str(e.get('position', '')).lower()
                or q in str(e.get('experience_text', '')).lower()
            ]
        if company:
            filtered = [e for e in filtered if company in str(e.get('company', '')).lower()]
        if interview_type:
            filtered = [e for e in filtered if interview_type in str(e.get('interview_type', '')).lower()]
        if outcome:
            filtered = [e for e in filtered if outcome in str(e.get('outcome', '')).lower()]
        if difficulty:
            filtered = [e for e in filtered if str(difficulty) in str(e.get('difficulty_rating', '')).lower()]

        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        total = len(filtered)
        start = (page - 1) * limit
        end = start + limit
        
        return jsonify({
            'success': True,
            'experiences': filtered[start:end],
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit if total > 0 else 1
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/experiences/<int:exp_id>', methods=['DELETE', 'OPTIONS'])
def delete_experience(exp_id):
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
    try:
        experiences = load_experiences_from_file()
        experiences = [e for e in experiences if int(e.get('id', 0)) != int(exp_id)]
        save_experiences_to_file(experiences)
        return jsonify({'success': True, 'message': 'Experience deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/experiences/<int:exp_id>/vote', methods=['POST', 'OPTIONS'])
def vote_experience(exp_id):
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
    try:
        data = request.get_json(silent=True) or {}
        is_helpful = bool(data.get('is_helpful', True))
        experiences = load_experiences_from_file()
        target = None
        for e in experiences:
            if int(e.get('id', 0)) == int(exp_id):
                target = e
                break
        if not target:
            return jsonify({'success': False, 'message': 'Experience not found'}), 404
        
        target['total_votes'] = target.get('total_votes', 0) + 1
        if is_helpful:
            target['helpful_votes'] = target.get('helpful_votes', 0) + 1
        target['helpfulness_ratio'] = round(target['helpful_votes'] / max(1, target['total_votes']), 2)
        save_experiences_to_file(experiences)
        return jsonify({
            'success': True,
            'helpful_votes': target['helpful_votes'],
            'total_votes': target['total_votes'],
            'helpfulness_ratio': target['helpfulness_ratio']
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Submissions endpoint for Coding Problems at root level
@app.route('/submissions', methods=['POST', 'OPTIONS'])
def root_submissions():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
    try:
        from problems_api import submit_solution
        return submit_solution()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



if __name__ == '__main__':
    print("[START] Starting Career Guidance Platform...")
    
    # Load model
    if load_model():
        print("[OK] Model loaded successfully!")
        print("[WEB] Starting web server on http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print("[ERROR] Failed to load model. Please check your data files.")