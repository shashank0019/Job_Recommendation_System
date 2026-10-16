#!/usr/bin/env python3
"""
Modified Flask app with lazy model loading to avoid startup hangs
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"]}})

# Global variables - will be loaded lazily
job_data = None
vectorizer = None
job_vectors = None

# Register coding problems API
try:
    from problems_api import problems_bp
    app.register_blueprint(problems_bp, url_prefix="/api")
    print("✅ Problems API registered at /api")
except Exception as e:
    print(f"ℹ️ Problems API not registered: {e}")

@app.route('/test')
def test_endpoint():
    """Simple test endpoint"""
    return jsonify({"success": True, "message": "Test endpoint working!"})

@app.route('/api/upload', methods=['POST'])
def upload_resume():
    """Handle resume file upload (PDF/TXT)"""
    try:
        if 'resume_file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'})

        file = request.files['resume_file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})

        # Read file content
        file_bytes = file.read()
        filename = file.filename.lower()

        resume_text = ""
        if filename.endswith('.pdf'):
            # Extract text from PDF
            resume_text = extract_text_from_pdf(file_bytes)
        elif filename.endswith('.txt'):
            # Read text file
            resume_text = file_bytes.decode('utf-8', errors='ignore')
        else:
            return jsonify({'success': False, 'error': 'Unsupported file type. Please upload PDF or TXT files only.'})

        if not resume_text.strip():
            return jsonify({'success': False, 'error': 'Could not extract text from file. Please ensure the file contains readable text.'})

        # Process the extracted text like a regular resume submission
        if job_data is None or vectorizer is None or job_vectors is None:
            print("🔄 Loading models for resume processing...")
            success = load_model_minimal()
            if not success:
                return jsonify({'success': False, 'error': 'Failed to load models'})

        # Simple matching logic (reuse existing logic)
        from sklearn.metrics.pairwise import cosine_similarity

        # Vectorize resume
        resume_vector = vectorizer.transform([resume_text])

        # Calculate similarities
        similarities = cosine_similarity(resume_vector, job_vectors).flatten()

        # Get top 5 matches
        top_indices = similarities.argsort()[-5:][::-1]

        jobs = []
        for idx in top_indices:
            if idx < 0 or idx >= len(job_data):
                continue
            if similarities[idx] > 0.01:  # Minimum similarity threshold
                job = job_data.iloc[idx]
                jobs.append({
                    'title': str(job.get('title', 'N/A')),
                    'company': str(job.get('company', 'N/A')),
                    'location': str(job.get('location', 'N/A')),
                    'similarity_score': float(similarities[idx])
                })

        parsed = extract_skills_and_experience(resume_text)

        # Compose keywords from parsed skills and top matched titles
        title_terms = []
        for j in jobs[:3]:
            if j.get("title"):
                title_terms.extend([t for t in re.split(r"[^a-zA-Z]+", j["title"].lower()) if t and len(t) > 2])
        # Prioritize skills; fallback to title terms
        keywords = parsed.get("skills", []) or list(dict.fromkeys(title_terms))

        print(f"🔍 Attempting to fetch live jobs for keywords: {keywords[:3]}")

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
            print("⚠️ No live jobs fetched from external APIs, using fallback")
            live_raw = generate_fallback_live_jobs(keywords, max_jobs=20)
        else:
            print(f"✅ Successfully fetched {len(live_raw)} live jobs from external APIs")

        live_jobs = score_live_jobs(resume_text, parsed.get("skills", []), live_raw)[:10]

        return jsonify({
            'success': True,
            'jobs': jobs,
            'parsed': parsed,
            'live_jobs': live_jobs
        })

    except Exception as e:
        print(f"Error in upload: {e}")
        return jsonify({'success': False, 'error': str(e)})

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file given as bytes."""
    try:
        from PyPDF2 import PdfReader
        from io import BytesIO
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


