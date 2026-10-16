from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app, 
     origins=["http://localhost:5173", "http://127.0.0.1:5173", 
              "http://localhost:5174", "http://127.0.0.1:5174", 
              "http://localhost:3000", "http://127.0.0.1:3000"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"])

# Data file for experiences
EXPERIENCES_FILE = 'data/interview_experiences.json'

def load_experiences():
    """Load experiences from JSON file"""
    try:
        if os.path.exists(EXPERIENCES_FILE):
            with open(EXPERIENCES_FILE, 'r', encoding='utf-8') as f:
                experiences = json.load(f)
                print(f"✅ Loaded {len(experiences)} experiences from file")
                return experiences
        else:
            print(f"⚠️ Experiences file not found: {EXPERIENCES_FILE}")
            return []
    except Exception as e:
        print(f"❌ Error loading experiences: {e}")
        return []

def save_experiences(experiences):
    """Save experiences to JSON file"""
    try:
        os.makedirs(os.path.dirname(EXPERIENCES_FILE), exist_ok=True)
        with open(EXPERIENCES_FILE, 'w', encoding='utf-8') as f:
            json.dump(experiences, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved {len(experiences)} experiences to file")
        return True
    except Exception as e:
        print(f"❌ Error saving experiences: {e}")
        return False

@app.route('/')
def index():
    """Health check"""
    experiences = load_experiences()
    return jsonify({
        'status': 'OK',
        'service': 'Interview Experience Server',
        'total_experiences': len(experiences),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Health endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Interview Experience API',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/experiences', methods=['GET', 'POST', 'OPTIONS'])
def api_experiences():
    """Handle experience API requests"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'})
    
    if request.method == 'GET':
        try:
            experiences = load_experiences()
            
            # Apply filters if provided
            company = request.args.get('company', '').lower()
            position = request.args.get('position', '').lower() 
            difficulty = request.args.get('difficulty_rating', '')
            
            filtered_experiences = []
            for exp in experiences:
                # Apply company filter
                if company and company not in exp.get('company', '').lower():
                    continue
                # Apply position filter    
                if position and position not in exp.get('position', '').lower():
                    continue
                # Apply difficulty filter
                if difficulty and difficulty != exp.get('difficulty_rating', ''):
                    continue
                    
                filtered_experiences.append(exp)
            
            print(f"📊 GET /api/experiences - Returning {len(filtered_experiences)} experiences")
            
            return jsonify({
                'success': True,
                'experiences': filtered_experiences,
                'total': len(filtered_experiences)
            })
            
        except Exception as e:
            print(f"❌ Error fetching experiences: {e}")
            return jsonify({
                'success': False,
                'error': f'Failed to fetch experiences: {str(e)}'
            }), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            print(f"📊 POST /api/experiences - Received data: {data}")
            
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
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
                'company': data.get('company'),
                'position': data.get('position'), 
                'interviewer': data.get('interviewer', ''),
                'experience_text': data.get('experience_text'),
                'difficulty_rating': data.get('difficulty_rating'),
                'outcome': data.get('outcome', 'Pending'),
                'interview_type': data.get('interview_type'),
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
            if save_experiences(experiences):
                print(f"✅ Created new experience ID {new_id} for {new_experience['company']}")
                
                return jsonify({
                    'success': True,
                    'experience': new_experience,
                    'message': 'Interview experience created successfully'
                }), 201
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to save experience to file'
                }), 500
            
        except Exception as e:
            print(f"❌ Error creating experience: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'Failed to create experience: {str(e)}'
            }), 500

if __name__ == '__main__':
    print("🚀 Starting Interview Experience Server...")
    
    experiences = load_experiences()
    print(f"📊 Current data stored in: {os.path.abspath(EXPERIENCES_FILE)}")
    print(f"📊 Available endpoints:")
    print(f"   - GET  /health")
    print(f"   - GET  /api/experiences")
    print(f"   - POST /api/experiences")
    
    print(f"🌐 Server starting on http://localhost:5003")
    
    try:
        app.run(host='127.0.0.1', port=5003, debug=False)
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        import traceback
        traceback.print_exc()