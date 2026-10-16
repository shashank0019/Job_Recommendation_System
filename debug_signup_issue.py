#!/usr/bin/env python3

"""
Debug the specific signup issue
"""

def debug_signup_issue():
    print("🔍 Debugging signup issue...")
    
    try:
        import time
        from auth.models import User
        from config.database import get_db_config
        
        # Test database connection
        print("\n1️⃣ Testing database connection...")
        db_config = get_db_config()
        if not db_config.connect():
            print("❌ Database connection failed")
            return
        print("✅ Database connected")
        
        # Create unique email
        timestamp = int(time.time())
        test_email = f"debugtest{timestamp}@example.com"
        print(f"\n2️⃣ Testing with email: {test_email}")
        
        # Check if email exists (should be False)
        print("   Checking if email exists...")
        existing_user = User.find_by_email(test_email)
        print(f"   Email exists: {'YES' if existing_user else 'NO'} ✅")
        
        if existing_user:
            print(f"   ❌ ERROR: Email should not exist but found user: {existing_user.name}")
            return
        
        # Try to create user step by step
        print("\n3️⃣ Creating user step by step...")
        
        # Validate inputs first
        from auth.utils import AuthUtils
        
        name = "Debug Test User"
        password = "DebugPassword123!"
        
        # Validate name
        name_valid, name_error = AuthUtils.validate_name(name)
        print(f"   Name validation: {'✅ Valid' if name_valid else f'❌ {name_error}'}")
        
        # Validate email
        email_valid = AuthUtils.validate_email(test_email)
        print(f"   Email validation: {'✅ Valid' if email_valid else '❌ Invalid'}")
        
        # Validate password
        password_valid, password_error = AuthUtils.validate_password(password)
        print(f"   Password validation: {'✅ Valid' if password_valid else f'❌ {password_error}'}")
        
        if name_valid and email_valid and password_valid:
            # Try to create user
            print("\n4️⃣ Attempting user creation...")
            new_user = User.create(name=name, email=test_email, password=password)
            
            if new_user:
                print(f"   ✅ User created successfully!")
                print(f"   - ID: {new_user._id}")
                print(f"   - Name: {new_user.name}")
                print(f"   - Email: {new_user.email}")
                
                # Test signin immediately
                print("\n5️⃣ Testing signin with new user...")
                signin_user = User.find_by_email(test_email)
                if signin_user:
                    password_check = signin_user.verify_password(password)
                    print(f"   Signin lookup: ✅ Found")
                    print(f"   Password check: {'✅ Valid' if password_check else '❌ Invalid'}")
                    
                    if password_check:
                        print(f"\n🎉 User creation and signin working correctly!")
                        print(f"   The issue might be in the API route error handling")
                    else:
                        print(f"\n❌ Password verification failed")
                else:
                    print(f"\n❌ Could not find user after creation")
            else:
                print(f"   ❌ User creation failed")
                
                # Debug why creation failed
                print("\n🔍 Debugging creation failure...")
                
                # Check database connection again
                if db_config.db is None:
                    print("   ❌ Database connection lost")
                else:
                    print("   ✅ Database still connected")
                
                # Check if email exists again (might be a race condition)
                existing_check = User.find_by_email(test_email)
                print(f"   Email exists after failed creation: {'YES' if existing_check else 'NO'}")
                
                # Try direct database insertion
                print("   Trying direct database insertion...")
                try:
                    password_hash = AuthUtils.hash_password(password)
                    user_doc = {
                        'name': name,
                        'email': test_email,
                        'password_hash': password_hash,
                        'created_at': time.time(),
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
                    
                    result = db_config.db.users.insert_one(user_doc)
                    if result.inserted_id:
                        print(f"   ✅ Direct insertion successful: {result.inserted_id}")
                    else:
                        print(f"   ❌ Direct insertion failed")
                        
                except Exception as e:
                    print(f"   ❌ Direct insertion error: {e}")
        else:
            print(f"\n❌ Input validation failed")
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_signup_issue()
