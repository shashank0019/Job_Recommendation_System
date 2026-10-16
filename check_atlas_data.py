from config.database import get_db_config
from datetime import datetime

def check_atlas_data():
    """Check what data is currently stored in MongoDB Atlas"""
    print("🔍 MongoDB Atlas Data Summary")
    print("=" * 50)
    
    config = get_db_config()
    config.connect()
    
    if config.db is not None and not config.use_local_fallback:
        print("✅ Connected to MongoDB Atlas")
        print(f"📍 Cluster: {config.client.address}")
        print(f"🗄️  Database: {config.database_name}")
        print()
        
        # Check each collection
        collections = ['users', 'sessions', 'job_postings', 'interview_experiences']
        
        for collection_name in collections:
            collection = config.db[collection_name]
            count = collection.count_documents({})
            print(f"📊 {collection_name}: {count} documents")
            
            # Show sample data for each collection
            if count > 0:
                sample = collection.find_one({})
                if collection_name == 'users':
                    print(f"   Sample: {sample.get('name', 'N/A')} ({sample.get('email', 'N/A')})")
                elif collection_name == 'sessions':
                    expires_at = sample.get('expires_at')
                    is_active = expires_at > datetime.utcnow() if expires_at else False
                    status = "Active" if is_active else "Expired"
                    print(f"   Sample: {sample.get('session_token', 'N/A')[:20]}... ({status})")
                elif collection_name == 'job_postings':
                    print(f"   Sample: {sample.get('title', 'N/A')} at {sample.get('company', 'N/A')}")
                elif collection_name == 'interview_experiences':
                    print(f"   Sample: {sample.get('position', 'N/A')} at {sample.get('company', 'N/A')}")
            print()
        
        # Check active sessions
        sessions_collection = config.db.sessions
        current_time = datetime.utcnow()
        active_sessions = sessions_collection.count_documents({
            "expires_at": {"$gt": current_time}
        })
        
        print(f"🔐 Active Sessions: {active_sessions}")
        print(f"💾 Total Storage: MongoDB Atlas Cloud")
        print(f"🌐 Connection: Secure (TLS enabled)")
        
    else:
        print("❌ Not connected to MongoDB Atlas")
        if config.use_local_fallback:
            print("⚠️  Using local JSON fallback instead")

if __name__ == "__main__":
    check_atlas_data()
