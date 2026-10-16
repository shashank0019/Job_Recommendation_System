"""
Force MongoDB Atlas Connection Test
This will attempt to connect WITHOUT falling back to local storage
"""
import os
import logging
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

print("=" * 80)
print("🔍 FORCING MONGODB ATLAS CONNECTION (NO FALLBACK)")
print("=" * 80)

mongodb_uri = os.getenv('MONGODB_URI')
mongodb_db = os.getenv('MONGODB_DB_NAME', 'career_guidance_db')

if not mongodb_uri:
    print("❌ ERROR: MONGODB_URI not found in .env file!")
    exit(1)

print(f"\n📍 Connection String: {mongodb_uri[:60]}...")
print(f"📊 Database Name: {mongodb_db}")
print()

try:
    print("⏳ Connecting to MongoDB Atlas (30 second timeout)...")
    
    client = MongoClient(
        mongodb_uri,
        serverSelectionTimeoutMS=30000,
        connectTimeoutMS=30000,
        socketTimeoutMS=30000
    )
    
    print("⏳ Testing connection with ping...")
    client.admin.command('ping')
    
    print("✅ Successfully connected to MongoDB Atlas!")
    print()
    
    # Get database
    db = client[mongodb_db]
    
    # List collections
    collections = db.list_collection_names()
    print(f"📁 Collections in database: {collections if collections else '(none yet)'}")
    print()
    
    # Check users collection
    if 'users' in collections:
        user_count = db.users.count_documents({})
        print(f"👥 Users in MongoDB Atlas: {user_count}")
        
        if user_count > 0:
            print("\n📋 Users found:")
            for user in db.users.find().limit(10):
                print(f"   - {user.get('name')} ({user.get('email')})")
        else:
            print("   (No users in Atlas yet)")
    else:
        print("👥 Users collection: Not created yet")
        print("   (Will be created automatically when first user signs up)")
    
    print()
    print("=" * 80)
    print("✅ MongoDB Atlas connection is WORKING!")
    print("   The issue is that your app is falling back to local storage.")
    print("   We need to prevent the fallback.")
    print("=" * 80)
    
    client.close()
    
except ConnectionFailure as e:
    print(f"\n❌ CONNECTION FAILURE: {e}")
    print("\n💡 Possible solutions:")
    print("   1. Check your internet connection")
    print("   2. Verify MongoDB Atlas Network Access settings")
    print("   3. Add your IP to the whitelist (or use 0.0.0.0/0 for testing)")
    exit(1)
    
except OperationFailure as e:
    print(f"\n❌ AUTHENTICATION FAILURE: {e}")
    print("\n💡 Check your credentials:")
    print(f"   Username: shashank22ise_db_user")
    print(f"   Password: (verify in MongoDB Atlas)")
    exit(1)
    
except Exception as e:
    print(f"\n❌ UNEXPECTED ERROR: {e}")
    print(f"   Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    exit(1)
