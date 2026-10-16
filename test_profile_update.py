"""
Test script to verify profile updates work in MongoDB Atlas
"""
import os
import sys
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from config.database import get_db_config, get_users_collection

def test_profile_update():
    """Test updating a user profile in MongoDB Atlas"""
    try:
        # Get database connection
        config = get_db_config()
        
        if not config.connect():
            print("❌ Failed to connect to database")
            return False
            
        if config.use_local_fallback:
            print("⚠️  Using local JSON storage instead of MongoDB Atlas")
        else:
            print("✅ Connected to MongoDB Atlas")
        
        # Get users collection
        users_collection = get_users_collection()
        
        # Find your user
        user_email = "shashikingmaker495@gmail.com"
        user = users_collection.find_one({"email": user_email})
        
        if not user:
            print(f"❌ User {user_email} not found")
            return False
            
        print(f"✅ Found user: {user['name']}")
        print(f"📋 Current profile: {user.get('profile', {})}")
        
        # Test update
        test_profile = user.get('profile', {})
        test_profile['mobile'] = '9876543210'
        test_profile['gender'] = 'male'
        test_profile['state'] = 'Karnataka'
        test_profile['employment_status'] = 'working'
        
        print(f"🔄 Updating profile with test data...")
        
        result = users_collection.update_one(
            {'_id': user['_id']},
            {'$set': {'profile': test_profile}}
        )
        
        print(f"📊 Update result - matched: {result.matched_count}, modified: {result.modified_count}")
        
        # Verify the update
        updated_user = users_collection.find_one({"email": user_email})
        print(f"✅ Updated profile: {updated_user.get('profile', {})}")
        
        if result.modified_count > 0:
            print("🎉 Profile update test SUCCESSFUL!")
            return True
        else:
            print("❌ Profile update test FAILED!")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("🧪 Testing profile update in MongoDB Atlas...")
    success = test_profile_update()
    
    if success:
        print("✅ Profile update test completed successfully!")
    else:
        print("❌ Profile update test failed!")
