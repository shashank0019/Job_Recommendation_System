#!/usr/bin/env python3
"""
Fix password hash - properly hash password123 and update database
"""

import pymongo
import bcrypt
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_password():
    """Fix password hash in database"""
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
        
        # Generate proper bcrypt hash
        password = "password123"
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)
        
        logger.info(f"Generated bcrypt hash: {hashed_password.decode('utf-8')[:30]}...")
        
        # Update user password
        email = "shashikingmaker495@gmail.com"
        users_collection = db.users
        
        result = users_collection.update_one(
            {"email": email},
            {"$set": {"password": hashed_password.decode('utf-8')}}
        )
        
        if result.modified_count > 0:
            logger.info("✅ Password hash updated successfully")
            
            # Verify the update worked
            user = users_collection.find_one({"email": email})
            if user:
                updated_password = user.get('password', '')
                logger.info(f"Verification - password length: {len(updated_password)}")
                logger.info(f"Verification - starts with: {updated_password[:10]}")
                
                # Test the new password
                if bcrypt.checkpw(password_bytes, updated_password.encode('utf-8')):
                    logger.info("🎉 PASSWORD VERIFICATION SUCCESSFUL!")
                    logger.info("User can now sign in with:")
                    logger.info(f"  Email: {email}")
                    logger.info(f"  Password: {password}")
                else:
                    logger.error("❌ Password verification failed")
            else:
                logger.error("❌ User not found after update")
        else:
            logger.error("❌ Password update failed - no documents modified")
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            client.close()
            logger.info("🔌 MongoDB connection closed")
        except:
            pass

if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("FIXING PASSWORD HASH")
    logger.info("=" * 50)
    fix_password()
    logger.info("=" * 50)