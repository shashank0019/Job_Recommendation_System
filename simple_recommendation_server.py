#!/usr/bin/env python3
"""
Simple Recommendation Server - Handles job recommendations and uploads without heavy ML dependencies
"""

import os
import json
import logging
import random
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:3000", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

def load_job_data():
    """Load job data from available sources - prioritize tech jobs"""
    jobs = []
    
    # Try to load from unified dataset
    try:
        import pandas as pd
        csv_file = os.path.join('data', 'unified_job_dataset.csv')
        if os.path.exists(csv_file):
            logger.info("📊 Loading jobs from CSV dataset...")
            
            # Load in chunks to find tech jobs efficiently
            tech_keywords = ['Software', 'Developer', 'Engineer', 'Programmer', 'Python', 
                           'JavaScript', 'React', 'Node', 'Full Stack', 'Backend', 'Frontend',
                           'Data Scientist', 'DevOps', 'Web Developer', 'Mobile Developer']
            
            # First, try to load tech jobs (up to 2000)
            chunk_size = 5000
            tech_jobs_df = pd.DataFrame()
            
            for chunk in pd.read_csv(csv_file, chunksize=chunk_size):
                # Filter for tech jobs
                tech_chunk = chunk[chunk['title'].str.contains('|'.join(tech_keywords), case=False, na=False)]
                tech_jobs_df = pd.concat([tech_jobs_df, tech_chunk])
                
                if len(tech_jobs_df) >= 2000:
                    tech_jobs_df = tech_jobs_df.head(2000)
                    break
            
            logger.info(f"📊 Found {len(tech_jobs_df)} tech jobs")
            
            # Convert to job format
            for _, row in tech_jobs_df.iterrows():
                # Handle NaN values properly
                skills_val = row.get('skills', '')
                if pd.isna(skills_val) or skills_val == 'nan':
                    # Infer skills from title
                    title_lower = str(row.get('title', '')).lower()
                    inferred_skills = []
                    if 'python' in title_lower:
                        inferred_skills.append('Python')
                    if 'javascript' in title_lower or 'js' in title_lower:
                        inferred_skills.append('JavaScript')
                    if 'react' in title_lower:
                        inferred_skills.append('React')
                    if 'node' in title_lower:
                        inferred_skills.append('Node.js')
                    if 'java' in title_lower and 'javascript' not in title_lower:
                        inferred_skills.append('Java')
                    if 'data' in title_lower:
                        inferred_skills.extend(['SQL', 'Python', 'Data Analysis'])
                    if 'frontend' in title_lower or 'front end' in title_lower:
                        inferred_skills.extend(['JavaScript', 'HTML', 'CSS', 'React'])
                    if 'backend' in title_lower or 'back end' in title_lower:
                        inferred_skills.extend(['Python', 'Node.js', 'SQL'])
                    if 'fullstack' in title_lower or 'full stack' in title_lower:
                        inferred_skills.extend(['JavaScript', 'React', 'Node.js', 'Python', 'SQL'])
                    
                    skills_list = inferred_skills if inferred_skills else ['Software Development']
                else:
                    skills_list = [s.strip() for s in str(skills_val).split(',')[:5]]
                
                jobs.append({
                    "id": str(row.get('job_id', len(jobs) + 1)),
                    "title": str(row.get('title', 'Software Developer')),
                    "company": str(row.get('company', 'Tech Company')) if pd.notna(row.get('company')) else 'Tech Company',
                    "location": str(row.get('location', 'Remote')) if pd.notna(row.get('location')) else 'Remote',
                    "description": str(row.get('description', 'Great opportunity'))[:200] + '...' if pd.notna(row.get('description')) else 'Great opportunity...',
                    "skills_required": skills_list,
                    "experience": str(row.get('experience_level', 'Entry level')) if pd.notna(row.get('experience_level')) else 'Entry level',
                    "salary": str(row.get('salary_range', '$50,000 - $80,000')) if pd.notna(row.get('salary_range')) else '$50,000 - $80,000',
                    "match_percentage": random.randint(70, 95)
                })
            
            logger.info(f"✅ Loaded {len(jobs)} tech jobs from CSV dataset")
    except Exception as e:
        logger.error(f"CSV loading failed: {e}", exc_info=True)
    
    # Try to load from posted jobs
    try:
        posted_jobs_file = os.path.join('data', 'posted_jobs.json')
        if os.path.exists(posted_jobs_file):
            with open(posted_jobs_file, 'r', encoding='utf-8') as f:
                live_jobs = json.load(f)
                if isinstance(live_jobs, list):
                    jobs.extend(live_jobs[:20])  # Add some live jobs
                    logger.info(f"📈 Added {len(live_jobs[:20])} live jobs")
    except Exception as e:
        logger.warning(f"Live jobs loading failed: {e}")
    
    # Fallback jobs if nothing loaded
    if len(jobs) == 0:
        jobs = [
            {
                "id": "1",
                "title": "Full Stack Developer",
                "company": "Tech Solutions Inc",
                "location": "Remote",
                "description": "Join our team as a full stack developer working with modern technologies...",
                "skills_required": ["Python", "JavaScript", "React", "Node.js"],
                "experience": "2+ years",
                "salary": "$60,000 - $80,000",
                "match_percentage": 85
            },
            {
                "id": "2", 
                "title": "Data Scientist",
                "company": "Data Corp",
                "location": "New York, NY",
                "description": "Work with machine learning and data analysis to drive business insights...",
                "skills_required": ["Python", "Machine Learning", "SQL", "Statistics"],
                "experience": "3+ years",
                "salary": "$70,000 - $90,000", 
                "match_percentage": 78
            },
            {
                "id": "3",
                "title": "Frontend Developer",
                "company": "Design Studio",
                "location": "San Francisco, CA",
                "description": "Create beautiful user interfaces with modern frontend frameworks...",
                "skills_required": ["JavaScript", "React", "CSS", "HTML"],
                "experience": "1+ years",
                "salary": "$55,000 - $75,000",
                "match_percentage": 82
            }
        ]
        logger.info("📋 Using fallback job data")
    
    return jobs

