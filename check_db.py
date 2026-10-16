#!/usr/bin/env python3
"""
Check database contents - users and sessions
"""
from config.database import get_db_config
from auth.models import User, Session
from bson import ObjectId

def check_database():
    print("🔍 Checking Database Contents")
    print("=" * 50)
    
    try:
        db_config = get_db_config()
        if not db_config.db:
            print("❌ Database connection failed")
            return
        
        print("✅ Database connected successfully")
        
        # Check users collection
        print("\n📋 Users Collection:")
        users_collection = db_config.db.users
        users = list(users_collection.find({}))
        print(f"   Total users: {len(users)}")
        
        for i, user in enumerate(users[:5]):  # Show first 5 users
            print(f"   User {i+1}:")
            print(f"     ID: {user.get('_id')}")
            print(f"     Name: {user.get('name')}")
            print(f"     Email: {user.get('email')}")
            print(f"     Created: {user.get('created_at', 'Unknown')}")
        
        # Check sessions collection
        print("\n🔑 Sessions Collection:")
        sessions_collection = db_config.db.sessions
        sessions = list(sessions_collection.find({}))
        print(f"   Total sessions: {len(sessions)}")
        
        for i, session in enumerate(sessions[:5]):  # Show first 5 sessions
            print(f"   Session {i+1}:")
            print(f"     ID: {session.get('_id')}")
            print(f"     User ID: {session.get('user_id')}")
            print(f"     Token: {session.get('session_token', '')[:20]}...")
            print(f"     Created: {session.get('created_at', 'Unknown')}")
            print(f"     Expires: {session.get('expires_at', 'Unknown')}")
        
        # Check if we have any valid sessions
        from datetime import datetime
        current_time = datetime.utcnow()
        valid_sessions = list(sessions_collection.find({
            'expires_at': {'$gt': current_time}
        }))
        print(f"\n✅ Valid (non-expired) sessions: {len(valid_sessions)}")
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database()
