"""
Bulletproof Authentication Server - Minimal Flask server for signin
No unnecessary features, just the basics that work.
"""

import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Enable CORS for React frontend
CORS(app, 
     origins=['http://localhost:5174', 'http://localhost:3000'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization'],
     supports_credentials=True)

# MongoDB Atlas connection - single connection
MONGO_URI = "mongodb+srv://Final_project:Atlas11924@cluster0.xseglna.mongodb.net/"
db = None

def init_db():
    """Initialize database connection"""
    global db
    try:
        logger.info("Connecting to MongoDB...")
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')  # Test connection
        db = client['job_portal']
        logger.info("✅ Database connected successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

@app.route('/health', methods=['GET'])
def health():
    """Simple health check"""
    return jsonify({'status': 'ok', 'message': 'Server is running'})

@app.route('/auth/signin', methods=['POST'])
def signin():
    """Handle user signin"""
    try:
        logger.info("🔑 Signin request received")
        
        # Get request data
        data = request.get_json()
        if not data:
            logger.error("No JSON data received")
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        logger.info(f"📧 Email: {email}")
        
        if not email or not password:
            logger.error("Missing email or password")
            return jsonify({'error': 'Email and password required'}), 400
        
        # Find user in database
        logger.info("🔍 Looking up user in database...")
        user = db.users.find_one({'email': email})
        
        if not user:
            logger.error(f"❌ User not found: {email}")
            return jsonify({'error': 'Invalid credentials'}), 401
        
        logger.info(f"✅ User found: {user.get('name', 'Unknown')}")
        
        # Check password
        stored_password = user.get('password', '')
        
        # Try bcrypt verification first
        try:
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                logger.info("✅ Password verified with bcrypt")
                password_match = True
            else:
                password_match = False
        except Exception as bcrypt_error:
            logger.warning(f"bcrypt failed, trying plain text: {bcrypt_error}")
            # Fallback to plain text comparison
            password_match = (password == stored_password)
        
        if not password_match:
            logger.error("❌ Password verification failed")
            return jsonify({'error': 'Invalid credentials'}), 401
        
        logger.info("🎉 Authentication successful!")
        
        # Return success response
        response_data = {
            'message': 'Signin successful',
            'user': {
                'id': str(user['_id']),
                'name': user.get('name', ''),
                'email': user.get('email', ''),
            }
        }
        
        logger.info("📤 Sending success response")
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"💥 Signin error: {e}")
        logger.exception("Full traceback:")
        return jsonify({'error': 'Server error during signin'}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 BULLETPROOF AUTH SERVER STARTING")
    print("=" * 50)
    
    # Initialize database
    if not init_db():
        print("❌ Failed to connect to database. Exiting.")
        sys.exit(1)
    
    print("✅ Server ready!")
    print("🌐 Access at: http://localhost:5000")
    print("🔗 Health check: http://localhost:5000/health")
    print("=" * 50)
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        sys.exit(1)