# Load jobs at startup
ALL_JOBS = load_job_data()

def extract_skills_from_text(text):
    """Simple skill extraction from resume text"""
    common_skills = [
        'python', 'javascript', 'java', 'c++', 'c#', 'react', 'angular', 'vue',
        'node.js', 'express', 'django', 'flask', 'spring', 'sql', 'mongodb',
        'postgresql', 'mysql', 'git', 'docker', 'kubernetes', 'aws', 'azure',
        'machine learning', 'data science', 'html', 'css', 'bootstrap', 'tailwind'
    ]
    
    text_lower = text.lower()
    found_skills = []
    
    for skill in common_skills:
        if skill in text_lower:
            found_skills.append(skill.title())
    
    return found_skills

def analyze_skill_gap(user_skills, job_skills):
    """Analyze skill gaps between user and job requirements"""
    user_skills_lower = [skill.lower() for skill in user_skills]
    job_skills_lower = [skill.lower() for skill in job_skills]
    
    matching_skills = [skill for skill in job_skills if skill.lower() in user_skills_lower]
    missing_skills = [skill for skill in job_skills if skill.lower() not in user_skills_lower]
    
    return {
        'matching_skills': matching_skills,
        'missing_skills': missing_skills,
        'match_percentage': int((len(matching_skills) / len(job_skills)) * 100) if job_skills else 0
    }

