"""
Create multiple test users for easy login
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

def create_test_users():
    """Create multiple test users"""
    try:
        # MongoDB Atlas connection
        connection_string = "mongodb+srv://Final_project:Atlas11924@cluster0.xseglna.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        db = client.career_guidance_platform
        
        # List of test users to create
        test_users = [
            {
                'name': 'Shashank C A',
                'email': 'shashikingmaker495@gmail.com',
                'password': 'MyPassword123!'
            },
            {
                'name': 'Test User 1',
                'email': 'test1@example.com',
                'password': 'password123'
            },
            {
                'name': 'Test User 2', 
                'email': 'test2@example.com',
                'password': 'password123'
            },
            {
                'name': 'Demo User',
                'email': 'demo@example.com',
                'password': 'demo123'
            },
            {
                'name': 'Admin User',
                'email': 'admin@example.com',
                'password': 'admin123'
            },
            {
                'name': 'John Doe',
                'email': 'john@example.com',
                'password': 'john123'
            }
        ]
        
        created_count = 0
        skipped_count = 0
        
        for user_data in test_users:
            # Check if user already exists
            existing = db.users.find_one({'email': user_data['email']})
            
            if existing:
                logger.info(f"⏭️  User {user_data['email']} already exists, skipping...")
                skipped_count += 1
                continue
            
            # Create new user document
            user_doc = {
                'name': user_data['name'],
                'email': user_data['email'],
                'password_hash': hash_password(user_data['password']),
                'created_at': datetime.utcnow(),
                'last_login': None,
                'profile': {
                    'resume_text': '',
                    'skills': [],
                    'preferences': {},
                    'mobile': '',
                    'gender': '',
                    'state': '',
                    'employment_status': ''
                }
            }
            
            # Insert user
            result = db.users.insert_one(user_doc)
            
            if result.inserted_id:
                logger.info(f"✅ Created user: {user_data['email']} (password: {user_data['password']})")
                created_count += 1
            else:
                logger.error(f"❌ Failed to create user: {user_data['email']}")
        
        # Show summary
        total_users = db.users.count_documents({})
        logger.info(f"\n📊 SUMMARY:")
        logger.info(f"  - Created: {created_count} new users")
        logger.info(f"  - Skipped: {skipped_count} existing users")
        logger.info(f"  - Total users in database: {total_users}")
        
        # List all users for easy reference
        logger.info(f"\n👥 ALL AVAILABLE LOGIN ACCOUNTS:")
        all_users = list(db.users.find({}, {"email": 1, "name": 1}))
        for user in all_users:
            email = user.get('email', 'no email')
            name = user.get('name', 'no name')
            
            # Show password for test accounts
            if email in [u['email'] for u in test_users]:
                test_user = next((u for u in test_users if u['email'] == email), None)
                if test_user:
                    logger.info(f"  📧 {email} | 👤 {name} | 🔑 {test_user['password']}")
                else:
                    logger.info(f"  📧 {email} | 👤 {name}")
            else:
                logger.info(f"  📧 {email} | 👤 {name}")
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"Error creating test users: {e}")
        return False

if __name__ == "__main__":
    success = create_test_users()
    
    if success:
        print(f"\n🎉 Test users setup completed!")
        print("You can now login with any of the emails listed above.")
        print("\n💡 QUICK LOGIN OPTIONS:")
        print("  Email: shashikingmaker495@gmail.com | Password: MyPassword123!")
        print("  Email: demo@example.com | Password: demo123")
        print("  Email: admin@example.com | Password: admin123")
    else:
        print(f"\n❌ Failed to create test users")