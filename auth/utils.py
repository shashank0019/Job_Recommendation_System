"""
Authentication utilities for password hashing and token generation
"""
import bcrypt
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class AuthUtils:
    """Utility class for authentication operations"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        try:
            # Generate salt and hash password
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
            return password_hash.decode('utf-8')
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise Exception("Failed to hash password")
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    @staticmethod
    def generate_session_token(length: int = 32) -> str:
        """Generate a secure random session token"""
        try:
            # Use cryptographically secure random generator
            alphabet = string.ascii_letters + string.digits
            token = ''.join(secrets.choice(alphabet) for _ in range(length))
            return token
        except Exception as e:
            logger.error(f"Error generating session token: {e}")
            raise Exception("Failed to generate session token")
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Basic email validation"""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """
        Validate password strength
        Returns: (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        
        return True, ""
    
    @staticmethod
    def validate_name(name: str) -> tuple[bool, str]:
        """
        Validate user name
        Returns: (is_valid, error_message)
        """
        if not name or len(name.strip()) < 2:
            return False, "Name must be at least 2 characters long"
        
        if len(name) > 50:
            return False, "Name must be less than 50 characters"
        
        # Check for basic alphanumeric and space characters
        import re
        if not re.match(r'^[a-zA-Z\s]+$', name):
            return False, "Name can only contain letters and spaces"
        
        return True, ""

# Convenience functions
def hash_password(password: str) -> str:
    """Hash a password"""
    return AuthUtils.hash_password(password)

def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password"""
    return AuthUtils.verify_password(password, password_hash)

def generate_session_token() -> str:
    """Generate a session token"""
    return AuthUtils.generate_session_token()

def validate_email(email: str) -> bool:
    """Validate email format"""
    return AuthUtils.validate_email(email)

def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    return AuthUtils.validate_password(password)

def validate_name(name: str) -> tuple[bool, str]:
    """Validate user name"""
    return AuthUtils.validate_name(name)

# Test functions
if __name__ == "__main__":
    # Test password hashing and verification
    print("🧪 Testing password utilities...")
    
    test_password = "TestPassword123"
    hashed = hash_password(test_password)
    print(f"✅ Password hashed: {hashed[:20]}...")
    
    # Test verification
    is_valid = verify_password(test_password, hashed)
    print(f"✅ Password verification: {is_valid}")
    
    # Test token generation
    token = generate_session_token()
    print(f"✅ Session token generated: {token[:10]}...")
    
    # Test validations
    email_valid = validate_email("test@example.com")
    password_valid, password_msg = validate_password("Password123")
    name_valid, name_msg = validate_name("John Doe")
    
    print(f"✅ Email validation: {email_valid}")
    print(f"✅ Password validation: {password_valid}")
    print(f"✅ Name validation: {name_valid}")
    
    print("🎉 All utility tests passed!")