# Add missing functions from app_minimal.py
def fetch_live_jobs_from_arbeitnow(keywords: list[str], max_jobs: int = 30) -> list[dict]:
    """Fetch live jobs from Arbeitnow API using provided keywords."""
    live_jobs: list[dict] = []
    try:
        if not keywords:
            print("⚠️ No keywords provided for live job search")
            return live_jobs

        print(f"🔍 Fetching live jobs for keywords: {keywords[:3]}")

        # Query per top skill to diversify results; cap to top 6 skills
        seen = set()
        for term in keywords[:6]:
            if not term or len(term) < 2:
                continue

            print(f"  Searching for: {term}")
            page = 1
            while len(live_jobs) < max_jobs and page <= 2:
                try:
                    import requests
                    resp = requests.get(
                        "https://arbeitnow.com/api/job-board-api",
                        params={"search": term, "page": page},
                        timeout=15,
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        }
                    )

                    if resp.status_code != 200:
                        print(f"    ❌ Page {page}: HTTP {resp.status_code}")
                        break

                    # Check content type
                    content_type = resp.headers.get("content-type", "")
                    if not content_type.startswith("application/json"):
                        print(f"    ⚠️ Page {page}: Non-JSON response ({content_type})")
                        break

                    try:
                        payload = resp.json()
                    except json.JSONDecodeError as e:
                        print(f"    ❌ Page {page}: JSON decode error - {e}")
                        break

                    if not isinstance(payload, dict):
                        print(f"    ⚠️ Page {page}: Response is not a dictionary")
                        break

                    items = payload.get("data", [])
                    if not items:
                        print(f"    ℹ️ Page {page}: No data found")
                        break

                    print(f"    ✅ Page {page}: Found {len(items)} jobs")

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
                    print(f"    ❌ Page {page}: Request error - {e}")
                    break
                except Exception as e:
                    print(f"    ❌ Page {page}: Unexpected error - {e}")
                    break

                if len(live_jobs) >= max_jobs:
                    break

        print(f"✅ Total live jobs fetched: {len(live_jobs)}")

    except Exception as e:
        print(f"❌ Error in fetch_live_jobs_from_arbeitnow: {e}")
        import traceback
        traceback.print_exc()

    return live_jobs


def fetch_live_jobs_from_custom_api(keywords: list[str], max_jobs: int = 50) -> list[dict]:
    """Fetch live jobs from a custom API requiring Bearer token."""
    live: list[dict] = []
    base = os.getenv("CUSTOM_JOBS_API_URL", "").strip()
    token = os.getenv("CUSTOM_JOBS_API_TOKEN", "").strip()
    if not base or not token or not keywords:
        return live

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    try:
        import requests
        seen = set()
        for term in keywords[:6] or [""]:
            if not term:
                page = 1
            else:
                page = 1
            while len(live) < max_jobs and page <= 4:
                try:
                    resp = requests.get(base, params={"search": term, "page": page, "limit": max_jobs}, headers=headers, timeout=20)
                    if resp.status_code != 200:
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
                        break
                    for it in items:
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
                except Exception:
                    break
            if len(live) >= max_jobs:
                break
    except Exception:
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

    print(f"✅ Generated {len(live_jobs)} fallback live jobs")
    return live_jobs


def score_live_jobs(resume_text: str, skills: list[str], jobs: list[dict]) -> list[dict]:
    """Score live jobs by skill overlap and TF-IDF similarity to resume."""
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
                from sklearn.metrics.pairwise import cosine_similarity
                job_vec = vectorizer.transform([combined_text])
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


def load_model_minimal():
    global job_data, vectorizer, job_vectors

    try:
        # Try to load just a small sample dataset first
        if os.path.exists("data/job_dataset_sample.csv"):
            import pandas as pd
            job_data = pd.read_csv("data/job_dataset_sample.csv")
            print(f"✅ Loaded {len(job_data):,} jobs from sample dataset")

            # Load smaller model files if available
            if os.path.exists("data/tfidf_vectorizer.joblib"):
                import joblib
                vectorizer = joblib.load("data/tfidf_vectorizer.joblib")
                print("✅ Loaded TF-IDF vectorizer")

            if os.path.exists("data/trained_model.joblib"):
                job_vectors = joblib.load("data/trained_model.joblib")
                print("✅ Loaded job vectors")

            return True
        else:
            print("⚠️ No sample dataset found")
            return False

    except Exception as e:
        print(f"❌ Error loading minimal model: {e}")
        return False

@app.route('/')
def index():
    return "Flask app is running!"

if __name__ == '__main__':
    print("🚀 Starting modified Flask app...")
    print("🌐 Web server will start on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=False)
