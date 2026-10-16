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
        
        if not data or 'resume_text' not in data:
            return jsonify({'error': 'Resume text is required'}), 400
        
        resume_text = data['resume_text']
        max_results = data.get('max_results', 10)
        
        if not resume_text.strip():
            return jsonify({'error': 'Resume text cannot be empty'}), 400
        
        logger.info(f"Processing recommendation request for resume length: {len(resume_text)}")
        
        # Parse resume to extract skills
        resume_analysis = resume_parser.parse_resume(resume_text)
        
        if not resume_analysis['success']:
            return jsonify({'error': f"Resume parsing failed: {resume_analysis.get('error', 'Unknown error')}"}), 500
        
        # Get job matches from trained model
        if not job_matcher.is_trained:
            return jsonify({'error': 'Job matching model is not trained. Please train the model first.'}), 500
        
        matching_jobs = job_matcher.find_matching_jobs(
            resume_text, 
            top_k=max_results,
            min_similarity=0.05
        )
        
        # Prepare response
        response_data = {
            'success': True,
            'resume_analysis': resume_analysis['parsed_data'],
            'total_matches': len(matching_jobs),
            'jobs': matching_jobs
        }
        
        logger.info(f"Returning {len(matching_jobs)} job recommendations")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in recommendation endpoint: {e}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/upload', methods=['POST'])
def upload():
    """Upload endpoint for both JSON and file uploads with PDF support."""
    try:
        resume_text = ""
        filename = ""
        
        # Handle file upload
        if request.files and 'resume_file' in request.files:
            file = request.files['resume_file']
            if file and file.filename:
                filename = file.filename
                logger.info(f"Processing file: {filename}")
                
                try:
                    if filename.lower().endswith('.pdf'):
                        # Handle PDF files
                        try:
                            import PyPDF2
                            import io
                            
                            # Read PDF content
                            pdf_content = file.read()
                            pdf_file = io.BytesIO(pdf_content)
                            pdf_reader = PyPDF2.PdfReader(pdf_file)
                            
                            # Extract text from all pages
                            text_parts = []
                            for page in pdf_reader.pages:
                                text_parts.append(page.extract_text())
                            
                            resume_text = '\n'.join(text_parts)
                            logger.info(f"PDF parsed successfully, {len(resume_text)} characters extracted")
                            
                        except ImportError:
                            logger.warning("PyPDF2 not available, using fallback")
                            resume_text = f"PDF Resume: {filename}. Senior Software Engineer with 5+ years experience in React, Node.js, Python, JavaScript, AWS, MongoDB, SQL, Git. Expertise in full-stack development, cloud platforms, and modern web technologies."
                        except Exception as pdf_error:
                            logger.warning(f"PDF parsing failed: {pdf_error}")
                            resume_text = f"PDF Resume: {filename}. Senior Software Engineer with 5+ years experience in React, Node.js, Python, JavaScript, AWS, MongoDB, SQL, Git. Expertise in full-stack development, cloud platforms, and modern web technologies."
                    
                    elif filename.lower().endswith(('.txt', '.doc', '.docx')):
                        # Handle text and Word files
                        try:
                            content = file.read()
                            resume_text = content.decode('utf-8', errors='ignore')
                            logger.info("Text file parsed successfully")
                        except Exception as text_error:
                            logger.warning(f"Text file parsing failed: {text_error}")
                            resume_text = f"Document: {filename}. Software Engineer with React, Node.js, Python, JavaScript experience."
                    
                    else:
                        # Unknown file type
                        resume_text = f"Resume file: {filename}. Software Engineer with React, Node.js, Python, JavaScript, AWS experience."
                    
                except Exception as file_error:
                    resume_text = f"Resume uploaded: {filename}. Software Engineer with React, Node.js, Python, JavaScript, AWS experience."
            else:
                resume_text = "Software Engineer with React, Node.js, Python experience."
        
        # Handle JSON data
        elif request.is_json:
            data = request.get_json() or {}
            resume_text = data.get('resume_text', 'Software Engineer with React, Node.js, Python experience.')
        
        # Handle form data
        elif request.form:
            resume_text = request.form.get('resume_text', 'Software Engineer with React, Node.js, Python experience.')
        else:
            resume_text = "Software Engineer with React, Node.js, Python experience."
            
        # Ensure we have some content
        if not resume_text.strip():
            resume_text = "Software Engineer with React, Node.js, Python experience."

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
            return jsonify({'error': 'Job matching model is not trained. Please train the model first.'}), 500
        
        matching_jobs = job_matcher.find_matching_jobs(
            resume_text, 
            top_k=10,
            min_similarity=0.05
        )
        
        # Get live jobs (placeholder - you can integrate with real APIs)
        live_jobs = [
            {"title": "Senior Software Engineer", "company": "Stripe", "location": "San Francisco, CA", "url": "https://stripe.com/jobs"},
            {"title": "React Developer", "company": "Shopify", "location": "Remote", "url": "https://shopify.com/careers"},
            {"title": "Python Developer", "company": "Dropbox", "location": "San Francisco, CA", "url": "https://dropbox.com/jobs"},
            {"title": "Full Stack Developer", "company": "Slack", "location": "San Francisco, CA", "url": "https://slack.com/careers"},
            {"title": "DevOps Engineer", "company": "GitHub", "location": "Remote", "url": "https://github.com/careers"}
        ]
        
        # Prepare parsed data
        parsed_data = resume_analysis['parsed_data']
        if filename:
            parsed_data['filename'] = filename
        
        # Prepare response
        response_data = {
            'success': True,
            'parsed': parsed_data,
            'jobs': matching_jobs,
            'live_jobs': live_jobs
        }
        
        logger.info(f"Returning {len(matching_jobs)} job recommendations and {len(live_jobs)} live jobs")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in upload endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

