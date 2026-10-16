#!/usr/bin/env python3
"""
Debug signin with detailed error logging
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import traceback

# Setup detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

# Import auth components
from config.database import db_config, get_users_collection, get_sessions_collection
from auth.models import User, Session
from auth.utils import verify_password, generate_session_token

# Connect to database
logger.info("Connecting to database...")
db_config.connect()
logger.info(f"Database connected. Fallback: {db_config.use_local_fallback}")

@app.route('/')
def home():
    return jsonify({'status': 'running', 'message': 'Debug signin server'})

@app.route('/auth/health')
def health():
    try:
        users_collection = get_users_collection()
        count = users_collection.count_documents({})
        return jsonify({
            'module': 'authentication',
            'status': 'healthy', 
            'success': True,
            'users_count': count
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/auth/signin', methods=['POST'])
def debug_signin():
    """Debug signin with detailed logging"""
    logger.info("=== SIGNIN REQUEST STARTED ===")
    
    try:
        # Step 1: Get request data
        logger.info("Step 1: Getting request data...")
        data = request.get_json()
        logger.info(f"Request data: {data}")
        
        if not data:
            logger.error("No data provided")
            return jsonify({'error': 'No data provided'}), 400
        
        # Step 2: Extract credentials
        logger.info("Step 2: Extracting credentials...")
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        logger.info(f"Email: {email}")
        logger.info(f"Password length: {len(password)}")
        
        if not email or not password:
            logger.error("Missing email or password")
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Step 3: Get users collection
        logger.info("Step 3: Getting users collection...")
        users_collection = get_users_collection()
        logger.info("Users collection obtained")
        
        # Step 4: Find user
        logger.info("Step 4: Finding user by email...")
        user_data = users_collection.find_one({'email': email})
        logger.info(f"User found: {user_data is not None}")
        
        if not user_data:
            logger.warning(f"User not found: {email}")
            return jsonify({'error': 'Invalid email or password'}), 401
        
        logger.info(f"User data keys: {list(user_data.keys())}")
        logger.info(f"User _id: {user_data.get('_id')} (type: {type(user_data.get('_id'))})")
        
        # Step 5: Create User object
        logger.info("Step 5: Creating User object...")
        user = User.from_dict(user_data)
        logger.info(f"User object created: {user.email}")
        logger.info(f"User _id in object: {user._id} (type: {type(user._id)})")
        
        # Step 6: Verify password
        logger.info("Step 6: Verifying password...")
        password_valid = verify_password(password, user.password_hash)
        logger.info(f"Password verification result: {password_valid}")
        
        if not password_valid:
            logger.warning("Password verification failed")
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Step 7: Generate session token
        logger.info("Step 7: Generating session token...")
        session_token = generate_session_token()
        logger.info(f"Session token generated: {session_token[:10]}...")
        
        # Step 8: Create session
        logger.info("Step 8: Creating session...")
        logger.info(f"Creating session with user_id: {user._id} (type: {type(user._id)})")
        
        session = Session(user_id=user._id, session_token=session_token)
        logger.info("Session object created")
        logger.info(f"Session user_id: {session.user_id} (type: {type(session.user_id)})")
        
        # Step 9: Insert session
        logger.info("Step 9: Inserting session...")
        sessions_collection = get_sessions_collection()
        logger.info("Sessions collection obtained")
        
        session_dict = session.to_dict()
        logger.info(f"Session dict keys: {list(session_dict.keys())}")
        logger.info(f"Session dict user_id: {session_dict['user_id']} (type: {type(session_dict['user_id'])})")
        
        result = sessions_collection.insert_one(session_dict)
        logger.info(f"Session inserted with ID: {result.inserted_id}")
        
        # Step 10: Update user last login
        logger.info("Step 10: Updating user last login...")
        user.update_last_login()
        users_collection.update_one(
            {'_id': user._id},
            {'$set': {'last_login': user.last_login}}
        )
        logger.info("User last login updated")
        
        # Step 11: Return success
        logger.info("Step 11: Returning success response...")
        response = {
            'success': True,
            'message': 'Signed in successfully',
            'token': session_token,
            'user': user.to_public_dict()
        }
        logger.info("=== SIGNIN REQUEST COMPLETED SUCCESSFULLY ===")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"=== SIGNIN ERROR: {e} ===")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Sign in failed. Please try again.'}), 500

if __name__ == '__main__':
    logger.info("🚀 Starting Debug Signin Server...")
    app.run(host='127.0.0.1', port=5001, debug=True)