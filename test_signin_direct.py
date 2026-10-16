"""Simple direct test of signin functionality"""
from auth.models import User
from config.database import get_db_config
from auth.utils import AuthUtils
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_signin_logic():
    """Test signin logic directly"""
    logger.info("=== Testing Signin Logic Directly ===")
    
    # Connect to database
    db_config = get_db_config()
    db_config.connect()
    
    # User credentials from frontend
    email = "shashikingmaker495@gmail.com"
    password = "Test@123"
    
    logger.info(f"Testing signin for: {email}")
    logger.info(f"Password: {password}")
    
    # Find user
    user = User.find_by_email(email)
    
    if not user:
        logger.error(f"❌ User not found: {email}")
        return False
    
    logger.info(f"✅ User found: {user.name}")
    logger.info(f"   Password hash: {user.password_hash[:50]}...")
    
    # Verify password
    logger.info(f"\nVerifying password...")
    is_valid = user.verify_password(password)
    
    if is_valid:
        logger.info(f"✅ Password is CORRECT!")
        return True
    else:
        logger.error(f"❌ Password is INCORRECT!")
        
        # Test what the correct hash should be
        logger.info("\n--- Debug Info ---")
        test_hash = AuthUtils.hash_password(password)
        logger.info(f"Test hash for '{password}': {test_hash[:50]}...")
        
        # Verify with new hash
        verify_new = AuthUtils.verify_password(password, test_hash)
        logger.info(f"Can verify with new hash: {verify_new}")
        
        # Try verifying stored hash
        verify_stored = AuthUtils.verify_password(password, user.password_hash)
        logger.info(f"Can verify with stored hash: {verify_stored}")
        
        return False

if __name__ == "__main__":
    result = test_signin_logic()
    
    if result:
        print("\n✅ SIGNIN WOULD WORK")
    else:
        print("\n❌ SIGNIN WOULD FAIL")
