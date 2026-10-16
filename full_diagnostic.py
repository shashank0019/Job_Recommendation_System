"""
Complete diagnostic - check everything about MongoDB connection
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("🔍 COMPLETE MONGODB DIAGNOSTIC")
print("=" * 80)

# Step 1: Check environment variables
print("\n1️⃣ ENVIRONMENT VARIABLES")
print("-" * 80)
mongodb_uri = os.getenv('MONGODB_URI')
mongodb_db = os.getenv('MONGODB_DB_NAME')

if mongodb_uri:
    print(f"✅ MONGODB_URI: {mongodb_uri[:60]}...")
else:
    print("❌ MONGODB_URI: NOT SET")
    sys.exit(1)

if mongodb_db:
    print(f"✅ MONGODB_DB_NAME: {mongodb_db}")
else:
    print("❌ MONGODB_DB_NAME: NOT SET")

# Step 2: Test direct MongoDB connection
print("\n2️⃣ DIRECT MONGODB CONNECTION TEST")
print("-" * 80)

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, OperationFailure
    
    print("⏳ Connecting to MongoDB Atlas (30 second timeout)...")
    client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=30000)
    
    print("⏳ Testing with ping...")
    client.admin.command('ping')
    
    print("✅ DIRECT CONNECTION: SUCCESS")
    
    db = client[mongodb_db]
    user_count = db.users.count_documents({})
    print(f"👥 Users in Atlas: {user_count}")
    
    # List users
    if user_count > 0:
        print("\n📋 Users in MongoDB Atlas:")
        for user in db.users.find().limit(10):
            print(f"   - {user.get('name')} ({user.get('email')})")
    
    client.close()
    
except ConnectionFailure as e:
    print(f"❌ CONNECTION FAILED: {e}")
    print("\n💡 SOLUTION:")
    print("   1. Go to MongoDB Atlas → Network Access")
    print("   2. Add IP Address: 0.0.0.0/0 (Allow from anywhere)")
    print("   3. Wait 1-2 minutes")
    print("   4. Try again")
    sys.exit(1)
    
except OperationFailure as e:
    print(f"❌ AUTHENTICATION FAILED: {e}")
    print("\n💡 Check credentials in MongoDB Atlas")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    sys.exit(1)

# Step 3: Check config/database.py
print("\n3️⃣ DATABASE CONFIG CHECK")
print("-" * 80)

try:
    from config.database import get_db_config
    
    db_config = get_db_config()
    print(f"📍 Config connection string: {db_config.connection_string[:60]}...")
    print(f"📊 Config database name: {db_config.database_name}")
    print(f"🔄 Local fallback enabled: {db_config.use_local_fallback}")
    
    # Try to connect using config
    print("\n⏳ Testing connection via config...")
    try:
        success = db_config.connect()
        if success:
            print("✅ CONFIG CONNECTION: SUCCESS")
            print(f"   Using local fallback: {db_config.use_local_fallback}")
        else:
            print("❌ CONFIG CONNECTION: FAILED")
    except Exception as e:
        print(f"❌ CONFIG CONNECTION ERROR: {e}")
        print("\n⚠️  This is EXPECTED if local fallback is disabled")
        print("   It means MongoDB Atlas connection is required")
        
except Exception as e:
    print(f"❌ Error loading config: {e}")

# Step 4: Check local files
print("\n4️⃣ LOCAL STORAGE CHECK")
print("-" * 80)

import json
from pathlib import Path

local_file = Path("data/auth/users.json")
if local_file.exists():
    with open(local_file, 'r') as f:
        local_users = json.load(f)
    print(f"📁 Local file: {local_file}")
    print(f"   Users: {len(local_users)}")
    
    # Show last 3 users
    if len(local_users) > 0:
        print("\n   Last 3 users in local file:")
        for user in local_users[-3:]:
            print(f"      - {user.get('name')} ({user.get('email')})")
            print(f"        Created: {user.get('created_at')}")
else:
    print(f"📁 Local file not found: {local_file}")

# Step 5: Test user creation
print("\n5️⃣ TEST USER CREATION")
print("-" * 80)

test_email = f"diagnostic_{os.urandom(4).hex()}@test.com"
print(f"🧪 Creating test user: {test_email}")

try:
    from auth.models import User
    
    test_user = User.create(
        name="Diagnostic Test",
        email=test_email,
        password="test123"
    )
    
    if test_user:
        print(f"✅ User created!")
        print(f"   User ID: {test_user._id}")
        
        # Check where it was stored
        print("\n   Checking storage location...")
        
        # Check MongoDB
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        db = client[mongodb_db]
        atlas_user = db.users.find_one({'email': test_email})
        
        if atlas_user:
            print(f"   ✅ FOUND IN MONGODB ATLAS")
            print(f"      This is CORRECT!")
        else:
            print(f"   ❌ NOT IN MONGODB ATLAS")
        
        # Check local file
        if local_file.exists():
            with open(local_file, 'r') as f:
                local_users = json.load(f)
            for user in local_users:
                if user.get('email') == test_email:
                    print(f"   ⚠️  FOUND IN LOCAL FILE")
                    print(f"      This is WRONG!")
                    break
        
        client.close()
        
        # Clean up test user
        print(f"\n   🧹 Cleaning up test user...")
        db = client[mongodb_db]
        db.users.delete_one({'email': test_email})
        
    else:
        print(f"❌ Failed to create user")
        
except Exception as e:
    print(f"❌ Error creating user: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("📊 DIAGNOSTIC COMPLETE")
print("=" * 80)
