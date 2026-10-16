from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# Simple CORS headers without flask_cors dependency
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

DATA_FILE = 'data/interview_experiences.json'

def load_experiences():
    """Load experiences from JSON file"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading experiences: {e}")
        return []

def save_experiences(experiences):
    """Save experiences to JSON file"""
    try:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(experiences, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving experiences: {e}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Interview Experience API',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/experiences', methods=['GET'])
def get_experiences():
    try:
        experiences = load_experiences()
        print(f"📊 Returning {len(experiences)} experiences")
        return jsonify({
            'success': True,
            'experiences': experiences,
            'total': len(experiences)
        })
    except Exception as e:
        print(f"❌ Error in GET /api/experiences: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/experiences', methods=['POST'])
def create_experience():
    try:
        data = request.get_json()
        print(f"📊 Received POST data: {data}")
        
        # Validate required fields
        required_fields = ['company', 'position', 'experience_text', 'interview_type', 'difficulty_rating']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Load existing experiences
        experiences = load_experiences()
        
        # Generate new ID
        new_id = max([exp.get('id', 0) for exp in experiences], default=0) + 1
        
        # Create new experience
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
        
        # Add to list and save
        experiences.append(new_experience)
        
        if save_experiences(experiences):
            print(f"✅ Successfully created experience ID {new_id} for {new_experience['company']}")
            return jsonify({
                'success': True,
                'experience': new_experience,
                'message': 'Interview experience created successfully'
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save experience'
            }), 500
            
    except Exception as e:
        print(f"❌ Error creating experience: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Interview Experience Flask Server...")
    
    experiences = load_experiences()
    print(f"✅ Loaded {len(experiences)} existing experiences")
    print(f"💾 Data stored in: {os.path.abspath(DATA_FILE)}")
    
    print("📊 Available endpoints:")
    print("   - GET  /api/experiences")
    print("   - POST /api/experiences")
    print("   - GET  /health")
    
    app.run(host='0.0.0.0', port=5003, debug=True)