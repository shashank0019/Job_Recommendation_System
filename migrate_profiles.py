"""
Migration script to add new profile fields to existing users
"""
import os
import sys
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from config.database import get_db_config

def migrate_user_profiles():
    """Add new profile fields to existing users"""
    try:
        # Get database connection
        db_config = get_db_config()
        
        # Initialize connection
        if not db_config.connect():
            print("❌ Failed to connect to database")
            return False
            
        if db_config.use_local_fallback:
            print("ℹ️  Using local JSON storage")
        else:
            print("ℹ️  Using MongoDB Atlas")
        
        # Get users collection (works for both MongoDB and local storage)
        from config.database import get_users_collection
        users_collection = get_users_collection()
        
        # Find all users
        if db_config.use_local_fallback:
            # For local storage, we need to load all data
            users = users_collection._load_data()
        else:
            # For MongoDB
            users = users_collection.find({})
        updated_count = 0
        
        for user in users:
            user_id = user['_id']
            profile = user.get('profile', {})
            
            # Check if profile needs migration
            needs_migration = False
            
            # Add missing fields with default values
            if 'mobile' not in profile:
                profile['mobile'] = ''
                needs_migration = True
            
            if 'gender' not in profile:
                profile['gender'] = ''
                needs_migration = True
                
            if 'state' not in profile:
                profile['state'] = ''
                needs_migration = True
                
            if 'employment_status' not in profile:
                profile['employment_status'] = ''
                needs_migration = True
            
            # Ensure existing fields exist
            if 'resume_text' not in profile:
                profile['resume_text'] = ''
                needs_migration = True
                
            if 'skills' not in profile:
                profile['skills'] = []
                needs_migration = True
                
            if 'preferences' not in profile:
                profile['preferences'] = {}
                needs_migration = True
            
            if needs_migration:
                # Update the user's profile
                result = users_collection.update_one(
                    {'_id': user_id},
                    {'$set': {'profile': profile}}
                )
                
                if result.modified_count > 0:
                    updated_count += 1
                    print(f"✅ Updated profile for user: {user.get('email', 'Unknown')}")
                else:
                    print(f"⚠️  Failed to update profile for user: {user.get('email', 'Unknown')}")
        
        print(f"\n🎉 Migration completed! Updated {updated_count} user profiles.")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("🔄 Starting profile migration...")
    success = migrate_user_profiles()
    
    if success:
        print("✅ Profile migration completed successfully!")
    else:
        print("❌ Profile migration failed!")
