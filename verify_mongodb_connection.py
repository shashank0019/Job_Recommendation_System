"""
Verify MongoDB Atlas Connection and Check User Data
"""
import os
from dotenv import load_dotenv
from config.database import get_db_config, get_users_collection

load_dotenv()

print("=" * 70)
print("🔍 MongoDB Atlas Connection Verification")
print("=" * 70)

# Get database configuration
db_config = get_db_config()

# Show connection details
print(f"\n📍 Connection String: {os.getenv('MONGODB_URI')[:50]}...")
print(f"📊 Database Name: {os.getenv('MONGODB_DB_NAME')}")
print()

# Connect to database
print("⏳ Connecting to MongoDB Atlas...")
success = db_config.connect()

if success and not db_config.use_local_fallback:
    print("✅ Connected to MongoDB Atlas successfully!")
    print()
    
    # Get users collection
    users_collection = get_users_collection()
    
    # Count users
    user_count = users_collection.count_documents({})
    print(f"👥 Total users in database: {user_count}")
    
    if user_count > 0:
        print("\n📋 User List:")
        print("-" * 70)
        for user in users_collection.find():
            print(f"  • Name: {user.get('name')}")
            print(f"    Email: {user.get('email')}")
            print(f"    Created: {user.get('created_at')}")
            print(f"    ID: {user.get('_id')}")
            print()
    else:
        print("\n⚠️  No users found in the database yet.")
        print("   Users will appear here after signup.")
    
    # Check database and collection info
    print("\n📊 Database Information:")
    print(f"  Database: {db_config.database_name}")
    print(f"  Collections: {db_config.db.list_collection_names()}")
    
    print("\n" + "=" * 70)
    print("✅ Your application is now connected to the correct database!")
    print("   New users will be stored in MongoDB Atlas.")
    print("=" * 70)
    
elif db_config.use_local_fallback:
    print("⚠️  WARNING: Using local JSON storage fallback!")
    print("   This means MongoDB Atlas connection failed.")
    print("   Check your internet connection and credentials.")
    
else:
    print("❌ Failed to connect to database!")
