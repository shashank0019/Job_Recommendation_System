"""
User and Session models for MongoDB
"""
from datetime import datetime, timedelta
from bson import ObjectId
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class User:
    """User model for MongoDB operations"""
    
    def __init__(self, name: str, email: str, password_hash: str, **kwargs):
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.last_login = kwargs.get('last_login', None)
        self.profile = kwargs.get('profile', {
            'resume_text': '',
            'skills': [],
            'preferences': {},
            'mobile': '',
            'gender': '',
            'state': '',
            'employment_status': ''  # 'working' or 'student'
        })
        self._id = kwargs.get('_id', None)
    
    @staticmethod
    def find_by_email(email: str) -> Optional['User']:
        """Find user by email"""
        try:
            from config.database import get_db_config
            db_config = get_db_config()
            
            if db_config.db is None:
                logger.error("Database connection not available")
                return None
            
            users_collection = db_config.db.users
            user_data = users_collection.find_one({'email': email})
            
            if user_data:
                return User.from_dict(user_data)
            return None
            
        except Exception as e:
            logger.error(f"Error finding user by email: {e}")
            return None
    
    @staticmethod
    def find_by_id(user_id) -> Optional['User']:
        """Find user by ID"""
        try:
            from config.database import get_db_config
            from bson import ObjectId
            
            db_config = get_db_config()
            
            if db_config.db is None:
                logger.error("Database connection not available")
                return None
            
            # Handle both string and ObjectId types
            if isinstance(user_id, str):
                user_id = ObjectId(user_id) if len(user_id) == 24 else user_id
            
            users_collection = db_config.db.users
            user_data = users_collection.find_one({'_id': user_id})
            
            if user_data:
                return User.from_dict(user_data)
            return None
            
        except Exception as e:
            logger.error(f"Error finding user by ID: {e}")
            return None
    
    @staticmethod
    def create(name: str, email: str, password: str) -> Optional['User']:
        """Create a new user"""
        try:
            from config.database import get_db_config
            from auth.utils import AuthUtils
            
            db_config = get_db_config()
            
            if db_config.db is None:
                logger.error("Database connection not available")
                return None
            
            # Check if user already exists
            if User.find_by_email(email):
                logger.warning(f"User with email {email} already exists")
                return None
            
            # Hash the password
            password_hash = AuthUtils.hash_password(password)
            
            # Create user object
            user = User(name=name, email=email, password_hash=password_hash)
            
            # Insert into database
            users_collection = db_config.db.users
            result = users_collection.insert_one(user.to_dict())
            
            if result.inserted_id:
                user._id = result.inserted_id
                logger.info(f"User created successfully: {email}")
                return user
            else:
                logger.error("Failed to insert user into database")
                return None
                
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    def save(self) -> bool:
        """Save user to database"""
        try:
            from config.database import get_db_config
            db_config = get_db_config()
            
            if db_config.db is None:
                logger.error("Database connection not available")
                return False
            
            users_collection = db_config.db.users
            
            if self._id:
                # Update existing user
                result = users_collection.update_one(
                    {'_id': self._id},
                    {'$set': self.to_dict()}
                )
                return result.modified_count > 0
            else:
                # Insert new user
                result = users_collection.insert_one(self.to_dict())
                if result.inserted_id:
                    self._id = result.inserted_id
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error saving user: {e}")
            return False
    
    def verify_password(self, password: str) -> bool:
        """Verify password against stored hash"""
        try:
            from auth.utils import AuthUtils
            return AuthUtils.verify_password(password, self.password_hash)
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user object to dictionary for MongoDB"""
        user_dict = {
            'name': self.name,
            'email': self.email,
            'password_hash': self.password_hash,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'profile': self.profile
        }
        if self._id:
            user_dict['_id'] = self._id
        return user_dict
    
    def to_public_dict(self) -> Dict[str, Any]:
        """Convert user object to public dictionary (without sensitive data)"""
        return {
            'id': str(self._id) if self._id else None,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'profile': self.profile
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create User object from dictionary"""
        from datetime import datetime
        
        # Parse datetime strings if they exist
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at)
            except:
                created_at = None
        
        last_login = data.get('last_login')
        if isinstance(last_login, str):
            try:
                last_login = datetime.fromisoformat(last_login)
            except:
                last_login = None
        
        # Ensure profile has all required fields for backward compatibility
        profile = data.get('profile', {})
        default_profile = {
            'resume_text': '',
            'skills': [],
            'preferences': {},
            'mobile': '',
            'gender': '',
            'state': '',
            'employment_status': ''
        }
        # Merge existing profile with defaults
        for key, default_value in default_profile.items():
            if key not in profile:
                profile[key] = default_value
        
        return cls(
            name=data['name'],
            email=data['email'],
            password_hash=data['password_hash'],
            created_at=created_at,
            last_login=last_login,
            profile=profile,
            _id=data.get('_id')
        )
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
    
    def update_profile(self, resume_text: str = None, skills: list = None, preferences: dict = None, 
                      mobile: str = None, gender: str = None, state: str = None, employment_status: str = None):
        """Update user profile"""
        if resume_text is not None:
            self.profile['resume_text'] = resume_text
        if skills is not None:
            self.profile['skills'] = skills
        if preferences is not None:
            self.profile['preferences'] = preferences
        if mobile is not None:
            self.profile['mobile'] = mobile
        if gender is not None:
            self.profile['gender'] = gender
        if state is not None:
            self.profile['state'] = state
        if employment_status is not None:
            self.profile['employment_status'] = employment_status