def calculate_job_match_score(user_skills, job):
    """Calculate match score between user skills and job"""
    score = 0
    user_skills_lower = [s.lower() for s in user_skills]
    
    # Get job title and skills
    job_title = str(job.get('title', '')).lower()
    job_skills_str = str(job.get('skills_required', ''))
    if isinstance(job.get('skills_required'), list):
        job_skills = [s.lower() for s in job.get('skills_required', [])]
    else:
        job_skills = [s.strip().lower() for s in job_skills_str.split(',')]
    
    # Match user skills with job title (high weight)
    for skill in user_skills_lower:
        if skill in job_title:
            score += 30  # Title match is very important
    
    # Match user skills with job skills
    for user_skill in user_skills_lower:
        for job_skill in job_skills:
            if user_skill in job_skill or job_skill in user_skill:
                score += 20  # Direct skill match
                break
    
    # Bonus for developer/engineer roles if user has programming skills
    programming_skills = ['python', 'javascript', 'java', 'c++', 'c#', 'react', 'node.js', 'angular', 'vue']
    has_programming = any(s.lower() in programming_skills for s in user_skills)
    if has_programming and any(word in job_title for word in ['developer', 'engineer', 'programmer', 'software']):
        score += 25
    
    return min(score, 100)  # Cap at 100

