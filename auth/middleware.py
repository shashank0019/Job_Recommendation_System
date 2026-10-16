"""
Authentication middleware for protecting routes
"""
from functools import wraps
from flask import request, jsonify, g
from datetime import datetime
import logging
from auth.models import User, Session
from bson import ObjectId

logger = logging.getLogger(__name__)

def require_auth(f):
    """
    Decorator to require authentication for routes
    Usage: @require_auth above route functions
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            logger.info("🔐 Auth middleware checking request...")
            # Get authorization header
            auth_header = request.headers.get('Authorization')
            logger.info(f"Authorization header present: {bool(auth_header)}")
            if not auth_header:
                logger.warning("❌ No Authorization header")
                return jsonify({'error': 'Authorization header required'}), 401
            
            # Extract token from "Bearer <token>" format
            try:
                token_type, token = auth_header.split(' ', 1)
                logger.info(f"Token type: {token_type}, Token length: {len(token)}")
                if token_type.lower() != 'bearer':
                    logger.warning(f"❌ Invalid token type: {token_type}")
                    return jsonify({'error': 'Invalid authorization format. Use Bearer <token>'}), 401
            except ValueError:
                logger.warning("❌ Failed to parse Authorization header")
                return jsonify({'error': 'Invalid authorization format. Use Bearer <token>'}), 401
            
            # Verify session token
            logger.info(f"Looking up session with token: {token[:20]}...")
            session = Session.find_by_token(token)
            
            if not session:
                logger.warning(f"❌ No session found for token: {token[:20]}...")
                return jsonify({'error': 'Invalid session token'}), 401
            
            logger.info(f"✅ Session found for user_id: {session.user_id}")
            
            # Check if session is expired
            if session.is_expired():
                logger.warning(f"❌ Session expired for user_id: {session.user_id}")
                # Clean up expired session
                session.delete()
                return jsonify({'error': 'Session expired'}), 401
            
            # Get user data by user_id
            from bson import ObjectId
            user_id_str = str(session.user_id)
            
            # Find user by ID - we need to implement this method
            logger.info(f"Looking up user with ID: {user_id_str}")
            user = User.find_by_id(session.user_id)
            
            if not user:
                logger.warning(f"❌ User not found with ID: {user_id_str}")
                return jsonify({'error': 'User not found'}), 401
            
            logger.info(f"✅ User authenticated: {user.email}")
            
            # Store user and session in Flask's g object for use in route
            g.current_user = user
            g.current_session = session
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'error': 'Authentication failed'}), 401
    
    return decorated_function

def optional_auth(f):
    """
    Decorator for optional authentication (user data available if authenticated)
    Usage: @optional_auth above route functions
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Initialize as None
            g.current_user = None
            g.current_session = None
            
            # Get authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return f(*args, **kwargs)
            
            # Extract token from "Bearer <token>" format
            try:
                token_type, token = auth_header.split(' ', 1)
                if token_type.lower() != 'bearer':
                    return f(*args, **kwargs)
            except ValueError:
                return f(*args, **kwargs)
            
            # Verify session token
            session = Session.find_by_token(token)
            
            if session:
                # Check if session is not expired
                if not session.is_expired():
                    # Get user data
                    user = User.find_by_id(session.user_id)
                    
                    if user:
                        g.current_user = user
                        g.current_session = session
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Optional authentication error: {e}")
            # Continue without authentication if error occurs
            return f(*args, **kwargs)
    
    return decorated_function

def get_current_user():
    """Get current authenticated user from Flask's g object"""
    return getattr(g, 'current_user', None)

def get_current_session():
    """Get current session from Flask's g object"""
    return getattr(g, 'current_session', None)

def is_authenticated():
    """Check if current request is authenticated"""
    return get_current_user() is not None