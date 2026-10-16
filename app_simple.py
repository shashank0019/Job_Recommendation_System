#!/usr/bin/env python3
"""
Simplified Career Guidance Platform Flask Application

This version focuses on core functionality without complex dependencies.
"""

from flask import Flask, render_template_string, request, jsonify
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import os
import logging
from typing import List, Dict, Any
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class SimpleJobMatcher:
    """Simplified job matcher without spaCy dependencies."""
    
    def __init__(self):
        self.vectorizer = None
        self.job_data = None
        self.job_vectors = None
        self.is_trained = False
        self._load_model()
    
    def _load_model(self):
        """Load existing trained model if available."""
        try:
            if os.path.exists("data/tfidf_vectorizer.joblib"):
                self.vectorizer = joblib.load("data/tfidf_vectorizer.joblib")
                logger.info("Loaded existing TF-IDF vectorizer")
                
            if os.path.exists("data/trained_model.joblib"):
                self.job_vectors = joblib.load("data/trained_model.joblib")
                logger.info("Loaded existing job vectors")
                
            if os.path.exists("data/job_dataset_sample.csv"):
                self.job_data = pd.read_csv("data/job_dataset_sample.csv")
                logger.info("Loaded existing job dataset")
                
            if self.vectorizer is not None and self.job_vectors is not None:
                self.is_trained = True
                logger.info("Model is ready for job matching")
                
        except Exception as e:
            logger.warning(f"Could not load existing model: {e}")
            self.is_trained = False
    
    def extract_skills_simple(self, text: str) -> List[str]:
        """Simple skill extraction without spaCy."""
        # Common technical skills
        technical_skills = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js',
            'django', 'flask', 'spring', 'sql', 'mysql', 'postgresql', 'mongodb',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'jenkins',
            'machine learning', 'ai', 'data science', 'analytics', 'agile',
            'scrum', 'project management', 'leadership', 'communication'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in technical_skills:
            if skill in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def find_matching_jobs(self, resume_text: str, top_k: int = 10, 
                          min_similarity: float = 0.05) -> List[Dict[str, Any]]:
        """Find matching jobs using TF-IDF and cosine similarity."""
        if not self.is_trained:
            logger.error("Model must be trained before finding matches")
            return []
        
        try:
            # Vectorize the resume
            resume_vector = self.vectorizer.transform([resume_text])
            
            # Calculate similarities with all jobs
            similarities = cosine_similarity(resume_vector, self.job_vectors).flatten()
            
            # Create list of (job_index, similarity_score) tuples
            job_scores = list(enumerate(similarities))
            
            # Sort by similarity score (descending)
            job_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Filter by minimum similarity and get top k
            matching_jobs = []
            for job_idx, score in job_scores:
                if score >= min_similarity and len(matching_jobs) < top_k:
                    job_info = self.job_data.iloc[job_idx].to_dict()
                    job_info['similarity_score'] = round(score, 4)
                    job_info['job_index'] = job_idx
                    matching_jobs.append(job_info)
            
            logger.info(f"Found {len(matching_jobs)} matching jobs")
            return matching_jobs
            
        except Exception as e:
            logger.error(f"Error finding matching jobs: {e}")
            return []

# Initialize the job matcher
job_matcher = SimpleJobMatcher()

