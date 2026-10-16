#!/usr/bin/env python3
"""
Direct authentication test - bypassing server completely
Tests user credentials directly against MongoDB Atlas
"""

import pymongo
import bcrypt
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_user_authentication():
    """Test user authentication directly"""
    try:
        # Connect to MongoDB Atlas directly
        logger.info("🔌 Connecting to MongoDB Atlas...")
        client = pymongo.MongoClient(
            "mongodb+srv://Final_project:Atlas11924@cluster0.xseglna.mongodb.net/",
            serverSelectionTimeoutMS=10000
        )
        
        # Get database
        db = client.career_guidance_platform
        
        # Test connection
        client.admin.command('ping')
        logger.info("✅ MongoDB Atlas connection successful")
        
        # Test credentials
        email = "shashikingmaker495@gmail.com"
        password = "password123"
        
        logger.info(f"🔍 Looking for user: {email}")
        
        # Find user
        users_collection = db.users
        user = users_collection.find_one({"email": email})
        
        if not user:
            logger.error(f"❌ User not found: {email}")
            return False
            
        logger.info(f"✅ User found: {user.get('name', 'No name')} ({email})")
        
        # Check password
        stored_password = user.get('password', '')
        logger.info(f"📝 Password type: {type(stored_password)}")
        
        if isinstance(stored_password, str):
            stored_password = stored_password.encode('utf-8')
        
        password_bytes = password.encode('utf-8')
        
        if bcrypt.checkpw(password_bytes, stored_password):
            logger.info("🎉 PASSWORD MATCH! Authentication successful!")
            
            # Show user details
            logger.info(f"User Details:")
            logger.info(f"  ID: {user['_id']}")
            logger.info(f"  Name: {user.get('name', 'N/A')}")
            logger.info(f"  Email: {user.get('email', 'N/A')}")
            logger.info(f"  Created: {user.get('created_at', 'N/A')}")
            
            return True
        else:
            logger.error("❌ PASSWORD MISMATCH! Authentication failed!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Authentication test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            client.close()
            logger.info("🔌 MongoDB connection closed")
        except:
            pass

if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("DIRECT AUTHENTICATION TEST")
    logger.info("=" * 50)
    
    success = test_user_authentication()
    
    logger.info("=" * 50)
    if success:
        logger.info("✅ RESULT: SIGNIN CREDENTIALS ARE VALID!")
        logger.info("The user can successfully sign in with:")
        logger.info("  Email: shashikingmaker495@gmail.com")
        logger.info("  Password: password123")
    else:
        logger.info("❌ RESULT: SIGNIN CREDENTIALS ARE INVALID!")
    logger.info("=" * 50)