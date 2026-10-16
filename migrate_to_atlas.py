"""
Migrate Local Users to MongoDB Atlas
This script will move all users from local JSON storage to MongoDB Atlas
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

load_dotenv()

print("=" * 80)
print("📦 MIGRATING LOCAL USERS TO MONGODB ATLAS")
print("=" * 80)

# Get MongoDB connection
mongodb_uri = os.getenv('MONGODB_URI')
mongodb_db = os.getenv('MONGODB_DB_NAME', 'career_guidance_db')

if not mongodb_uri:
    print("❌ ERROR: MONGODB_URI not found in .env file!")
    exit(1)

# Connect to MongoDB
print(f"\n⏳ Connecting to MongoDB Atlas...")
try:
    client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=30000)
    client.admin.command('ping')
    db = client[mongodb_db]
    print(f"✅ Connected to MongoDB Atlas")
    print(f"📊 Database: {mongodb_db}")
except Exception as e:
    print(f"❌ Failed to connect to MongoDB Atlas: {e}")
    exit(1)

# Read local users
local_users_file = Path("data/auth/users.json")

if not local_users_file.exists():
    print(f"\n⚠️  No local users file found at: {local_users_file}")
    print("   Nothing to migrate.")
    exit(0)

print(f"\n📁 Reading local users from: {local_users_file}")
with open(local_users_file, 'r') as f:
    local_users = json.load(f)

print(f"👥 Found {len(local_users)} users in local storage")

if len(local_users) == 0:
    print("   Nothing to migrate.")
    exit(0)

# Migrate users
print(f"\n⏳ Migrating users to MongoDB Atlas...")
migrated_count = 0
skipped_count = 0

for user in local_users:
    email = user.get('email')
    
    # Check if user already exists in Atlas
    existing = db.users.find_one({'email': email})
    
    if existing:
        print(f"   ⏭️  Skipped: {email} (already exists in Atlas)")
        skipped_count += 1
        continue
    
    # Convert datetime strings to datetime objects if needed
    if isinstance(user.get('created_at'), str):
        try:
            user['created_at'] = datetime.fromisoformat(user['created_at'])
        except:
            user['created_at'] = datetime.utcnow()
    
    if isinstance(user.get('last_login'), str):
        try:
            user['last_login'] = datetime.fromisoformat(user['last_login'])
        except:
            pass
    
    # Ensure profile structure
    if 'profile' not in user:
        user['profile'] = {
            'resume_text': '',
            'skills': [],
            'preferences': {},
            'mobile': '',
            'gender': '',
            'state': '',
            'employment_status': ''
        }
    
    # Remove the old _id if it's a string (will be replaced with ObjectId)
    if '_id' in user and isinstance(user['_id'], str):
        del user['_id']
    
    # Insert into MongoDB
    try:
        result = db.users.insert_one(user)
        print(f"   ✅ Migrated: {email}")
        migrated_count += 1
    except Exception as e:
        print(f"   ❌ Failed to migrate {email}: {e}")

# Summary
print(f"\n" + "=" * 80)
print(f"📊 MIGRATION SUMMARY")
print(f"=" * 80)
print(f"✅ Migrated: {migrated_count} users")
print(f"⏭️  Skipped: {skipped_count} users (already in Atlas)")
print(f"📊 Total in Atlas now: {db.users.count_documents({})}")

# List all users in Atlas
print(f"\n👥 Users now in MongoDB Atlas:")
for user in db.users.find():
    print(f"   - {user.get('name')} ({user.get('email')})")

print(f"\n" + "=" * 80)
print(f"✅ MIGRATION COMPLETE!")
print(f"=" * 80)

# Ask if user wants to backup and delete local files
print(f"\n💡 RECOMMENDATION:")
print(f"   1. Verify users appear in MongoDB Atlas dashboard")
print(f"   2. Test login with migrated users")
print(f"   3. Backup local files: data/auth/users.json")
print(f"   4. Optionally delete local files after verification")

client.close()
