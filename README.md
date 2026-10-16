# 🚀 Smart Career Guidance & AI Job Recommendation Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Backend-Flask-black.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/Frontend-React%20%7C%20Vite-61DAFB.svg?logo=react&logoColor=black)](https://reactjs.org/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![MongoDB Atlas](https://img.shields.io/badge/Database-MongoDB%20Atlas-47A248.svg?logo=mongodb&logoColor=white)](https://www.mongodb.com/atlas)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An intelligent, end-to-end career guidance platform powered by Machine Learning and NLP. The system extracts skills from candidate resumes, matches and ranks job opportunities using TF-IDF vectorization and cosine similarity, provides AI-driven mock interviews with automated scoring, and includes a curated technical problem practice module.

---

## 📌 Table of Contents
- [✨ Key Features](#-key-features)
- [🏗️ System Architecture](#️-system-architecture)
- [🛠️ Tech Stack](#️-tech-stack)
- [📂 Project Directory Structure](#-project-directory-structure)
- [📊 Datasets & Machine Learning](#-datasets--machine-learning)
- [⚡ Quick Start & Installation](#-quick-start--installation)
- [🔌 API Endpoints](#-api-endpoints)
- [👨‍💻 Author](#-author)

---

## ✨ Key Features

### 1. 📄 Smart Resume Parsing & Skill Extraction
- Multi-format resume parsing (`.pdf`, `.docx`, `.txt`).
- NLP-driven keyword and entity recognition using **spaCy** and **NLTK** to detect programming languages, frameworks, libraries, and tools.
- Real-time text preprocessing, tokenization, lemmatization, and stopword removal.

### 2. 🎯 Machine Learning Job Recommendation
- **TF-IDF Vectorization & Cosine Similarity**: Converts job descriptions and candidate profiles into vector spaces to calculate exact mathematical relevance scores.
- **Skill Overlap & Gap Analysis**: Highlights matching skills and pinpoints missing skills required for target job roles.
- **Pre-trained Offline Models**: Precomputed vectors saved with **Joblib** for sub-second recommendation responses without retraining.

### 3. 🤖 AI-Powered Mock Interview Platform
- Dynamic interview question generation tailored to candidate experience and selected roles (Software Engineer, Data Scientist, Product Manager, etc.).
- Integrated **OpenAI API** support with automated response quality scoring.
- Audio speech-to-text recording support and browser camera proctoring simulation.

### 4. 💻 Coding Practice Module
- Built-in repository of **200+ curated programming problems** (LeetCode patterns).
- Filter by difficulty (Easy, Medium, Hard), topic tags, and acceptance rate.

### 5. 🔐 User Authentication & Profiles
- User registration, login, and JWT-authenticated session tokens.
- Cloud persistence with **MongoDB Atlas** with automated local JSON fallback.

---

## 🏗️ System Architecture

```text
+-------------------------------------------------------------+
|                 Frontend (React + Vite)                     |
|  - Resume Upload & Parsing UI    - Job Recommendation Cards |
|  - Skill Gap Visualization       - AI Mock Interview Arena  |
+------------------------------+------------------------------+
                               | REST API (Axios)
                               v
+-------------------------------------------------------------+
|                  Backend (Flask REST API)                   |
|  - /recommend & /upload           - /api/interview          |
|  - /auth (JWT + MongoDB)          - /api/problems           |
+------------------------------+------------------------------+
                               |
        +----------------------+----------------------+
        |                                             |
        v                                             v
+-----------------------------+         +-----------------------------+
|     NLP & Machine Learning  |         |      Data Persistence       |
|  - spaCy / NLTK Extraction  |         |  - MongoDB Atlas (Cloud)    |
|  - TF-IDF Vectorizer        |         |  - Joblib Models (.joblib)  |
|  - Cosine Similarity Scorer |         |  - Filtered Job Datasets    |
+-----------------------------+         +-----------------------------+
```

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: React.js (Vite)
- **Styling**: Vanilla CSS3 (Modern dark-mode glassmorphic design)
- **HTTP Client**: Axios
- **Icons & UI**: Lucide React

### Backend
- **Framework**: Python Flask, Flask-CORS
- **Natural Language Processing**: spaCy, NLTK
- **Machine Learning**: Scikit-learn (TfidfVectorizer, Cosine Similarity)
- **Model Serialization**: Joblib
- **Database**: MongoDB Atlas (PyMongo) / Local JSON Fallback
- **PDF/Document Parsing**: PyPDF2, pdfplumber, python-docx

---

## 📂 Project Directory Structure

```text
Job_Recommendation_System/
├── api/                        # Modular API routes
├── auth/                       # Authentication middlewares and user models
├── config/                     # Database & environment configurations
├── data/                       # Datasets, models & precomputed vectorizers
│   ├── job_dataset_medium.csv  # Included clean dataset (~18 MB)
│   ├── job_dataset_sample.csv  # Lightweight sample dataset
│   ├── tfidf_vectorizer.joblib # Serialized TF-IDF model
│   ├── trained_model.joblib    # Serialized job vector matrix
│   └── Problems/               # Problem sets for coding practice
├── frontend/                   # Modern React (Vite) UI
│   ├── src/                    # Components, pages, hooks, styles
│   ├── package.json
│   └── vite.config.js
├── models/                     # Data schemas & evaluation helpers
├── scripts/                    # Maintenance & dataset utilities
├── app.py                      # Main Flask application entrypoint
├── app_minimal.py              # Lightweight production server
├── interview_openai.py         # AI Interview generator
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## 📊 Datasets & Machine Learning

### Included Dataset
This repository includes [`data/job_dataset_medium.csv`](data/job_dataset_medium.csv) (~18 MB), pre-cleaned and pre-processed to run efficiently out of the box without requiring massive memory consumption.

### Full Kaggle Dataset
For large-scale offline experiments, the project supports the **LinkedIn 1.3M Job Postings** dataset:
- If you have the full `unified_job_dataset.csv` (~476 MB), place it inside the `data/` directory.
- The system automatically detects and scales to the largest available dataset.
- *Note: Datasets exceeding 100 MB are excluded from Git commits via `.gitignore` in accordance with GitHub policy.*

---

## ⚡ Quick Start & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Clone the Repository
```bash
git clone https://github.com/shashank0019/Job_Recommendation_System.git
cd Job_Recommendation_System
```

### 2. Backend Setup
```bash
# Create and activate virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download required NLP language models
python -m spacy download en_core_web_sm
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```env
FLASK_ENV=development
PORT=5000
MONGODB_URI=your_mongodb_connection_string_optional
OPENAI_API_KEY=your_openai_api_key_optional
```

### 4. Run the Backend Server
```bash
python app_minimal.py
```
*Backend runs on `http://localhost:5000`*

### 5. Frontend Setup
In a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
*Frontend runs on `http://localhost:3000` or `http://localhost:5173`*

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/recommend` | Matches raw resume text against the job corpus and returns ranked results |
| `POST` | `/upload` | Accepts `.pdf`, `.docx`, or `.txt` resume files and outputs skill & job analysis |
| `POST` | `/auth/register` | Registers a new user account |
| `POST` | `/auth/login` | Authenticates user and returns JWT session |
| `GET` | `/api/problems` | Retrieves curated coding practice problems with tags and difficulty |
| `POST` | `/api/interview/start` | Starts an AI interview session for a specified role |
| `POST` | `/api/interview/evaluate`| Scores an interview answer against rubric standards |

---

## 👨‍💻 Author

**Shashank C. A.**  
- GitHub: [@shashank0019](https://github.com/shashank0019)
- Academic Project: Career Guidance Platform & Machine Learning Job Matcher

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
