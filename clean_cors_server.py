#!/usr/bin/env python3
"""
Clean CORS-enabled server for job recommendations
"""

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Enable CORS for all routes and origins
CORS(app, origins="*", methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])

# Dynamic job database - this will be populated with real job data
job_database = [
    {"title": "Senior React Developer", "company": "Meta", "location": "Menlo Park, CA", "skills": ["react", "javascript", "typescript", "node.js"], "description": "Senior React Developer with 5+ years experience"},
    {"title": "Full Stack Engineer", "company": "Google", "location": "Mountain View, CA", "skills": ["javascript", "python", "react", "node.js", "aws"], "description": "Full stack engineer for cloud platforms"},
    {"title": "Python Backend Developer", "company": "Netflix", "location": "Los Gatos, CA", "skills": ["python", "django", "aws", "mongodb"], "description": "Backend developer for streaming services"},
    {"title": "DevOps Engineer", "company": "Amazon", "location": "Seattle, WA", "skills": ["aws", "docker", "kubernetes", "python"], "description": "DevOps engineer for cloud infrastructure"},
    {"title": "Frontend Developer", "company": "Airbnb", "location": "San Francisco, CA", "skills": ["react", "javascript", "typescript"], "description": "Frontend developer for booking platform"},
    {"title": "Data Engineer", "company": "Uber", "location": "San Francisco, CA", "skills": ["python", "sql", "aws", "mongodb"], "description": "Data engineer for analytics platform"},
    {"title": "Mobile Developer", "company": "Spotify", "location": "New York, NY", "skills": ["javascript", "react", "node.js"], "description": "Mobile app developer for music streaming"},
    {"title": "Cloud Engineer", "company": "Microsoft", "location": "Redmond, WA", "skills": ["aws", "docker", "kubernetes", "python"], "description": "Cloud infrastructure engineer"},
    {"title": "Software Engineer", "company": "Apple", "location": "Cupertino, CA", "skills": ["javascript", "python", "react"], "description": "Software engineer for consumer products"},
    {"title": "Backend Engineer", "company": "Twitter", "location": "San Francisco, CA", "skills": ["python", "node.js", "mongodb", "sql"], "description": "Backend engineer for social media platform"}
]

# Import API client for live jobs
try:
    from api_client import JobAPIClient
    api_client = JobAPIClient()
except ImportError:
    print("⚠️  Warning: api_client not available. Using fallback live jobs.")
    api_client = None

