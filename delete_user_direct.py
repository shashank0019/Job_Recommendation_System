"""
Direct MongoDB user deletion script
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pymongo import MongoClient
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def delete_user_by_email(email):
    """Delete user directly from MongoDB"""
    try:
        # MongoDB Atlas connection
        connection_string = "mongodb+srv://Final_project:Atlas11924@cluster0.xseglna.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        db = client.career_guidance_platform
        
        # Delete from users collection
        users_result = db.users.delete_many({"email": email.lower()})
        
        # Delete from sessions collection
        sessions_result = db.sessions.delete_many({"email": email.lower()})
        
        logger.info(f"✅ Deleted {users_result.deleted_count} users with email: {email}")
        logger.info(f"✅ Deleted {sessions_result.deleted_count} sessions for email: {email}")
        
        # Also show all users for verification
        all_users = list(db.users.find({}, {"email": 1, "name": 1}))
        logger.info(f"Remaining users in database: {len(all_users)}")
        for user in all_users:
            logger.info(f"  - {user.get('email', 'no email')} ({user.get('name', 'no name')})")
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python delete_user_direct.py <email>")
        sys.exit(1)
    
    email = sys.argv[1].strip().lower()
    success = delete_user_by_email(email)
    
    if success:
        print(f"\n🎉 User '{email}' deleted successfully!")
        print("You can now sign up with this email or any new email.")
    else:
        print(f"\n❌ Failed to delete user '{email}'")