@app.route('/recommend', methods=['POST', 'OPTIONS'])
def recommend_jobs():
    """Job recommendation endpoint"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'})
    
    try:
        logger.info("🚀 Processing job recommendation request...")
        
        # Handle file upload or direct text
        resume_text = ""
        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename:
                resume_text = file.read().decode('utf-8', errors='ignore')
                logger.info(f"📄 Resume file uploaded: {file.filename}")
        elif request.is_json:
            data = request.get_json()
            resume_text = data.get('resume_text', '')
        else:
            resume_text = request.form.get('resume_text', '')
        
        if not resume_text.strip():
            return jsonify({
                'success': False,
                'error': 'No resume text provided'
            }), 400
        
        # Extract skills from resume
        user_skills = extract_skills_from_text(resume_text)
        logger.info(f"🔍 Extracted skills: {user_skills}")
        
        if not user_skills:
            logger.warning("⚠️ No skills extracted, using generic matching")
            user_skills = ['software', 'technology']  # Fallback
        
        # Score ALL jobs based on skill match
        scored_jobs = []
        for job in ALL_JOBS:
            match_score = calculate_job_match_score(user_skills, job)
            if match_score > 0:  # Only include jobs with some match
                scored_jobs.append((match_score, job))
        
        # Sort by score descending
        scored_jobs.sort(key=lambda x: x[0], reverse=True)
        logger.info(f"📊 Scored {len(scored_jobs)} jobs, top score: {scored_jobs[0][0] if scored_jobs else 0}")
        
        # Get top 8 recommendations
        recommendations = []
        all_missing_skills = set()
        
        for match_score, job in scored_jobs[:8]:
            job_skills = job.get('skills_required', [])
            if isinstance(job_skills, str):
                job_skills = [s.strip() for s in job_skills.split(',')]
            
            # Calculate skill gaps
            user_skills_lower = [s.lower() for s in user_skills]
            job_skills_lower = [s.lower() for s in job_skills if s]
            
            matching_skills = [s for s in job_skills if s.lower() in [us.lower() for us in user_skills]]
            missing_skills = [s for s in job_skills if s.lower() not in user_skills_lower][:3]
            
            all_missing_skills.update(missing_skills)
            
            recommendations.append({
                **job,
                "match_percentage": int(match_score),
                "matching_skills": matching_skills,
                "missing_skills": missing_skills
            })
        
        # Fallback if no good matches found - get any tech jobs
        if len(recommendations) == 0:
            logger.warning("⚠️ No skill matches, returning generic tech jobs")
            for job in ALL_JOBS[:8]:
                recommendations.append({
                    **job,
                    "match_percentage": 60,
                    "matching_skills": [],
                    "missing_skills": []
                })
        
        # Overall skill gap analysis
        skill_gap_analysis = {
            "missing_skills": list(all_missing_skills)[:15],
            "skills_you_have": user_skills,
            "total_recommendations": len(recommendations),
            "avg_match_percentage": sum(r['match_percentage'] for r in recommendations) / len(recommendations) if recommendations else 0,
            "skill_improvement_suggestions": [
                "Focus on learning the most common missing skills",
                "Consider taking online courses for skill development", 
                "Build projects to demonstrate new skills",
                "Get certifications in high-demand technologies"
            ]
        }
        
        logger.info(f"✅ Generated {len(recommendations)} recommendations")
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'skill_gap_analysis': skill_gap_analysis,
            'parsed_resume': {
                'skills': user_skills,
                'experience_level': 'Mid-level' if len(user_skills) > 3 else 'Entry level',
                'summary': f"Resume with {len(user_skills)} technical skills identified"
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Recommendation error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload_file():
    """File upload endpoint"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'})
    
    try:
        logger.info("📁 Processing file upload...")
        logger.info(f"🔍 Content-Type: {request.content_type}")
        logger.info(f"📋 Available files: {list(request.files.keys())}")
        logger.info(f"📝 Form data: {list(request.form.keys())}")
        
        # Check for file in multiple field names (file, resume_file, resume)
        file = None
        for field_name in ['file', 'resume_file', 'resume']:
            if field_name in request.files:
                file = request.files[field_name]
                logger.info(f"📄 Found file in field: {field_name}")
                break
        
        if not file:
            return jsonify({
                'success': False,
                'error': 'No file provided. Expected field names: file, resume_file, or resume'
            }), 400
        
        if not file.filename:
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Create upload directory
        upload_dir = os.path.join('data', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)
        
        file.save(file_path)
        logger.info(f"💾 File saved: {file_path}")
        
        # Process the uploaded file to extract text
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                resume_text = f.read()
            logger.info(f"📄 Extracted text from file ({len(resume_text)} chars)")
        except Exception as read_error:
            logger.error(f"❌ Error reading file: {read_error}")
            resume_text = ""
        
        if not resume_text.strip():
            return jsonify({
                'success': False,
                'error': 'Could not extract text from uploaded file'
            }), 400
        
        # Extract skills and get recommendations (same logic as /recommend endpoint)
        user_skills = extract_skills_from_text(resume_text)
        logger.info(f"🔍 Extracted skills from uploaded file: {user_skills}")
        
        # Get job recommendations
        recommendations = []
        all_missing_skills = set()
        
        for job in ALL_JOBS[:8]:  # Limit to top 8 recommendations
            job_skills = job.get('skills_required', [])
            if isinstance(job_skills, str):
                job_skills = [s.strip() for s in job_skills.split(',')]
            
            skill_analysis = analyze_skill_gap(user_skills, job_skills)
            
            # Add missing skills to global set
            all_missing_skills.update(skill_analysis['missing_skills'])
            
            # Calculate match percentage
            if job_skills:
                match_count = len([skill for skill in job_skills if skill.lower() in [s.lower() for s in user_skills]])
                match_percentage = max(int((match_count / len(job_skills)) * 100), 65)
            else:
                match_percentage = 75
            
            recommendation = {
                "id": job.get('id', len(recommendations) + 1),
                "title": job.get('title', 'Software Developer'),
                "company": job.get('company', 'Tech Company'),
                "location": job.get('location', 'Remote'),
                "description": job.get('description', 'Great opportunity')[:200] + '...',
                "skills_required": job_skills[:5],  # Limit skills shown
                "experience": job.get('experience', '2+ years'),
                "salary": job.get('salary', '$50,000 - $70,000'),
                "match_percentage": match_percentage
            }
            recommendations.append(recommendation)
        
        # Calculate overall skill gap analysis
        all_job_skills = set()
        for job in ALL_JOBS[:20]:
            skills = job.get('skills_required', [])
            if isinstance(skills, str):
                skills = [s.strip() for s in skills.split(',')]
            all_job_skills.update([s.lower() for s in skills])
        
        user_skills_lower = [s.lower() for s in user_skills]
        missing_skills = [s for s in all_job_skills if s not in user_skills_lower]
        coverage = int((len(user_skills_lower) / max(len(all_job_skills), 1)) * 100)
        
        skill_gap_analysis = {
            'user_skills': user_skills,
            'missing_skills': list(missing_skills)[:10],  # Top 10 missing skills
            'coverage_percentage': coverage,
            'total_skills_analyzed': len(all_job_skills)
        }
        
        return jsonify({
            'success': True,
            'message': 'File uploaded and processed successfully',
            'filename': filename,
            'parsed_resume': {
                'skills': user_skills,
                'text_length': len(resume_text)
            },
            'recommendations': recommendations,
            'skill_gap_analysis': skill_gap_analysis,
            'live_jobs': []  # Add empty live_jobs for consistency
        })
        
    except Exception as e:
        logger.error(f"❌ Upload error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'OK',
        'message': 'Simple Recommendation Server Running',
        'endpoints': {
            'recommend': 'POST /recommend - Job recommendations',
            'upload': 'POST /upload - File upload',
            'health': 'GET / - Health check',
            'jobs': 'GET /api/jobs - Job listings',
            'experiences': 'GET /api/experiences - Interview experiences'
        },
        'jobs_loaded': len(ALL_JOBS)
    })

