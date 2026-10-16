#!/usr/bin/env python3
"""
Ultra-stable Flask authentication server
Uses connection pooling with better error handling to prevent crashes
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pymongo
import bcrypt
import secrets
import logging
from datetime import datetime
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=['http://localhost:5174', 'http://localhost:3000', 'http://localhost:5173'])

# Global MongoDB client with proper connection settings
mongodb_client = None
mongodb_db = None

def init_mongodb():
    """Initialize MongoDB connection with retry logic"""
    global mongodb_client, mongodb_db
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting MongoDB connection (attempt {attempt + 1}/{max_retries})...")
            
            mongodb_client = pymongo.MongoClient(
                "mongodb+srv://Final_project:Atlas11924@cluster0.xseglna.mongodb.net/",
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
                maxPoolSize=5,
                minPoolSize=1,
                maxIdleTimeMS=30000,
                waitQueueMultiple=1
            )
            
            # Test connection
            mongodb_client.admin.command('ping')
            mongodb_db = mongodb_client.career_guidance_platform
            
            logger.info("✅ MongoDB Atlas connected successfully")
            return True
            
        except Exception as e:
            logger.warning(f"MongoDB connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                logger.error("❌ All MongoDB connection attempts failed")
                return False
    
    return False

def get_db_with_retry():
    """Get database with retry logic"""
    global mongodb_db, mongodb_client
    
    if mongodb_db is None:
        if not init_mongodb():
            return None
    
    try:
        # Test if connection is alive
        mongodb_client.admin.command('ping')
        return mongodb_db
    except:
        logger.warning("MongoDB connection lost, reconnecting...")
        if init_mongodb():
            return mongodb_db
        return None

@app.route('/auth/signin', methods=['POST', 'OPTIONS'])
def signin():
    """Signin endpoint with error handling"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        logger.info(f"🔐 Signin attempt for: {email}")
        
        # Get database
        db = get_db_with_retry()
        if not db:
            logger.error("Database connection failed during signin")
            return jsonify({"error": "Database temporarily unavailable"}), 503
        
        # Find user
        user = db.users.find_one({"email": email})
        if not user:
            logger.warning(f"❌ User not found: {email}")
            return jsonify({"success": False, "error": "Invalid email or password"}), 401
        
        # Check password
        stored_password = user.get('password', '')
        if isinstance(stored_password, str):
            stored_password = stored_password.encode('utf-8')
        
        if not stored_password:
            logger.error(f"❌ No password hash for user: {email}")
            return jsonify({"success": False, "error": "Account configuration error"}), 500
        
        password_bytes = password.encode('utf-8')
        
        if bcrypt.checkpw(password_bytes, stored_password):
            # Generate session token
            session_token = secrets.token_urlsafe(32)
            
            # Store session
            try:
                db.sessions.insert_one({
                    "token": session_token,
                    "user_id": str(user['_id']),
                    "email": email,
                    "created_at": datetime.now()
                })
            except Exception as e:
                logger.error(f"Failed to create session: {e}")
                return jsonify({"error": "Session creation failed"}), 500
            
            logger.info(f"✅ Signin successful: {email}")
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
        else:
            # Log some debug info to help diagnose mismatches
            try:
                pwd_preview = stored_password[:20]
                logger.debug(f"Invalid password for {email} - user_id={user.get('_id')} - stored_password_preview={pwd_preview} - stored_length={len(stored_password)}")
            except Exception:
                logger.debug("Invalid password and failed to preview stored hash")

            logger.warning(f"❌ Invalid password for: {email}")
            return jsonify({"success": False, "error": "Invalid email or password"}), 401
        
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
        
        logger.info(f"📝 Signup attempt for: {email}")
        
        # Get database
        db = get_db_with_retry()
        if not db:
            return jsonify({"error": "Database temporarily unavailable"}), 503
        
        # Check if user exists
        if db.users.find_one({"email": email}):
            logger.warning(f"❌ User already exists: {email}")
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
        
        logger.info(f"✅ Signup successful: {email}")
        return jsonify({
            "message": "Signup successful",
            "token": session_token,
            "user": {
                "id": str(result.inserted_id),
                "name": name,
                "email": email
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Signup error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/auth/verify', methods=['GET', 'OPTIONS'])
def verify_token():
    """Verify authentication token"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({"error": "No token provided"}), 401
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Get database
        db = get_db_with_retry()
        if not db:
            return jsonify({"error": "Database temporarily unavailable"}), 503
        
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
        
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        db = get_db_with_retry()
        db_status = "connected" if db else "disconnected"
        return jsonify({
            "status": "ok", 
            "message": "Auth server running",
            "database": db_status
        }), 200
    except:
        return jsonify({
            "status": "ok", 
            "message": "Auth server running",
            "database": "error"
        }), 200

@app.route('/', methods=['GET'])
def index():
    """Index endpoint"""
    return jsonify({
        "message": "Stable Auth Server", 
        "status": "running",
        "version": "2.0"
    }), 200

# Initialize MongoDB on startup
if __name__ == '__main__':
    logger.info("🚀 Starting Stable Authentication Server...")
    
    # Initialize MongoDB
    if init_mongodb():
        logger.info("✅ Database initialized successfully")
    else:
        logger.warning("⚠️  Starting server without database connection (will retry on requests)")
    
    logger.info("📋 Available endpoints:")
    logger.info("  POST /auth/signin - User signin")
    logger.info("  POST /auth/signup - User signup")
    logger.info("  GET /auth/verify - Verify token")
    logger.info("  GET /health - Health check")
    logger.info("  GET / - Server info")
    
    logger.info("🌐 CORS enabled for React frontend on localhost:5174")
    logger.info("🔥 Starting server on http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)