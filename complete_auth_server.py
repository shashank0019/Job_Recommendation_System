#!/usr/bin/env python3
"""
Complete working authentication server - fixes all signin/signup issues
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pymongo
import bcrypt
import secrets
import logging
from datetime import datetime
import traceback

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=['http://localhost:5174', 'http://localhost:3000', 'http://localhost:5173'])

def get_db():
    """Get MongoDB connection - fresh connection each time to avoid issues"""
    try:
        client = pymongo.MongoClient(
            "mongodb+srv://Final_project:Atlas11924@cluster0.xseglna.mongodb.net/",
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
            maxPoolSize=1
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
    """Signin endpoint - matches frontend expectations exactly"""
    if request.method == 'OPTIONS':
        return '', 200
    
    logger.info("=== SIGNIN REQUEST ===")
    
    try:
        # Get request data
        data = request.get_json()
        logger.info(f"Request data: {data}")
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        logger.info(f"Signin attempt - Email: {email}, Password length: {len(password)}")
        
        if not email or not password:
            return jsonify({"success": False, "error": "Email and password are required"}), 400
        
        # Get database
        db, client = get_db()
        if not db:
            return jsonify({"success": False, "error": "Database connection failed"}), 500
        
        try:
            # Find user
            user = db.users.find_one({"email": email})
            logger.info(f"User lookup result: {'Found' if user else 'Not found'}")
            
            if not user:
                return jsonify({"success": False, "error": "Invalid email or password"}), 401
            
            # Get stored password
            stored_password = user.get('password', '')
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')
            
            logger.info(f"Password hash type: {type(stored_password)}, length: {len(stored_password)}")
            
            # Verify password
            password_bytes = password.encode('utf-8')
            password_valid = bcrypt.checkpw(password_bytes, stored_password)
            
            logger.info(f"Password verification result: {password_valid}")
            
            if not password_valid:
                return jsonify({"success": False, "error": "Invalid email or password"}), 401
            
            # Generate session token
            session_token = secrets.token_urlsafe(32)
            
            # Store session
            db.sessions.insert_one({
                "token": session_token,
                "user_id": str(user['_id']),
                "email": email,
                "created_at": datetime.now()
            })
            
            logger.info(f"✅ Signin successful for: {email}")
            
            # Return response matching frontend expectations
            return jsonify({
                "success": True,
                "message": "Signin successful",
                "token": session_token,
                "user": {
                    "id": str(user['_id']),
                    "name": user.get('name', ''),
                    "email": email
                }
            }), 200
            
        finally:
            if client:
                client.close()
        
    except Exception as e:
        logger.error(f"Signin error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"success": False, "error": "Internal server error"}), 500

@app.route('/auth/signup', methods=['POST', 'OPTIONS'])
def signup():
    """Signup endpoint - matches frontend expectations exactly"""
    if request.method == 'OPTIONS':
        return '', 200
    
    logger.info("=== SIGNUP REQUEST ===")
    
    try:
        # Get request data
        data = request.get_json()
        logger.info(f"Request data: {data}")
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        logger.info(f"Signup attempt - Name: {name}, Email: {email}, Password length: {len(password)}")
        
        if not all([name, email, password]):
            return jsonify({"success": False, "error": "Name, email and password are required"}), 400
        
        # Basic validation
        if len(name) < 2:
            return jsonify({"success": False, "error": "Name must be at least 2 characters"}), 400
        
        if '@' not in email or '.' not in email:
            return jsonify({"success": False, "error": "Invalid email format"}), 400
        
        if len(password) < 6:
            return jsonify({"success": False, "error": "Password must be at least 6 characters"}), 400
        
        # Get database
        db, client = get_db()
        if not db:
            return jsonify({"success": False, "error": "Database connection failed"}), 500
        
        try:
            # Check if user already exists
            existing_user = db.users.find_one({"email": email})
            if existing_user:
                logger.warning(f"User already exists: {email}")
                return jsonify({"success": False, "error": "User already exists"}), 409
            
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Create user document
            user_doc = {
                "name": name,
                "email": email,
                "password": password_hash.decode('utf-8'),
                "created_at": datetime.now(),
                "profile": {
                    "resume_text": "",
                    "skills": [],
                    "preferences": {},
                    "mobile": "",
                    "gender": "",
                    "state": "",
                    "employment_status": ""
                }
            }
            
            # Insert user
            result = db.users.insert_one(user_doc)
            logger.info(f"User created with ID: {result.inserted_id}")
            
            # Generate session token for auto-login
            session_token = secrets.token_urlsafe(32)
            
            # Store session
            db.sessions.insert_one({
                "token": session_token,
                "user_id": str(result.inserted_id),
                "email": email,
                "created_at": datetime.now()
            })
            
            logger.info(f"✅ Signup successful for: {email}")
            
            # Return response matching frontend expectations
            return jsonify({
                "success": True,
                "message": "Account created successfully",
                "token": session_token,
                "user": {
                    "id": str(result.inserted_id),
                    "name": name,
                    "email": email
                }
            }), 201
            
        finally:
            if client:
                client.close()
        
    except Exception as e:
        logger.error(f"Signup error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"success": False, "error": "Internal server error"}), 500

@app.route('/auth/verify', methods=['GET', 'OPTIONS'])
def verify_token():
    """Verify authentication token"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({"success": False, "error": "No token provided"}), 401
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Get database
        db, client = get_db()
        if not db:
            return jsonify({"success": False, "error": "Database connection failed"}), 500
        
        try:
            # Find session
            session = db.sessions.find_one({"token": token})
            if not session:
                return jsonify({"success": False, "error": "Invalid token"}), 401
            
            # Find user
            user = db.users.find_one({"email": session['email']})
            if not user:
                return jsonify({"success": False, "error": "User not found"}), 401
            
            return jsonify({
                "success": True,
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
        return jsonify({"success": False, "error": "Internal server error"}), 500

@app.route('/auth/logout', methods=['POST', 'OPTIONS'])
def logout():
    """Logout endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            
            # Get database
            db, client = get_db()
            if db:
                try:
                    # Delete session
                    db.sessions.delete_one({"token": token})
                finally:
                    client.close()
        
        return jsonify({"success": True, "message": "Logged out successfully"}), 200
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({"success": True, "message": "Logged out"}), 200  # Always succeed

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    db, client = get_db()
    if client:
        client.close()
    
    return jsonify({
        "status": "ok", 
        "message": "Auth server running",
        "database": "connected" if db else "disconnected"
    }), 200

@app.route('/', methods=['GET'])
def index():
    """Index endpoint"""
    return jsonify({
        "message": "Complete Auth Server", 
        "status": "running",
        "version": "3.0",
        "endpoints": [
            "POST /auth/signin",
            "POST /auth/signup", 
            "GET /auth/verify",
            "POST /auth/logout",
            "GET /health"
        ]
    }), 200

if __name__ == '__main__':
    logger.info("🚀 Starting Complete Authentication Server v3.0")
    logger.info("🔧 Features:")
    logger.info("  ✅ Proper error handling")
    logger.info("  ✅ Frontend-compatible responses") 
    logger.info("  ✅ Fresh DB connections")
    logger.info("  ✅ Comprehensive logging")
    logger.info("  ✅ CORS enabled")
    
    logger.info("📋 Endpoints:")
    logger.info("  POST /auth/signin - User signin")
    logger.info("  POST /auth/signup - User signup")
    logger.info("  GET /auth/verify - Verify token")
    logger.info("  POST /auth/logout - User logout")
    logger.info("  GET /health - Health check")
    
    logger.info("🌐 Starting server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)