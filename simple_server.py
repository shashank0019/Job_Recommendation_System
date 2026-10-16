#!/usr/bin/env python3
"""Simple working server for testing"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

# Sample job data
job_database = [
    {"title": "Senior React Developer", "company": "Meta", "location": "Menlo Park, CA", "skills": ["react", "javascript", "typescript", "node.js"]},
    {"title": "Full Stack Engineer", "company": "Google", "location": "Mountain View, CA", "skills": ["javascript", "python", "react", "node.js", "aws"]},
    {"title": "Python Backend Developer", "company": "Netflix", "location": "Los Gatos, CA", "skills": ["python", "django", "aws", "mongodb"]},
    {"title": "DevOps Engineer", "company": "Amazon", "location": "Seattle, WA", "skills": ["aws", "docker", "kubernetes", "python"]},
    {"title": "Frontend Developer", "company": "Airbnb", "location": "San Francisco, CA", "skills": ["react", "javascript", "typescript"]}
]

# Live jobs data
live_jobs = [
    {"title": "Senior Software Engineer", "company": "Stripe", "location": "San Francisco, CA", "url": "https://stripe.com/jobs"},
    {"title": "React Developer", "company": "Shopify", "location": "Remote", "url": "https://shopify.com/careers"},
    {"title": "Python Developer", "company": "Dropbox", "location": "San Francisco, CA", "url": "https://dropbox.com/jobs"},
    {"title": "Full Stack Developer", "company": "Slack", "location": "San Francisco, CA", "url": "https://slack.com/careers"},
    {"title": "DevOps Engineer", "company": "GitHub", "location": "Remote", "url": "https://github.com/careers"}
]

def extract_skills(text):
    """Extract skills from resume text"""
    skills = []
    skill_keywords = ['react', 'node.js', 'node', 'javascript', 'python', 'aws', 'docker', 'mongodb', 'sql', 'git', 'typescript', 'angular', 'vue', 'django', 'flask', 'kubernetes']
    text_lower = text.lower()
    
    for skill in skill_keywords:
        if skill in text_lower:
            skills.append(skill)
    
    if not skills:
        skills = ['javascript', 'react', 'node.js']
    
    return skills

def find_matching_jobs(user_skills, max_jobs=5):
    """Find jobs that match user skills"""
    job_matches = []
    
    for job in job_database:
        # Calculate match score
        job_skills = job.get('skills', [])
        matched_skills = set(user_skills).intersection(set(job_skills))
        
        if matched_skills:
            match_score = len(matched_skills) / len(job_skills) if job_skills else 0
            job_match = {
                'title': job['title'],
                'company': job['company'],
                'location': job['location'],
                'similarity_score': match_score,
                'matched_skills': list(matched_skills)
            }
            job_matches.append(job_match)
    
    # Sort by match score
    job_matches.sort(key=lambda x: x['similarity_score'], reverse=True)
    return job_matches[:max_jobs]

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'message': 'Server is running'})

@app.route('/recommend', methods=['POST'])
def recommend():
    """Job recommendation endpoint"""
    try:
        data = request.get_json() or {}
        resume_text = data.get('resume_text', '')
        
        if not resume_text.strip():
            return jsonify({'success': False, 'error': 'No resume text provided'})
        
        print(f"Processing resume: {len(resume_text)} characters")
        
        # Extract skills
        skills = extract_skills(resume_text)
        print(f"Extracted skills: {skills}")
        
        # Extract years of experience
        years_exp = 5  # default
        year_matches = re.findall(r'(\d+)\+?\s*(?:years?|yrs?)', resume_text.lower())
        if year_matches:
            years_exp = max([int(y) for y in year_matches])
        
        # Find matching jobs
        matching_jobs = find_matching_jobs(skills, max_jobs=5)
        print(f"Found {len(matching_jobs)} matching jobs")
        
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
        print(f"Recommend error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload():
    """Upload endpoint for both JSON and file uploads"""
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
        
        # Extract skills
        skills = extract_skills(resume_text)
        print(f"Extracted skills: {skills}")
        
        # Extract years of experience
        years_exp = 5  # default
        year_matches = re.findall(r'(\d+)\+?\s*(?:years?|yrs?)', resume_text.lower())
        if year_matches:
            years_exp = max([int(y) for y in year_matches])
        
        parsed = {
            'skills': skills,
            'years_experience': years_exp,
            'filename': filename if filename else None
        }
        
        print(f"Extracted {len(skills)} skills: {skills[:3]}...")
        
        # Find matching jobs
        matching_jobs = find_matching_jobs(skills, max_jobs=5)
        print(f"Found {len(matching_jobs)} matching jobs")
        
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
        
        error_response = jsonify({
            'success': False, 
            'error': str(e),
            'message': 'Failed to process upload. Please check server logs.'
        })
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500

if __name__ == '__main__':
    print("Starting Simple Server...")
    print("Server: http://localhost:5000")
    print("CORS: Enabled for all origins")
    print("Endpoints:")
    print("   - GET  /health")
    print("   - POST /recommend")
    print("   - POST /upload")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
