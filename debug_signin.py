#!/usr/bin/env python3
"""
Debug authentication signin issue
"""

from config.database import get_users_collection
from auth.models import User
from auth.utils import verify_password
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_signin():
    """Debug the signin process step by step"""
    try:
        print("🔍 Step 1: Getting users collection...")
        users_collection = get_users_collection()
        print("✅ Users collection obtained")
        
        print("🔍 Step 2: Finding user by email...")
        user_data = users_collection.find_one({'email': 'mongodb@example.com'})
        print(f"✅ User found: {user_data is not None}")
        
        if user_data:
            print(f"User data keys: {list(user_data.keys())}")
            print(f"User _id type: {type(user_data.get('_id'))}")
            print(f"User _id value: {user_data.get('_id')}")
            
            print("🔍 Step 3: Creating User object...")
            user = User.from_dict(user_data)
            print(f"✅ User object created: {user.email}")
            
            print("🔍 Step 4: Verifying password...")
            result = verify_password('MongoPass123', user.password_hash)
            print(f"✅ Password verification: {result}")
            
            if result:
                print("🔍 Step 5: Creating session...")
                from auth.utils import generate_session_token
                from auth.models import Session
                
                session_token = generate_session_token()
                print(f"Session token generated: {session_token[:10]}...")
                
                # This is where it might be failing
                print(f"User _id for session: {user._id} (type: {type(user._id)})")
                session = Session(user_id=user._id, session_token=session_token)
                print("✅ Session created successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_signin()