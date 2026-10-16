#!/usr/bin/env python3
"""
Simple Problems Server - serves only the problems from the database
This avoids the heavy dependencies in the main app.py
"""

import os
import json
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

def load_problems():
    """Load problems from the JSON file"""
    try:
        problems_file = os.path.join('data', 'Problems', 'problems.json')
        with open(problems_file, 'r', encoding='utf-8') as f:
            problems = json.load(f)
            logger.info(f"✅ Loaded {len(problems)} problems from {problems_file}")
            return problems
    except Exception as e:
        logger.error(f"❌ Error loading problems: {e}")
        # Fallback to sample problems if file loading fails
        return [
            {
                'id': '1',
                'title': 'Two Sum',
                'difficulty': 'Easy',
                'topics': ['Array', 'Hash Table'],
                'statement': {
                    'description': 'Given an array of integers, return indices of the two numbers such that they add up to a specific target.',
                    'samples': [
                        {
                            'input': '[2,7,11,15], 9',
                            'output': '[0,1]',
                            'explanation': 'Because nums[0] + nums[1] == 9, we return [0, 1].'
                        }
                    ],
                    'constraints': ['2 <= nums.length <= 10^4', '-10^9 <= nums[i] <= 10^9']
                },
                'languages': ['python', 'javascript', 'java', 'cpp']
            }
        ]

# Load all problems at startup
ALL_PROBLEMS = load_problems()

@app.route('/problems', methods=['GET', 'OPTIONS'])
def get_problems():
    """
    Get a list of coding problems with optional filtering.
    Query parameters:
    - difficulty: Filter by difficulty level (Easy, Medium, Hard)
    - topic: Filter by topic (e.g., Array, String, etc.)
    - search: Search in problem title or description
    - limit: Maximum number of problems to return (default: 200)
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
        limit = min(int(request.args.get('limit', 200)), 1000)  # Cap at 1000 for safety
        
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
        
        logger.info(f"🔍 Returning {len(filtered_problems)} problems (filtered from {len(ALL_PROBLEMS)} total)")
        
        # Return the filtered list of problems in the format expected by React
        return jsonify({
            'success': True,
            'problems': filtered_problems,  # React expects 'problems' not 'items'
            'total': len(ALL_PROBLEMS),
            'filtered_count': len(filtered_problems)
        })
        
    except Exception as e:
        logger.error(f"❌ Error in get_problems: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'problems': []
        }), 500

@app.route('/problems/<problem_id>', methods=['GET', 'OPTIONS'])
def get_problem(problem_id):
    """Get a specific problem by ID"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return response
        
    try:
        # Find the problem by ID
        problem = next((p for p in ALL_PROBLEMS if p['id'] == problem_id), None)
        
        if not problem:
            return jsonify({
                'success': False,
                'error': f'Problem with ID {problem_id} not found'
            }), 404
        
        return jsonify({
            'success': True,
            'problem': problem
        })
        
    except Exception as e:
        logger.error(f"❌ Error in get_problem: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'OK',
        'message': 'Problems Server Running',
        'total_problems': len(ALL_PROBLEMS)
    })

if __name__ == '__main__':
    port = 5001  # Use different port to avoid conflicts
    print(f"🚀 Starting Problems Server...")
    print(f"📚 Serving {len(ALL_PROBLEMS)} problems")
    print(f"🌐 Server will run at http://localhost:{port}")
    print(f"🔧 Endpoints:")
    print(f"   GET /problems - List all problems")
    print(f"   GET /problems/<id> - Get specific problem")
    print(f"   GET / - Health check")
    
    try:
        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        print("🔧 Try using a different port or check if another process is running.")