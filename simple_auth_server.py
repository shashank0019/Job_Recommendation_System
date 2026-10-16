#!/usr/bin/env python3

from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os
sys.path.append('.')

print("Creating simple test server...")

app = Flask(__name__)
CORS(app, origins=["http://localhost:5174"])

@app.route('/health')
def health():
    return jsonify({"status": "ok", "message": "Server is running"})

@app.route('/auth/test', methods=['POST'])
def test_auth():
    data = request.get_json()
    return jsonify({"message": "Test endpoint working", "received": data})

try:
    print("Importing auth components...")
    from config.database import get_db_config
    from auth.models import User, Session
    from auth.utils import AuthUtils
    
    print("Database and auth components imported successfully")
    
    @app.route('/auth/signup', methods=['POST'])
    def signup():
        print("Signup endpoint called")
        try:
            data = request.get_json()
            print(f"Received data: {data}")
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            name = data.get('name', '').strip()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            
            print(f"Processing signup for: {email}")
            
            # Basic validation
            if not name or not email or not password:
                return jsonify({'error': 'Name, email, and password are required'}), 400
            
            # Check if user exists
            existing_user = User.find_by_email(email)
            if existing_user:
                return jsonify({'error': 'User already exists'}), 409
            
            # Create user
            user = User.create(name, email, password)
            if user:
                return jsonify({
                    'message': 'User created successfully',
                    'user': user.to_public_dict()
                }), 201
            else:
                return jsonify({'error': 'Failed to create user'}), 500
                
        except Exception as e:
            print(f"Signup error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/auth/signin', methods=['POST'])
    def signin():
        print("Signin endpoint called")
        try:
            data = request.get_json()
            print(f"Received data: {data}")
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            
            print(f"Processing signin for: {email}")
            
            if not email or not password:
                return jsonify({'error': 'Email and password are required'}), 400
            
            # Find user
            user = User.find_by_email(email)
            if not user:
                return jsonify({'error': 'Invalid email or password'}), 401
            
            # Verify password
            if not user.verify_password(password):
                return jsonify({'error': 'Invalid email or password'}), 401
            
            # Create session
            session = Session.create(user._id)
            if session:
                user.update_last_login()
                user.save()
                
                return jsonify({
                    'message': 'Signin successful',
                    'user': user.to_public_dict(),
                    'token': session.session_token
                }), 200
            else:
                return jsonify({'error': 'Failed to create session'}), 500
                
        except Exception as e:
            print(f"Signin error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': 'Internal server error'}), 500
    
    print("Auth routes added successfully")
    
except Exception as e:
    print(f"Error importing auth components: {e}")
    import traceback
    traceback.print_exc()

if __name__ == '__main__':
    print("Starting simple test server on port 5001...")
    app.run(debug=False, port=5001, host='127.0.0.1')