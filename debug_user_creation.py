#!/usr/bin/env python3

"""
Debug user creation process step by step
"""

def debug_user_creation():
    print("🔍 Debugging user creation process...")
    
    try:
        # Step 1: Test database connection
        print("\n1️⃣ Testing database connection...")
        from config.database import get_db_config
        db_config = get_db_config()
        
        if not db_config.connect():
            print("❌ Failed to connect to database")
            return
            
        print("✅ Database connection successful")
        print(f"   Using local fallback: {db_config.use_local_fallback}")
        
        # Step 2: Test email lookup
        print("\n2️⃣ Testing email lookup...")
        from auth.models import User
        
        test_email = "nonexistent@example.com"
        existing_user = User.find_by_email(test_email)
        print(f"   Looking for {test_email}: {'Found' if existing_user else 'Not found'} ✅")
        
        # Test with existing email
        existing_email = "test@example.com"
        existing_user2 = User.find_by_email(existing_email)
        print(f"   Looking for {existing_email}: {'Found' if existing_user2 else 'Not found'}")
        if existing_user2:
            print(f"      Name: {existing_user2.name}")
            print(f"      Email: {existing_user2.email}")
        
        # Step 3: Test password validation
        print("\n3️⃣ Testing password validation...")
        from auth.utils import AuthUtils
        
        test_password = "TestPassword123!"
        is_valid, error = AuthUtils.validate_password(test_password)
        print(f"   Password '{test_password}': {'Valid' if is_valid else f'Invalid - {error}'}")
        
        # Step 4: Test user creation with unique email
        print("\n4️⃣ Testing user creation...")
        import time
        unique_email = f"debug{int(time.time())}@test.com"
        
        print(f"   Creating user with email: {unique_email}")
        
        # Check if email exists first
        check_existing = User.find_by_email(unique_email)
        print(f"   Email exists check: {'Exists' if check_existing else 'Available'} ✅")
        
        if not check_existing:
            # Try to create user
            new_user = User.create(
                name="Debug Test User",
                email=unique_email,
                password=test_password
            )
            
            if new_user:
                print(f"   ✅ User created successfully!")
                print(f"      ID: {new_user._id}")
                print(f"      Name: {new_user.name}")
                print(f"      Email: {new_user.email}")
                
                # Test password verification
                print("\n5️⃣ Testing password verification...")
                is_password_valid = new_user.verify_password(test_password)
                print(f"   Password verification: {'✅ Valid' if is_password_valid else '❌ Invalid'}")
                
                # Test signin process
                print("\n6️⃣ Testing signin process...")
                signin_user = User.find_by_email(unique_email)
                if signin_user:
                    signin_valid = signin_user.verify_password(test_password)
                    print(f"   Signin lookup: ✅ Found user")
                    print(f"   Signin password: {'✅ Valid' if signin_valid else '❌ Invalid'}")
                    
                    if signin_valid:
                        # Create session
                        from auth.models import Session
                        session = Session.create(signin_user._id)
                        if session:
                            print(f"   ✅ Session created: {session.session_token[:20]}...")
                        else:
                            print(f"   ❌ Session creation failed")
                else:
                    print(f"   ❌ Could not find user for signin")
                    
            else:
                print(f"   ❌ User creation failed")
        else:
            print(f"   ⚠️ Email already exists, skipping creation")
            
        # Step 5: List all users
        print("\n7️⃣ Current users in database...")
        if not db_config.use_local_fallback:
            users_collection = db_config.db.users
            user_count = users_collection.count_documents({})
            print(f"   Total users: {user_count}")
            
            # Show last 3 users
            recent_users = list(users_collection.find({}).sort('created_at', -1).limit(3))
            for i, user_data in enumerate(recent_users):
                print(f"   User {i+1}: {user_data.get('name')} ({user_data.get('email')})")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_user_creation()
