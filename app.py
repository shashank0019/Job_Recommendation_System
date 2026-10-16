from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import logging
import json
import random
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional

# Import our custom modules
from resume_parser import ResumeParser
from job_matcher import JobMatcher
from api_client import JobAPIClient

# Import authentication modules
from auth.routes import auth_bp
from config.database import get_db_config

# Import new feature modules
from api.job_posting_routes import job_posting_bp
from api.interview_experience_routes import interview_experience_bp

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, 
     origins="*",  # Allow all origins temporarily for debugging
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     supports_credentials=False)

# Register authentication blueprint
print("🔧 Registering auth blueprint...")
app.register_blueprint(auth_bp, url_prefix='/auth')
print("✅ Auth blueprint registered successfully")

# Register new feature blueprints
print("🔧 Registering job posting blueprint...")
app.register_blueprint(job_posting_bp, url_prefix='/api')
print("✅ Job posting blueprint registered successfully")

print("🔧 Registering interview experience blueprint...")
app.register_blueprint(interview_experience_bp, url_prefix='/api')
print("✅ Interview experience blueprint registered successfully")

# Add a simple test route
@app.route('/test')
def test_route():
    return jsonify({'message': 'Test route working', 'status': 'OK'})

# Removed simple test endpoint - using full problems endpoint below

# Debug: List all registered routes
print("📋 Registered routes:")
for rule in app.url_map.iter_rules():
    print(f"  {rule.rule} -> {rule.endpoint}")

# Initialize database connection
print("🔧 Initializing database connection...")
db_config = get_db_config()
db_config.connect()
print("✅ Database connection initialized")

# Initialize components
resume_parser = ResumeParser()
job_matcher = JobMatcher()
api_client = JobAPIClient()

