# Job Recommendation System

## Interview and Technical Documentation

**Prepared for:** Shashank C.A.  
**Academic project:** Career Guidance Platform  
**Primary contribution:** Job Recommendation System  
**Team size:** Four members

> This document focuses on the part of the team project owned and developed by
> Shashank: recommending suitable jobs from a resume. Interview practice and
> coding practice are other modules in the larger platform and are outside the
> primary scope of this document.

---

## 1. Project overview

The Job Recommendation System is a resume-to-job matching application. A user
can paste resume text or upload a PDF/TXT resume. The backend extracts skills and
important terms, represents both the resume and job postings as numerical
TF-IDF vectors, calculates cosine similarity, and returns the highest-scoring
jobs.

The system also returns a small set of skill-based job cards. These cards can
come from the configured live-job integration, while the current `/recommend`
and `/upload` routes also contain a local categorized fallback list. The
similarity-ranked results are the core machine-learning recommendation output.

### Problem statement

Job seekers often search manually through many postings and may miss relevant
opportunities because job descriptions and resumes use different wording. This
system automates an initial matching step by comparing the language of a
resume with the language used in job postings.

### Main objectives

1. Accept resume text or a resume file.
2. Extract technical skills and useful keywords.
3. Compare the candidate profile with available job descriptions.
4. Rank jobs by textual relevance.
5. Display job title, company, location, job details, and a similarity score.
6. Provide a useful fallback when external job APIs are unavailable.
7. Keep the recommendation model reusable by saving it with Joblib.

---

## 2. My contribution and a good interview introduction

### Short introduction

> “Our project is a Career Guidance Platform developed by a four-member team.
> My main contribution was the Job Recommendation System. I implemented the
> resume-processing and job-matching workflow: resume text is extracted and
> cleaned, technical skills are identified using spaCy/ NLTK-based processing,
> job-posting text is converted into TF-IDF vectors, and cosine similarity is
> used to rank the most relevant jobs. The backend is implemented in Python
> with Flask, the user interface is React, job data is stored in CSV files for
> model training, and MongoDB Atlas supports platform authentication and
> related application data. I also worked on PDF upload handling, saved model
> artifacts, API integration, validation, and testing.”

### Contribution boundary

The complete application contains job recommendations, interview practice,
coding practice, authentication, job posting, and interview-experience
features. The recommendation pipeline is the part to present as my primary
ownership:

```text
Resume input
    -> text extraction
    -> cleaning and skill/keyword extraction
    -> TF-IDF vectorization
    -> cosine similarity against job vectors
    -> filtering and top-K ranking
    -> recommendation response and UI
```

---

## 3. Technologies used

### Programming languages

- **Python**: backend, NLP, machine learning, file processing, API client, and
  model training.
- **JavaScript / JSX**: React frontend and browser interaction.
- **HTML/CSS**: page structure and styling.
- **JSON**: API payloads, skill configuration, and local application data.
- **CSV**: training dataset for job postings.

### Backend and machine-learning libraries

- **Flask**: REST API and server-side application.
- **Flask-CORS**: cross-origin communication between the React frontend and
  Flask backend.
- **pandas**: loading and manipulating the job dataset.
- **NumPy**: numerical arrays and vector operations.
- **scikit-learn**: `TfidfVectorizer` and `cosine_similarity`.
- **spaCy**: tokenization, part-of-speech information, noun chunks, and named
  entities when the English model is available.
- **NLTK**: tokenization and English stop-word removal.
- **PyPDF2**: extracting text from uploaded PDF resumes.
- **Joblib**: persisting the trained TF-IDF vectorizer and job vectors.
- **requests**: calling external job-search APIs.
- **python-dotenv**: loading configuration from `.env`.

### Frontend libraries

- **React**: component-based user interface.
- **Vite**: frontend development server and production build.
- **Axios**: HTTP requests from the browser to Flask.
- **React Router**: navigation for the larger platform.

### Data stores

| Data store | Role in this project |
|---|---|
| `data/job_dataset.csv` | Main offline job-posting dataset used to train the matcher |
| `data/job_dataset_sample.csv` and `job_dataset_medium.csv` | Smaller datasets useful for development/testing |
| `data/trained_model.joblib` | Saved matrix of job vectors |
| `data/tfidf_vectorizer.joblib` | Saved fitted vocabulary and IDF weights |
| MongoDB Atlas | Authentication, user profiles, sessions, and other platform records |
| JSON files under `data/` | Local application data such as users, sessions, posted jobs, and skills |

The recommendation model itself is trained from CSV data; it does not query
MongoDB to calculate similarity.

