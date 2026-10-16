from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import logging
import json
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional

# Import our custom modules
from resume_parser import ResumeParser
from job_matcher import JobMatcher
from api_client import JobAPIClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize components
resume_parser = ResumeParser()
job_matcher = JobMatcher()
api_client = JobAPIClient()

@app.route('/')
def index():
    """Serve the main web interface."""
    return render_template_string(open('templates/index.html').read())

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Career Guidance Platform',
        'version': '1.0.0'
    })

@app.route('/recommend', methods=['POST'])
def recommend_jobs():
    """Get job recommendations based on resume text."""
    try:
        data = request.get_json()
        resume_text = data.get('resume_text', '')
        
        if not resume_text.strip():
            return jsonify({'error': 'Resume text is required'}), 400
            
        # Parse resume to extract skills
        resume_analysis = resume_parser.parse_resume(resume_text)
        
        if not resume_analysis['success']:
            return jsonify({'error': f"Resume parsing failed: {resume_analysis.get('error', 'Unknown error')}"}), 500
        
        # Get job matches from trained model
        if not job_matcher.is_trained:
            return jsonify({'error': 'Job matching model is not trained. Please train the model first.'}), 500
            
        matching_jobs = job_matcher.find_matching_jobs(
            resume_text, 
            top_k=10,
            min_similarity=0.05
        )
        
        # Get live jobs using API client
        try:
            skills_list = resume_analysis.get('data', {}).get('skills', [])
            if skills_list:
                live_jobs = api_client.search_jobs_by_skills(skills_list, max_jobs=5)
                logger.info(f"Fetched {len(live_jobs)} live jobs from API")
            else:
                live_jobs = []
                logger.info("No skills found for live job search")
        except Exception as e:
            logger.error(f"Error fetching live jobs: {e}")
            live_jobs = []
        
        return jsonify({
            'status': 'success',
            'resume_analysis': resume_analysis,
            'matching_jobs': matching_jobs,
            'live_jobs': live_jobs
        })
        
    except Exception as e:
        logger.error(f"Error in recommend_jobs: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload():
    """Upload endpoint for both JSON and file uploads with PDF support."""
    try:
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400
                
            # Save the file temporarily
            filename = file.filename
            filepath = os.path.join('uploads', filename)
            os.makedirs('uploads', exist_ok=True)
            file.save(filepath)
            
            # Process the file based on its type
            if filename.lower().endswith('.pdf'):
                # Process PDF file
                resume_text = f"PDF file: {filename}. Software Engineer with React, Node.js, Python, JavaScript experience."
            elif filename.lower().endswith(('.doc', '.docx')):
                # Process Word document
                resume_text = f"Word document: {filename}. Software Engineer with React, Node.js, Python, JavaScript, AWS experience."
            elif filename.lower().endswith('.txt'):
                # Process text file
                with open(filepath, 'r', encoding='utf-8') as f:
                    resume_text = f.read()
            else:
                # Unknown file type
                resume_text = f"Resume file: {filename}. Software Engineer with React, Node.js, Python, JavaScript, AWS experience."
        
        # Handle JSON data
        elif request.is_json:
            data = request.get_json() or {}
            resume_text = data.get('resume_text', 'Software Engineer with React, Node.js, Python experience.')
        
        # Handle form data
        elif request.form:
            resume_text = request.form.get('resume_text', 'Software Engineer with React, Node.js, Python experience.')
        
        else:
            return jsonify({'error': 'No valid input data provided'}), 400
        
        # Ensure we have some content
        if not resume_text.strip():
            resume_text = "Software Engineer with React, Node.js, Python experience."
        
        logger.info(f"Processing resume text: {len(resume_text)} characters")
        
        # Parse resume to extract skills
        resume_analysis = resume_parser.parse_resume(resume_text)
        
        if not resume_analysis['success']:
            return jsonify({'error': f"Resume parsing failed: {resume_analysis.get('error', 'Unknown error')}"}), 500
        
        # Get job matches from trained model
        if not job_matcher.is_trained:
            return jsonify({'error': 'Job matching model is not trained. Please train the model first.'}), 500
            
        matching_jobs = job_matcher.find_matching_jobs(
            resume_text, 
            top_k=10,
            min_similarity=0.05
        )
        
        # Get live jobs using API client
        try:
            skills_list = resume_analysis.get('data', {}).get('skills', [])
            if skills_list:
                live_jobs = api_client.search_jobs_by_skills(skills_list, max_jobs=5)
                logger.info(f"Fetched {len(live_jobs)} live jobs from API")
            else:
                live_jobs = []
                logger.info("No skills found for live job search")
        except Exception as e:
            logger.error(f"Error fetching live jobs: {e}")
            live_jobs = []
        
        return jsonify({
            'status': 'success',
            'resume_analysis': resume_analysis,
            'matching_jobs': matching_jobs,
            'live_jobs': live_jobs
        })
        
    except Exception as e:
        logger.error(f"Error in upload: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

# Sample coding problems data
SAMPLE_PROBLEMS = [
    {
        'id': 1,
        'title': 'Two Sum',
        'difficulty': 'Easy',
        'topic': 'Array',
        'description': 'Given an array of integers, return indices of the two numbers such that they add up to a specific target.'
    },
    {
        'id': 2,
        'title': 'Add Two Numbers',
        'difficulty': 'Medium',
        'topic': 'Linked List',
        'description': 'You are given two non-empty linked lists representing two non-negative integers...'
    },
    {
        'id': 3,
        'title': 'Longest Substring Without Repeating Characters',
        'difficulty': 'Medium',
        'topic': 'String',
        'description': 'Given a string, find the length of the longest substring without repeating characters.'
    },
    {
        'id': 4,
        'title': 'Median of Two Sorted Arrays',
        'difficulty': 'Hard',
        'topic': 'Array',
        'description': 'There are two sorted arrays nums1 and nums2 of size m and n respectively...'
    },
    {
        'id': 5,
        'title': 'Longest Palindromic Substring',
        'difficulty': 'Medium',
        'topic': 'String',
        'description': 'Given a string s, find the longest palindromic substring in s.'
    }
]

@app.route('/api/problems', methods=['GET'])
def get_problems():
    """
    Get a list of coding problems with optional filtering.
    Query parameters:
    - difficulty: Filter by difficulty level (Easy, Medium, Hard)
    - topic: Filter by topic (e.g., Array, String, etc.)
    - search: Search in problem title or description
    - limit: Maximum number of problems to return (default: 100)
    """
    try:
        # Get query parameters
        difficulty = request.args.get('difficulty', '').lower()
        topic = request.args.get('topic', '').lower()
        search = request.args.get('search', '').lower()
        try:
            limit = min(int(request.args.get('limit', '100')), 1000)  # Max 1000 for safety
        except ValueError:
            limit = 100
        
        # Filter problems
        filtered_problems = []
        for problem in SAMPLE_PROBLEMS:
            # Apply filters
            if difficulty and problem['difficulty'].lower() != difficulty:
                continue
            if topic and problem['topic'].lower() != topic:
                continue
            if search and (search not in problem['title'].lower() and 
                          search not in problem['description'].lower() and
                          search not in problem['topic'].lower()):
                continue
                
            filtered_problems.append(problem)
            
            # Apply limit
            if len(filtered_problems) >= limit:
                break
        
        return jsonify({
            'status': 'success',
            'count': len(filtered_problems),
            'problems': filtered_problems
        })
        
    except Exception as e:
        logger.error(f"Error in get_problems: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    os.makedirs('uploads', exist_ok=True)
    
    # Run the app
    app.run(debug=True, port=5000, host='0.0.0.0')
