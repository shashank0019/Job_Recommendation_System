#!/usr/bin/env python3
import http.server
import socketserver
import json
import os
from urllib.parse import urlparse, parse_qs
from datetime import datetime

PORT = 5003
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

class ExperienceHandler(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if path == '/api/experiences':
            experiences = load_experiences()
            response = {
                'success': True,
                'experiences': experiences,
                'total': len(experiences)
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        elif path == '/health':
            response = {
                'status': 'healthy',
                'service': 'Interview Experience API',
                'timestamp': datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        else:
            self.send_error(404, 'Not Found')
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/api/experiences':
            try:
                # Read request body
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                print(f"📊 Received POST data: {data}")
                
                # Validate required fields
                required_fields = ['company', 'position', 'experience_text', 'interview_type', 'difficulty_rating']
                for field in required_fields:
                    if not data.get(field):
                        self.send_error(400, f'Missing required field: {field}')
                        return
                
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
                
                # Add to list
                experiences.append(new_experience)
                
                # Save to file
                if save_experiences(experiences):
                    print(f"✅ Successfully saved new experience: {new_experience['company']}")
                    
                    # Send success response
                    self.send_response(201)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    response = {
                        'success': True,
                        'experience': new_experience,
                        'message': 'Interview experience created successfully'
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                else:
                    self.send_error(500, 'Failed to save experience')
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                self.send_error(400, 'Invalid JSON data')
            except Exception as e:
                print(f"❌ Error creating experience: {e}")
                self.send_error(500, 'Internal server error')
        else:
            self.send_error(404, 'Not Found')

if __name__ == '__main__':
    print(f"🚀 Starting Interview Experience API Server on port {PORT}...")
    
    # Load and display current experiences
    experiences = load_experiences()
    print(f"✅ Loaded {len(experiences)} existing interview experiences")
    
    print(f"📊 Available endpoints:")
    print(f"   - GET  http://localhost:{PORT}/api/experiences")
    print(f"   - POST http://localhost:{PORT}/api/experiences")
    print(f"   - GET  http://localhost:{PORT}/health")
    
    try:
        with socketserver.TCPServer(("", PORT), ExperienceHandler) as httpd:
            print(f"🌐 Server running at http://localhost:{PORT}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")