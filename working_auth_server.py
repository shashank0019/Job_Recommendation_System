#!/usr/bin/env python3
"""
Simple working authentication server that won't crash
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pymongo
import bcrypt
import secrets
import json
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=['http://localhost:5174', 'http://localhost:3000', 'http://localhost:5173'])

# Simple MongoDB connection
def get_mongo_connection():
    """Get fresh MongoDB connection"""
    try:
        client = pymongo.MongoClient(
            "mongodb+srv://Final_project:Atlas11924@cluster0.xseglna.mongodb.net/career_guidance_platform",
            serverSelectionTimeoutMS=5000
        )
        return client.career_guidance_platform
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        return None

@app.route('/auth/signin', methods=['POST', 'OPTIONS'])
def signin():
    if request.method == 'OPTIONS':
        return '', 200
    
    print(f"=== SIGNIN REQUEST ===")
    try:
        # Get data
        data = request.get_json()
        print(f"Request data: {data}")
        
        if not data:
            print("No JSON data received")
            return jsonify({"error": "No data provided", "success": False}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        print(f"Email: {email}")
        print(f"Password length: {len(password) if password else 0}")
        
        if not email or not password:
            print("Missing email or password")
            return jsonify({"error": "Email and password required", "success": False}), 400
        
        # Connect to database
        db = get_mongo_connection()
        if not db:
            print("Database connection failed")
            return jsonify({"error": "Database error", "success": False}), 500
        
        # Find user
        print(f"Looking for user: {email}")
        user = db.users.find_one({"email": email})
        
        if not user:
            print(f"User not found: {email}")
            return jsonify({"error": "Invalid credentials", "success": False}), 401
        
        print(f"User found: {user.get('name', 'No name')}")
        
        # Check password
        stored_password = user.get('password', '')
        print(f"Stored password type: {type(stored_password)}")
        print(f"Stored password length: {len(stored_password) if stored_password else 0}")
        
        if not stored_password:
            print("No password hash in database")
            return jsonify({"error": "Account error", "success": False}), 500
        
        # Convert to bytes if needed
        if isinstance(stored_password, str):
            stored_password_bytes = stored_password.encode('utf-8')
        else:
            stored_password_bytes = stored_password
        
        password_bytes = password.encode('utf-8')
        
        # Check password with bcrypt
        try:
            password_match = bcrypt.checkpw(password_bytes, stored_password_bytes)
            print(f"Password match: {password_match}")
        except Exception as e:
            print(f"Password check error: {e}")
            return jsonify({"error": "Password verification failed", "success": False}), 500
        
        if password_match:
            # Generate token
            token = secrets.token_urlsafe(32)
            
            # Store session
            try:
                db.sessions.insert_one({
                    "token": token,
                    "user_id": str(user['_id']),
                    "email": email,
                    "created_at": datetime.now()
                })
            except Exception as e:
                print(f"Session creation error: {e}")
                return jsonify({"error": "Session creation failed", "success": False}), 500
            
            print(f"Signin successful for: {email}")
            return jsonify({
                "success": True,
                "message": "Signin successful", 
                "token": token,
                "user": {
                    "id": str(user['_id']),
                    "name": user.get('name', ''),
                    "email": email
                }
            }), 200
        else:
            print(f"Invalid password for: {email}")
            return jsonify({"error": "Invalid credentials", "success": False}), 401
        
    except Exception as e:
        print(f"Signin error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Server error", "success": False}), 500

@app.route('/auth/signup', methods=['POST', 'OPTIONS'])  
def signup():
    if request.method == 'OPTIONS':
        return '', 200
        
    print(f"=== SIGNUP REQUEST ===")
    try:
        data = request.get_json()
        print(f"Request data: {data}")
        
        if not data:
            return jsonify({"error": "No data provided", "success": False}), 400
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower() 
        password = data.get('password', '')
        
        if not all([name, email, password]):
            return jsonify({"error": "All fields required", "success": False}), 400
        
        # Connect to database
        db = get_mongo_connection()
        if not db:
            return jsonify({"error": "Database error", "success": False}), 500
        
        # Check if user exists
        if db.users.find_one({"email": email}):
            return jsonify({"error": "User already exists", "success": False}), 409
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user
        user_doc = {
            "name": name,
            "email": email,
            "password": hashed_password.decode('utf-8'),
            "created_at": datetime.now()
        }
        
        result = db.users.insert_one(user_doc)
        
        # Generate token
        token = secrets.token_urlsafe(32)
        
        # Store session
        db.sessions.insert_one({
            "token": token,
            "user_id": str(result.inserted_id),
            "email": email,
            "created_at": datetime.now()
        })
        
        print(f"Signup successful for: {email}")
        return jsonify({
            "success": True,
            "message": "Signup successful",
            "token": token,
            "user": {
                "id": str(result.inserted_id),
                "name": name,
                "email": email
            }
        }), 201
        
    except Exception as e:
        print(f"Signup error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Server error", "success": False}), 500

@app.route('/health')
def health():
    return jsonify({"status": "ok", "message": "Server running"}), 200

@app.route('/')
def index():
    return jsonify({"message": "Auth Server", "status": "running"}), 200

if __name__ == '__main__':
    print("🚀 Starting Working Auth Server...")
    print("📊 Endpoints available:")
    print("  POST /auth/signin")
    print("  POST /auth/signup") 
    print("  GET /health")
    print("🌐 CORS enabled for React frontend")
    print("🔥 Server starting on http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)