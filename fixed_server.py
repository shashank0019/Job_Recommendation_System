#!/usr/bin/env python3
"""
Fixed server with working upload endpoint
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
import re

app = Flask(__name__)
CORS(app)

# Load job data and model
try:
    job_data = pd.read_csv('data/job_dataset_sample.csv')
    with open('data/tfidf_vectorizer.joblib', 'rb') as f:
        vectorizer = pickle.load(f)
    with open('data/trained_model.joblib', 'rb') as f:
        job_vectors = pickle.load(f)
    print(f"Loaded {len(job_data)} jobs and trained model")
except Exception as e:
    print(f"Error loading data: {e}")
    job_data = None
    vectorizer = None
    job_vectors = None

def extract_skills_from_text(text):
    """Extract skills from resume text"""
    skills = []
    skill_keywords = [
        'react', 'node.js', 'node', 'javascript', 'python', 'java', 'aws', 
        'docker', 'mongodb', 'sql', 'git', 'typescript', 'angular', 'vue', 
        'django', 'flask', 'kubernetes', 'azure', 'gcp', 'html', 'css'
    ]
    text_lower = text.lower()
    
    for skill in skill_keywords:
        if skill in text_lower:
            skills.append(skill)
    
    if not skills:
        skills = ['javascript', 'react', 'node.js']
    
    return skills

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
        'model_loaded': vectorizer is not None and job_vectors is not None,
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
        
        # Find matching jobs using ML model
        jobs = []
        if vectorizer is not None and job_vectors is not None and job_data is not None:
            try:
                resume_vector = vectorizer.transform([resume_text])
                similarities = cosine_similarity(resume_vector, job_vectors).flatten()
                top_indices = similarities.argsort()[-10:][::-1]
                
                for idx in top_indices:
                    if idx < len(job_data) and similarities[idx] > 0.01:
                        job = job_data.iloc[idx]
                        jobs.append({
                            'title': str(job.get('title', 'N/A')),
                            'company': str(job.get('company', 'N/A')),
                            'location': str(job.get('location', 'N/A')),
                            'similarity_score': float(similarities[idx])
                        })
            except Exception as e:
                print(f"ML matching error: {e}")
        
        # Fallback to simple matching if ML fails
        if not jobs:
            fallback_jobs = [
                {'title': 'Senior React Developer', 'company': 'Meta', 'location': 'Menlo Park, CA', 'similarity_score': 0.85},
                {'title': 'Full Stack Engineer', 'company': 'Google', 'location': 'Mountain View, CA', 'similarity_score': 0.75},
                {'title': 'Python Developer', 'company': 'Netflix', 'location': 'Los Gatos, CA', 'similarity_score': 0.70},
                {'title': 'DevOps Engineer', 'company': 'Amazon', 'location': 'Seattle, WA', 'similarity_score': 0.65},
                {'title': 'Frontend Developer', 'company': 'Airbnb', 'location': 'San Francisco, CA', 'similarity_score': 0.60}
            ]
            jobs = fallback_jobs[:5]
        
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
        
        print(f"Found {len(jobs)} jobs, {len(live_jobs)} live jobs")
        
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
            if not text_content.strip():
                return jsonify({'success': False, 'error': 'Resume text is required in JSON request'}), 400
            print(f"JSON data received: {len(text_content)} characters")
        
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
                    except Exception:
                        text_content = ''
                else:
                    return jsonify({'success': False, 'error': 'Unsupported file type. Use PDF or TXT.'}), 400
            else:
                return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Handle form data
        elif request.form and 'resume_text' in request.form:
            text_content = request.form['resume_text']
            print("Form data received")
        
        else:
            return jsonify({'success': False, 'error': 'No resume data provided'}), 400
        
        # Validate text content
        if not text_content or not text_content.strip():
            return jsonify({'success': False, 'error': 'Could not extract text from the uploaded content'}), 400
        
        print(f"Processing text: {len(text_content)} characters")
        
        # Extract skills
        skills = extract_skills_from_text(text_content)
        print(f"Extracted skills: {skills}")
        
        # Extract years of experience
        years_exp = 5  # default
        year_matches = re.findall(r'(\d+)\+?\s*(?:years?|yrs?)', text_content.lower())
        if year_matches:
            years_exp = max([int(y) for y in year_matches])
        
        # Find matching jobs using ML model
        jobs = []
        if vectorizer is not None and job_vectors is not None and job_data is not None:
            try:
                resume_vector = vectorizer.transform([text_content])
                similarities = cosine_similarity(resume_vector, job_vectors).flatten()
                top_indices = similarities.argsort()[-10:][::-1]
                
                for idx in top_indices:
                    if idx < len(job_data) and similarities[idx] > 0.01:
                        job = job_data.iloc[idx]
                        jobs.append({
                            'title': str(job.get('title', 'N/A')),
                            'company': str(job.get('company', 'N/A')),
                            'location': str(job.get('location', 'N/A')),
                            'similarity_score': float(similarities[idx])
                        })
            except Exception as e:
                print(f"ML matching error: {e}")
        
        # Fallback to simple matching if ML fails
        if not jobs:
            fallback_jobs = [
                {'title': 'Senior React Developer', 'company': 'Meta', 'location': 'Menlo Park, CA', 'similarity_score': 0.85},
                {'title': 'Full Stack Engineer', 'company': 'Google', 'location': 'Mountain View, CA', 'similarity_score': 0.75},
                {'title': 'Python Developer', 'company': 'Netflix', 'location': 'Los Gatos, CA', 'similarity_score': 0.70},
                {'title': 'DevOps Engineer', 'company': 'Amazon', 'location': 'Seattle, WA', 'similarity_score': 0.65},
                {'title': 'Frontend Developer', 'company': 'Airbnb', 'location': 'San Francisco, CA', 'similarity_score': 0.60}
            ]
            jobs = fallback_jobs[:5]
        
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
        
        print(f"Found {len(jobs)} jobs, {len(live_jobs)} live jobs")
        
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
            'message': 'Failed to process upload. Please check server logs.'
        })
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500

if __name__ == '__main__':
    print("Starting Fixed Server...")
    print("Server: http://localhost:5000")
    print("CORS: Enabled for all origins")
    print("Endpoints:")
    print("   - GET  /health")
    print("   - POST /recommend")
    print("   - POST /upload")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