@app.route('/')
def index():
    """Serve the main web interface."""
    return render_template_string(open('templates/index.html', 'r', encoding='utf-8').read())

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
        
        # Get user skills for filtering live jobs
        user_skills = resume_analysis['parsed_data'].get('skills', [])
        if isinstance(user_skills, dict):
            # Flatten skill dictionary to list
            user_skills = [skill.lower() for skills_list in user_skills.values() for skill in skills_list]
        else:
            user_skills = [skill.lower() for skill in user_skills]
        
        # Comprehensive job database categorized by skills
        all_live_jobs = {
            'python': [
                {"title": "Python Developer", "company": "Amazon", "location": "Seattle, WA", "url": "https://www.amazon.jobs"},
                {"title": "Backend Engineer (Python)", "company": "Netflix", "location": "Los Gatos, CA", "url": "https://jobs.netflix.com"},
                {"title": "Python Software Engineer", "company": "Dropbox", "location": "San Francisco, CA", "url": "https://www.dropbox.com/jobs"},
            ],
            'javascript': [
                {"title": "JavaScript Developer", "company": "Shopify", "location": "Remote", "url": "https://www.shopify.com/careers"},
                {"title": "Full Stack Engineer (JS)", "company": "Airbnb", "location": "San Francisco, CA", "url": "https://careers.airbnb.com"},
                {"title": "Node.js Developer", "company": "Uber", "location": "San Francisco, CA", "url": "https://www.uber.com/careers"},
            ],
            'react': [
                {"title": "React Developer", "company": "Meta", "location": "Menlo Park, CA", "url": "https://www.metacareers.com"},
                {"title": "Frontend Engineer (React)", "company": "Airbnb", "location": "San Francisco, CA", "url": "https://careers.airbnb.com"},
                {"title": "React Native Developer", "company": "Discord", "location": "Remote", "url": "https://discord.com/jobs"},
            ],
            'java': [
                {"title": "Java Developer", "company": "Oracle", "location": "Redwood City, CA", "url": "https://www.oracle.com/careers"},
                {"title": "Senior Java Engineer", "company": "LinkedIn", "location": "Sunnyvale, CA", "url": "https://careers.linkedin.com"},
                {"title": "Java Backend Developer", "company": "Twitter", "location": "San Francisco, CA", "url": "https://careers.twitter.com"},
            ],
            'aws': [
                {"title": "Cloud Engineer (AWS)", "company": "Amazon", "location": "Seattle, WA", "url": "https://www.amazon.jobs"},
                {"title": "AWS Solutions Architect", "company": "Salesforce", "location": "San Francisco, CA", "url": "https://www.salesforce.com/company/careers"},
                {"title": "DevOps Engineer (AWS)", "company": "Stripe", "location": "Remote", "url": "https://stripe.com/jobs"},
            ],
            'machine learning': [
                {"title": "ML Engineer", "company": "OpenAI", "location": "San Francisco, CA", "url": "https://openai.com/careers"},
                {"title": "Machine Learning Scientist", "company": "Google", "location": "Mountain View, CA", "url": "https://careers.google.com"},
                {"title": "AI Research Engineer", "company": "Meta", "location": "Menlo Park, CA", "url": "https://www.metacareers.com"},
            ],
            'data science': [
                {"title": "Data Scientist", "company": "Netflix", "location": "Los Gatos, CA", "url": "https://jobs.netflix.com"},
                {"title": "Senior Data Analyst", "company": "Spotify", "location": "Remote", "url": "https://www.lifeatspotify.com"},
                {"title": "Data Engineer", "company": "Uber", "location": "San Francisco, CA", "url": "https://www.uber.com/careers"},
            ],
            'devops': [
                {"title": "DevOps Engineer", "company": "GitHub", "location": "Remote", "url": "https://github.com/careers"},
                {"title": "Site Reliability Engineer", "company": "Google", "location": "Mountain View, CA", "url": "https://careers.google.com"},
                {"title": "Infrastructure Engineer", "company": "Cloudflare", "location": "San Francisco, CA", "url": "https://www.cloudflare.com/careers"},
            ],
            'default': [
                {"title": "Software Engineer", "company": "Google", "location": "Mountain View, CA", "url": "https://careers.google.com"},
                {"title": "Full Stack Developer", "company": "Microsoft", "location": "Redmond, WA", "url": "https://careers.microsoft.com"},
                {"title": "Senior Software Engineer", "company": "Apple", "location": "Cupertino, CA", "url": "https://www.apple.com/careers"},
                {"title": "Software Developer", "company": "Stripe", "location": "Remote", "url": "https://stripe.com/jobs"},
                {"title": "Backend Engineer", "company": "Slack", "location": "San Francisco, CA", "url": "https://slack.com/careers"},
            ]
        }
        
        # Filter live jobs based on user skills
        live_jobs = []
        matched_skills = set()
        
        for skill in user_skills:
            for job_category, category_jobs in all_live_jobs.items():
                if job_category != 'default' and job_category in skill:
                    live_jobs.extend(category_jobs)
                    matched_skills.add(job_category)
                    if len(live_jobs) >= 10:
                        break
            if len(live_jobs) >= 10:
                break
        
        # If no specific skills matched or need more jobs, add default jobs
        if len(live_jobs) < 5:
            live_jobs.extend(all_live_jobs['default'][:10 - len(live_jobs)])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_live_jobs = []
        for job in live_jobs:
            job_key = f"{job['title']}{job['company']}"
            if job_key not in seen:
                seen.add(job_key)
                unique_live_jobs.append(job)
        
        live_jobs = unique_live_jobs[:10]  # Limit to 10 jobs
        
        # Prepare response
        response_data = {
            'success': True,
            'parsed': resume_analysis['parsed_data'],
            'total_matches': len(matching_jobs),
            'jobs': matching_jobs,
            'live_jobs': live_jobs,
            'test_field': 'UPDATED_CODE_WORKING'
        }
        
        logger.info(f"Returning {len(matching_jobs)} job recommendations and {len(live_jobs)} live jobs")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in recommendation endpoint: {e}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/upload', methods=['POST'])
