"""
Reset password for a specific user
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pymongo import MongoClient
import bcrypt
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def reset_user_password(email, new_password):
    """Reset user password in MongoDB"""
    try:
        # MongoDB Atlas connection
        connection_string = "mongodb+srv://Final_project:Atlas11924@cluster0.xseglna.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        db = client.career_guidance_platform
        
        # Hash the new password
        hashed_password = hash_password(new_password)
        
        # Update user password
        result = db.users.update_one(
            {"email": email.lower()},
            {"$set": {"password_hash": hashed_password}}
        )
        
        if result.modified_count > 0:
            logger.info(f"✅ Password updated for user: {email}")
            logger.info(f"   New password: {new_password}")
            client.close()
            return True
        else:
            logger.error(f"❌ No user found with email: {email}")
            client.close()
            return False
        
    except Exception as e:
        logger.error(f"Error resetting password: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python reset_password.py <email> <new_password>")
        sys.exit(1)
    
    email = sys.argv[1].strip().lower()
    password = sys.argv[2].strip()
    
    success = reset_user_password(email, password)
    
    if success:
        print(f"\n🎉 Password reset successful!")
        print(f"Email: {email}")
        print(f"New Password: {password}")
        print("\nYou can now sign in with these credentials!")
    else:
        print(f"\n❌ Failed to reset password for '{email}'")