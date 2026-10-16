"""
Real-time check: Is the app using MongoDB Atlas or Local Storage?
Run this while your Flask app is running
"""
import os
from dotenv import load_dotenv
from config.database import get_db_config

load_dotenv()

print("=" * 80)
print("🔍 CHECKING CURRENT DATABASE CONNECTION STATUS")
print("=" * 80)

# Get the database config (this is what your running app uses)
db_config = get_db_config()

print(f"\n📍 Connection String: {db_config.connection_string[:60]}...")
print(f"📊 Database Name: {db_config.database_name}")
print(f"\n⏳ Checking connection status...")

# Check if already connected
if db_config.db is not None:
    print(f"✅ Database connection already established")
    if db_config.use_local_fallback:
        print(f"⚠️  STATUS: Using LOCAL JSON STORAGE")
        print(f"   📁 Local directory: {db_config.local_data_dir}")
    else:
        print(f"✅ STATUS: Using MONGODB ATLAS")
        print(f"   📊 Database: {db_config.database_name}")
else:
    print(f"ℹ️  No active connection yet, attempting to connect...")
    success = db_config.connect()
    
    if success:
        if db_config.use_local_fallback:
            print(f"⚠️  STATUS: Using LOCAL JSON STORAGE")
            print(f"   📁 Local directory: {db_config.local_data_dir}")
            print(f"\n❌ PROBLEM: MongoDB Atlas connection failed!")
            print(f"   Your app is still saving to local files.")
        else:
            print(f"✅ STATUS: Using MONGODB ATLAS")
            print(f"   📊 Database: {db_config.database_name}")
            
            # Count users
            users_count = db_config.db.users.count_documents({})
            print(f"   👥 Users in Atlas: {users_count}")

print("\n" + "=" * 80)

# Check local files for new users
import json
from pathlib import Path
from datetime import datetime, timedelta

local_file = Path("data/auth/users.json")
if local_file.exists():
    with open(local_file, 'r') as f:
        local_users = json.load(f)
    
    print(f"📁 LOCAL FILE CHECK: {local_file}")
    print(f"   Total users in local file: {len(local_users)}")
    
    # Check for recently created users (last 10 minutes)
    recent_users = []
    cutoff_time = datetime.utcnow() - timedelta(minutes=10)
    
    for user in local_users:
        created_at_str = user.get('created_at', '')
        try:
            created_at = datetime.fromisoformat(created_at_str)
            if created_at > cutoff_time:
                recent_users.append(user)
        except:
            pass
    
    if recent_users:
        print(f"\n   ⚠️  RECENT USERS (last 10 min) in LOCAL file:")
        for user in recent_users:
            print(f"      - {user.get('name')} ({user.get('email')})")
            print(f"        Created: {user.get('created_at')}")
        print(f"\n   ❌ NEW USERS ARE STILL GOING TO LOCAL STORAGE!")
    else:
        print(f"   ✅ No recent users in local file")

print("=" * 80)

if db_config.use_local_fallback:
    print("\n🔧 SOLUTION:")
    print("   1. Check MongoDB Atlas Network Access")
    print("   2. Whitelist your IP address (or use 0.0.0.0/0)")
    print("   3. Verify internet connection")
    print("   4. Check server logs for connection errors")
    print("   5. Restart Flask server after fixing")
else:
    print("\n✅ Everything looks good!")
    print("   New users should be going to MongoDB Atlas")
