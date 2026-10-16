"""
Authentication routes for signup, signin, logout, and profile management
"""
from flask import Blueprint, request, jsonify, g
from datetime import datetime
import logging
from auth.models import User, Session
from auth.utils import AuthUtils
from auth.middleware import require_auth, get_current_user, get_current_session
from config.database import get_users_collection, get_sessions_collection
from bson import ObjectId

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract and validate input data
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validate required fields
        if not name or not email or not password:
            return jsonify({'error': 'Name, email, and password are required'}), 400
        
        # Validate name
        name_valid, name_error = AuthUtils.validate_name(name)
        if not name_valid:
            return jsonify({'error': name_error}), 400
        
        # Validate email
        if not AuthUtils.validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password
        password_valid, password_error = AuthUtils.validate_password(password)
        if not password_valid:
            return jsonify({'error': password_error}), 400
        
        # Check if user already exists and create new user
        user = User.create(name=name, email=email, password=password)
        
        if not user:
            return jsonify({'error': 'User with this email already exists or registration failed'}), 409
        
        logger.info(f"New user registered: {email}")
        
        # Return success response (without sensitive data)
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': user.to_public_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Signup error: {e}")
        return jsonify({'error': 'Registration failed. Please try again.'}), 500

@auth_bp.route('/signin', methods=['POST'])
def signin():
    """User login endpoint"""
    try:
        logger.info("=== SIGNIN REQUEST RECEIVED ===")
        data = request.get_json()
        logger.info(f"Request data keys: {list(data.keys()) if data else 'None'}")
        
        if not data:
            logger.warning("No data provided in request")
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract input data
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        logger.info(f"Signin attempt for email: {email}")
        logger.info(f"Password provided: {'Yes' if password else 'No'}")
        logger.info(f"Password length: {len(password) if password else 0}")
        
        # Validate required fields
        if not email or not password:
            logger.warning("Email or password missing")
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user by email using the new User model method
        logger.info(f"Looking up user by email: {email}")
        user = User.find_by_email(email)
        
        if not user:
            logger.warning(f"User not found: {email}")
            return jsonify({'error': 'Invalid email or password'}), 401
        
        logger.info(f"User found: {user.name} (ID: {user._id})")
        logger.info(f"Password hash from DB: {user.password_hash[:30]}...")
        
        # Verify password using the User model method
        logger.info(f"Attempting password verification for user: {email}")
        logger.info(f"Password to verify: {password}")
        password_valid = user.verify_password(password)
        logger.info(f"Password verification result: {password_valid}")
        
        if not password_valid:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Create new session using the Session model method
        session = Session.create(user_id=user._id)
        
        if not session:
            logger.error("Failed to create session")
            return jsonify({'error': 'Login failed. Please try again.'}), 500
        
        # Update user's last login
        user.update_last_login()
        user.save()
        
        logger.info(f"User signed in: {email}")
        
        # Return success response with token
        return jsonify({
            'success': True,
            'message': 'Signed in successfully',
            'token': session.session_token,
            'user': user.to_public_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Signin error: {e}")
        import traceback
        logger.error(f"Signin traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Sign in failed. Please try again.'}), 500

@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """User logout endpoint"""
    try:
        current_session = get_current_session()
        current_user = get_current_user()
        
        if current_session:
            # Delete session from database
            sessions_collection = get_sessions_collection()
            sessions_collection.delete_one({'_id': current_session._id})
            
            logger.info(f"User logged out: {current_user.email}")
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'error': 'Logout failed'}), 500

@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """Get user profile endpoint"""
    try:
        current_user = get_current_user()
        
        return jsonify({
            'success': True,
            'user': current_user.to_public_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        return jsonify({'error': 'Failed to get profile'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@require_auth
def update_profile():
    """Update user profile endpoint"""
    try:
        current_user = get_current_user()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract update data
        name = data.get('name')
        resume_text = data.get('resume_text')
        skills = data.get('skills')
        preferences = data.get('preferences')
        mobile = data.get('mobile')
        gender = data.get('gender')
        state = data.get('state')
        employment_status = data.get('employment_status')
        
        
        # Validate name if provided
        if name is not None:
            name = name.strip()
            name_valid, name_error = AuthUtils.validate_name(name)
            if not name_valid:
                return jsonify({'error': name_error}), 400
            current_user.name = name
        
        # Update profile data
        current_user.update_profile(
            resume_text=resume_text,
            skills=skills,
            preferences=preferences,
            mobile=mobile,
            gender=gender,
            state=state,
            employment_status=employment_status
        )
        
        # Update in database
        users_collection = get_users_collection()
        update_data = {}
        if name is not None:
            update_data['name'] = current_user.name
        update_data['profile'] = current_user.profile
        
        logger.info(f"Updating database for user {current_user.email} with data: {update_data}")
        
        result = users_collection.update_one(
            {'_id': current_user._id},
            {'$set': update_data}
        )
        
        logger.info(f"Database update result - matched: {result.matched_count}, modified: {result.modified_count}")
        logger.info(f"Profile updated for user: {current_user.email}")
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'user': current_user.to_public_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Update profile error: {e}")
        return jsonify({'error': 'Failed to update profile'}), 500

@auth_bp.route('/verify', methods=['GET'])
@require_auth
def verify_token():
    """Verify session token endpoint"""
    try:
        current_user = get_current_user()
        current_session = get_current_session()
        
        return jsonify({
            'success': True,
            'valid': True,
            'user': current_user.to_public_dict(),
            'expires_at': current_session.expires_at.isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return jsonify({'error': 'Token verification failed'}), 500

# Health check for auth module
@auth_bp.route('/health', methods=['GET'])
def auth_health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Authentication service is running',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@auth_bp.route('/cleanup/<email>', methods=['DELETE'])
def cleanup_user(email):
    """Delete user by email - for development only"""
    try:
        from config.database import get_db_config
        
        db_config = get_db_config()
        if db_config.db is None:
            return jsonify({'error': 'Database connection not available'}), 500
        
        # Delete user
        users_collection = db_config.db.users
        result = users_collection.delete_one({"email": email.lower()})
        
        # Also delete any sessions for this user
        sessions_collection = db_config.db.sessions
        user = User.find_by_email(email.lower())
        if user:
            sessions_collection.delete_many({"user_id": str(user._id)})
        
        if result.deleted_count > 0:
            logger.info(f"Deleted user: {email}")
            return jsonify({'success': True, 'message': f'User {email} deleted successfully'}), 200
        else:
            return jsonify({'success': False, 'message': f'No user found with email: {email}'}), 404
            
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        return jsonify({'error': 'Failed to delete user'}), 500