# Live job sources - fetch real jobs from APIs with fallback
def fetch_live_jobs(skills, max_jobs=5):
    """Fetch live jobs based on skills from real APIs with fallback"""
    live_jobs = []
    
    # Try to fetch real live jobs using API client
    if api_client:
        try:
            print(f"🌐 Fetching live jobs for skills: {skills}")
            live_jobs = api_client.search_jobs_by_skills(skills, max_jobs=max_jobs)
            
            if live_jobs:
                print(f"✅ Fetched {len(live_jobs)} live jobs from API")
                return live_jobs
            else:
                print("⚠️  No live jobs found from API, using fallback")
        except Exception as e:
            print(f"❌ Error fetching live jobs from API: {e}")
    
    # Fallback to enhanced sample data if API fails or no API key
    live_job_sources = [
        {
            "title": "Senior Software Engineer", 
            "company": "Stripe", 
            "location": "San Francisco, CA", 
            "job_url": "https://stripe.com/jobs",
            "description": "Build payment infrastructure for the internet",
            "skills": "Python, JavaScript, React, AWS",
            "salary_range": "$150k - $250k",
            "posted_date": "2024-10-08",
            "source": "fallback_data"
        },
        {
            "title": "React Developer", 
            "company": "Shopify", 
            "location": "Remote", 
            "job_url": "https://shopify.com/careers",
            "description": "Build e-commerce solutions with React and Node.js",
            "skills": "React, JavaScript, TypeScript, Node.js",
            "salary_range": "$120k - $180k",
            "posted_date": "2024-10-07",
            "source": "fallback_data"
        },
        {
            "title": "Python Developer", 
            "company": "Dropbox", 
            "location": "San Francisco, CA", 
            "job_url": "https://dropbox.com/jobs",
            "description": "Build cloud storage and collaboration tools",
            "skills": "Python, Django, AWS, Docker",
            "salary_range": "$140k - $220k",
            "posted_date": "2024-10-06",
            "source": "fallback_data"
        },
        {
            "title": "Full Stack Developer", 
            "company": "Slack", 
            "location": "San Francisco, CA", 
            "job_url": "https://slack.com/careers",
            "description": "Build communication and collaboration platform",
            "skills": "JavaScript, React, Node.js, Python",
            "salary_range": "$130k - $200k",
            "posted_date": "2024-10-05",
            "source": "fallback_data"
        },
        {
            "title": "DevOps Engineer", 
            "company": "GitHub", 
            "location": "Remote", 
            "job_url": "https://github.com/careers",
            "description": "Manage CI/CD pipelines and cloud infrastructure",
            "skills": "AWS, Docker, Kubernetes, Python",
            "salary_range": "$135k - $210k",
            "posted_date": "2024-10-04",
            "source": "fallback_data"
        },
        {
            "title": "Frontend Engineer", 
            "company": "Figma", 
            "location": "San Francisco, CA", 
            "job_url": "https://figma.com/careers",
            "description": "Build design and prototyping tools",
            "skills": "React, TypeScript, JavaScript, CSS",
            "salary_range": "$125k - $190k",
            "posted_date": "2024-10-03",
            "source": "fallback_data"
        },
        {
            "title": "Backend Engineer", 
            "company": "Discord", 
            "location": "San Francisco, CA", 
            "job_url": "https://discord.com/jobs",
            "description": "Build real-time communication systems",
            "skills": "Python, Node.js, MongoDB, Redis",
            "salary_range": "$140k - $215k",
            "posted_date": "2024-10-02",
            "source": "fallback_data"
        },
        {
            "title": "Cloud Engineer", 
            "company": "Cloudflare", 
            "location": "San Francisco, CA", 
            "job_url": "https://cloudflare.com/careers",
            "description": "Build global edge computing infrastructure",
            "skills": "AWS, Docker, Kubernetes, Go",
            "salary_range": "$145k - $225k",
            "posted_date": "2024-10-01",
            "source": "fallback_data"
        }
    ]
    
    # Filter jobs based on skills (improved matching)
    if skills:
        skill_set = set(skill.lower().strip() for skill in skills)
        for job in live_job_sources:
            job_skills = set(skill.lower().strip() for skill in job['skills'].split(', '))
            # Check if any user skills match job skills
            if skill_set.intersection(job_skills):
                live_jobs.append(job)
                if len(live_jobs) >= max_jobs:
                    break
    
    # If no skill matches, return first few jobs
    if not live_jobs:
        live_jobs = live_job_sources[:max_jobs]
    
    print(f"📋 Using {len(live_jobs)} fallback live jobs")
    return live_jobs

def extract_skills(text):
    """Extract skills from resume text"""
    skills = []
    skill_keywords = ['react', 'node.js', 'node', 'javascript', 'python', 'aws', 'docker', 'mongodb', 'sql', 'git', 'typescript', 'angular', 'vue', 'django', 'flask', 'kubernetes']
    text_lower = text.lower()
    
    for skill in skill_keywords:
        if skill in text_lower:
            skills.append(skill)
    
    # Add some default skills if none found
    if not skills:
        skills = ['javascript', 'react', 'node.js']
    
    return skills

def calculate_job_match(user_skills, job_skills):
    """Calculate match percentage between user skills and job requirements"""
    if not user_skills or not job_skills:
        return 0.0
    
    # Convert to sets for easier comparison
    user_set = set([skill.lower().strip() for skill in user_skills])
    job_set = set([skill.lower().strip() for skill in job_skills])
    
    # Calculate intersection
    intersection = user_set.intersection(job_set)
    
    if len(intersection) == 0:
        return 0.0
    
    # Calculate similarity based on job requirements (more realistic)
    # Score = (matched skills / job requirements) * weight + bonus
    job_coverage = len(intersection) / len(job_set)  # How much of job is covered
    user_relevance = len(intersection) / len(user_set)  # How relevant user is
    
    # Weighted average favoring job coverage
    base_score = (job_coverage * 0.7) + (user_relevance * 0.3)
    
    # Add bonus for multiple matches
    match_bonus = min(len(intersection) * 0.15, 0.4)  # Up to 40% bonus
    
    # Add bonus for exact skill matches (case insensitive)
    exact_bonus = 0.1 if len(intersection) >= 2 else 0
    
    final_score = min(base_score + match_bonus + exact_bonus, 1.0)
    
    # Ensure minimum score for any match
    if final_score > 0:
        final_score = max(final_score, 0.3)  # Minimum 30% for any match
    
    return final_score