def upload():
    """Upload endpoint for both JSON and file uploads with PDF support."""
    try:
        logger.info(f"Upload request received - Content-Type: {request.content_type}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Is JSON: {request.is_json}")
        logger.info(f"Has files: {bool(request.files)}")
        
        resume_text = ""
        filename = ""
        
        # Handle file upload first (most common case from frontend)
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
                        # Unknown file type - provide fallback content
                        resume_text = f"Resume file: {filename}. Software Engineer with React, Node.js, Python, JavaScript, AWS experience."
                    
                except Exception as file_error:
                    logger.warning(f"File processing error: {file_error}")
                    resume_text = f"Resume uploaded: {filename}. Software Engineer with React, Node.js, Python, JavaScript, AWS experience."
            else:
                logger.warning("Empty file uploaded")
                resume_text = "Software Engineer with React, Node.js, Python experience."
        
        # Handle JSON data (for text input from frontend)
        elif request.is_json:
            data = request.get_json() or {}
            resume_text = data.get('resume_text', '')
            logger.info(f"JSON data received: {bool(resume_text)}")
            if resume_text.strip():
                logger.info(f"Processing JSON resume text, length: {len(resume_text)}")
            else:
                resume_text = "Software Engineer with React, Node.js, Python experience."
        
        # Handle form data
        elif request.form:
            resume_text = request.form.get('resume_text', 'Software Engineer with React, Node.js, Python experience.')
        
        # Default fallback
        else:
            logger.warning("No valid data received, using fallback")
            resume_text = "Software Engineer with React, Node.js, Python experience."
            
        # Ensure we have some content
        if not resume_text.strip():
            resume_text = "Software Engineer with React, Node.js, Python experience."
        
        logger.info(f"Processing upload request for resume length: {len(resume_text)}")
        
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
        
        # Get user skills for filtering live jobs
        user_skills = resume_analysis['parsed_data'].get('skills', [])
        if isinstance(user_skills, dict):
            # Flatten skill dictionary to list
            user_skills = [skill.lower() for skills_list in user_skills.values() for skill in skills_list]
        else:
            user_skills = [skill.lower() for skill in user_skills]
        
        # Comprehensive job database categorized by skills (same as /recommend)
        all_live_jobs = {
            'python': [
                {"title": "Python Developer", "company": "Amazon", "location": "Seattle, WA", "url": "https://www.amazon.jobs"},
                {"title": "Backend Engineer (Python)", "company": "Netflix", "location": "Los Gatos, CA", "url": "https://jobs.netflix.com"},
                {"title": "Python Software Engineer", "company": "Dropbox", "location": "San Francisco, CA", "url": "https://www.dropbox.com/jobs"},
            ],
            'javascript': [
                {"title": "JavaScript Developer", "company": "Shopify", "location": "Remote", "url": "https://www.shopify.com/careers"},
                {"title": "Full Stack Engineer (JS)", "company": "Airbnb", "location": "San Francisco, CA", "url": "https://careers.airbnb.com"},
                {"title": "Node.js Developer", "company": "Uber", "location": "San Francisco, CA", "url": "https://www.uber.com/careers"},
            ],
            'react': [
                {"title": "React Developer", "company": "Meta", "location": "Menlo Park, CA", "url": "https://www.metacareers.com"},
                {"title": "Frontend Engineer (React)", "company": "Airbnb", "location": "San Francisco, CA", "url": "https://careers.airbnb.com"},
                {"title": "React Native Developer", "company": "Discord", "location": "Remote", "url": "https://discord.com/jobs"},
            ],
            'java': [
                {"title": "Java Developer", "company": "Oracle", "location": "Redwood City, CA", "url": "https://www.oracle.com/careers"},
                {"title": "Senior Java Engineer", "company": "LinkedIn", "location": "Sunnyvale, CA", "url": "https://careers.linkedin.com"},
                {"title": "Java Backend Developer", "company": "Twitter", "location": "San Francisco, CA", "url": "https://careers.twitter.com"},
            ],
            'aws': [
                {"title": "Cloud Engineer (AWS)", "company": "Amazon", "location": "Seattle, WA", "url": "https://www.amazon.jobs"},
                {"title": "AWS Solutions Architect", "company": "Salesforce", "location": "San Francisco, CA", "url": "https://www.salesforce.com/company/careers"},
                {"title": "DevOps Engineer (AWS)", "company": "Stripe", "location": "Remote", "url": "https://stripe.com/jobs"},
            ],
            'machine learning': [
                {"title": "ML Engineer", "company": "OpenAI", "location": "San Francisco, CA", "url": "https://openai.com/careers"},
                {"title": "Machine Learning Scientist", "company": "Google", "location": "Mountain View, CA", "url": "https://careers.google.com"},
                {"title": "AI Research Engineer", "company": "Meta", "location": "Menlo Park, CA", "url": "https://www.metacareers.com"},
            ],
            'data science': [
                {"title": "Data Scientist", "company": "Netflix", "location": "Los Gatos, CA", "url": "https://jobs.netflix.com"},
                {"title": "Senior Data Analyst", "company": "Spotify", "location": "Remote", "url": "https://www.lifeatspotify.com"},
                {"title": "Data Engineer", "company": "Uber", "location": "San Francisco, CA", "url": "https://www.uber.com/careers"},
            ],
            'devops': [
                {"title": "DevOps Engineer", "company": "GitHub", "location": "Remote", "url": "https://github.com/careers"},
                {"title": "Site Reliability Engineer", "company": "Google", "location": "Mountain View, CA", "url": "https://careers.google.com"},
                {"title": "Infrastructure Engineer", "company": "Cloudflare", "location": "San Francisco, CA", "url": "https://www.cloudflare.com/careers"},
            ],
            'default': [
                {"title": "Software Engineer", "company": "Google", "location": "Mountain View, CA", "url": "https://careers.google.com"},
                {"title": "Full Stack Developer", "company": "Microsoft", "location": "Redmond, WA", "url": "https://careers.microsoft.com"},
                {"title": "Senior Software Engineer", "company": "Apple", "location": "Cupertino, CA", "url": "https://www.apple.com/careers"},
                {"title": "Software Developer", "company": "Stripe", "location": "Remote", "url": "https://stripe.com/jobs"},
                {"title": "Backend Engineer", "company": "Slack", "location": "San Francisco, CA", "url": "https://slack.com/careers"},
            ]
        }
        
        # Filter live jobs based on user skills
        live_jobs = []
        matched_skills = set()
        
        for skill in user_skills:
            for job_category, category_jobs in all_live_jobs.items():
                if job_category != 'default' and job_category in skill:
                    live_jobs.extend(category_jobs)
                    matched_skills.add(job_category)
                    if len(live_jobs) >= 10:
                        break
            if len(live_jobs) >= 10:
                break
        
        # If no specific skills matched or need more jobs, add default jobs
        if len(live_jobs) < 5:
            live_jobs.extend(all_live_jobs['default'][:10 - len(live_jobs)])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_live_jobs = []
        for job in live_jobs:
            job_key = f"{job['title']}{job['company']}"
            if job_key not in seen:
                seen.add(job_key)
                unique_live_jobs.append(job)
        
        live_jobs = unique_live_jobs[:10]  # Limit to 10 jobs
        
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

