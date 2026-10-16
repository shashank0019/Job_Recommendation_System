#!/usr/bin/env python3

"""
Debug users in database to understand authentication issues
"""

def debug_users():
    print("🔍 Debugging users in database...")
    
    try:
        from config.database import get_db_config
        from auth.models import User
        
        db_config = get_db_config()
        if not db_config.connect():
            print("❌ Failed to connect to database")
            return
            
        print("✅ Database connection successful")
        
        # Check users collection
        if db_config.use_local_fallback:
            print("📁 Using local storage")
        else:
            users_collection = db_config.db.users
            users = list(users_collection.find({}))
            print(f"👥 Found {len(users)} users in database:")
            
            for i, user_data in enumerate(users):
                print(f"\n   User {i+1}:")
                print(f"   - ID: {user_data.get('_id')}")
                print(f"   - Name: {user_data.get('name')}")
                print(f"   - Email: {user_data.get('email')}")
                print(f"   - Created: {user_data.get('created_at')}")
                print(f"   - Last Login: {user_data.get('last_login')}")
                
                # Test password verification for testuser
                if user_data.get('email') == 'testuser@example.com':
                    print(f"   🔑 Testing password for testuser@example.com...")
                    user_obj = User.from_dict(user_data)
                    
                    # Test different passwords
                    test_passwords = [
                        "TestPassword123!",
                        "testpassword123",
                        "TestPassword123"
                    ]
                    
                    for pwd in test_passwords:
                        is_valid = user_obj.verify_password(pwd)
                        print(f"      Password '{pwd}': {'✅ Valid' if is_valid else '❌ Invalid'}")
            
            # Check sessions
            sessions_collection = db_config.db.sessions
            sessions = list(sessions_collection.find({}))
            print(f"\n🔐 Found {len(sessions)} sessions in database:")
            
            for i, session_data in enumerate(sessions):
                print(f"\n   Session {i+1}:")
                print(f"   - ID: {session_data.get('_id')}")
                print(f"   - User ID: {session_data.get('user_id')}")
                print(f"   - Token: {session_data.get('session_token', '')[:20]}...")
                print(f"   - Created: {session_data.get('created_at')}")
                print(f"   - Expires: {session_data.get('expires_at')}")
                
                # Check if expired
                from datetime import datetime
                expires_at = session_data.get('expires_at')
                if expires_at:
                    if isinstance(expires_at, str):
                        try:
                            expires_at = datetime.fromisoformat(expires_at)
                        except:
                            expires_at = None
                    
                    if expires_at:
                        is_expired = datetime.utcnow() > expires_at
                        print(f"   - Status: {'❌ Expired' if is_expired else '✅ Valid'}")
                        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_users()