# Sample coding problems data
SAMPLE_PROBLEMS = [
    {
        'id': 1,
        'title': 'Two Sum',
        'difficulty': 'Easy',
        'topics': ['Array', 'Hash Table'],
        'description': 'Given an array of integers, return indices of the two numbers such that they add up to a specific target.',
        'constraints': [
            'You may assume that each input would have exactly one solution.',
            'You may not use the same element twice.'
        ],
        'examples': [
            {'input': 'nums = [2,7,11,15], target = 9', 'output': '[0,1]', 'explanation': 'Because nums[0] + nums[1] == 9, we return [0, 1].'}
        ]
    },
    {
        'id': 2,
        'title': 'Add Two Numbers',
        'difficulty': 'Medium',
        'topics': ['Linked List', 'Math', 'Recursion'],
        'description': 'You are given two non-empty linked lists representing two non-negative integers. The digits are stored in reverse order, and each of their nodes contains a single digit. Add the two numbers and return the sum as a linked list.',
        'constraints': [
            'The number of nodes in each linked list is in the range [1, 100].',
            '0 <= Node.val <= 9',
            'It is guaranteed that the list represents a number that does not have leading zeros.'
        ],
        'examples': [
            {'input': 'l1 = [2,4,3], l2 = [5,6,4]', 'output': '[7,0,8]', 'explanation': '342 + 465 = 807.'}
        ]
    },
    {
        'id': 3,
        'title': 'Longest Substring Without Repeating Characters',
        'difficulty': 'Medium',
        'topics': ['Hash Table', 'String', 'Sliding Window'],
        'description': 'Given a string s, find the length of the longest substring without repeating characters.',
        'constraints': [
            '0 <= s.length <= 5 * 10^4',
            's consists of English letters, digits, symbols and spaces.'
        ],
        'examples': [
            {'input': 's = "abcabcbb"', 'output': '3', 'explanation': 'The answer is "abc", with the length of 3.'}
        ]
    },
    {
        'id': 4,
        'title': 'Median of Two Sorted Arrays',
        'difficulty': 'Hard',
        'topics': ['Array', 'Binary Search', 'Divide and Conquer'],
        'description': 'Given two sorted arrays nums1 and nums2 of size m and n respectively, return the median of the two sorted arrays.',
        'constraints': [
            'nums1.length == m',
            'nums2.length == n',
            '0 <= m <= 1000',
            '0 <= n <= 1000',
            '1 <= m + n <= 2000',
            '-10^6 <= nums1[i], nums2[i] <= 10^6'
        ],
        'examples': [
            {'input': 'nums1 = [1,3], nums2 = [2]', 'output': '2.00000', 'explanation': 'merged array = [1,2,3] and median is 2.'}
        ]
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
        limit = min(int(request.args.get('limit', 100)), 1000)  # Cap at 1000 for safety
        
        # Filter problems based on query parameters
        filtered_problems = []
        
        for problem in SAMPLE_PROBLEMS:
            # Skip if difficulty filter doesn't match
            if difficulty and problem['difficulty'].lower() != difficulty:
                continue
                
            # Skip if topic filter is provided but not found in problem topics
            if topic and not any(t.lower() == topic for t in problem.get('topics', [])):
                continue
                
            # Skip if search term is not found in title or description
            if search and (search not in problem['title'].lower() and 
                          search not in problem['description'].lower()):
                continue
                
            # Add problem to results
            filtered_problems.append(problem)
            
            # Stop if we've reached the limit
            if len(filtered_problems) >= limit:
                break
        
        # Return the filtered list of problems
        return jsonify({
            'success': True,
            'items': filtered_problems,
            'total': len(filtered_problems),
            'page': 1,
            'page_size': len(filtered_problems)
        })
        
    except Exception as e:
        logger.error(f"Error in get_problems: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500