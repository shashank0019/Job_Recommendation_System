#!/usr/bin/env python3
"""
Simple CORS-enabled server for testing job recommendations
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)

# Enable CORS for all origins (for testing)
CORS(app, resources={
    r"/*": {
        "origins": "*",  # Allow all origins for testing
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Origin", "Accept"]
    }
})

# Simple job data for testing
sample_jobs = [
    {
        "title": "Senior Software Engineer",
        "company": "TechCorp",
        "location": "San Francisco, CA",
        "similarity_score": 0.95
    },
    {
        "title": "Full Stack Developer", 
        "company": "StartupXYZ",
        "location": "Remote",
        "similarity_score": 0.87
    },
    {
        "title": "React Developer",
        "company": "WebCompany", 
        "location": "New York, NY",
        "similarity_score": 0.82
    }
]

sample_live_jobs = [
    {
        "title": "Software Engineer",
        "company": "Google",
        "location": "Mountain View, CA",
        "url": "https://careers.google.com"
    },
    {
        "title": "Frontend Developer",
        "company": "Facebook", 
        "location": "Menlo Park, CA",
        "url": "https://careers.facebook.com"
    }
]

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'CORS-enabled server running',
        'cors_enabled': True
    })

@app.route('/recommend', methods=['POST', 'OPTIONS'])
def recommend():
    """Simple job recommendation endpoint"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Origin,Accept')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
    
    try:
        data = request.get_json() or {}
        resume_text = data.get('resume_text', '')
        
        if not resume_text:
            error_response = jsonify({'success': False, 'error': 'No resume text provided'})
            error_response.headers.add('Access-Control-Allow-Origin', '*')
            return error_response
        
        # Simple skill extraction
        skills = []
        skill_keywords = ['react', 'node.js', 'node', 'javascript', 'python', 'aws', 'docker', 'mongodb', 'sql', 'git']
        resume_lower = resume_text.lower()
        
        for skill in skill_keywords:
            if skill.lower() in resume_lower:
                skills.append(skill)
        
        # If no skills found, add some default ones
        if not skills:
            skills = ['javascript', 'react', 'node.js']
        
        # Mock parsed data
        parsed = {
            'skills': skills,
            'years_experience': 5  # Mock experience
        }
        
        response = jsonify({
            'success': True,
            'jobs': sample_jobs,  # Model matches
            'live_jobs': sample_live_jobs,  # Live jobs
            'parsed': parsed
        })
        
        # Add CORS headers explicitly
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        print(f"Recommend error: {e}")
        error_response = jsonify({'success': False, 'error': str(e)})
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload():
    """Simple upload endpoint with proper CORS handling"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Origin,Accept')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
    
    try:
        resume_text = ""
        
        # Check content type and handle accordingly
        content_type = request.content_type or ""
        
        if 'multipart/form-data' in content_type:
            # Handle file upload
            if 'resume_file' in request.files:
                file = request.files['resume_file']
                if file and file.filename:
                    try:
                        if file.filename.endswith('.txt'):
                            resume_text = file.read().decode('utf-8')
                        else:
                            resume_text = f"File uploaded: {file.filename}. Software Engineer with React, Node.js, Python experience."
                    except:
                        resume_text = f"File uploaded: {file.filename}. Software Engineer with React, Node.js, Python experience."
                else:
                    resume_text = "Software Engineer with React, Node.js, Python experience."
            else:
                resume_text = "Software Engineer with React, Node.js, Python experience."
        else:
            # Handle JSON data
            try:
                data = request.get_json() or {}
                resume_text = data.get('resume_text', 'Software Engineer with React, Node.js, Python experience.')
            except:
                # If no JSON, use default
                resume_text = "Software Engineer with React, Node.js, Python experience."
        
        # Simple skill extraction
        skills = []
        skill_keywords = ['react', 'node.js', 'node', 'javascript', 'python', 'aws', 'docker', 'mongodb', 'sql', 'git']
        resume_lower = resume_text.lower()
        
        for skill in skill_keywords:
            if skill.lower() in resume_lower:
                skills.append(skill)
        
        # If no skills found, add some default ones
        if not skills:
            skills = ['javascript', 'react', 'node.js']
        
        parsed = {
            'skills': skills,
            'years_experience': 5
        }
        
        response = jsonify({
            'success': True,
            'jobs': sample_jobs,
            'live_jobs': sample_live_jobs, 
            'parsed': parsed
        })
        
        # Add CORS headers explicitly
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        print(f"Upload error: {e}")
        error_response = jsonify({'success': False, 'error': str(e)})
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500

if __name__ == '__main__':
    print("🚀 Starting Simple CORS-enabled Server...")
    print("🌐 Server will run on http://localhost:5000")
    print("✅ CORS enabled for all origins")
    print("📝 Endpoints available:")
    print("   - GET  /health")
    print("   - POST /recommend") 
    print("   - POST /upload")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
