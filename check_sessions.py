from config.database import get_db_config
from datetime import datetime

def check_sessions():
    """Check all sessions and their expiry status"""
    config = get_db_config()
    config.connect()
    
    if config.db is not None:
        sessions_collection = config.db.sessions
        sessions = list(sessions_collection.find({}))
        
        print(f"📊 Found {len(sessions)} total sessions")
        print("=" * 50)
        
        current_time = datetime.utcnow()
        active_sessions = 0
        
        for i, session in enumerate(sessions):
            expires_at = session.get('expires_at')
            created_at = session.get('created_at')
            token = session.get('session_token', 'No token')[:20]
            
            is_expired = expires_at < current_time if expires_at else True
            status = "❌ EXPIRED" if is_expired else "✅ ACTIVE"
            
            if not is_expired:
                active_sessions += 1
            
            print(f"Session {i+1}: {status}")
            print(f"  Token: {token}...")
            print(f"  Created: {created_at}")
            print(f"  Expires: {expires_at}")
            print(f"  User ID: {session.get('user_id')}")
            print()
        
        print(f"📈 Summary: {active_sessions} active, {len(sessions) - active_sessions} expired")
        
        if active_sessions == 0:
            print("⚠️  No active sessions found. User needs to sign in again.")
        else:
            print("✅ Active sessions available for API calls.")
    else:
        print("❌ Database not available")

if __name__ == "__main__":
    check_sessions()
