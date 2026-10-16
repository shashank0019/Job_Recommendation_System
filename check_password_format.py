#!/usr/bin/env python3
"""
Check password hash format in database
"""

import pymongo
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_password_format():
    """Check the actual password format in database"""
    try:
        # Connect to MongoDB Atlas
        logger.info("🔌 Connecting to MongoDB Atlas...")
        client = pymongo.MongoClient(
            "mongodb+srv://Final_project:Atlas11924@cluster0.xseglna.mongodb.net/",
            serverSelectionTimeoutMS=10000
        )
        
        db = client.career_guidance_platform
        client.admin.command('ping')
        logger.info("✅ MongoDB Atlas connected")
        
        # Find the user
        email = "shashikingmaker495@gmail.com"
        users_collection = db.users
        user = users_collection.find_one({"email": email})
        
        if user:
            logger.info(f"✅ User found: {user.get('name', 'No name')}")
            
            # Check password field
            password_field = user.get('password', '')
            logger.info(f"Password field type: {type(password_field)}")
            logger.info(f"Password field length: {len(password_field)}")
            logger.info(f"Password field (first 20 chars): {str(password_field)[:20]}...")
            
            # Check if it's a valid bcrypt hash
            if isinstance(password_field, str):
                logger.info(f"Password starts with: {password_field[:10]}")
                if password_field.startswith('$2b$') or password_field.startswith('$2a$'):
                    logger.info("✅ Password appears to be bcrypt format")
                else:
                    logger.info("❌ Password is NOT in bcrypt format")
                    logger.info("This explains why bcrypt.checkpw() is failing")
            elif isinstance(password_field, bytes):
                logger.info(f"Password is bytes, starts with: {password_field[:10]}")
            
        else:
            logger.error(f"❌ User not found: {email}")
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            client.close()
        except:
            pass

if __name__ == '__main__':
    check_password_format()