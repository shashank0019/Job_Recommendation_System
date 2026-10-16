# Career Guidance Platform

Career Guidance Platform is a full-stack web application for career preparation and job discovery. It combines a Flask backend, a React/Vite frontend, authentication, local JSON persistence, resume-based recommendations, interview practice, coding problems, job postings, and community interview experiences.

## Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Project](#running-the-project)
- [Frontend Pages](#frontend-pages)
- [Backend API](#backend-api)
- [Authentication](#authentication)
- [Local Database](#local-database)
- [Job Recommendations](#job-recommendations)
- [Interview Practice](#interview-practice)
- [Development Commands](#development-commands)
- [Troubleshooting](#troubleshooting)
- [Security Notes](#security-notes)

## Features

### User accounts

- Sign up with name, email, and password.
- Sign in with an existing account.
- Backend session-token authentication.
- Profile viewing and profile updates.
- Logout and session cleanup.

### Career dashboard

- Central dashboard for career tools.
- Navigation between recommendations, jobs, interviews, problems, and profile.
- Authentication gate for protected application areas.

### Job recommendations

- Resume upload support.
- Resume text extraction.
- Job recommendation endpoint.
- TF-IDF and machine-learning-based matching support.
- Job dataset and job-matching utilities.

### Job postings

- Browse job postings.
- Search by title, company, description, or location.
- Filter by job type, experience level, tags, and remote availability.
- Create a job posting.
- Edit a job posting created by the signed-in user.
- Delete a job posting created by the signed-in user.
- Add requirements, salary, contact email, application URL, tags, and deadline.

### Interview practice

- Select an interview category.
- Generate interview questions.
- Run a virtual interview.
- Optional camera and face-detection components.
- Submit interview answers.
- View interview results and feedback.
- Store interview history locally in the browser.

### Interview experiences

- Browse community interview experiences.
- Filter experiences.
- Create an interview experience.
- Edit or delete the user's own experience.
- Vote on experiences.
- Search experiences by company.

### Coding problems

- Browse the problem collection.
- Load problem details.
- Submit solutions.
- Track problem-related responses through the backend.

## Technology Stack

### Backend

- Python 3.13
- Flask 3
- Flask-CORS
- Python dotenv
- bcrypt
- Flask JWT dependencies
- PyMongo-compatible model interfaces
- scikit-learn and joblib for recommendation support
- pandas and NumPy for data processing
- spaCy and NLTK for language processing
- PyPDF2 for PDF resume extraction
- OpenAI client for optional enhanced interview functionality

### Frontend

- React 19
- React DOM 19
- React Router 6
- Vite 7
- Axios
- MediaPipe Tasks Vision
- PropTypes

### Storage

The active development configuration uses local JSON files. MongoDB support remains in the codebase, but local mode is enabled so the project can run without a MongoDB server.

## Architecture

```text
Browser
  |
  | React/Vite frontend :5173
  |
  | HTTP requests
  v
Flask backend :5000
  |
  +-- Authentication routes and session middleware
  +-- Job posting routes
  +-- Interview experience routes
  +-- Resume and recommendation routes
  +-- Interview and problem routes
  |
  v
Local JSON database in data\auth\
```

The frontend stores the active backend session token in browser local storage. Protected requests send it as:

```text
Authorization: Bearer <session-token>
```

## Project Structure

```text
Final_pro/
├── app.py                         # Main Flask application
├── requirements.txt               # Python dependencies
├── .env                           # Local environment values; do not commit secrets
├── .env.example                   # Environment configuration example
├── api/
│   ├── job_posting_routes.py      # Job posting endpoints
│   └── interview_experience_routes.py
├── auth/
│   ├── middleware.py              # Authentication decorators
│   ├── models.py                  # User and session models
│   ├── routes.py                  # Signup, signin, profile, logout
│   └── utils.py                   # Password and input utilities
├── config/
│   └── database.py                # Mongo/local database configuration
├── models/
│   ├── job_posting.py             # Job posting model
│   └── interview_experience.py    # Interview experience model
├── data/
│   └── auth/                      # Local JSON database files
├── frontend/
│   ├── package.json               # Frontend dependencies and scripts
│   ├── src/
│   │   ├── components/            # Shared React components
│   │   ├── context/               # Authentication context
│   │   ├── pages/                 # Application pages
│   │   ├── main.jsx               # React entry point and routes
│   │   └── styles.css             # Global styles
│   └── dist/                      # Generated production build
└── projectshanshank.md            # This documentation file
```

## Requirements

- Windows PowerShell
- Python 3.13
- Node.js and npm
- A modern web browser

MongoDB is not required when local database mode is enabled.

## Installation

### Backend setup

From the project root:

```powershell
cd "C:\Users\shash\OneDrive\Desktop\Projects\Final_pro\Final_pro"
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If `.venv` already exists, only the dependency installation command is normally needed.

### Frontend setup

```powershell
cd "C:\Users\shash\OneDrive\Desktop\Projects\Final_pro\Final_pro\frontend"
npm install
```

## Configuration

The backend reads configuration from `.env`. The important development settings are:

```env
USE_LOCAL_DATABASE=true
PORT=5000
HOST=0.0.0.0
```

Optional job API settings:

```env
RAPIDAPI_KEY=your_rapidapi_key_here
RAPIDAPI_HOST=jsearch.p.rapidapi.com
```

Optional OpenAI or other service keys may be used by enhanced features. Keep real keys only in `.env` or another secret store.

## Running the Project

### Start the backend

Open the first PowerShell terminal:

```powershell
cd "C:\Users\shash\OneDrive\Desktop\Projects\Final_pro\Final_pro"
.\.venv\Scripts\python.exe .\app.py
```

The backend runs at:

```text
http://127.0.0.1:5000
```

Keep this terminal open.

### Start the frontend

Open a second PowerShell terminal:

```powershell
cd "C:\Users\shash\OneDrive\Desktop\Projects\Final_pro\Final_pro\frontend"
npm run dev
```

Open the URL shown by Vite, normally:

```text
http://127.0.0.1:5173
```

### Startup order

1. Start the backend.
2. Start the frontend.
3. Open the frontend URL in the browser.

To stop a server, press `Ctrl+C` in its terminal.

## Frontend Pages

| Path | Purpose |
|---|---|
| `/` | Main career dashboard |
| `/classic` | Job recommendation and resume workflow |
| `/jobs` | Browse, create, edit, and delete job postings |
| `/experiences` | Browse and share interview experiences |
| `/interview/setup` | Choose an interview category |
| `/interview/run` | Run a virtual interview |
| `/interview/results` | View interview results |
| `/interview/results-demo` | View demo interview results |
| `/problems` | Browse coding problems |
| `/profile` | View and edit the user profile |

## Backend API

The backend base URL is:

```text
http://127.0.0.1:5000
```

### System and recommendation routes

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Backend root response |
| `GET` | `/health` | Health check |
| `GET` | `/test` | Basic backend test route |
| `POST` | `/recommend` | Generate job recommendations |
| `POST` | `/upload` | Upload and process a resume |
| `POST` | `/train` | Train or refresh recommendation data |

### Authentication routes

| Method | Endpoint | Auth |
|---|---|---|
| `POST` | `/auth/signup` | Public |
| `POST` | `/auth/signin` | Public |
| `POST` | `/auth/logout` | Required |
| `GET` | `/auth/profile` | Required |
| `PUT` | `/auth/profile` | Required |
| `GET` | `/auth/verify` | Required |
| `GET` | `/auth/health` | Public |

### Job routes

| Method | Endpoint | Auth |
|---|---|---|
| `GET` | `/api/jobs` | Public |
| `GET` | `/api/jobs/<job_id>` | Public |
| `POST` | `/api/jobs` | Required |
| `PUT` | `/api/jobs/<job_id>` | Required and owner-only |
| `DELETE` | `/api/jobs/<job_id>` | Required and owner-only |
| `GET` | `/api/my-jobs` | Required |

### Interview experience routes

| Method | Endpoint | Auth |
|---|---|---|
| `GET` | `/api/experiences` | Public |
| `GET` | `/api/experiences/<experience_id>` | Public |
| `GET` | `/api/experiences/company/<company>` | Public |
| `POST` | `/api/experiences` | Required |
| `PUT` | `/api/experiences/<experience_id>` | Required and owner-only |
| `DELETE` | `/api/experiences/<experience_id>` | Required and owner-only |
| `POST` | `/api/experiences/<experience_id>/vote` | Required |
| `GET` | `/api/my-experiences` | Required |

### Interview and problem routes

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/problems` | List problems |
| `GET` | `/api/problems/<problem_id>` | Get one problem |
| `POST` | `/submissions` | Submit a problem solution |
| `POST` | `/interview/questions` | Generate interview questions |
| `POST` | `/interview/submit` | Submit an interview |

## Authentication

### Signup

The frontend sends the name, email, and password to `/auth/signup`. Email addresses are normalized and duplicate accounts are rejected.

### Signin

The frontend sends the email and password to `/auth/signin`. A successful response includes:

- User public data
- Backend session token

The browser stores the token and sends it on protected API calls.

### Session validation

When the frontend starts, it validates the saved token through `/auth/profile`. Invalid or expired tokens are cleared so the user can sign in again.

### Ownership

Job postings and interview experiences are associated with the authenticated backend user. Only the owner can edit or delete their own content.

## Local Database

Local mode is enabled with:

```env
USE_LOCAL_DATABASE=true
```

Data is stored in:

```text
data\auth\
```

Main files:

| File | Contents |
|---|---|
| `users.json` | User accounts and password hashes |
| `sessions.json` | Active backend sessions |
| `job_postings.json` | Job postings |
| `interview_experiences.json` | Community interview experiences |

The local database provides Mongo-like collection operations used by the existing models, including lookup, filtering, sorting, pagination, insert, update, and delete.

Do not delete `data\auth\` unless you intentionally want to remove local application data.

## Job Recommendations

The recommendation workflow can accept resume content, process extracted text, and compare it with available job data. The project includes:

- Resume upload handling
- PDF text extraction
- Dataset loading
- TF-IDF vectorization
- Similarity-based matching
- Job recommendation response generation

Some live job integrations require external API credentials. Without those credentials, local or bundled job data can still be used where supported.

## Interview Practice

The interview workflow consists of:

1. Selecting an interview category.
2. Requesting interview questions.
3. Running the interview in the browser.
4. Capturing answers and optional camera-related data.
5. Submitting the interview.
6. Displaying feedback and results.

Browser permissions may be required for camera or microphone features.

## Development Commands

### Backend

Start the backend:

```powershell
.\.venv\Scripts\python.exe .\app.py
```

Run a Python script with the project interpreter:

```powershell
.\.venv\Scripts\python.exe .\script_name.py
```

### Frontend

Start the Vite development server:

```powershell
npm run dev
```

Build the frontend:

```powershell
npm run build
```

Preview a production build:

```powershell
npm run preview
```

## Verification Commands

Check backend health:

```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:5000/health" -UseBasicParsing
```

Check jobs:

```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/jobs?page=1&limit=20" -UseBasicParsing
```

Check interview experiences:

```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/experiences?page=1&limit=20" -UseBasicParsing
```

## Troubleshooting

### `ERR_CONNECTION_REFUSED`

The backend is not running or is not listening on port `5000`. Start it from the project root:

```powershell
.\.venv\Scripts\python.exe .\app.py
```

### `401 Unauthorized`

The saved browser session may be expired or invalid:

1. Log out.
2. Refresh the browser.
3. Sign in again with the existing email and password.

### Same email cannot sign up again

This is expected. Use **Sign In** for an existing account. Signup with a duplicate email returns a conflict response.

### Frontend cannot reach the backend

Confirm that:

- The backend is running on port `5000`.
- The frontend is running on port `5173`.
- The browser is using `http://127.0.0.1:5173`.
- No firewall or another process is blocking port `5000`.

### Port 5000 is already in use

Find the process:

```powershell
Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
```

Stop only the specific process ID if necessary:

```powershell
Stop-Process -Id <PROCESS_ID>
```

### Backend dependency error

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Frontend dependency error

```powershell
cd frontend
npm install
npm run build
```

## Security Notes

- Never commit `.env`.
- Never commit API keys, passwords, or session tokens.
- Use strong passwords for local accounts.
- Rotate any API key that has been exposed.
- The Flask development server is intended for local development, not production hosting.
- For production, use a production WSGI server, secure secret management, HTTPS, and a managed database.

## Git Location

The actual Git repository is the inner project folder:

```text
C:\Users\shash\OneDrive\Desktop\Projects\Final_pro\Final_pro
```

Run Git commands from that folder:

```powershell
cd "C:\Users\shash\OneDrive\Desktop\Projects\Final_pro\Final_pro"
git status
git add .
git commit -m "Update project documentation"
```
