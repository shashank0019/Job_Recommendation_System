#!/usr/bin/env python3
"""
New Upload Server with Working TF-IDF Model
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import pickle
import re
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = Flask(__name__)
CORS(app)

# Global variables for model and data
job_data = None
vectorizer = None
job_vectors = None

def load_model_and_data():
    """Load job data and ML model"""
    global job_data, vectorizer, job_vectors
    
    try:
        # Load job data
        job_data = pd.read_csv('data/job_dataset_sample.csv')
        print(f"✅ Loaded {len(job_data)} jobs")
        
        # Load TF-IDF vectorizer
        with open('data/tfidf_vectorizer.joblib', 'rb') as f:
            vectorizer = pickle.load(f)
        print("✅ Loaded TF-IDF vectorizer")
        
        # Load job vectors
        with open('data/trained_model.joblib', 'rb') as f:
            job_vectors = pickle.load(f)
        print(f"✅ Loaded job vectors: {job_vectors.shape}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False

def extract_skills_from_text(text):
    """Extract skills from resume text"""
    skills = []
    skill_keywords = [
        'react', 'node.js', 'node', 'javascript', 'python', 'java', 'aws', 
        'docker', 'mongodb', 'sql', 'git', 'typescript', 'angular', 'vue', 
        'django', 'flask', 'kubernetes', 'azure', 'gcp', 'html', 'css',
        'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin',
        'spring', 'express', 'fastapi', 'postgresql', 'mysql', 'redis',
        'jenkins', 'terraform', 'ansible', 'linux', 'windows'
    ]
    text_lower = text.lower()
    
    for skill in skill_keywords:
        if skill in text_lower:
            skills.append(skill)
    
    # Remove duplicates and sort
    skills = sorted(list(set(skills)))
    
    if not skills:
        skills = ['javascript', 'react', 'node.js']
    
    return skills

def find_jobs_with_ml(resume_text, max_jobs=5):
    """Find matching jobs using ML model"""
    global job_data, vectorizer, job_vectors
    
    if not all([job_data is not None, vectorizer is not None, job_vectors is not None]):
        return []
    
    try:
        # Transform resume text
        resume_vector = vectorizer.transform([resume_text])
        
        # Calculate similarities
        similarities = cosine_similarity(resume_vector, job_vectors).flatten()
        
        # Get top matches
        top_indices = similarities.argsort()[-max_jobs*2:][::-1]  # Get more to filter
        
        jobs = []
        for idx in top_indices:
            if len(jobs) >= max_jobs:
                break
                
            if idx < len(job_data) and similarities[idx] > 0.01:  # Minimum threshold
                job = job_data.iloc[idx]
                jobs.append({
                    'title': str(job.get('title', 'N/A')),
                    'company': str(job.get('company', 'N/A')),
                    'location': str(job.get('location', 'N/A')),
                    'similarity_score': round(float(similarities[idx]), 3),
                    'description': str(job.get('description', ''))[:200] + '...' if len(str(job.get('description', ''))) > 200 else str(job.get('description', '')),
                    'experience_level': str(job.get('experience_level', 'N/A')),
                    'work_type': str(job.get('work_type', 'N/A'))
                })
        
        return jobs
        
    except Exception as e:
        print(f"ML matching error: {e}")
        return []

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
        return "PDF parsing not available. Please install PyPDF2: pip install PyPDF2"
    except Exception as e:
        return f"Error parsing PDF: {str(e)}"

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'jobs_loaded': job_data is not None,
        'model_loaded': vectorizer is not None and job_vectors is not None,
        'pdf_enabled': True,
        'total_jobs': len(job_data) if job_data is not None else 0
    })

@app.route('/recommend', methods=['POST'])
def recommend():
    """Job recommendation endpoint"""
    try:
        data = request.get_json() or {}
        resume_text = data.get('resume_text', '')
        
        if not resume_text.strip():
            return jsonify({'success': False, 'error': 'No resume text provided'})
        
        print(f"📝 Processing resume: {len(resume_text)} characters")
        
        # Extract skills
        skills = extract_skills_from_text(resume_text)
        print(f"🎯 Extracted skills: {skills}")
        
        # Extract years of experience
        years_exp = 5  # default
        year_matches = re.findall(r'(\d+)\+?\s*(?:years?|yrs?)', resume_text.lower())
        if year_matches:
            years_exp = max([int(y) for y in year_matches])
        
        # Find matching jobs using ML
        jobs = find_jobs_with_ml(resume_text, max_jobs=5)
        print(f"🎯 Found {len(jobs)} matching jobs")
        
        # Live jobs (curated list)
        live_jobs = [
            {'title': 'Senior Software Engineer', 'company': 'Stripe', 'location': 'San Francisco, CA', 'url': 'https://stripe.com/jobs', 'posted': '2 days ago'},
            {'title': 'React Developer', 'company': 'Shopify', 'location': 'Remote', 'url': 'https://shopify.com/careers', 'posted': '1 week ago'},
            {'title': 'Python Developer', 'company': 'Dropbox', 'location': 'San Francisco, CA', 'url': 'https://dropbox.com/jobs', 'posted': '3 days ago'},
            {'title': 'Full Stack Developer', 'company': 'Slack', 'location': 'San Francisco, CA', 'url': 'https://slack.com/careers', 'posted': '5 days ago'},
            {'title': 'DevOps Engineer', 'company': 'GitHub', 'location': 'Remote', 'url': 'https://github.com/careers', 'posted': '1 day ago'}
        ]
        
        parsed = {
            'skills': skills,
            'years_experience': years_exp,
            'skill_count': len(skills)
        }
        
        return jsonify({
            'success': True,
            'jobs': jobs,
            'live_jobs': live_jobs,
            'parsed': parsed,
            'total_matches': len(jobs)
        })
        
    except Exception as e:
        print(f"❌ Recommend error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload():
    """NEW Upload endpoint for resume files and text"""
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Origin,Accept')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
    
    try:
        text_content = ''
        filename = ''
        upload_type = 'unknown'
        
        print("📥 Upload request received")
        
        # 1. Handle JSON request (text input)
        if request.is_json:
            data = request.get_json() or {}
            text_content = data.get('resume_text', '').strip()
            upload_type = 'json'
            
            if not text_content:
                return jsonify({
                    'success': False, 
                    'error': 'Resume text is required'
                }), 400
            
            print(f"📄 JSON upload: {len(text_content)} characters")
        
        # 2. Handle file upload
        elif request.files and 'resume_file' in request.files:
            file = request.files['resume_file']
            upload_type = 'file'
            
            if not file or not file.filename:
                return jsonify({
                    'success': False, 
                    'error': 'No file selected'
                }), 400
            
            filename = file.filename
            print(f"📁 File upload: {filename}")
            
            # Read file content
            file_bytes = file.read()
            filename_lower = filename.lower()
            
            # Process based on file type
            if filename_lower.endswith('.pdf'):
                text_content = extract_text_from_pdf(file_bytes)
                if 'Error' in text_content or 'not available' in text_content:
                    return jsonify({
                        'success': False, 
                        'error': text_content
                    }), 400
                    
            elif filename_lower.endswith('.txt'):
                try:
                    text_content = file_bytes.decode('utf-8', errors='ignore')
                except Exception as e:
                    return jsonify({
                        'success': False, 
                        'error': f'Error reading text file: {str(e)}'
                    }), 400
                    
            else:
                return jsonify({
                    'success': False, 
                    'error': 'Unsupported file type. Please upload PDF or TXT files only.'
                }), 400
            
            if not text_content.strip():
                return jsonify({
                    'success': False, 
                    'error': 'Could not extract text from the uploaded file'
                }), 400
        
        # 3. Handle form data
        elif request.form and 'resume_text' in request.form:
            text_content = request.form.get('resume_text', '').strip()
            upload_type = 'form'
            
            if not text_content:
                return jsonify({
                    'success': False, 
                    'error': 'Resume text cannot be empty'
                }), 400
            
            print(f"📋 Form upload: {len(text_content)} characters")
        
        else:
            return jsonify({
                'success': False, 
                'error': 'No resume data provided. Please upload a file or provide text.'
            }), 400
        
        # Process the resume text
        print(f"🔍 Processing {upload_type} upload: {len(text_content)} characters")
        
        # Extract skills
        skills = extract_skills_from_text(text_content)
        print(f"🎯 Extracted {len(skills)} skills: {skills[:5]}...")
        
        # Extract years of experience
        years_exp = 5  # default
        year_matches = re.findall(r'(\d+)\+?\s*(?:years?|yrs?)', text_content.lower())
        if year_matches:
            years_exp = max([int(y) for y in year_matches])
        
        # Find matching jobs using ML model
        jobs = find_jobs_with_ml(text_content, max_jobs=5)
        print(f"🎯 Found {len(jobs)} matching jobs")
        
        # Live jobs
        live_jobs = [
            {'title': 'Senior Software Engineer', 'company': 'Stripe', 'location': 'San Francisco, CA', 'url': 'https://stripe.com/jobs', 'posted': '2 days ago'},
            {'title': 'React Developer', 'company': 'Shopify', 'location': 'Remote', 'url': 'https://shopify.com/careers', 'posted': '1 week ago'},
            {'title': 'Python Developer', 'company': 'Dropbox', 'location': 'San Francisco, CA', 'url': 'https://dropbox.com/jobs', 'posted': '3 days ago'},
            {'title': 'Full Stack Developer', 'company': 'Slack', 'location': 'San Francisco, CA', 'url': 'https://slack.com/careers', 'posted': '5 days ago'},
            {'title': 'DevOps Engineer', 'company': 'GitHub', 'location': 'Remote', 'url': 'https://github.com/careers', 'posted': '1 day ago'}
        ]
        
        # Prepare response data
        parsed = {
            'skills': skills,
            'years_experience': years_exp,
            'filename': filename if filename else None,
            'upload_type': upload_type,
            'text_length': len(text_content)
        }
        
        print(f"✅ Returning {len(jobs)} jobs and {len(live_jobs)} live jobs")
        
        response = jsonify({
            'success': True,
            'jobs': jobs,
            'live_jobs': live_jobs,
            'parsed': parsed,
            'total_matches': len(jobs),
            'message': f'Successfully processed {upload_type} upload'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        print(f"❌ Upload error: {e}")
        import traceback
        traceback.print_exc()
        
        error_response = jsonify({
            'success': False, 
            'error': str(e),
            'message': 'Failed to process upload. Please try again.'
        })
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500

# Load model on startup
print("🚀 Starting New Upload Server...")
if load_model_and_data():
    print("✅ Model and data loaded successfully")
else:
    print("⚠️ Running without ML model (fallback mode)")

if __name__ == '__main__':
    print("🌐 Server: http://localhost:5000")
    print("✅ CORS: Enabled for all origins")
    print("📝 Endpoints:")
    print("   - GET  /health")
    print("   - POST /recommend")
    print("   - POST /upload (NEW & IMPROVED)")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
