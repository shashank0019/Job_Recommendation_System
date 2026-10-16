"""Debug script to test signup flow"""
from auth.models import User
from config.database import get_db_config
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_signup_flow():
    """Test the signup flow step by step"""
    
    # Initialize database
    logger.info("=== Step 1: Initialize Database ===")
    db_config = get_db_config()
    db_config.connect()
    
    if db_config.db is None:
        logger.error("Database connection failed!")
        return
    
    logger.info(f"Database connected: {db_config.db.name}")
    
    # Test email from frontend
    test_email = "shashikingmaker495@gmail.com"
    test_name = "Shashank"
    test_password = "Test@123"
    
    logger.info(f"\n=== Step 2: Check if user exists ===")
    logger.info(f"Looking for email: {test_email}")
    
    existing_user = User.find_by_email(test_email)
    
    if existing_user:
        logger.warning(f"User already exists: {existing_user.to_public_dict()}")
        logger.info("\nDeleting existing user for clean test...")
        # Delete for clean test
        db_config.db.users.delete_one({'email': test_email})
        logger.info("User deleted")
    else:
        logger.info("User does not exist - good for signup")
    
    logger.info(f"\n=== Step 3: Try to create user ===")
    logger.info(f"Name: {test_name}")
    logger.info(f"Email: {test_email}")
    logger.info(f"Password: {test_password}")
    
    new_user = User.create(name=test_name, email=test_email, password=test_password)
    
    if new_user:
        logger.info(f"✅ User created successfully!")
        logger.info(f"User data: {new_user.to_public_dict()}")
    else:
        logger.error("❌ User creation failed!")
    
    logger.info(f"\n=== Step 4: Verify user was saved ===")
    
    saved_user = User.find_by_email(test_email)
    
    if saved_user:
        logger.info(f"✅ User found in database: {saved_user.to_public_dict()}")
    else:
        logger.error("❌ User not found in database after creation!")
    
    # Check all users in database
    logger.info(f"\n=== Step 5: List all users ===")
    users = db_config.db.users.find()
    for user in users:
        logger.info(f"User: {user.get('name')} - {user.get('email')}")

if __name__ == "__main__":
    test_signup_flow()