class Session:
    """Session model for MongoDB operations"""
    
    def __init__(self, user_id, session_token: str, expires_in_hours: int = 24, **kwargs):
        # Handle both string and ObjectId types
        if isinstance(user_id, str):
            from bson import ObjectId
            self.user_id = ObjectId(user_id) if len(user_id) == 24 else user_id
        else:
            self.user_id = user_id
        self.session_token = session_token
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.expires_at = kwargs.get('expires_at', self.created_at + timedelta(hours=expires_in_hours))
        self._id = kwargs.get('_id', None)
    
    @staticmethod
    def create(user_id, expires_in_hours: int = 24) -> Optional['Session']:
        """Create a new session"""
        try:
            from config.database import get_db_config
            from auth.utils import AuthUtils
            
            db_config = get_db_config()
            
            if db_config.db is None:
                logger.error("Database connection not available")
                return None
            
            # Generate session token
            session_token = AuthUtils.generate_session_token()
            
            # Create session object
            session = Session(user_id=user_id, session_token=session_token, expires_in_hours=expires_in_hours)
            
            # Insert into database
            sessions_collection = db_config.db.sessions
            result = sessions_collection.insert_one(session.to_dict())
            
            if result.inserted_id:
                session._id = result.inserted_id
                logger.info(f"Session created successfully for user: {user_id}")
                return session
            else:
                logger.error("Failed to insert session into database")
                return None
                
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return None
    
    @staticmethod
    def find_by_token(session_token: str) -> Optional['Session']:
        """Find session by token"""
        try:
            from config.database import get_db_config
            db_config = get_db_config()
            
            if db_config.db is None:
                logger.error("Database connection not available")
                return None
            
            sessions_collection = db_config.db.sessions
            session_data = sessions_collection.find_one({'session_token': session_token})
            
            if session_data:
                return Session.from_dict(session_data)
            return None
            
        except Exception as e:
            logger.error(f"Error finding session by token: {e}")
            return None
    
    def delete(self) -> bool:
        """Delete session from database"""
        try:
            from config.database import get_db_config
            db_config = get_db_config()
            
            if db_config.db is None:
                logger.error("Database connection not available")
                return False
            
            sessions_collection = db_config.db.sessions
            
            if self._id:
                result = sessions_collection.delete_one({'_id': self._id})
                return result.deleted_count > 0
            else:
                result = sessions_collection.delete_one({'session_token': self.session_token})
                return result.deleted_count > 0
                
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session object to dictionary for MongoDB"""
        session_dict = {
            'user_id': self.user_id,
            'session_token': self.session_token,
            'created_at': self.created_at,
            'expires_at': self.expires_at
        }
        if self._id:
            session_dict['_id'] = self._id
        return session_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """Create Session object from dictionary"""
        from datetime import datetime
        
        # Parse datetime strings if they exist
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at)
            except:
                created_at = None
        
        expires_at = data.get('expires_at')
        if isinstance(expires_at, str):
            try:
                expires_at = datetime.fromisoformat(expires_at)
            except:
                expires_at = None
        
        return cls(
            user_id=data['user_id'],
            session_token=data['session_token'],
            created_at=created_at,
            expires_at=expires_at,
            _id=data.get('_id')
        )
    
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at
    
    def extend_session(self, hours: int = 24):
        """Extend session expiration"""
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)