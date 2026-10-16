"""
Comprehensive diagnostic to check where user data is being stored
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 80)
print("🔍 STORAGE LOCATION DIAGNOSTIC")
print("=" * 80)

# Check 1: Environment Variables
print("\n1️⃣ ENVIRONMENT VARIABLES CHECK")
print("-" * 80)
mongodb_uri = os.getenv('MONGODB_URI')
mongodb_db = os.getenv('MONGODB_DB_NAME')

if mongodb_uri:
    print(f"✅ MONGODB_URI is set: {mongodb_uri[:60]}...")
else:
    print("❌ MONGODB_URI is NOT set in .env file")

if mongodb_db:
    print(f"✅ MONGODB_DB_NAME is set: {mongodb_db}")
else:
    print("❌ MONGODB_DB_NAME is NOT set in .env file")

# Check 2: Database Configuration
print("\n2️⃣ DATABASE CONFIGURATION CHECK")
print("-" * 80)
try:
    from config.database import get_db_config
    
    db_config = get_db_config()
    print(f"📍 Connection String: {db_config.connection_string[:60]}...")
    print(f"📊 Database Name: {db_config.database_name}")
    print(f"🔄 Local Fallback Mode: {db_config.use_local_fallback}")
    
    # Try to connect
    print("\n⏳ Attempting to connect...")
    success = db_config.connect()
    
    if success:
        if db_config.use_local_fallback:
            print("⚠️  WARNING: Using LOCAL JSON STORAGE (not MongoDB Atlas)")
            print(f"   Local data directory: {db_config.local_data_dir}")
        else:
            print("✅ Connected to MONGODB ATLAS successfully!")
            print(f"   Database: {db_config.database_name}")
    else:
        print("❌ Failed to connect to database")
        
except Exception as e:
    print(f"❌ Error loading database config: {e}")
    import traceback
    traceback.print_exc()

# Check 3: Local Storage Files
print("\n3️⃣ LOCAL STORAGE CHECK")
print("-" * 80)

local_files = [
    "data/users.json",
    "data/sessions.json",
    "data/auth/users.json",
    "data/auth/sessions.json"
]

for file_path in local_files:
    path = Path(file_path)
    if path.exists():
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            print(f"📁 {file_path}: {len(data)} records")
            if len(data) > 0:
                print(f"   ⚠️  DATA FOUND IN LOCAL FILE!")
                for item in data[:3]:  # Show first 3
                    if 'email' in item:
                        print(f"      - {item.get('name')} ({item.get('email')})")
        except Exception as e:
            print(f"📁 {file_path}: Error reading - {e}")
    else:
        print(f"📁 {file_path}: Not found")

# Check 4: MongoDB Atlas Check
print("\n4️⃣ MONGODB ATLAS CHECK")
print("-" * 80)

if mongodb_uri and not db_config.use_local_fallback:
    try:
        from pymongo import MongoClient
        
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        
        db = client[mongodb_db]
        collections = db.list_collection_names()
        
        print(f"✅ MongoDB Atlas Connection: SUCCESS")
        print(f"📊 Database: {mongodb_db}")
        print(f"📁 Collections: {collections if collections else '(none yet)'}")
        
        if 'users' in collections:
            user_count = db.users.count_documents({})
            print(f"👥 Users in Atlas: {user_count}")
            
            if user_count > 0:
                print("\n   Users found in MongoDB Atlas:")
                for user in db.users.find().limit(5):
                    print(f"      - {user.get('name')} ({user.get('email')})")
        else:
            print("👥 Users collection: Not created yet")
            
        client.close()
        
    except Exception as e:
        print(f"❌ MongoDB Atlas Error: {e}")
else:
    print("⚠️  Skipped (using local storage or no URI)")

# Check 5: Test User Creation
print("\n5️⃣ TEST USER CREATION")
print("-" * 80)

try:
    from auth.models import User
    
    # Try to create a test user
    test_email = "diagnostic_test@example.com"
    
    # Check if test user exists
    existing = User.find_by_email(test_email)
    if existing:
        print(f"ℹ️  Test user already exists: {test_email}")
    else:
        print(f"🧪 Creating test user: {test_email}")
        test_user = User.create(
            name="Diagnostic Test User",
            email=test_email,
            password="test123"
        )
        
        if test_user:
            print(f"✅ Test user created successfully!")
            print(f"   User ID: {test_user._id}")
            
            # Now check where it was stored
            print("\n   Checking storage location...")
            
            # Check local files
            for file_path in local_files:
                path = Path(file_path)
                if path.exists():
                    with open(path, 'r') as f:
                        data = json.load(f)
                    for item in data:
                        if item.get('email') == test_email:
                            print(f"   ⚠️  FOUND IN LOCAL FILE: {file_path}")
                            break
            
            # Check MongoDB
            if mongodb_uri and not db_config.use_local_fallback:
                client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
                db = client[mongodb_db]
                atlas_user = db.users.find_one({'email': test_email})
                if atlas_user:
                    print(f"   ✅ FOUND IN MONGODB ATLAS")
                else:
                    print(f"   ❌ NOT FOUND IN MONGODB ATLAS")
                client.close()
        else:
            print(f"❌ Failed to create test user")
            
except Exception as e:
    print(f"❌ Error in test user creation: {e}")
    import traceback
    traceback.print_exc()

# Final Summary
print("\n" + "=" * 80)
print("📊 DIAGNOSTIC SUMMARY")
print("=" * 80)

if db_config.use_local_fallback:
    print("⚠️  STATUS: Using LOCAL JSON STORAGE")
    print("   Your data is being stored in local files, NOT MongoDB Atlas!")
    print("\n   Possible reasons:")
    print("   1. MongoDB Atlas connection failed")
    print("   2. Internet connectivity issues")
    print("   3. Incorrect credentials")
    print("   4. IP not whitelisted in MongoDB Atlas")
else:
    print("✅ STATUS: Using MONGODB ATLAS")
    print("   Your data should be stored in MongoDB Atlas")
    print(f"   Database: {mongodb_db}")

print("=" * 80)
