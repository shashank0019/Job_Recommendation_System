#!/usr/bin/env python3
"""
Fix MongoDB Atlas Connection String
This script fixes the connection string encoding issue and tests the connection.
"""

import urllib.parse
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from datetime import datetime

def fix_and_test_connection():
    """Fix the connection string and test MongoDB Atlas connection"""
    
    print("🔧 Fixing MongoDB Atlas Connection String")
    print("=" * 60)
    
    # Original credentials
    username = "shashankgowda494_db_user"
    password = "Atlas@1111"  # Contains @ symbol that needs encoding
    cluster = "cluster0.xjpsgo5.mongodb.net"
    database_name = "career_guidance_platform"
    
    # URL encode the password to handle special characters
    encoded_password = urllib.parse.quote_plus(password)
    
    print(f"Original password: {password}")
    print(f"Encoded password: {encoded_password}")
    print()
    
    # Create the fixed connection string
    fixed_connection_string = f"mongodb+srv://{username}:{encoded_password}@{cluster}/?retryWrites=true&w=majority&appName=Cluster0"
    
    print("🔄 Testing connection with fixed string...")
    
    try:
        # Test connection
        client = MongoClient(
            fixed_connection_string,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=15000,
        )
        
        # Ping the server
        client.admin.command('ping')
        print("✅ Connection successful!")
        
        # Test database access
        db = client[database_name]
        collections = db.list_collection_names()
        print(f"📊 Found {len(collections)} collections: {collections}")
        
        # Test collections
        if 'users' in collections:
            users_count = db['users'].count_documents({})
            print(f"👥 Users: {users_count}")
        
        if 'sessions' in collections:
            sessions_count = db['sessions'].count_documents({})
            print(f"🔐 Sessions: {sessions_count}")
        
        client.close()
        
        print("\n" + "=" * 60)
        print("🎉 MongoDB Atlas is CONNECTED and working!")
        print("=" * 60)
        
        # Show the correct connection string for the config file
        print("\n📝 Use this corrected connection string in your database.py:")
        print(f'"{fixed_connection_string}"')
        
        return True, fixed_connection_string
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False, fixed_connection_string

if __name__ == "__main__":
    success, connection_string = fix_and_test_connection()
    
    if success:
        print("\n🔧 Next steps:")
        print("1. Update the connection string in config/database.py")
        print("2. Your MongoDB Atlas connection will work properly")
    else:
        print("\n🔧 Troubleshooting:")
        print("1. Check if your IP is whitelisted in MongoDB Atlas")
        print("2. Verify the cluster is running")
        print("3. Check your internet connection")
