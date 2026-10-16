"""
Check if a specific email exists in the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pymongo import MongoClient
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_user_exists(email):
    """Check if user exists in MongoDB"""
    try:
        # MongoDB Atlas connection
        connection_string = "mongodb+srv://Final_project:Atlas11924@cluster0.xseglna.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        db = client.career_guidance_platform
        
        # Check if user exists
        user = db.users.find_one({"email": email.lower()})
        
        if user:
            logger.info(f"✅ User EXISTS: {email}")
            logger.info(f"   Name: {user.get('name', 'No name')}")
            logger.info(f"   Created: {user.get('created_at', 'No date')}")
            logger.info(f"   ID: {user.get('_id', 'No ID')}")
            client.close()
            return True
        else:
            logger.info(f"❌ User DOES NOT EXIST: {email}")
            client.close()
            return False
        
    except Exception as e:
        logger.error(f"Error checking user: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_user_exists.py <email>")
        sys.exit(1)
    
    email = sys.argv[1].strip().lower()
    exists = check_user_exists(email)
    
    if exists:
        print(f"\n🟢 The email '{email}' IS ALREADY REGISTERED in the database.")
        print("This is why you're getting a 409 CONFLICT error.")
        print("Either:")
        print("  1. Use a different email for signup")
        print("  2. Try signing in with this email instead")
    else:
        print(f"\n🔴 The email '{email}' is NOT in the database.")
        print("You should be able to sign up with this email.")