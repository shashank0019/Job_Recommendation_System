#!/usr/bin/env python3
"""
Simple Flask authentication server without complex MongoDB connection patterns
Focuses on stable server operation for signin testing
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import bcrypt
import secrets
import pymongo
import logging

app = Flask(__name__)
CORS(app, origins=['http://localhost:5174', 'http://localhost:3000', 'http://localhost:5173'])

# Simple logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection - simplified and direct
def get_db_connection():
    """Get a direct MongoDB connection"""
    try:
        client = pymongo.MongoClient(
            "mongodb+srv://Final_project:Atlas11924@cluster0.xseglna.mongodb.net/",
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
            maxPoolSize=10
        )
        db = client.career_guidance_platform
        # Test connection
        client.admin.command('ping')
        logger.info("✅ MongoDB connection successful")
        return db
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        return None

# Initialize database connection
db = get_db_connection()
if db is None:
    logger.error("Failed to connect to database - exiting")
    exit(1)

@app.route('/auth/signin', methods=['POST', 'OPTIONS'])
def signin():
    """Simple signin endpoint"""
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
        
        # Find user in database
        users_collection = db.users
        user = users_collection.find_one({"email": email})
        
        if not user:
            logger.warning(f"User not found: {email}")
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Check password
        stored_password = user.get('password', '')
        if isinstance(stored_password, str):
            stored_password = stored_password.encode('utf-8')
        
        password_bytes = password.encode('utf-8')
        
        if bcrypt.checkpw(password_bytes, stored_password):
            # Generate session token
            session_token = secrets.token_urlsafe(32)
            
            # Store session (simplified)
            sessions_collection = db.sessions
            sessions_collection.insert_one({
                "token": session_token,
                "user_id": str(user['_id']),
                "email": email,
                "created_at": "2025-11-01T12:00:00Z"
            })
            
            logger.info(f"✅ User signed in successfully: {email}")
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
            logger.warning(f"Invalid password for user: {email}")
            return jsonify({"error": "Invalid email or password"}), 401
        
    except Exception as e:
        logger.error(f"Signin error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "Server is running"}), 200

@app.route('/', methods=['GET'])
def index():
    """Index endpoint"""
    return jsonify({"message": "Simple Auth Server", "status": "running"}), 200

if __name__ == '__main__':
    logger.info("Starting Simple Auth Server...")
    logger.info("Available endpoints:")
    logger.info("  POST /auth/signin - User signin")
    logger.info("  GET /health - Health check")
    logger.info("  GET / - Index")
    
    app.run(host='0.0.0.0', port=5000, debug=False)