@app.route('/')
def index():
    """Main page with a simple form."""
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Career Guidance Platform</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            .header h1 {
                margin: 0;
                font-size: 2.5em;
                font-weight: 300;
            }
            .header p {
                margin: 10px 0 0 0;
                opacity: 0.9;
                font-size: 1.1em;
            }
            .content {
                padding: 40px;
            }
            .form-group {
                margin-bottom: 25px;
            }
            label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #555;
            }
            textarea {
                width: 100%;
                height: 200px;
                padding: 15px;
                border: 2px solid #e1e5e9;
                border-radius: 8px;
                font-size: 16px;
                font-family: inherit;
                resize: vertical;
                transition: border-color 0.3s ease;
            }
            textarea:focus {
                outline: none;
                border-color: #667eea;
            }
            .btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 15px 30px;
                font-size: 16px;
                border-radius: 8px;
                cursor: pointer;
                transition: transform 0.2s ease;
                font-weight: 600;
            }
            .btn:hover {
                transform: translateY(-2px);
            }
            .btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            .results {
                margin-top: 30px;
                display: none;
            }
            .job-card {
                background: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
                border-left: 4px solid #667eea;
            }
            .job-title {
                font-size: 1.3em;
                font-weight: 600;
                color: #333;
                margin-bottom: 10px;
            }
            .job-company {
                color: #667eea;
                font-weight: 500;
                margin-bottom: 8px;
            }
            .job-location {
                color: #666;
                margin-bottom: 15px;
            }
            .job-description {
                color: #555;
                line-height: 1.6;
                margin-bottom: 15px;
            }
            .job-similarity {
                background: #667eea;
                color: white;
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 0.9em;
                font-weight: 500;
            }
            .loading {
                text-align: center;
                padding: 20px;
                color: #666;
            }
            .error {
                background: #fee;
                color: #c33;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #c33;
                margin-top: 20px;
            }
            .stats {
                background: #f0f4ff;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 30px;
                text-align: center;
            }
            .stats h3 {
                margin: 0 0 15px 0;
                color: #667eea;
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
            }
            .stat-item {
                background: white;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .stat-number {
                font-size: 1.5em;
                font-weight: 600;
                color: #667eea;
            }
            .stat-label {
                color: #666;
                font-size: 0.9em;
                margin-top: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Career Guidance Platform</h1>
                <p>AI-Powered Job Matching with Real Job Data</p>
            </div>
            
            <div class="content">
                <div class="stats">
                    <h3>📊 Platform Statistics</h3>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-number">1,000+</div>
                            <div class="stat-label">Real Jobs</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">800+</div>
                            <div class="stat-label">Companies</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">500+</div>
                            <div class="stat-label">Locations</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">AI</div>
                            <div class="stat-label">Powered</div>
                        </div>
                    </div>
                </div>
                
                <form id="resumeForm">
                    <div class="form-group">
                        <label for="resumeText">📝 Paste Your Resume or Job Description:</label>
                        <textarea 
                            id="resumeText" 
                            name="resumeText" 
                            placeholder="Paste your resume text here... Include your skills, experience, and what you're looking for in a job."
                            required
                        ></textarea>
                    </div>
                    
                    <button type="submit" class="btn" id="submitBtn">
                        🔍 Find Matching Jobs
                    </button>
                </form>
                
                <div id="loading" class="loading" style="display: none;">
                    🤖 AI is analyzing your resume and finding the best job matches...
                </div>
                
                <div id="results" class="results">
                    <h3>🎯 Your Job Matches</h3>
                    <div id="jobResults"></div>
                </div>
                
                <div id="error" class="error" style="display: none;"></div>
            </div>
        </div>
        
        <script>
            document.getElementById('resumeForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const resumeText = document.getElementById('resumeText').value.trim();
                if (!resumeText) {
                    alert('Please enter your resume text');
                    return;
                }
                
                // Show loading
                document.getElementById('loading').style.display = 'block';
                document.getElementById('results').style.display = 'none';
                document.getElementById('error').style.display = 'none';
                document.getElementById('submitBtn').disabled = true;
                
                try {
                    const response = await fetch('/recommend', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ resume_text: resumeText })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        displayResults(data.jobs);
                    } else {
                        showError(data.error || 'An error occurred while processing your request');
                    }
                } catch (error) {
                    showError('Network error. Please try again.');
                } finally {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('submitBtn').disabled = false;
                }
            });
            
            function displayResults(jobs) {
                const resultsDiv = document.getElementById('results');
                const jobResultsDiv = document.getElementById('jobResults');
                
                if (jobs.length === 0) {
                    jobResultsDiv.innerHTML = '<p>No matching jobs found. Try adjusting your resume text or skills.</p>';
                } else {
                    jobResultsDiv.innerHTML = jobs.map((job, index) => `
                        <div class="job-card">
                            <div class="job-title">${job.title || 'Job Title'}</div>
                            <div class="job-company">🏢 ${job.company || 'Company'}</div>
                            <div class="job-location">📍 ${job.location || 'Location'}</div>
                            <div class="job-description">${job.description ? job.description.substring(0, 200) + '...' : 'No description available'}</div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span class="job-similarity">Match: ${(job.similarity_score * 100).toFixed(1)}%</span>
                                ${job.skills ? `<small style="color: #666;">Skills: ${job.skills}</small>` : ''}
                            </div>
                        </div>
                    `).join('');
                }
                
                resultsDiv.style.display = 'block';
            }
            
            function showError(message) {
                const errorDiv = document.getElementById('error');
                errorDiv.textContent = message;
                errorDiv.style.display = 'block';
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/recommend', methods=['POST'])
def recommend_jobs():
    """API endpoint for job recommendations."""
    try:
        data = request.get_json()
        resume_text = data.get('resume_text', '')
        
        if not resume_text:
            return jsonify({'success': False, 'error': 'Resume text is required'})
        
        # Find matching jobs
        matching_jobs = job_matcher.find_matching_jobs(resume_text, top_k=5, min_similarity=0.05)
        
        if not matching_jobs:
            return jsonify({'success': False, 'error': 'No matching jobs found'})
        
        # Format jobs for response
        jobs = []
        for job in matching_jobs:
            jobs.append({
                'title': job.get('title', 'N/A'),
                'company': job.get('company', 'N/A'),
                'location': job.get('location', 'N/A'),
                'description': job.get('description', 'N/A'),
                'skills': job.get('skills', 'N/A'),
                'similarity_score': job.get('similarity_score', 0.0)
            })
        
        return jsonify({
            'success': True,
            'jobs': jobs,
            'total_matches': len(jobs)
        })
        
    except Exception as e:
        logger.error(f"Error in recommend endpoint: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'model_trained': job_matcher.is_trained,
        'total_jobs': len(job_matcher.job_data) if job_matcher.job_data is not None else 0
    })

if __name__ == '__main__':
    logger.info("Starting Career Guidance Platform on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=True) 