@app.route('/api/jobs', methods=['GET', 'OPTIONS'])
def get_jobs():
    """Get job postings for the frontend"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'})
    
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        start = (page - 1) * limit
        end = start + limit
        
        jobs_slice = ALL_JOBS[start:end]
        return jsonify({
            'success': True,
            'jobs': jobs_slice,
            'total': len(ALL_JOBS),
            'page': page,
            'limit': limit
        })
    except Exception as e:
        logger.error(f"Error in get_jobs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/experiences', methods=['GET', 'OPTIONS'])
def get_experiences():
    """Get interview experiences for the frontend"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'})
    
    try:
        # Return sample experiences
        sample_experiences = [
            {
                'id': '1',
                'company': 'Tech Corp',
                'role': 'Software Developer',
                'difficulty': 'Medium',
                'experience': 'Great technical interview, focus on algorithms',
                'date': '2024-10-15'
            },
            {
                'id': '2', 
                'company': 'StartupXYZ',
                'role': 'Full Stack Developer',
                'difficulty': 'Hard',
                'experience': 'System design round was challenging',
                'date': '2024-10-10'
            }
        ]
        
        return jsonify({
            'success': True,
            'experiences': sample_experiences,
            'total': len(sample_experiences)
        })
    except Exception as e:
        logger.error(f"Error in get_experiences: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/interview/questions', methods=['POST', 'OPTIONS'])
def get_interview_questions():
    """Get interview questions based on category"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'})
    
    try:
        data = request.get_json() or {}
        category = data.get('category', 'general')
        
        # Sample interview questions by category
        questions_db = {
            'fullstack': [
                {
                    'id': 1,
                    'text': 'What is the difference between REST and GraphQL APIs?',
                    'type': 'technical',
                    'difficulty': 'medium',
                    'category': 'fullstack',
                    'skills': ['API Design', 'Backend Development']
                },
                {
                    'id': 2,
                    'text': 'Explain the Virtual DOM in React and how it improves performance.',
                    'type': 'technical',
                    'difficulty': 'medium',
                    'category': 'fullstack',
                    'skills': ['React', 'Frontend Development']
                },
                {
                    'id': 3,
                    'text': 'How would you implement authentication in a full-stack application?',
                    'type': 'technical',
                    'difficulty': 'hard',
                    'category': 'fullstack',
                    'skills': ['Security', 'Authentication', 'Full Stack']
                }
            ],
            'backend': [
                {
                    'id': 4,
                    'text': 'Explain database indexing and when you would use it.',
                    'type': 'technical',
                    'difficulty': 'medium',
                    'category': 'backend',
                    'skills': ['Database', 'SQL', 'Performance']
                },
                {
                    'id': 5,
                    'text': 'What are microservices and what are their advantages?',
                    'type': 'technical',
                    'difficulty': 'hard',
                    'category': 'backend',
                    'skills': ['Architecture', 'Microservices', 'Backend']
                }
            ],
            'frontend': [
                {
                    'id': 6,
                    'text': 'What is the difference between var, let, and const in JavaScript?',
                    'type': 'technical',
                    'difficulty': 'easy',
                    'category': 'frontend',
                    'skills': ['JavaScript', 'ES6']
                },
                {
                    'id': 7,
                    'text': 'How do you handle state management in large React applications?',
                    'type': 'technical',
                    'difficulty': 'hard',
                    'category': 'frontend',
                    'skills': ['React', 'State Management', 'Redux']
                }
            ]
        }
        
        # Get questions for the requested category
        questions = questions_db.get(category, questions_db['fullstack'])
        
        return jsonify({
            'success': True,
            'questions': questions,
            'category': category,
            'total': len(questions)
        })
        
    except Exception as e:
        logger.error(f"Error in get_interview_questions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/problems', methods=['GET', 'OPTIONS'])
def get_problems():
    """Get coding problems list"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'})
    
    try:
        problems_file = os.path.join('data', 'Problems', 'problems.json')
        if os.path.exists(problems_file):
            with open(problems_file, 'r', encoding='utf-8') as f:
                problems = json.load(f)
            
            # Apply filters if provided
            difficulty = request.args.get('difficulty', '')
            topic = request.args.get('topic', '')
            search = request.args.get('search', '')
            
            filtered_problems = []
            for problem in problems:
                # Filter by difficulty
                if difficulty and problem.get('difficulty', '').lower() != difficulty.lower():
                    continue
                
                # Filter by topic
                if topic:
                    problem_topics = [t.lower() for t in problem.get('topics', [])]
                    if topic.lower() not in problem_topics:
                        continue
                
                # Filter by search term
                if search:
                    search_lower = search.lower()
                    title_match = search_lower in problem.get('title', '').lower()
                    desc_match = search_lower in problem.get('statement', {}).get('description', '').lower()
                    if not (title_match or desc_match):
                        continue
                
                filtered_problems.append(problem)
            
            return jsonify({
                'success': True,
                'problems': filtered_problems,
                'total': len(filtered_problems)
            })
        else:
            return jsonify({'success': False, 'error': 'Problems file not found'}), 404
    
    except Exception as e:
        logger.error(f"Error in get_problems: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/problems/<problem_id>', methods=['GET', 'OPTIONS'])
def get_problem_detail(problem_id):
    """Get specific problem details"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'})
    
    try:
        problems_file = os.path.join('data', 'Problems', 'problems.json')
        if os.path.exists(problems_file):
            with open(problems_file, 'r', encoding='utf-8') as f:
                problems = json.load(f)
            
            # Find problem by ID
            for problem in problems:
                if str(problem.get('id')) == str(problem_id):
                    return jsonify({
                        'success': True,
                        'problem': problem
                    })
            
            return jsonify({'success': False, 'error': f'Problem {problem_id} not found'}), 404
        else:
            return jsonify({'success': False, 'error': 'Problems file not found'}), 404
    
    except Exception as e:
        logger.error(f"Error in get_problem_detail: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = 5000
    print(f"🚀 Starting Simple Recommendation Server...")
    print(f"📊 Loaded {len(ALL_JOBS)} jobs for recommendations")
    print(f"🌐 Server will run at http://localhost:{port}")
    print(f"🔧 Endpoints:")
    print(f"   POST /recommend - Job recommendations")
    print(f"   POST /upload - File upload")
    print(f"   GET / - Health check")
    
    try:
        app.run(host='127.0.0.1', port=port, debug=False)
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        print("🔧 Make sure port 5000 is available")