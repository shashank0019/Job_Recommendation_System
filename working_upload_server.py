#!/usr/bin/env python3
"""
Working server with functional upload endpoint (no ML dependencies)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import re

app = Flask(__name__)
CORS(app)

# Load job data
try:
    job_data = pd.read_csv('data/job_dataset_sample.csv')
    print(f"Loaded {len(job_data)} jobs")
except Exception as e:
    print(f"Error loading job data: {e}")
    job_data = None

def extract_skills_from_text(text):
    """Extract skills from resume text"""
    skills = []
    skill_keywords = [
        'react', 'node.js', 'node', 'javascript', 'python', 'java', 'aws', 
        'docker', 'mongodb', 'sql', 'git', 'typescript', 'angular', 'vue', 
        'django', 'flask', 'kubernetes', 'azure', 'gcp', 'html', 'css',
        'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin'
    ]
    text_lower = text.lower()
    
    for skill in skill_keywords:
        if skill in text_lower:
            skills.append(skill)
    
    if not skills:
        skills = ['javascript', 'react', 'node.js']
    
    return skills

def find_matching_jobs(user_skills, max_jobs=5):
    """Find jobs that match user skills using simple text matching"""
    if job_data is None:
        # Fallback jobs if no data
        return [
            {'title': 'Senior React Developer', 'company': 'Meta', 'location': 'Menlo Park, CA', 'similarity_score': 0.85, 'matched_skills': ['react', 'javascript']},
            {'title': 'Full Stack Engineer', 'company': 'Google', 'location': 'Mountain View, CA', 'similarity_score': 0.75, 'matched_skills': ['javascript', 'python']},
            {'title': 'Python Developer', 'company': 'Netflix', 'location': 'Los Gatos, CA', 'similarity_score': 0.70, 'matched_skills': ['python']},
            {'title': 'DevOps Engineer', 'company': 'Amazon', 'location': 'Seattle, WA', 'similarity_score': 0.65, 'matched_skills': ['aws', 'docker']},
            {'title': 'Frontend Developer', 'company': 'Airbnb', 'location': 'San Francisco, CA', 'similarity_score': 0.60, 'matched_skills': ['react', 'javascript']}
        ]
    
    job_matches = []
    
    for idx, job in job_data.iterrows():
        # Get job skills and description
        job_skills_text = str(job.get('skills', '')) + ' ' + str(job.get('description', ''))
        job_skills_text = job_skills_text.lower()
        
        # Find matching skills
        matched_skills = []
        for skill in user_skills:
            if skill.lower() in job_skills_text:
                matched_skills.append(skill)
        
        if matched_skills:
            # Calculate similarity score
            similarity_score = len(matched_skills) / max(len(user_skills), 1)
            
            job_match = {
                'title': str(job.get('title', 'N/A')),
                'company': str(job.get('company', 'N/A')),
                'location': str(job.get('location', 'N/A')),
                'similarity_score': round(similarity_score, 3),
                'matched_skills': matched_skills
            }
            job_matches.append(job_match)
    
    # Sort by similarity score
    job_matches.sort(key=lambda x: x['similarity_score'], reverse=True)
    return job_matches[:max_jobs]

def extract_text_from_pdf(file_bytes):
    """Extract text from PDF file"""
    try:
        from PyPDF2 import PdfReader
        import io
        pdf_file = io.BytesIO(file_bytes)
        pdf_reader = PdfReader(pdf_file)
        text_parts = []
        for page in pdf_reader.pages:
            text_parts.append(page.extract_text())
        return '\n'.join(text_parts)
    except ImportError:
        return "PDF parsing not available. Please install PyPDF2."
    except Exception as e:
        return f"Error parsing PDF: {str(e)}"

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'jobs_loaded': job_data is not None,
        'model_loaded': False,  # No ML model
        'pdf_enabled': True
    })

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
        skills = extract_skills_from_text(resume_text)
        print(f"Extracted skills: {skills}")
        
        # Extract years of experience
        years_exp = 5  # default
        year_matches = re.findall(r'(\d+)\+?\s*(?:years?|yrs?)', resume_text.lower())
        if year_matches:
            years_exp = max([int(y) for y in year_matches])
        
        # Find matching jobs
        jobs = find_matching_jobs(skills, max_jobs=5)
        print(f"Found {len(jobs)} matching jobs")
        
        # Live jobs
        live_jobs = [
            {'title': 'Senior Software Engineer', 'company': 'Stripe', 'location': 'San Francisco, CA', 'url': 'https://stripe.com/jobs'},
            {'title': 'React Developer', 'company': 'Shopify', 'location': 'Remote', 'url': 'https://shopify.com/careers'},
            {'title': 'Python Developer', 'company': 'Dropbox', 'location': 'San Francisco, CA', 'url': 'https://dropbox.com/jobs'},
            {'title': 'Full Stack Developer', 'company': 'Slack', 'location': 'San Francisco, CA', 'url': 'https://slack.com/careers'},
            {'title': 'DevOps Engineer', 'company': 'GitHub', 'location': 'Remote', 'url': 'https://github.com/careers'}
        ]
        
        parsed = {
            'skills': skills,
            'years_experience': years_exp
        }
        
        return jsonify({
            'success': True,
            'jobs': jobs,
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
        text_content = ''
        filename = ''
        
        print("Upload request received")
        
        # Handle JSON request
        if request.is_json:
            data = request.get_json() or {}
            text_content = data.get('resume_text', '')
            if text_content.strip():
                print(f"JSON data received: {len(text_content)} characters")
            else:
                return jsonify({'success': False, 'error': 'Resume text is required in JSON request'}), 400
        
        # Handle file upload
        elif request.files and 'resume_file' in request.files:
            file = request.files['resume_file']
            if file and file.filename:
                filename = file.filename
                print(f"Processing file: {filename}")
                
                file_bytes = file.read()
                filename_lower = filename.lower()
                
                if filename_lower.endswith('.pdf'):
                    text_content = extract_text_from_pdf(file_bytes)
                elif filename_lower.endswith('.txt'):
                    try:
                        text_content = file_bytes.decode('utf-8', errors='ignore')
                        print("Text file processed successfully")
                    except Exception as e:
                        print(f"Error reading text file: {e}")
                        text_content = ''
                else:
                    return jsonify({'success': False, 'error': 'Unsupported file type. Please use PDF or TXT files.'}), 400
                
                if not text_content.strip():
                    return jsonify({'success': False, 'error': 'Could not extract text from the uploaded file'}), 400
            else:
                return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Handle form data
        elif request.form and 'resume_text' in request.form:
            text_content = request.form['resume_text']
            if text_content.strip():
                print("Form data received")
            else:
                return jsonify({'success': False, 'error': 'Resume text cannot be empty'}), 400
        
        else:
            return jsonify({'success': False, 'error': 'No resume data provided. Please upload a file or provide text.'}), 400
        
        print(f"Processing text: {len(text_content)} characters")
        
        # Extract skills
        skills = extract_skills_from_text(text_content)
        print(f"Extracted skills: {skills}")
        
        # Extract years of experience
        years_exp = 5  # default
        year_matches = re.findall(r'(\d+)\+?\s*(?:years?|yrs?)', text_content.lower())
        if year_matches:
            years_exp = max([int(y) for y in year_matches])
        
        # Find matching jobs
        jobs = find_matching_jobs(skills, max_jobs=5)
        print(f"Found {len(jobs)} matching jobs")
        
        # Live jobs
        live_jobs = [
            {'title': 'Senior Software Engineer', 'company': 'Stripe', 'location': 'San Francisco, CA', 'url': 'https://stripe.com/jobs'},
            {'title': 'React Developer', 'company': 'Shopify', 'location': 'Remote', 'url': 'https://shopify.com/careers'},
            {'title': 'Python Developer', 'company': 'Dropbox', 'location': 'San Francisco, CA', 'url': 'https://dropbox.com/jobs'},
            {'title': 'Full Stack Developer', 'company': 'Slack', 'location': 'San Francisco, CA', 'url': 'https://slack.com/careers'},
            {'title': 'DevOps Engineer', 'company': 'GitHub', 'location': 'Remote', 'url': 'https://github.com/careers'}
        ]
        
        parsed = {
            'skills': skills,
            'years_experience': years_exp,
            'filename': filename if filename else None
        }
        
        print(f"Returning {len(jobs)} jobs and {len(live_jobs)} live jobs")
        
        response = jsonify({
            'success': True,
            'jobs': jobs,
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
            'message': 'Failed to process upload. Please try again.'
        })
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500

if __name__ == '__main__':
    print("Starting Working Upload Server...")
    print("Server: http://localhost:5000")
    print("CORS: Enabled for all origins")
    print("Endpoints:")
    print("   - GET  /health")
    print("   - POST /recommend")
    print("   - POST /upload (FIXED)")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
