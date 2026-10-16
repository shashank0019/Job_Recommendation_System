#!/usr/bin/env python3
"""
Test authentication components directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_components():
    """Test each authentication component"""
    
    print("🔍 Testing database connection...")
    try:
        from config.database import db_config
        db_config.connect()
        print(f"✅ Database connected. Using fallback: {db_config.use_local_fallback}")
        
        from config.database import get_users_collection
        users_collection = get_users_collection()
        print("✅ Users collection obtained")
        
        # Test creating a user
        print("🔍 Testing user creation...")
        from auth.models import User
        from auth.utils import hash_password
        
        password_hash = hash_password("TestPass123")
        user = User(name="Test User", email="direct@test.com", password_hash=password_hash)
        print("✅ User object created")
        
        # Test inserting user
        result = users_collection.insert_one(user.to_dict())
        print(f"✅ User inserted with ID: {result.inserted_id}")
        
        # Test finding user
        found_user_data = users_collection.find_one({'email': 'direct@test.com'})
        print(f"✅ User found: {found_user_data is not None}")
        
        if found_user_data:
            print(f"User ID type: {type(found_user_data.get('_id'))}")
            print(f"User ID value: {found_user_data.get('_id')}")
            
            # Test User.from_dict
            found_user = User.from_dict(found_user_data)
            print(f"✅ User object recreated: {found_user.email}")
            
            # Test password verification
            from auth.utils import verify_password
            result = verify_password("TestPass123", found_user.password_hash)
            print(f"✅ Password verification: {result}")
            
            if result:
                # Test session creation
                print("🔍 Testing session creation...")
                from auth.models import Session
                from auth.utils import generate_session_token
                
                session_token = generate_session_token()
                session = Session(user_id=found_user._id, session_token=session_token)
                print("✅ Session object created")
                
                # Test session insertion
                from config.database import get_sessions_collection
                sessions_collection = get_sessions_collection()
                session_result = sessions_collection.insert_one(session.to_dict())
                print(f"✅ Session inserted with ID: {session_result.inserted_id}")
                
                print("🎉 All authentication components working!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_components()