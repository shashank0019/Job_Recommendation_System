#!/usr/bin/env python3
"""
Minimal stable Flask authentication server for React frontend
Uses simpler MongoDB connection pattern to avoid heartbeat issues
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pymongo
import bcrypt
import secrets
import logging
from datetime import datetime
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=['http://localhost:5174', 'http://localhost:3000', 'http://localhost:5173'])

# Simple MongoDB connection function - reconnect each time to avoid heartbeat issues
def get_db():
    """Get a fresh MongoDB connection"""
    try:
        client = pymongo.MongoClient(
            "mongodb+srv://Final_project:Atlas11924@cluster0.xseglna.mongodb.net/",
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
            maxPoolSize=1  # Keep pool small to avoid connection issues
        )
        db = client.career_guidance_platform
        # Test connection
        client.admin.command('ping')
        return db, client
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None, None

@app.route('/auth/signin', methods=['POST', 'OPTIONS'])
def signin():
    """Signin endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # Get fresh database connection
        db, client = get_db()
        if not db:
            return jsonify({"error": "Database connection failed"}), 500
        
        try:
            # Find user
            user = db.users.find_one({"email": email})
            if not user:
                return jsonify({"error": "Invalid email or password"}), 401
            
            # Check password
            stored_password = user.get('password', '')
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')
            
            if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                # Create session token
                session_token = secrets.token_urlsafe(32)
                
                # Store session
                db.sessions.insert_one({
                    "token": session_token,
                    "user_id": str(user['_id']),
                    "email": email,
                    "created_at": datetime.now()
                })
                
                logger.info(f"✅ User signed in: {email}")
                return jsonify({
                    "message": "Signin successful",
                    "token": session_token,
                    "user": {
                        "id": str(user['_id']),
                        "name": user.get('name', ''),
                        "email": email
                    }
                }), 200
            else:
                return jsonify({"error": "Invalid email or password"}), 401
                
        finally:
            # Always close connection to avoid heartbeat issues
            if client:
                client.close()
        
    except Exception as e:
        logger.error(f"Signin error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/auth/signup', methods=['POST', 'OPTIONS'])
def signup():
    """Signup endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not all([name, email, password]):
            return jsonify({"error": "Name, email and password are required"}), 400
        
        # Get fresh database connection
        db, client = get_db()
        if not db:
            return jsonify({"error": "Database connection failed"}), 500
        
        try:
            # Check if user exists
            if db.users.find_one({"email": email}):
                return jsonify({"error": "User already exists"}), 409
            
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
            
            # Create session token
            session_token = secrets.token_urlsafe(32)
            
            # Store session
            db.sessions.insert_one({
                "token": session_token,
                "user_id": str(result.inserted_id),
                "email": email,
                "created_at": datetime.now()
            })
            
            logger.info(f"✅ New user created: {email}")
            return jsonify({
                "message": "Signup successful",
                "token": session_token,
                "user": {
                    "id": str(result.inserted_id),
                    "name": name,
                    "email": email
                }
            }), 201
            
        finally:
            # Always close connection
            if client:
                client.close()
        
    except Exception as e:
        logger.error(f"Signup error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/auth/verify', methods=['GET', 'OPTIONS'])
def verify_token():
    """Verify token endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({"error": "No token provided"}), 401
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Get fresh database connection
        db, client = get_db()
        if not db:
            return jsonify({"error": "Database connection failed"}), 500
        
        try:
            # Find session
            session = db.sessions.find_one({"token": token})
            if not session:
                return jsonify({"error": "Invalid token"}), 401
            
            # Find user
            user = db.users.find_one({"email": session['email']})
            if not user:
                return jsonify({"error": "User not found"}), 401
            
            return jsonify({
                "valid": True,
                "user": {
                    "id": str(user['_id']),
                    "name": user.get('name', ''),
                    "email": user['email']
                }
            }), 200
            
        finally:
            if client:
                client.close()
        
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({"status": "ok", "message": "Auth server running"}), 200

@app.route('/', methods=['GET'])
def index():
    """Index endpoint"""
    return jsonify({"message": "Minimal Auth Server", "status": "running"}), 200

if __name__ == '__main__':
    logger.info("🚀 Starting Minimal Auth Server...")
    logger.info("📊 Data storage: MongoDB Atlas")
    logger.info("🌐 CORS enabled for React frontend")
    logger.info("Available endpoints:")
    logger.info("  POST /auth/signin - User signin")
    logger.info("  POST /auth/signup - User signup") 
    logger.info("  GET /auth/verify - Verify token")
    logger.info("  GET /health - Health check")
    
    app.run(host='0.0.0.0', port=5000, debug=False)