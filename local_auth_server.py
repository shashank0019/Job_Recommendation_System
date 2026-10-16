#!/usr/bin/env python3
"""
Local File-Based Authentication Server
Uses JSON files for user storage instead of MongoDB
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import bcrypt
import secrets
import os
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=['http://localhost:5174', 'http://localhost:3000', 'http://localhost:5173'])

# File paths for local storage
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.json")

def ensure_data_dir():
    """Ensure data directory exists"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        logger.info(f"Created data directory: {DATA_DIR}")

def load_users():
    """Load users from JSON file"""
    if not os.path.exists(USERS_FILE):
        return {}
    
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading users: {e}")
        return {}

def save_users(users):
    """Save users to JSON file"""
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2, default=str)
        return True
    except Exception as e:
        logger.error(f"Error saving users: {e}")
        return False

def load_sessions():
    """Load sessions from JSON file"""
    if not os.path.exists(SESSIONS_FILE):
        return {}
    
    try:
        with open(SESSIONS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading sessions: {e}")
        return {}

def save_sessions(sessions):
    """Save sessions to JSON file"""
    try:
        with open(SESSIONS_FILE, 'w') as f:
            json.dump(sessions, f, indent=2, default=str)
        return True
    except Exception as e:
        logger.error(f"Error saving sessions: {e}")
        return False

def create_test_user():
    """Create test user if it doesn't exist"""
    users = load_users()
    email = "shashikingmaker495@gmail.com"
    
    if email not in users:
        # Hash the password
        password = "password123"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        users[email] = {
            "id": secrets.token_hex(12),
            "name": "Shashank C A",
            "email": email,
            "password": hashed_password.decode('utf-8'),
            "created_at": datetime.now().isoformat()
        }
        
        if save_users(users):
            logger.info(f"✅ Created test user: {email}")
        else:
            logger.error("❌ Failed to save test user")

@app.route('/auth/signin', methods=['POST', 'OPTIONS'])
def signin():
    """Signin endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({"success": False, "error": "Email and password are required"}), 400
        
        logger.info(f"🔐 Signin attempt for: {email}")
        
        # Load users
        users = load_users()
        
        # Find user
        if email not in users:
            logger.warning(f"❌ User not found: {email}")
            return jsonify({"success": False, "error": "Invalid email or password"}), 401
        
        user = users[email]
        
        # Check password
        stored_password = user.get('password', '')
        if not stored_password:
            logger.error(f"❌ No password hash for user: {email}")
            return jsonify({"success": False, "error": "Account configuration error"}), 500
        
        # Convert password to bytes for bcrypt
        password_bytes = password.encode('utf-8')
        stored_password_bytes = stored_password.encode('utf-8')
        
        if bcrypt.checkpw(password_bytes, stored_password_bytes):
            # Generate session token
            session_token = secrets.token_urlsafe(32)
            
            # Load and update sessions
            sessions = load_sessions()
            sessions[session_token] = {
                "user_id": user['id'],
                "email": email,
                "created_at": datetime.now().isoformat()
            }
            
            if not save_sessions(sessions):
                logger.error("Failed to save session")
                return jsonify({"success": False, "error": "Session creation failed"}), 500
            
            logger.info(f"✅ Signin successful: {email}")
            return jsonify({
                "success": True,
                "message": "Signin successful",
                "token": session_token,
                "user": {
                    "id": user['id'],
                    "name": user.get('name', ''),
                    "email": email
                }
            }), 200
        else:
            logger.warning(f"❌ Invalid password for: {email}")
            return jsonify({"success": False, "error": "Invalid email or password"}), 401
        
    except Exception as e:
        logger.error(f"Signin error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": "Internal server error"}), 500

@app.route('/auth/signup', methods=['POST', 'OPTIONS'])
def signup():
    """Signup endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not all([name, email, password]):
            return jsonify({"success": False, "error": "Name, email and password are required"}), 400
        
        logger.info(f"📝 Signup attempt for: {email}")
        
        # Load users
        users = load_users()
        
        # Check if user exists
        if email in users:
            logger.warning(f"❌ User already exists: {email}")
            return jsonify({"success": False, "error": "User already exists"}), 409
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user
        user_id = secrets.token_hex(12)
        users[email] = {
            "id": user_id,
            "name": name,
            "email": email,
            "password": hashed_password.decode('utf-8'),
            "created_at": datetime.now().isoformat()
        }
        
        if not save_users(users):
            return jsonify({"success": False, "error": "Failed to create user"}), 500
        
        # Create session token
        session_token = secrets.token_urlsafe(32)
        
        # Load and update sessions
        sessions = load_sessions()
        sessions[session_token] = {
            "user_id": user_id,
            "email": email,
            "created_at": datetime.now().isoformat()
        }
        
        if not save_sessions(sessions):
            return jsonify({"success": False, "error": "Failed to create session"}), 500
        
        logger.info(f"✅ Signup successful: {email}")
        return jsonify({
            "success": True,
            "message": "Signup successful",
            "token": session_token,
            "user": {
                "id": user_id,
                "name": name,
                "email": email
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Signup error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": "Internal server error"}), 500

@app.route('/auth/verify', methods=['GET', 'OPTIONS'])
def verify_token():
    """Verify authentication token"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({"success": False, "error": "No token provided"}), 401
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Load sessions
        sessions = load_sessions()
        
        # Find session
        if token not in sessions:
            return jsonify({"success": False, "error": "Invalid token"}), 401
        
        session = sessions[token]
        email = session['email']
        
        # Load users and find user
        users = load_users()
        if email not in users:
            return jsonify({"success": False, "error": "User not found"}), 401
        
        user = users[email]
        
        return jsonify({
            "success": True,
            "valid": True,
            "user": {
                "id": user['id'],
                "name": user.get('name', ''),
                "email": user['email']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500

@app.route('/auth/profile', methods=['PUT', 'OPTIONS'])
def update_profile():
    """Update user profile endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({"success": False, "error": "No token provided"}), 401
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Load sessions and find user
        sessions = load_sessions()
        if token not in sessions:
            return jsonify({"success": False, "error": "Invalid token"}), 401
        
        session = sessions[token]
        email = session['email']
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        logger.info(f"📝 Profile update request for: {email}")
        logger.info(f"📋 Profile data: {data}")
        
        # Load users
        users = load_users()
        if email not in users:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        user = users[email]
        
        # Update user profile fields
        allowed_fields = ['name', 'mobile', 'gender', 'state', 'skills', 'experience', 'education']
        updated = False
        
        for field in allowed_fields:
            if field in data:
                user[field] = data[field]
                updated = True
        
        if updated:
            user['updated_at'] = datetime.now().isoformat()
            
            # Save updated users
            if save_users(users):
                logger.info(f"✅ Profile updated successfully for: {email}")
                return jsonify({
                    "success": True,
                    "message": "Profile updated successfully",
                    "user": {
                        "id": user['id'],
                        "name": user.get('name', ''),
                        "email": user['email'],
                        "mobile": user.get('mobile', ''),
                        "gender": user.get('gender', ''),
                        "state": user.get('state', ''),
                        "skills": user.get('skills', []),
                        "experience": user.get('experience', ''),
                        "education": user.get('education', '')
                    }
                }), 200
            else:
                return jsonify({"success": False, "error": "Failed to save profile"}), 500
        else:
            return jsonify({"success": False, "error": "No valid fields to update"}), 400
        
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": "Internal server error"}), 500

@app.route('/auth/logout', methods=['POST', 'OPTIONS'])
def logout():
    """Logout endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            
            # Load sessions and remove token
            sessions = load_sessions()
            if token in sessions:
                del sessions[token]
                save_sessions(sessions)
                logger.info("✅ Session deleted")
        
        return jsonify({"success": True, "message": "Logged out successfully"}), 200
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok", 
        "message": "Local Auth Server running",
        "storage": "local_files"
    }), 200

@app.route('/api/problems', methods=['GET', 'OPTIONS'])
def get_problems():
    """Get coding problems endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Load problems from existing file
        problems_file = os.path.join(DATA_DIR, "Problems", "problems.json")
        
        if not os.path.exists(problems_file):
            logger.error(f"❌ Problems file not found: {problems_file}")
            return jsonify({"success": False, "error": "Problems file not found"}), 404
            
        with open(problems_file, 'r', encoding='utf-8') as f:
            problems = json.load(f)
        
        logger.info(f"📚 Loaded {len(problems)} problems from existing file")
        
        # Apply filters if provided
        difficulty = request.args.get('difficulty', '').lower()
        topic = request.args.get('topic', '').lower()
        search = request.args.get('search', '').lower()
        limit = int(request.args.get('limit', 100))
        
        filtered_problems = problems
        
        if difficulty:
            filtered_problems = [p for p in filtered_problems if p.get('difficulty', '').lower() == difficulty]
        
        if topic:
            filtered_problems = [p for p in filtered_problems if any(topic in t.lower() for t in p.get('topics', []))]
            
        if search:
            filtered_problems = [p for p in filtered_problems if 
                                search in p.get('title', '').lower() or 
                                search in p.get('description', '').lower()]
        
        # Apply limit
        filtered_problems = filtered_problems[:limit]
        
        logger.info(f"📝 Returned {len(filtered_problems)} problems")
        
        return jsonify({
            "success": True,
            "problems": filtered_problems,
            "items": filtered_problems,  # Keep for backward compatibility
            "total": len(problems),
            "filtered_count": len(filtered_problems)
        }), 200
        
    except Exception as e:
        logger.error(f"Problems endpoint error: {e}")
        return jsonify({"success": False, "error": "Failed to load problems"}), 500

@app.route('/problems', methods=['GET', 'OPTIONS'])
def get_problems_alt():
    """Alternative problems endpoint (without /api prefix) for React compatibility"""
    return get_problems()

@app.route('/problems/<int:problem_id>', methods=['GET', 'OPTIONS'])
def get_single_problem(problem_id):
    """Get a single problem by ID"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Load problems from existing file
        problems_file = os.path.join(DATA_DIR, "Problems", "problems.json")
        
        if not os.path.exists(problems_file):
            logger.error(f"❌ Problems file not found: {problems_file}")
            return jsonify({"success": False, "error": "Problems file not found"}), 404
        
        with open(problems_file, 'r', encoding='utf-8') as f:
            problems_data = json.load(f)
        
        # Find problem by ID (problems are 1-indexed in the frontend)
        if 1 <= problem_id <= len(problems_data):
            problem = problems_data[problem_id - 1]  # Convert to 0-indexed
            logger.info(f"📚 Retrieved problem {problem_id}: {problem.get('title', 'Unknown')}")
            return jsonify({
                "success": True, 
                "problem": problem,
                "id": problem_id
            }), 200
        else:
            logger.warning(f"❌ Problem {problem_id} not found (valid range: 1-{len(problems_data)})")
            return jsonify({"success": False, "error": f"Problem {problem_id} not found"}), 404
            
    except Exception as e:
        logger.error(f"Single problem endpoint error: {e}")
        return jsonify({"success": False, "error": "Failed to load problem"}), 500

@app.route('/recommend', methods=['POST', 'OPTIONS'])
def recommend_jobs():
    """Job recommendations endpoint with proper matching and skill gap analysis"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        resume_text = data.get('resume_text', '')
        
        logger.info(f"📝 Job recommendation request, resume length: {len(resume_text)}")
        
        # Import job matcher and resume parser
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))
        
        try:
            # Try to use AI models (with timeout protection)
            parsed_resume = None
            recommendations = []
            
            if resume_text.strip():
                # Basic skill extraction first (fast fallback)
                common_skills = ['python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring', 'sql', 'postgresql', 'mysql', 'mongodb', 'aws', 'azure', 'docker', 'kubernetes', 'git', 'html', 'css', 'typescript', 'php', 'ruby', 'go', 'rust', 'c++', 'c#']
                found_skills = []
                resume_lower = resume_text.lower()
                
                for skill in common_skills:
                    if skill in resume_lower:
                        found_skills.append(skill.title())
                
                # Extract basic info
                name = "User"
                email = "user@example.com"
                experience = "Entry level"
                
                # Simple name extraction
                lines = resume_text.split('\n')[:3]  # Check first 3 lines
                for line in lines:
                    if '@' in line:
                        email = line.strip()
                    elif len(line.strip()) < 50 and any(char.isupper() for char in line):
                        name = line.strip()
                
                # Experience level detection
                if any(word in resume_lower for word in ['senior', '5+ years', '6+ years', '7+ years', 'lead', 'architect']):
                    experience = "Senior (5+ years)"
                elif any(word in resume_lower for word in ['3+ years', '4+ years', 'mid-level', 'intermediate']):
                    experience = "Mid-level (3-4 years)"
                elif any(word in resume_lower for word in ['1+ year', '2+ years', 'junior']):
                    experience = "Junior (1-2 years)"
                
                parsed_resume = {
                    "name": name,
                    "email": email,
                    "skills": found_skills if found_skills else ["Python", "JavaScript"],
                    "experience": experience,
                    "education": "Bachelor's Degree"
                }
                logger.info(f"� Parsed resume: {len(parsed_resume.get('skills', []))} skills found")
                
                # Try AI matching with timeout
                try:
                    from job_matcher import JobMatcher
                    job_matcher = JobMatcher()
                    recommendations = job_matcher.recommend_jobs(parsed_resume, top_n=8)
                    logger.info(f"🎯 Generated {len(recommendations)} AI job recommendations")
                except Exception as ai_error:
                    logger.warning(f"AI matching failed: {ai_error}, using basic matching")
                    recommendations = []
            
            else:
                # Empty resume fallback
                parsed_resume = {
                    "name": "User",
                    "email": "user@example.com", 
                    "skills": ["Python", "JavaScript", "React"],
                    "experience": "Entry level",
                    "education": "Bachelor's Degree"
                }
                logger.info("📝 Using default resume data")
            
            # If AI didn't generate recommendations, use basic CSV matching
            if not recommendations:
                logger.info("🔄 Using basic job matching from CSV")
                jobs_file = os.path.join(DATA_DIR, "unified_job_dataset.csv")
                if not os.path.exists(jobs_file):
                    jobs_file = os.path.join(DATA_DIR, "job_dataset.csv")
                
                if os.path.exists(jobs_file):
                    import pandas as pd
                    user_skills = set(skill.lower() for skill in parsed_resume.get('skills', []))
                    logger.info(f"🔍 User skills for matching: {user_skills}")
                    
                    try:
                        # Load a subset of jobs for performance (first 1000 rows)
                        df = pd.read_csv(jobs_file, nrows=1000)
                        logger.info(f"📚 Loaded {len(df)} jobs from dataset for matching")
                        
                        job_matches = []
                        
                        for i, row in df.iterrows():
                            if len(job_matches) >= 8:  # Limit to 8 recommendations
                                break
                            
                            # Handle both 'skills' and 'requirements' columns
                            skills_text = str(row.get('skills', '')) + ' ' + str(row.get('requirements', ''))
                            job_skills = set(skill.strip().lower() for skill in skills_text.replace(',', ' ').split() if skill.strip())
                            
                            # Calculate match score
                            if job_skills and user_skills:
                                match_count = len(user_skills.intersection(job_skills))
                                match_percentage = int((match_count / len(job_skills)) * 100)
                            else:
                                match_percentage = 75  # Default match
                            
                            # Only include jobs with some relevance
                            if match_percentage >= 20 or not job_skills:
                                job_matches.append({
                                    "id": row.get('job_id', f'job_{i}'),
                                    "title": row.get('title', 'Software Developer'),
                                    "company": row.get('company', 'Tech Company'),
                                    "location": row.get('location', 'Remote'),
                                    "description": row.get('description', 'Great opportunity to advance your career')[:200] + '...',
                                    "skills_required": [s.strip().title() for s in str(row.get('skills', '')).split(',')[:6] if s.strip()],
                                    "experience": row.get('experience_level', 'Entry level'),
                                    "salary": row.get('salary_range', '$50,000 - $70,000'),
                                    "match_percentage": max(match_percentage, 65)
                                })
                        
                        # Sort by match percentage
                        job_matches.sort(key=lambda x: x.get('match_percentage', 0), reverse=True)
                        recommendations = job_matches
                        logger.info(f"📊 Generated {len(recommendations)} job matches")
                        
                    except Exception as csv_error:
                        logger.error(f"CSV processing error: {csv_error}")
                        # Fallback to basic jobs if CSV fails
                        recommendations = [
                            {
                                "id": "fallback_1",
                                "title": "Software Developer",
                                "company": "Tech Solutions Inc",
                                "location": "Remote",
                                "description": "Join our team as a software developer...",
                                "skills_required": list(user_skills)[:5] if user_skills else ["Python", "JavaScript"],
                                "experience": "2+ years",
                                "salary": "$60,000 - $80,000",
                                "match_percentage": 85
                            }
                        ]

            # Get live jobs (jobs posted in the system)
            live_jobs_file = os.path.join(DATA_DIR, "posted_jobs.json")
            live_jobs = []
            
            if os.path.exists(live_jobs_file):
                import json
                try:
                    with open(live_jobs_file, 'r', encoding='utf-8') as f:
                        live_jobs_raw = json.load(f)
                        
                    # Handle both array and object format
                    if isinstance(live_jobs_raw, list):
                        live_jobs = live_jobs_raw[:5]  # Get first 5 live jobs
                    elif isinstance(live_jobs_raw, dict):
                        live_jobs = live_jobs_raw.get('jobs', [])[:5]
                    
                    # Calculate match percentages for live jobs
                    user_skills = set(skill.lower() for skill in parsed_resume.get('skills', []))
                    for job in live_jobs:
                        job_skills = set(skill.lower() for skill in job.get('skills_required', []))
                        if job_skills and user_skills:
                            match_count = len(user_skills.intersection(job_skills))
                            match_percentage = int((match_count / len(job_skills)) * 100)
                            job['match_percentage'] = max(match_percentage, 70)
                        else:
                            job['match_percentage'] = 75
                        job['is_live'] = True
                    
                    logger.info(f"💼 Loaded {len(live_jobs)} live job postings")
                except Exception as e:
                    logger.error(f"Error loading live jobs: {e}")
                    live_jobs = []
            
            if not live_jobs:
                logger.info("📝 Creating sample live jobs")
                live_jobs = [
                    {
                        "id": "live_1",
                        "title": "Frontend Developer",
                        "company": "Tech Startup Inc",
                        "location": "Remote",
                        "description": "Looking for a React developer with 2+ years experience",
                        "skills_required": ["React", "JavaScript", "HTML", "CSS"],
                        "experience": "2+ years",
                        "salary": "$60,000 - $80,000",
                        "match_percentage": 88,
                        "posted_date": "2025-11-01",
                        "is_live": True
                    },
                    {
                        "id": "live_2", 
                        "title": "Python Developer",
                        "company": "Data Solutions",
                        "location": "Remote",
                        "description": "Python developer for backend services and APIs",
                        "skills_required": ["Python", "Django", "PostgreSQL", "REST API"],
                        "experience": "3+ years",
                        "salary": "$70,000 - $90,000", 
                        "match_percentage": 85,
                        "posted_date": "2025-10-30",
                        "is_live": True
                    }
                ]
            
            # Calculate skill gap analysis
            user_skills = set(skill.lower() for skill in parsed_resume.get('skills', []))
            all_job_skills = set()
            
            # Collect all required skills from jobs
            for job in recommendations + live_jobs:
                job_skills = job.get('skills_required', [])
                all_job_skills.update(skill.lower() for skill in job_skills)
            
            # Find missing skills
            missing_skills = list(all_job_skills - user_skills)
            
            # Count skill frequency to find most important missing skills
            skill_frequency = {}
            for job in recommendations + live_jobs:
                for skill in job.get('skills_required', []):
                    skill_lower = skill.lower()
                    if skill_lower in missing_skills:
                        skill_frequency[skill_lower] = skill_frequency.get(skill_lower, 0) + 1
            
            # Get top missing skills
            top_missing = sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
            top_missing_skills = [skill.title() for skill, _ in top_missing]

            return jsonify({
                "success": True,
                "parsed": parsed_resume,
                "jobs": recommendations,
                "live_jobs": live_jobs,
                "total_jobs": len(recommendations) + len(live_jobs),
                "skill_match_summary": {
                    "user_skills": parsed_resume.get('skills', []),
                    "total_user_skills": len(parsed_resume.get('skills', [])),
                    "top_missing_skills": top_missing_skills,
                    "missing_skills_count": len(missing_skills),
                    "experience_level": parsed_resume.get('experience', 'Not specified'),
                    "skill_coverage": f"{len(user_skills)} / {len(all_job_skills)} market skills"
                },
                "recommendations_note": "Jobs ranked by skill match and experience fit"
            }), 200
            
        except ImportError as e:
            logger.error(f"❌ Failed to import job matching modules: {e}")
            # Fallback to basic implementation
            return _basic_job_recommendation(resume_text)
            
    except Exception as e:
        logger.error(f"❌ Job recommendation error: {e}")
        return jsonify({"success": False, "error": "Failed to generate recommendations"}), 500


def _basic_job_recommendation(resume_text):
    """Fallback basic job recommendation when AI modules fail"""
    try:
        # Load jobs from CSV (prefer unified dataset)
        jobs_file = os.path.join(DATA_DIR, "unified_job_dataset.csv")
        if not os.path.exists(jobs_file):
            jobs_file = os.path.join(DATA_DIR, "job_dataset.csv")
        jobs = []
        
        if os.path.exists(jobs_file):
            import csv
            with open(jobs_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    if i >= 10:  # Limit to 10 jobs
                        break
                    jobs.append({
                        "id": row.get('job_id', f'job_{i}'),
                        "title": row.get('title', 'Software Developer'),
                        "company": row.get('company', 'Tech Company'),
                        "location": row.get('location', 'Remote'),
                        "description": row.get('description', 'Great opportunity to grow your career'),
                        "skills_required": row.get('skills', '').split(',') if row.get('skills') else ['Python', 'JavaScript'],
                        "experience": row.get('experience_level', 'Entry level'),
                        "salary": row.get('salary_range', '$50,000 - $70,000'),
                        "match_percentage": max(70, 90 - i * 2)  # Decreasing match percentage
                    })
            logger.info(f"📊 Loaded {len(jobs)} jobs from CSV (basic mode)")
        
        # Basic skill extraction from resume text
        common_skills = ['python', 'javascript', 'react', 'java', 'sql', 'git', 'html', 'css']
        found_skills = [skill.title() for skill in common_skills if skill.lower() in resume_text.lower()]
        
        if not found_skills:
            found_skills = ['Python', 'JavaScript', 'HTML']
        
        parsed = {
            "name": "User",
            "email": "user@example.com",
            "skills": found_skills,
            "experience": "2+ years" if len(resume_text) > 100 else "Entry level",
            "education": "Bachelor's Degree"
        }
        
        # Sample live jobs
        live_jobs = [
            {
                "id": "live_basic_1",
                "title": "Junior Developer",
                "company": "StartupXYZ",
                "location": "Remote",
                "description": "Entry-level position for new graduates",
                "skills_required": found_skills[:3],
                "experience": "0-2 years",
                "salary": "$45,000 - $60,000",
                "match_percentage": 85,
                "posted_date": "2025-11-01",
                "is_live": True
            }
        ]
        
        return jsonify({
            "success": True,
            "parsed": parsed,
            "jobs": jobs,
            "live_jobs": live_jobs,
            "note": "Using basic recommendation mode"
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Basic recommendation error: {e}")
        return jsonify({"success": False, "error": "Failed to generate basic recommendations"}), 500
        
    except Exception as e:
        logger.error(f"Recommend endpoint error: {e}")
        return jsonify({"success": False, "error": "Failed to get recommendations"}), 500

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload_file():
    """File upload endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Handle both file uploads and JSON data
        if 'resume_file' in request.files:
            file = request.files['resume_file']
            logger.info(f"📄 File upload started: {file.filename}")
            
            # Validate file
            if not file.filename:
                return jsonify({"success": False, "error": "No file selected"}), 400
                
            # Save the file locally
            uploads_dir = os.path.join(DATA_DIR, "uploads")
            if not os.path.exists(uploads_dir):
                os.makedirs(uploads_dir)
                logger.info(f"📁 Created uploads directory: {uploads_dir}")
            
            file_path = os.path.join(uploads_dir, file.filename)
            file.save(file_path)
            
            # Load a smaller number of jobs quickly for faster response
            jobs_file = os.path.join(DATA_DIR, "job_dataset.csv")
            jobs = []
            
            if os.path.exists(jobs_file):
                import csv
                with open(jobs_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    count = 0
                    for row in reader:
                        if count >= 5:  # Only load first 5 jobs for fast response
                            break
                        jobs.append({
                            "id": row.get('job_id'),
                            "title": row.get('title'),
                            "company": row.get('company'),
                            "location": row.get('location'),
                            "description": row.get('description'),
                            "skills_required": row.get('skills', '').split(',') if row.get('skills') else [],
                            "experience": row.get('experience_level'),
                            "salary": row.get('salary_range'),
                            "match_percentage": 90
                        })
                        count += 1
                logger.info(f"📊 Loaded {len(jobs)} jobs for file upload response")
            
            # Simple parsed resume data
            sample_parsed = {
                "name": "User",
                "email": "user@example.com", 
                "skills": ["Python", "JavaScript", "React"],
                "experience": "2+ years",
                "education": "Bachelor's Degree"
            }
            
            logger.info(f"✅ File upload completed: {file.filename}")
            return jsonify({
                "success": True,
                "message": "File uploaded successfully",
                "filename": file.filename,
                "path": file_path,
                "parsed": sample_parsed,
                "jobs": jobs,  # Return all loaded jobs (max 5)
                "live_jobs": []
            }), 200
        else:
            # Handle JSON upload
            data = request.get_json()
            logger.info(f"📝 JSON upload: {len(str(data))} characters")
            
            return jsonify({
                "success": True,
                "message": "Data received successfully"
            }), 200
        
    except Exception as e:
        logger.error(f"Upload endpoint error: {e}")
        import traceback
        logger.error(f"Upload traceback: {traceback.format_exc()}")
        return jsonify({"success": False, "error": f"Upload failed: {str(e)}"}), 500

@app.route('/interview/questions', methods=['GET', 'OPTIONS'])
def get_interview_questions():
    """Get interview questions"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Try to load from existing interview questions file
        questions_file = os.path.join(DATA_DIR, "interview", "hr_interview_questions_dataset.json")
        questions = []
        
        if os.path.exists(questions_file):
            try:
                with open(questions_file, 'r', encoding='utf-8') as f:
                    interview_data = json.load(f)
                    
                # Convert to expected format
                if isinstance(interview_data, list):
                    for i, item in enumerate(interview_data[:10]):  # Limit to 10 questions
                        if isinstance(item, dict):
                            questions.append({
                                "id": i + 1,
                                "text": item.get('question', item.get('text', str(item))),
                                "category": item.get('category', 'General'),
                                "time_limit": item.get('time_limit', 90)
                            })
                        
                logger.info(f"📝 Loaded {len(questions)} interview questions from existing dataset")
            except Exception as e:
                logger.warning(f"⚠️ Could not load interview questions: {e}")
        
        # Fallback to basic questions if no file or error
        if not questions:
            questions = [
                {
                    "id": 1,
                    "text": "Tell me about yourself and your background.",
                    "category": "General",
                    "time_limit": 120
                },
                {
                    "id": 2, 
                    "text": "What are your strengths and weaknesses?",
                    "category": "General",
                    "time_limit": 90
                },
                {
                    "id": 3,
                    "text": "Why do you want to work for this company?",
                    "category": "Behavioral", 
                    "time_limit": 90
                }
            ]
        
        return jsonify({
            "success": True,
            "questions": questions
        }), 200
        
    except Exception as e:
        logger.error(f"Interview questions error: {e}")
        return jsonify({"success": False, "error": "Failed to load questions"}), 500

@app.route('/', methods=['GET'])
def index():
    """Index endpoint"""
    return jsonify({
        "message": "Local File Auth Server", 
        "status": "running",
        "version": "1.0",
        "storage": "local_files"
    }), 200

@app.route('/api/jobs', methods=['GET', 'POST', 'OPTIONS'])
def handle_jobs():
    """Handle job operations with local storage"""
    if request.method == 'OPTIONS':
        return '', 200
    
    jobs_storage_file = os.path.join(DATA_DIR, "posted_jobs.json")
    
    if request.method == 'GET':
        try:
            # Load posted jobs from local file
            jobs = []
            if os.path.exists(jobs_storage_file):
                with open(jobs_storage_file, 'r', encoding='utf-8') as f:
                    jobs = json.load(f)
            
            # Handle pagination
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 20))
            start = (page - 1) * limit
            end = start + limit
            
            paginated_jobs = jobs[start:end]
            
            logger.info(f"📋 Retrieved {len(paginated_jobs)} jobs (page {page})")
            return jsonify({
                "success": True,
                "jobs": paginated_jobs,
                "total": len(jobs),
                "page": page,
                "limit": limit,
                "total_pages": (len(jobs) + limit - 1) // limit
            }), 200
            
        except Exception as e:
            logger.error(f"Get jobs error: {e}")
            return jsonify({"success": False, "error": "Failed to get jobs"}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # Load existing jobs
            jobs = []
            if os.path.exists(jobs_storage_file):
                with open(jobs_storage_file, 'r', encoding='utf-8') as f:
                    jobs = json.load(f)
            
            # Create new job with ID
            new_job = {
                "id": len(jobs) + 1,
                "title": data.get('title', ''),
                "company": data.get('company', ''),
                "location": data.get('location', ''),
                "description": data.get('description', ''),
                "requirements": data.get('requirements', ''),
                "salary": data.get('salary', ''),
                "type": data.get('type', 'Full-time'),
                "posted_date": datetime.now().isoformat(),
                "status": "active"
            }
            
            # Add to jobs list
            jobs.append(new_job)
            
            # Save to local file
            with open(jobs_storage_file, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💼 Created job: {new_job['title']} at {new_job['company']}")
            return jsonify({
                "success": True,
                "message": "Job posted successfully",
                "job": new_job
            }), 201
            
        except Exception as e:
            logger.error(f"Post job error: {e}")
            return jsonify({"success": False, "error": "Failed to create job"}), 500

@app.route('/api/experiences', methods=['GET', 'POST', 'OPTIONS'])
def handle_experiences():
    """Handle interview experiences with local storage"""
    if request.method == 'OPTIONS':
        return '', 200
    
    experiences_storage_file = os.path.join(DATA_DIR, "interview_experiences.json")
    
    if request.method == 'GET':
        try:
            # Load interview experiences from local file
            experiences = []
            if os.path.exists(experiences_storage_file):
                with open(experiences_storage_file, 'r', encoding='utf-8') as f:
                    experiences = json.load(f)
            
            # Handle pagination
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 20))
            start = (page - 1) * limit
            end = start + limit
            
            paginated_experiences = experiences[start:end]
            
            logger.info(f"📚 Retrieved {len(paginated_experiences)} experiences (page {page})")
            return jsonify({
                "success": True,
                "experiences": paginated_experiences,
                "total": len(experiences),
                "page": page,
                "limit": limit,
                "total_pages": (len(experiences) + limit - 1) // limit
            }), 200
            
        except Exception as e:
            logger.error(f"Get experiences error: {e}")
            return jsonify({"success": False, "error": "Failed to get experiences"}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # Load existing experiences
            experiences = []
            if os.path.exists(experiences_storage_file):
                with open(experiences_storage_file, 'r', encoding='utf-8') as f:
                    experiences = json.load(f)
            
            # Create new experience with ID - match React component field names
            new_experience = {
                "id": len(experiences) + 1,
                "company": data.get('company', ''),
                "position": data.get('position', ''),
                "interviewer": data.get('interviewer', ''),
                "experience_text": data.get('experience', data.get('experience_text', '')),  # Support both field names
                "difficulty_rating": data.get('difficulty_rating', data.get('difficulty', 'Medium')),
                "outcome": data.get('outcome', data.get('result', 'Pending')),
                "interview_type": data.get('interview_type', 'Technical'),
                "interview_rounds": data.get('interview_rounds', 1),
                "preparation_time": data.get('preparation_time', ''),
                "location": data.get('location', ''),
                "questions_asked": data.get('questions_asked', []),
                "tags": data.get('tags', []),
                "date": data.get('date', datetime.now().isoformat()),
                "created_at": datetime.now().isoformat(),
                "status": "published"
            }
            
            # Add to experiences list
            experiences.append(new_experience)
            
            # Save to local file
            with open(experiences_storage_file, 'w', encoding='utf-8') as f:
                json.dump(experiences, f, indent=2, ensure_ascii=False)
            
            logger.info(f"🎤 Created experience: {new_experience['position']} at {new_experience['company']}")
            return jsonify({
                "success": True,
                "message": "Experience shared successfully",
                "experience": new_experience
            }), 201
            
        except Exception as e:
            logger.error(f"Post experience error: {e}")
            return jsonify({"success": False, "error": "Failed to create experience"}), 500

# Initialize on startup
if __name__ == '__main__':
    logger.info("🚀 Starting Local File Authentication Server...")
    
    # Setup data directory and test user
    ensure_data_dir()
    create_test_user()
    
    logger.info("📋 Available endpoints:")
    logger.info("  POST /auth/signin - User signin")
    logger.info("  POST /auth/signup - User signup")
    logger.info("  GET /auth/verify - Verify token")
    logger.info("  PUT /auth/profile - Update profile")
    logger.info("  POST /auth/logout - Logout")
    logger.info("  GET /api/problems - Get coding problems")
    logger.info("  GET /problems - Get coding problems (alt)")
    logger.info("  GET /problems/<id> - Get single problem by ID")
    logger.info("  POST /recommend - Job recommendations")
    logger.info("  POST /upload - File upload")
    logger.info("  GET /interview/questions - Interview questions")
    logger.info("  GET /api/jobs - Get job listings")
    logger.info("  POST /api/jobs - Create new job")
    logger.info("  GET /api/experiences - Get interview experiences")
    logger.info("  POST /api/experiences - Share interview experience")
    logger.info("  GET /health - Health check")
    logger.info("  GET / - Server info")
    
    logger.info("💾 Using local file storage (no MongoDB required)")
    logger.info("🌐 CORS enabled for React frontend")
    logger.info("🔥 Starting server on http://localhost:5000")
    
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)