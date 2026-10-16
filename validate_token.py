#!/usr/bin/env python3
"""
Validate a session token from the database
"""
from auth.models import Session, User
from config.database import get_db_config
from datetime import datetime

def validate_token(token_to_check):
    print(f"🔍 Validating token: {token_to_check[:20]}...")
    
    try:
        # Find session by token
        session = Session.find_by_token(token_to_check)
        
        if not session:
            print("❌ Session not found in database")
            return False
        
        print(f"✅ Session found for user ID: {session.user_id}")
        
        # Check if expired
        if session.is_expired():
            print("❌ Session is expired")
            return False
        
        print("✅ Session is valid and not expired")
        
        # Find user
        user = User.find_by_id(session.user_id)
        if user:
            print(f"✅ User found: {user.name} ({user.email})")
            return True
        else:
            print("❌ User not found")
            return False
            
    except Exception as e:
        print(f"❌ Error validating token: {e}")
        return False

def list_recent_sessions():
    print("\n🔑 Recent Sessions:")
    try:
        db_config = get_db_config()
        if not db_config.connect():
            print("❌ Database connection failed")
            return
        
        sessions_collection = db_config.db.sessions if not db_config.use_local_fallback else db_config.sessions_file
        
        if db_config.use_local_fallback:
            import json
            with open(sessions_collection, 'r') as f:
                sessions = json.load(f)
        else:
            sessions = list(sessions_collection.find({}).sort('created_at', -1).limit(5))
        
        for i, session in enumerate(sessions[:5]):
            print(f"   Session {i+1}:")
            print(f"     Token: {session.get('session_token', '')[:20]}...")
            print(f"     User ID: {session.get('user_id')}")
            print(f"     Created: {session.get('created_at')}")
            print(f"     Expires: {session.get('expires_at')}")
            
            # Check if expired
            if isinstance(session.get('expires_at'), str):
                from datetime import datetime
                expires_at = datetime.fromisoformat(session['expires_at'].replace('Z', '+00:00'))
                is_expired = expires_at < datetime.utcnow()
                print(f"     Status: {'Expired' if is_expired else 'Valid'}")
            
    except Exception as e:
        print(f"❌ Error listing sessions: {e}")

if __name__ == "__main__":
    print("🔍 Session Validation Tool")
    print("=" * 50)
    
    # List recent sessions first
    list_recent_sessions()
    
    # You can test a specific token here
    # test_token = "your_token_here"
    # validate_token(test_token)