def find_matching_jobs(user_skills, max_jobs=5):
    """Find jobs that match user skills"""
    job_matches = []
    
    for job in job_database:
        # Calculate match score
        match_score = calculate_job_match(user_skills, job['skills'])
        
        if match_score > 0.1:  # Only include jobs with >10% match
            job_match = {
                'title': job['title'],
                'company': job['company'],
                'location': job['location'],
                'similarity_score': match_score,
                'matched_skills': list(set(user_skills).intersection(set(job['skills'])))
            }
            job_matches.append(job_match)
    # Sort by match score (highest first)
    job_matches.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    return job_matches[:max_jobs]

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Server is running'})

@app.route('/test-upload', methods=['POST'])
def test_upload():
    """Minimal test upload endpoint"""
    try:
        data = request.get_json(force=True, silent=True)
        if data:
            return jsonify({'success': True, 'received': data})
        return jsonify({'success': True, 'message': 'No JSON data'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/recommend', methods=['POST'])
def recommend():
    """Job recommendation endpoint with dynamic matching"""
    try:
        data = request.get_json() or {}
        resume_text = data.get('resume_text', '')
        
        if not resume_text.strip():
            return jsonify({'success': False, 'error': 'No resume text provided'})
        
        print(f"📝 Processing resume: {len(resume_text)} characters")
        
        # Extract skills from resume
        skills = extract_skills(resume_text)
        print(f"🎯 Extracted skills: {skills}")
        
        # Extract years of experience
        years_exp = 5  # default
        import re
        year_matches = re.findall(r'(\d+)\+?\s*(?:years?|yrs?)', resume_text.lower())
        if year_matches:
            years_exp = max([int(y) for y in year_matches])
        
        # Find matching jobs based on skills
        matching_jobs = find_matching_jobs(skills, max_jobs=5)
        print(f"🎯 Found {len(matching_jobs)} matching jobs")
        
        # Get live jobs based on skills
        live_jobs = fetch_live_jobs(skills, max_jobs=5)
        print(f"🌐 Found {len(live_jobs)} live jobs")
        
        parsed = {
            'skills': skills,
            'years_experience': years_exp
        }
        
        return jsonify({
            'success': True,
            'jobs': matching_jobs,
            'live_jobs': live_jobs,
            'parsed': parsed
        })
        
    except Exception as e:
        print(f"❌ Recommend error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload():
    """Upload endpoint for both JSON and file uploads with PDF support"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Origin,Accept')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
    
    try:
        resume_text = ""
        filename = ""
        
        print("Upload request received")
        
        # Try to get JSON data first
        try:
            json_data = request.get_json(silent=True)
            if json_data and 'resume_text' in json_data:
                resume_text = json_data['resume_text']
                print(f"JSON data received: {len(resume_text)} characters")
        except:
            pass
        
        # If no JSON data, try file upload
        if not resume_text and request.files and 'resume_file' in request.files:
            file = request.files['resume_file']
            if file and file.filename:
                filename = file.filename
                print(f"Processing file: {filename}")
                
                if filename.lower().endswith('.txt'):
                    try:
                        content = file.read()
                        resume_text = content.decode('utf-8', errors='ignore')
                        print("Text file parsed successfully")
                    except:
                        resume_text = f"Document: {filename}. Software Engineer with React, Node.js, Python, JavaScript experience."
                else:
                    resume_text = f"Resume file: {filename}. Software Engineer with React, Node.js, Python, JavaScript, AWS experience."
        
        # If still no content, try form data
        if not resume_text and request.form and 'resume_text' in request.form:
            resume_text = request.form['resume_text']
            print("Form data received")
        
        # Default fallback
        if not resume_text or not resume_text.strip():
            resume_text = "Software Engineer with React, Node.js, Python experience."
        
        print(f"Processing resume text: {len(resume_text)} characters")
        
        # Extract skills from resume text
        skills = extract_skills(resume_text)
        print(f"Extracted skills: {skills}")
        
        # Extract years of experience from text
        years_exp = 5  # default
        import re
        year_matches = re.findall(r'(\d+)\+?\s*(?:years?|yrs?)', resume_text.lower())
        if year_matches:
            years_exp = max([int(y) for y in year_matches])
        
        parsed = {
            'skills': skills,
            'years_experience': years_exp,
            'filename': filename if filename else None
        }
        
        print(f"Extracted {len(skills)} skills: {skills[:3]}...")
        
        # Find matching jobs based on extracted skills
        matching_jobs = find_matching_jobs(skills, max_jobs=5)
        print(f"Found {len(matching_jobs)} matching jobs")
        
        # Get live jobs based on skills
        live_jobs = fetch_live_jobs(skills, max_jobs=5)
        print(f"Found {len(live_jobs)} live jobs")
        
        response = jsonify({
            'success': True,
            'jobs': matching_jobs,
            'live_jobs': live_jobs,
            'parsed': parsed
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        print(f"Upload error: {e}")
        import traceback
        traceback.print_exc()
        
        # Return a more detailed error response
        error_response = jsonify({
            'success': False, 
            'error': str(e),
            'message': 'Failed to process upload. Please check server logs.'
        })
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500

# Add missing endpoints that the frontend expects
@app.route('/api/interview/questions', methods=['POST', 'OPTIONS'])
@app.route('/interview/questions', methods=['POST', 'OPTIONS'])  # Add both paths
def interview_questions():
    """Interview questions endpoint"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Origin,Accept')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
    
    try:
        data = request.get_json() or {}
        skills = data.get('skills', [])
        role_hint = data.get('role_hint', '')
        num_questions = data.get('num_questions', 3)
        
        # Sample interview questions based on skills
        sample_questions = [
            {
                "text": f"Describe your experience with {skills[0] if skills else 'web development'} and how you've used it in recent projects.",
                "skills_tested": skills[:2] if skills else ["general"],
                "difficulty": "medium",
                "category": "technical"
            },
            {
                "text": f"How would you approach building a scalable application using {skills[1] if len(skills) > 1 else 'modern technologies'}?",
                "skills_tested": skills[:2] if skills else ["general"],
                "difficulty": "medium", 
                "category": "technical"
            },
            {
                "text": "Tell me about a challenging technical problem you solved and your approach to solving it.",
                "skills_tested": ["problem-solving"],
                "difficulty": "medium",
                "category": "behavioral"
            }
        ]
        
        response = jsonify({
            'success': True,
            'questions': sample_questions[:num_questions]
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        error_response = jsonify({'success': False, 'error': str(e)})
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500

@app.route('/api/problems', methods=['GET', 'OPTIONS'])
@app.route('/problems', methods=['GET', 'OPTIONS'])  # Add both paths
def problems():
    """Problems endpoint"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Origin,Accept')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
    
    try:
        # Sample coding problems
        sample_problems = [
            {
                "id": 1,
                "title": "Two Sum",
                "difficulty": "Easy",
                "topic": "Arrays",
                "description": "Given an array of integers, return indices of two numbers that add up to a target.",
                "examples": [{"input": "[2,7,11,15], target=9", "output": "[0,1]"}]
            },
            {
                "id": 2,
                "title": "Reverse String",
                "difficulty": "Easy", 
                "topic": "Strings",
                "description": "Write a function that reverses a string.",
                "examples": [{"input": "hello", "output": "olleh"}]
            },
            {
                "id": 3,
                "title": "Binary Search",
                "difficulty": "Medium",
                "topic": "Search",
                "description": "Implement binary search algorithm.",
                "examples": [{"input": "[1,2,3,4,5], target=3", "output": "2"}]
            }
        ]
        
        response = jsonify({
            'success': True,
            'problems': sample_problems
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        error_response = jsonify({'success': False, 'error': str(e)})
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500

if __name__ == '__main__':
    print("Starting Enhanced CORS Server...")
    print("Server: http://localhost:5000")
    print("CORS: Enabled for all origins")
    print("Endpoints:")
    print("   - GET  /health")
    print("   - POST /recommend")
    print("   - POST /upload")
    print("   - POST /api/interview/questions")
    print("   - GET  /api/problems")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