---

## 4. System architecture

```text
                         +----------------------+
                         | React + Vite frontend |
                         +----------+-----------+
                                    |
                         Axios / HTTP requests
                                    |
                         +----------v-----------+
                         | Flask REST backend   |
                         | app.py               |
                         +---+--------------+---+
                             |              |
                  +----------v---+   +------v-------+
                  | ResumeParser |   | JobMatcher   |
                  | spaCy/NLTK   |   | sklearn      |
                  +----------+---+   +------+-------+
                             |              |
                    parsed skills       job vectors
                             |              |
                         +---v--------------v---+
                         | ranked recommendations|
                         +-----------------------+

 CSV job data -> model training -> Joblib artifacts
 MongoDB Atlas -> authentication and platform data
 RapidAPI JSearch -> optional external job integration
```

### Important modules

| File | Responsibility |
|---|---|
| `app.py` | Creates Flask app, registers routes, handles `/recommend`, `/upload`, and `/train` |
| `resume_parser.py` | Cleans resume text and extracts categorized skills/keywords |
| `job_matcher.py` | Loads data/artifacts, trains TF-IDF, computes similarity, and ranks jobs |
| `train_model.py` | Validates data, trains the matcher, and runs a sample match |
| `api_client.py` | Optional RapidAPI JSearch client and response normalization |
| `config/database.py` | MongoDB Atlas connection and supporting local JSON helpers |
| `frontend/src/App.jsx` | Resume input/upload, recommendation request, and result display |
| `data/job_dataset.csv` | Offline training records |

---

## 5. End-to-end recommendation workflow

### Step 1: Resume input

The frontend accepts either:

- Text pasted into the resume text area.
- A `.pdf` or `.txt` upload.

`POST /recommend` receives JSON containing `resume_text`. `POST /upload`
receives a multipart file named `resume_file`. For PDF files, the backend reads
all pages with PyPDF2 before continuing with the same matching workflow.

### Step 2: Input validation

The backend verifies that JSON exists, `resume_text` is present for the text
route, and the extracted text is not empty. It also verifies that the matcher
has been trained before attempting recommendation.

### Step 3: Resume preprocessing

`ResumeParser.clean_text()`:

1. Converts text to lowercase.
2. Replaces punctuation and special characters with spaces.
3. Normalizes repeated whitespace.
4. Preserves digits because experience information may be useful.

### Step 4: Skill and keyword extraction

The parser maintains categorized technical skills, including:

- Programming languages: Python, Java, JavaScript, C++, and others.
- Frameworks: React, Django, Flask, Spring, Angular, and others.
- Databases: MySQL, PostgreSQL, MongoDB, Redis, and others.
- Cloud platforms: AWS, Azure, GCP, and others.
- Tools: Git, Docker, Kubernetes, Jenkins, Jira, and others.

When `en_core_web_sm` is available, spaCy contributes entities, noun chunks,
and part-of-speech filtering. NLTK removes stop words and tokenizes text. If
spaCy cannot load, the parser uses a fallback based on tokenization,
stop-word removal, and matching the configured skill dictionary.

The parser returns:

- Skills grouped by category.
- Up to 50 keywords.
- Top skills by category.
- Total skill count.
- Keyword count.
- Detected categories.

### Step 5: Job text construction

For every job row, `JobMatcher` combines the available fields into one
document:

```text
title + description + requirements + skills + industry
       + benefits + company + work_type + experience_level
```

The current main dataset contains fields such as `job_id`, `title`, `company`,
`location`, `description`, `requirements`, `skills`, `experience_level`, and
`salary_range`.

### Step 6: TF-IDF representation

The model uses scikit-learn's `TfidfVectorizer` with:

- English stop-word removal.
- Unigrams and bigrams: `ngram_range=(1, 2)`.
- A maximum vocabulary of 5,000 features.
- `min_df=1`.
- `max_df=0.95`.

For a term `t` in document `d`, TF-IDF gives a high weight when the term is
important in that document but not common across every document. Conceptually:

```text
TF-IDF(t, d) = term_frequency(t, d) * inverse_document_frequency(t)
```

The fitted vectorizer creates the vocabulary and IDF values from job postings.
The same vectorizer must be used for both job postings and the incoming
resume; otherwise their vector dimensions and meanings would not match.

### Step 7: Similarity scoring

The resume is transformed using the fitted vectorizer. The system compares that
resume vector with every saved job vector using cosine similarity:

```text
cosine_similarity(A, B) = (A . B) / (||A|| * ||B||)
```

With TF-IDF vectors, the score is normally between 0 and 1:

