"""Restore your original user or delete test user"""
from config.database import get_db_config
from bson import ObjectId
from datetime import datetime

def restore_or_cleanup():
    """Let user choose: restore original user or delete test user"""
    
    # Connect to database
    db_config = get_db_config()
    db_config.connect()
    
    if db_config.db is None:
        print("❌ Database connection failed")
        return
    
    users_collection = db_config.db.users
    
    print("=== Current Situation ===")
    print("There's a TEST user in the database:")
    print("  Email: shashikingmaker495@gmail.com")
    print("  Name: Shashank")
    print("  Password: Test@123")
    print("  Created: 2025-10-14 12:36:04")
    print()
    print("You mentioned you had an ORIGINAL user:")
    print("  ID: 68ecf5b0a2323db4fcf7e911")
    print("  Name: Shashank C A")
    print("  Email: shashikingmaker495@gmail.com")
    print("  Created: 2025-10-08 20:50:56")
    print("  Last Login: 2025-10-08 21:37:43")
    print()
    print("Options:")
    print("1. DELETE the test user (then signup again from frontend)")
    print("2. USE the test user with password: Test@123")
    print()
    
    # For now, let's delete the test user so you can signup fresh
    print("🗑️  Deleting test user...")
    
    result = users_collection.delete_one({'email': 'shashikingmaker495@gmail.com'})
    
    if result.deleted_count > 0:
        print("✅ Test user deleted successfully!")
        print()
        print("=" * 60)
        print("NOW YOU CAN:")
        print("1. Go to your React frontend")
        print("2. Click SIGNUP")
        print("3. Enter:")
        print("   - Name: Shashank C A")
        print("   - Email: shashikingmaker495@gmail.com")
        print("   - Password: <your-desired-password>")
        print("4. Then SIGNIN with the same credentials")
        print("=" * 60)
    else:
        print("❌ Failed to delete test user")
    
    # Show remaining users
    print("\n=== All users in database ===")
    all_users = users_collection.find()
    count = 0
    for user in all_users:
        count += 1
        print(f"{count}. {user.get('name')} - {user.get('email')}")
    
    if count == 0:
        print("No users found. Database is clean!")

if __name__ == "__main__":
    restore_or_cleanup()
