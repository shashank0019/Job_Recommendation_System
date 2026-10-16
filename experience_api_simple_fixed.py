"""
Simple Interview Experience API Server
Loads data from data/interview_experiences.json
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)

# Enable CORS for your frontend
CORS(app, origins=['http://localhost:5173', 'http://localhost:5174', 'http://localhost:3000'])

DATA_FILE = 'data/interview_experiences.json'

def load_experiences_from_file():
    """Load interview experiences from JSON file"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as file:
                experiences = json.load(file)
                print(f"✅ Loaded {len(experiences)} interview experiences from {DATA_FILE}")
                return experiences
        else:
            print(f"❌ Data file {DATA_FILE} not found")
            return []
    except Exception as e:
        print(f"❌ Error loading experiences: {e}")
        return []

def save_experiences_to_file(experiences):
    """Save interview experiences to JSON file"""
    try:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, 'w', encoding='utf-8') as file:
            json.dump(experiences, file, indent=2, ensure_ascii=False)
        print(f"✅ Saved {len(experiences)} interview experiences to {DATA_FILE}")
        return True
    except Exception as e:
        print(f"❌ Error saving experiences: {e}")
        return False

@app.route('/api/experiences', methods=['GET'])
def get_experiences():
    """Get all interview experiences with optional filtering"""
    try:
        experiences = load_experiences_from_file()
        
        # Get query parameters for filtering
        company = request.args.get('company')
        position = request.args.get('position') 
        interview_type = request.args.get('interview_type')
        difficulty = request.args.get('difficulty_rating')
        outcome = request.args.get('outcome')
        search = request.args.get('search')
        
        # Apply filters
        filtered_experiences = []
        for exp in experiences:
            # Company filter
            if company and company.lower() not in exp.get('company', '').lower():
                continue
                
            # Position filter  
            if position and position.lower() not in exp.get('position', '').lower():
                continue
                
            # Interview type filter
            if interview_type and interview_type.lower() != exp.get('interview_type', '').lower():
                continue
                
            # Difficulty filter
            if difficulty and difficulty != exp.get('difficulty_rating', ''):
                continue
                
            # Outcome filter
            if outcome and outcome.lower() != exp.get('outcome', '').lower():
                continue
                
            # Search filter - search in company, position, experience_text
            if search:
                search_term = search.lower()
                searchable_text = f"{exp.get('company', '')} {exp.get('position', '')} {exp.get('experience_text', '')}"
                if search_term not in searchable_text.lower():
                    continue
            
            # Only include published experiences
            if exp.get('status', 'published') == 'published':
                filtered_experiences.append(exp)
        
        # Sort by created_at (newest first)
        filtered_experiences.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return jsonify({
            'success': True,
            'experiences': filtered_experiences,
            'total': len(filtered_experiences),
            'message': f'Found {len(filtered_experiences)} interview experiences'
        })
        
    except Exception as e:
        print(f"❌ Error fetching experiences: {e}")
        return jsonify({
            'success': False,
            'experiences': [],
            'error': str(e)
        }), 500

@app.route('/api/experiences', methods=['POST'])
def create_experience():
    """Create a new interview experience"""
    print(f"🔄 POST request received for /api/experiences")
    try:
        data = request.get_json()
        print(f"📊 Request data: {data}")
        
        # Validate required fields
        required_fields = ['company', 'position', 'experience_text', 'interview_type', 'difficulty_rating']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Load existing experiences
        experiences = load_experiences_from_file()
        
        # Generate new ID
        new_id = max([exp.get('id', 0) for exp in experiences], default=0) + 1
        
        # Create new experience object
        new_experience = {
            'id': new_id,
            'company': data['company'],
            'position': data['position'],
            'interviewer': data.get('interviewer', ''),
            'experience_text': data['experience_text'],
            'difficulty_rating': data['difficulty_rating'],
            'outcome': data.get('outcome', 'Pending'),
            'interview_type': data['interview_type'],
            'interview_rounds': data.get('interview_rounds', 1),
            'preparation_time': data.get('preparation_time', ''),
            'location': data.get('location', ''),
            'questions_asked': data.get('questions_asked', []),
            'tags': data.get('tags', []),
            'date': data.get('date', datetime.now().isoformat()),
            'created_at': datetime.now().isoformat(),
            'status': 'published'
        }
        
        # Add to experiences list
        experiences.append(new_experience)
        
        # Save to file
        if save_experiences_to_file(experiences):
            print(f"✅ Successfully created experience: {new_experience}")
            return jsonify({
                'success': True,
                'experience': new_experience,
                'message': 'Interview experience created successfully'
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save interview experience'
            }), 500
            
    except Exception as e:
        print(f"❌ Error creating experience: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/experiences/<int:experience_id>', methods=['GET'])
def get_experience(experience_id):
    """Get a specific interview experience by ID"""
    try:
        experiences = load_experiences_from_file()
        
        for exp in experiences:
            if exp.get('id') == experience_id:
                return jsonify({
                    'success': True,
                    'experience': exp
                })
        
        return jsonify({
            'success': False,
            'error': 'Interview experience not found'
        }), 404
        
    except Exception as e:
        print(f"❌ Error fetching experience: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/experiences/company/<company>', methods=['GET'])
def get_experiences_by_company(company):
    """Get interview experiences for a specific company"""
    try:
        experiences = load_experiences_from_file()
        
        # Filter experiences by company (case-insensitive)
        company_experiences = []
        for exp in experiences:
            if company.lower() in exp.get('company', '').lower():
                if exp.get('status', 'published') == 'published':
                    company_experiences.append(exp)
        
        # Sort by created_at (newest first)
        company_experiences.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return jsonify({
            'success': True,
            'experiences': company_experiences,
            'total': len(company_experiences),
            'company': company
        })
        
    except Exception as e:
        print(f"❌ Error fetching company experiences: {e}")
        return jsonify({
            'success': False,
            'experiences': [],
            'error': str(e)
        }), 500

@app.route('/api/experiences/stats', methods=['GET'])
def get_experience_stats():
    """Get interview experience statistics"""
    try:
        experiences = load_experiences_from_file()
        
        # Calculate stats
        total_experiences = len(experiences)
        companies = set(exp.get('company', '') for exp in experiences)
        outcomes = {}
        difficulty_levels = {}
        interview_types = {}
        
        for exp in experiences:
            # Count outcomes
            outcome = exp.get('outcome', 'Unknown')
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
            
            # Count difficulty levels
            difficulty = exp.get('difficulty_rating', 'Unknown')
            difficulty_levels[difficulty] = difficulty_levels.get(difficulty, 0) + 1
            
            # Count interview types
            int_type = exp.get('interview_type', 'Unknown')
            interview_types[int_type] = interview_types.get(int_type, 0) + 1
        
        return jsonify({
            'success': True,
            'stats': {
                'total_experiences': total_experiences,
                'total_companies': len(companies),
                'companies': list(companies),
                'outcomes': outcomes,
                'difficulty_levels': difficulty_levels,
                'interview_types': interview_types
            }
        })
        
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Interview Experience API',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Starting Interview Experience API Server...")
    print("📊 Loading existing interview experiences...")
    
    experiences = load_experiences_from_file()
    print(f"✅ Loaded {len(experiences)} interview experiences")
    
    print("🌐 Server will be available at:")
    print("   - http://localhost:5001/api/experiences")
    print("   - http://localhost:5001/api/experiences/stats")
    print("   - http://localhost:5001/health")
    
    try:
        app.run(debug=True, host='127.0.0.1', port=5002)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()