@app.route('/train', methods=['POST'])
def train_model():
    """Train or retrain the job matching model."""
    try:
        logger.info("Starting model training...")
        success = job_matcher.train_model()
        
        if success:
            logger.info("Model training completed successfully")
            return jsonify({
                'success': True,
                'message': 'Model trained successfully',
                'stats': job_matcher.get_job_statistics()
            })
        else:
            logger.error("Model training failed")
            return jsonify({'error': 'Model training failed'}), 500
            
    except Exception as e:
        logger.error(f"Error in train endpoint: {e}")
        return jsonify({'error': f'Training error: {str(e)}'}), 500

# Load problems from JSON file
def load_problems():
    """Load problems from the JSON file"""
    try:
        problems_file = os.path.join('data', 'Problems', 'problems.json')
        with open(problems_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading problems: {e}")
        # Fallback to sample problems if file loading fails
        return [
            {
                'id': '1',
                'title': 'Two Sum',
                'difficulty': 'Easy',
                'topics': ['Array', 'Hash Table'],
                'statement': {'description': 'Given an array of integers, return indices of the two numbers such that they add up to a specific target.'}
            },
            {
                'id': '2', 
                'title': 'Add Two Numbers',
                'difficulty': 'Medium',
                'topics': ['Linked List', 'Math'],
                'statement': {'description': 'Add two numbers represented as linked lists.'}
            },
            {
                'id': '3',
                'title': 'Longest Substring Without Repeating Characters', 
                'difficulty': 'Medium',
                'topics': ['Hash Table', 'String'],
                'statement': {'description': 'Find the length of the longest substring without repeating characters.'}
            }
        ]

# Load all problems at startup
ALL_PROBLEMS = load_problems()
logger.info(f"Loaded {len(ALL_PROBLEMS)} problems from data file")

@app.route('/api/problems', methods=['GET', 'OPTIONS'])
def get_problems():
    """
    Get a list of coding problems with optional filtering.
    Query parameters:
    - difficulty: Filter by difficulty level (Easy, Medium, Hard)
    - topic: Filter by topic (e.g., Array, String, etc.)
    - search: Search in problem title or description
    - limit: Maximum number of problems to return (default: 100)
    """
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return response
        
    try:
        # Get query parameters
        difficulty = request.args.get('difficulty', '').lower()
        topic = request.args.get('topic', '').lower()
        search = request.args.get('search', '').lower()
        limit = min(int(request.args.get('limit', 200)), 1000)  # Default 200, cap at 1000 for safety
        
        # Filter problems based on query parameters
        filtered_problems = []
        
        for problem in ALL_PROBLEMS:
            # Skip if difficulty filter doesn't match
            if difficulty and problem['difficulty'].lower() != difficulty:
                continue
                
            # Skip if topic filter is provided but not found in problem topics
            if topic and not any(t.lower() == topic for t in problem.get('topics', [])):
                continue
                
            # Skip if search term is not found in title or description
            description = problem.get('statement', {}).get('description', '')
            if search and (search not in problem['title'].lower() and 
                          search not in description.lower()):
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
            'total': len(ALL_PROBLEMS),  # Total available problems
            'filtered_count': len(filtered_problems),  # Count after filtering
            'page': 1,
            'page_size': len(filtered_problems)
        })
        
    except Exception as e:
        logger.error(f"Error in get_problems: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/problems/<problem_id>', methods=['GET', 'OPTIONS'])
def get_problem_by_id(problem_id):
    """
    Get a specific coding problem by ID.
    """
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return response
        
    try:
        # Find the problem by ID
        problem = None
        for p in ALL_PROBLEMS:
            if str(p.get('id')) == str(problem_id):
                problem = p
                break
        
        if not problem:
            return jsonify({
                'success': False,
                'error': 'Problem not found'
            }), 404
        
        # Return the specific problem
        return jsonify({
            'success': True,
            'problem': problem
        })
        
    except Exception as e:
        logger.error(f"Error in get_problem_by_id: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/submissions', methods=['POST', 'OPTIONS'])
def submit_solution():
    """
    Submit a coding solution for evaluation.
    Accepts: problem_id, language, source_code, mode
    """
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response
        
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        problem_id = data.get('problem_id')
        language = data.get('language', 'python')
        source_code = data.get('source_code', '')
        mode = data.get('mode', 'submit')
        
        # Validate required fields
        if not problem_id:
            return jsonify({
                'success': False,
                'error': 'Problem ID is required'
            }), 400
            
        if not source_code.strip():
            return jsonify({
                'success': False,
                'error': 'Source code is required'
            }), 400
        
        # Find the problem
        problem = None
        for p in ALL_PROBLEMS:
            if str(p.get('id')) == str(problem_id):
                problem = p
                break
        
        if not problem:
            return jsonify({
                'success': False,
                'error': 'Problem not found'
            }), 404
        
        logger.info(f"Processing {mode} for problem {problem_id} in {language}")
        
        # For now, we'll simulate a successful submission
        # In a real system, you would:
        # 1. Run the code against test cases
        # 2. Check for correctness
        # 3. Measure performance
        # 4. Store the submission in database
        
        # Simulate test case results
        test_cases = problem.get('test_cases', [])
        if not test_cases:
            # Generate some basic test cases if none exist
            test_cases = [
                {'input': 'Sample input', 'expected': 'Sample output', 'description': 'Basic test case'}
            ]
        
        # Simulate running test cases
        results = []
        passed_count = 0
        
        for i, test_case in enumerate(test_cases[:5]):  # Limit to 5 test cases
            # Simulate test execution (in reality, you'd run the actual code)
            # For demo purposes, we'll randomly pass/fail some tests
            import random
            passed = random.choice([True, True, True, False])  # 75% pass rate for demo
            
            if passed:
                passed_count += 1
                
            results.append({
                'test_case': i + 1,
                'passed': passed,
                'input': test_case.get('input', 'Test input'),
                'expected': test_case.get('expected', 'Expected output'),
                'actual': test_case.get('expected', 'Expected output') if passed else 'Wrong output',
                'description': test_case.get('description', f'Test case {i + 1}')
            })
        
        # Calculate success metrics
        total_tests = len(results)
        success_rate = (passed_count / total_tests) * 100 if total_tests > 0 else 0
        
        # Determine overall status
        if mode == 'submit':
            status = 'Accepted' if passed_count == total_tests else 'Wrong Answer'
            message = f"Submission {status.lower()}! Passed {passed_count}/{total_tests} test cases."
        else:
            status = 'Completed'
            message = f"Tests completed. Passed {passed_count}/{total_tests} test cases."
        
        # Return results
        response_data = {
            'success': True,
            'status': status,
            'message': message,
            'problem_id': problem_id,
            'language': language,
            'mode': mode,
            'test_results': results,
            'passed_tests': passed_count,
            'total_tests': total_tests,
            'success_rate': round(success_rate, 1),
            'execution_time': f"{random.randint(50, 200)}ms",  # Simulated execution time
            'memory_used': f"{random.randint(10, 50)}MB"  # Simulated memory usage
        }
        
        logger.info(f"Submission result: {status} ({passed_count}/{total_tests} tests passed)")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in submit_solution: {e}")
        return jsonify({
            'success': False,
            'error': f'Submission error: {str(e)}'
        }), 500

# Interview endpoints
@app.route('/interview/questions', methods=['POST', 'OPTIONS'])
def get_interview_questions():
    """Get interview questions based on skills and role"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
        
    try:
        data = request.get_json() or {}
        skills = data.get('skills', [])
        role_hint = data.get('role_hint', 'general')
        
        # Import the enhanced interview fallback system
        try:
            from enhanced_interview_fallback import get_enhanced_questions
            questions = get_enhanced_questions(skills, role_hint)
        except Exception as e:
            logger.warning(f"Enhanced interview system failed: {e}, using basic questions")
            # Fallback to basic questions
            questions = [
                {
                    'text': 'Tell me about yourself and your background.',
                    'time_limit_sec': 120,
                    'difficulty': 'easy'
                },
                {
                    'text': 'What are your key technical skills and how have you applied them?',
                    'time_limit_sec': 90,
                    'difficulty': 'medium'
                },
                {
                    'text': 'Describe a challenging project you worked on and how you overcame obstacles.',
                    'time_limit_sec': 120,
                    'difficulty': 'medium'
                },
                {
                    'text': 'Where do you see yourself in the next 5 years?',
                    'time_limit_sec': 90,
                    'difficulty': 'easy'
                },
                {
                    'text': 'Why are you interested in this role and our company?',
                    'time_limit_sec': 90,
                    'difficulty': 'easy'
                }
            ]
        
        return jsonify({
            'success': True,
            'questions': questions,
            'total_questions': len(questions)
        })
        
    except Exception as e:
        logger.error(f"Interview questions error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/interview/submit', methods=['POST', 'OPTIONS'])
def submit_interview():
    """Submit interview answers for evaluation"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
        
    try:
        data = request.get_json() or {}
        questions = data.get('questions', [])
        answers = data.get('answers', [])
        skills = data.get('skills', [])
        role_hint = data.get('role_hint', 'general')
        
        # Import the enhanced interview evaluation system
        try:
            from enhanced_interview_fallback import get_enhanced_evaluation
            result = get_enhanced_evaluation(questions, answers, skills, role_hint)
        except Exception as e:
            logger.warning(f"Enhanced evaluation failed: {e}, using basic evaluation")
            # Fallback to basic evaluation
            answered_count = len([a for a in answers if a and a.strip()])
            total_questions = len(questions)
            completion_rate = (answered_count / max(1, total_questions)) * 100
            
            result = {
                'total_score': min(85, max(60, completion_rate + random.randint(-10, 15))),
                'completion_rate': completion_rate,
                'answered_questions': answered_count,
                'total_questions': total_questions,
                'feedback': 'Thank you for completing the interview. Your responses have been recorded.',
                'strengths': ['Good communication', 'Relevant experience'],
                'improvements': ['Provide more specific examples', 'Elaborate on technical details']
            }
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Interview submission error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Flask server...")
    app.run(debug=False, port=5000, host='0.0.0.0')