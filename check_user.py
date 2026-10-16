#!/usr/bin/env python3
"""
Check if a specific user exists in the database
"""
from config.database import get_db_config
from auth.models import User
import json

def check_user_exists(email):
    print(f"🔍 Checking for user: {email}")
    print("=" * 50)
    
    try:
        db_config = get_db_config()
        if not db_config.connect():
            print("❌ Database connection failed")
            return
        
        print("✅ Database connected successfully")
        
        # Try to find user by email
        user = User.find_by_email(email)
        
        if user:
            print(f"✅ User found!")
            print(f"   ID: {user._id}")
            print(f"   Name: {user.name}")
            print(f"   Email: {user.email}")
            print(f"   Created: {user.created_at}")
            print(f"   Last Login: {user.last_login}")
            return True
        else:
            print(f"❌ User not found with email: {email}")
            
            # List all users to see what's in the database
            print("\n📋 All users in database:")
            if db_config.use_local_fallback:
                with open(db_config.users_file, 'r') as f:
                    users = json.load(f)
            else:
                users_collection = db_config.db.users
                users = list(users_collection.find({}, {'email': 1, 'name': 1, '_id': 1}))
            
            for i, user_data in enumerate(users[:10]):  # Show first 10 users
                print(f"   User {i+1}: {user_data.get('email')} ({user_data.get('name')})")
            
            if len(users) > 10:
                print(f"   ... and {len(users) - 10} more users")
            
            return False
            
    except Exception as e:
        print(f"❌ Error checking user: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_password(email, test_password):
    print(f"\n🔐 Testing password for: {email}")
    try:
        user = User.find_by_email(email)
        if not user:
            print("❌ User not found")
            return False
        
        print(f"✅ User found: {user.name}")
        print(f"   Password hash: {user.password_hash[:30]}...")
        
        # Test password verification
        is_valid = user.verify_password(test_password)
        print(f"   Password '{test_password}' is {'✅ VALID' if is_valid else '❌ INVALID'}")
        
        return is_valid
    except Exception as e:
        print(f"❌ Error testing password: {e}")
        return False

def reset_user_password(email, new_password):
    print(f"\n🔧 Resetting password for: {email}")
    try:
        user = User.find_by_email(email)
        if not user:
            print("❌ User not found")
            return False
        
        # Update password using the auth utils
        from auth.utils import AuthUtils
        user.password_hash = AuthUtils.hash_password(new_password)
        
        # Save the user
        success = user.save()
        if success:
            print(f"✅ Password reset successfully!")
            print(f"   New password: '{new_password}'")
            print(f"   User can now sign in with this password")
            return True
        else:
            print("❌ Failed to save new password")
            return False
    except Exception as e:
        print(f"❌ Error resetting password: {e}")
        return False

def create_test_user(email, name, password):
    print(f"\n🔧 Creating test user: {email}")
    try:
        user = User.create(name=name, email=email, password=password)
        if user:
            print(f"✅ Test user created successfully!")
            print(f"   ID: {user._id}")
            print(f"   Name: {user.name}")
            print(f"   Email: {user.email}")
            return True
        else:
            print("❌ Failed to create test user")
            return False
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return False

if __name__ == "__main__":
    target_email = "vv88610705@gmail.com"
    
    # Check if user exists
    user_exists = check_user_exists(target_email)
    
    if user_exists:
        print(f"\n💡 User {target_email} exists in database.")
        print("Testing common passwords...")
        
        # Test common passwords
        common_passwords = ["password", "123456", "password123", "admin", "shashi", "test"]
        for pwd in common_passwords:
            if test_password(target_email, pwd):
                print(f"\n🎉 SUCCESS! The password is: '{pwd}'")
                break
        else:
            print(f"\n❌ None of the common passwords worked.")
            print("Options:")
            print("1. Remember their correct password")
            print("2. Reset password to a known value (for development)")
            print("3. Create a new account with a different email")
            
            # Offer to reset password for development
            print(f"\n🔧 DEVELOPMENT SOLUTION:")
            print(f"Resetting password to 'password123' for user: {target_email}")
            if reset_user_password(target_email, "password123"):
                print(f"\n🎉 SUCCESS! User can now sign in with:")
                print(f"   Email: {target_email}")
                print(f"   Password: password123")
    else:
        print(f"\n💡 User {target_email} doesn't exist in database.")
        print("Options:")
        print("1. Create this user with a test password")
        print("2. Try signing up through the frontend first")
        print("3. Check if there's a typo in the email")
        
        # Optionally create the user (uncomment if needed)
        # create_test_user(target_email, "Test User", "password123")
