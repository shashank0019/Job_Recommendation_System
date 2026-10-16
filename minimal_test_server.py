#!/usr/bin/env python3

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

print("Creating minimal Flask test server...")

app = Flask(__name__)

# Configure CORS properly for the React frontend
CORS(app, origins=["http://localhost:5174", "http://127.0.0.1:5174"], 
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

@app.route('/')
def home():
    return jsonify({"message": "Minimal server working"})

@app.route('/auth/signup', methods=['POST', 'OPTIONS'])
def test_signup():
    logger.info("=== SIGNUP ROUTE CALLED ===")
    
    if request.method == 'OPTIONS':
        logger.info("OPTIONS preflight request")
        return '', 200
    
    try:
        data = request.get_json()
        logger.info(f"Received data: {data}")
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Basic validation
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        logger.info(f"Processing signup for: {email}")
        
        if not name or not email or not password:
            return jsonify({'error': 'Name, email, and password are required'}), 400
        
        # Return success for testing
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'name': name,
                'email': email
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error in signup: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/auth/signin', methods=['POST', 'OPTIONS'])
def test_signin():
    logger.info("=== SIGNIN ROUTE CALLED ===")
    
    if request.method == 'OPTIONS':
        logger.info("OPTIONS preflight request")
        return '', 200
    
    try:
        data = request.get_json()
        logger.info(f"Received data: {data}")
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        logger.info(f"Processing signin for: {email}")
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Return success for testing
        return jsonify({
            'message': 'Login successful',
            'user': {
                'name': 'Test User',
                'email': email
            },
            'token': 'test-token-123'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in signin: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting minimal test server...")
    print("Available routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint} [{', '.join(rule.methods)}]")
    
    app.run(debug=False, port=5000, host='127.0.0.1')