- `1.0`: very similar term direction.
- `0.0`: no shared weighted vocabulary.
- Higher score: stronger textual relevance, not a guarantee of hiring success.

### Step 8: Ranking and filtering

The system sorts all `(job_index, similarity_score)` pairs in descending order,
keeps scores at or above the configured threshold, and returns at most `top_k`
jobs. The main Flask route calls the matcher with `top_k=10` and
`min_similarity=0.05`.

Each returned offline result includes the original job fields, a rounded
`similarity_score`, and `job_index`.

### Step 9: Live/fallback job cards

The response also contains up to 10 `live_jobs`. The route extracts skills from
the resume, matches them against categories such as Python, JavaScript, React,
Java, AWS, machine learning, data science, and DevOps, removes duplicates, and
fills missing results with default job cards.

`api_client.py` additionally implements an optional RapidAPI JSearch client. It
normalizes external records into the project's common format and can search by
query or a list of skills. A RapidAPI key is required for real external API
calls. The current recommendation route's fallback cards should not be
described as guaranteed real-time results; they are local categorized data.

---

## 6. Model training and persistence

Run training from the project directory:

```powershell
python train_model.py
```

Training:

1. Checks that `data/job_dataset.csv` exists.
2. Loads job rows with pandas.
3. Combines the job fields into documents.
4. Fits the TF-IDF vectorizer.
5. Transforms every job document.
6. Saves the vectorizer to `data/tfidf_vectorizer.joblib`.
7. Saves the job matrix to `data/trained_model.joblib`.
8. Tests the model with a sample resume.

At application startup, `JobMatcher` loads these artifacts when present. The
matcher also loads up to 5,000 CSV rows by default for runtime performance.
If the stored vector count and loaded data row count disagree, the code
attempts to retrain before matching.

### Why save the model?

Without persistence, the server would need to fit TF-IDF every time it starts.
Saving the vocabulary, IDF values, and job vectors makes normal recommendation
requests much faster. Retraining is needed when the dataset or preprocessing
strategy changes.

---

## 7. API contract

### `POST /recommend`

Request:

```json
{
  "resume_text": "Python developer with Django, React, SQL and AWS experience",
  "max_results": 10
}
```

Successful response shape:

```json
{
  "success": true,
  "parsed": {
    "skills": {},
    "keywords": [],
    "total_skills": 0,
    "keyword_count": 0,
    "categories": []
  },
  "total_matches": 1,
  "jobs": [
    {
      "title": "Software Engineer",
      "company": "TechCorp",
      "similarity_score": 0.42,
      "job_index": 0
    }
  ],
  "live_jobs": []
}
```

The exact job fields depend on the CSV row. Empty input returns a client error;
an unavailable/untrained model returns a server error.

### `POST /upload`

Send a multipart request with a file field named `resume_file`. PDF and text
files are supported. The response returns parsed resume data, ranked jobs, and
skill-based live/fallback jobs.

### `POST /train`

Trains or retrains the matcher from `data/job_dataset.csv` and returns training
statistics.

### `GET /health`

Returns a basic service-health response.

---

## 8. Setup and execution

### Backend

```powershell
cd C:\Users\shash\OneDrive\Desktop\Projects\Final_pro\Final_pro
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python train_model.py
python app.py
```

The backend is normally available at `http://localhost:5000`.

### Frontend

In a second terminal:

```powershell
cd C:\Users\shash\OneDrive\Desktop\Projects\Final_pro\Final_pro\frontend
npm install
npm run dev
```

Vite normally serves the frontend at `http://localhost:5173`.

### Configuration

Copy `.env.example` to `.env` and configure only the values needed for the
environment:

```text
RAPIDAPI_KEY=your_key
RAPIDAPI_HOST=jsearch.p.rapidapi.com
MONGODB_URI=your_mongodb_atlas_uri
MONGODB_DB_NAME=career_guidance_platform
```

Never commit real API keys, passwords, or MongoDB connection strings.

---

## 9. Why this technique was selected

### Advantages of TF-IDF plus cosine similarity

- Easy to explain in an academic interview.
- Fast to train and fast to query for a moderate dataset.
- Does not require labelled “good match/bad match” examples.
- Works well when resumes and job descriptions share skill terminology.
- Supports interpretable features such as Python, React, SQL, and AWS.
- Easy to retrain when new job data is added.

### Limitations

- It is lexical: synonyms with no shared words may receive a low score.
- It does not deeply understand seniority, salary, commute, or career goals.
- Common terms can dominate unless preprocessing is carefully maintained.
- Skill presence does not prove proficiency.
- A cosine score is a relevance signal, not an accuracy percentage.
- The hard-coded fallback job cards are not a substitute for a verified live
  job feed.

### Future improvements

1. Use sentence-transformer or other embedding models for semantic similarity.
2. Add explicit weights for required skills, experience, location, work type,
   and salary.
3. Use a hybrid score:

   ```text
   final_score =
       0.60 * text_similarity
       + 0.25 * skill_overlap
       + 0.10 * experience_fit
       + 0.05 * location/work-type fit
   ```

4. Collect anonymous clicks, saves, applications, and skips for feedback-based
   personalization.
5. Add a labelled evaluation set and measure Precision@K, Recall@K, MRR, and
   NDCG instead of claiming that cosine similarity is “accuracy”.
6. Move large-scale job search to a database/search index and add deduplication,
   expiry, and source tracking for live postings.
7. Protect uploads with file-size limits, extension/content checks, and malware
   scanning before production deployment.

---

## 10. Testing and troubleshooting

Useful checks in this repository include:

```powershell
python test_job_matching.py
python test_job_recommendation.py
python test_model_training.py
python test_file_upload.py
```

If the model is not ready:

```powershell
python train_model.py
```

If spaCy reports that the model is missing:

```powershell
python -m spacy download en_core_web_sm
```

If the external job API is unavailable, recommendations from the offline CSV
still provide the main matching path. Check `.env`, network access, the RapidAPI
key, and the API host before debugging the external integration.

---

## 11. Interview questions and answers

### What is the recommendation algorithm?

It is a content-based recommender. The system represents the resume and each
job posting as TF-IDF vectors and uses cosine similarity to rank jobs by textual
relevance.

### Why did you use content-based filtering?

There was no large user-item interaction history or labelled feedback dataset.
Content-based matching can work for a new user immediately from the resume,
without a cold-start problem caused by missing ratings.

### What is TF-IDF?

TF-IDF weights a term by how often it appears in one document and how rare it is
across the document collection. A skill that is important to a particular job
but not present in every job receives a stronger discriminative weight.

### Why cosine similarity?

Cosine similarity compares the direction of two vectors rather than their raw
length. This is useful because a long resume should not automatically be
considered a better match simply because it contains more words.

### What happens if spaCy is unavailable?

The parser falls back to tokenization, stop-word removal, and configured
technical-skill matching. This preserves a basic recommendation workflow
instead of making the complete feature unusable.

### Why use the same vectorizer for the resume and jobs?

The vectorizer defines the vocabulary and IDF weights. Transforming both sides
with the same fitted object ensures that feature index 100 means the same term
for the resume and every job.

### How would you evaluate the system?

I would create a test set where recruiters or domain experts label relevant
jobs for sample resumes. I would then report Precision@K, Recall@K, MRR/NDCG,
coverage, latency, and a comparison with a keyword baseline. I would not call a
similarity threshold an accuracy measurement.

### What was the main engineering challenge?

Keeping the model artifacts synchronized with the job rows was important. The
matcher loads both the saved vectors and CSV data, checks their sizes, and can
retrain when they do not correspond. PDF extraction, missing fields, external
API failures, and fallback skill extraction were additional reliability cases.

### How would you make it production-ready?

I would add authentication and authorization around sensitive routes, strict
upload validation, secret management, rate limiting, structured logging,
monitoring, API retries with bounded backoff, live-job expiry, model versioning,
and offline evaluation before changing ranking behavior.

---

## 12. One-minute explanation of the full data flow

> “The user pastes a resume or uploads a PDF. Flask receives the request and
> extracts PDF text when necessary. `ResumeParser` normalizes the text and
> identifies technical skills and keywords using spaCy and NLTK, with a
> dictionary-based fallback. `JobMatcher` combines important fields from each
> CSV job record and uses a fitted scikit-learn TF-IDF vectorizer to create job
> vectors. The incoming resume is transformed using the same vectorizer.
> Cosine similarity is calculated between the resume vector and all job vectors,
> the results are sorted, and the top jobs above the threshold are returned as
> JSON. React calls the endpoint with Axios and displays the parsed skills,
> similarity-ranked jobs, and additional skill-based job cards. Joblib stores
> the vectorizer and job matrix so the server does not retrain for every
> request.”

---

## 13. Honest project positioning

This is a strong academic content-based recommendation system, not a
replacement for a recruiter or a complete employment marketplace. Its main
implemented strength is transparent resume/job text matching with a reusable
offline model and a usable Flask/React interface. The next technical step is
measured evaluation and a richer hybrid ranking model that includes semantic
embeddings, structured constraints, and user feedback.

