#!/usr/bin/env python3
"""
MongoDB Atlas Connection Test Script
This script tests the connection to MongoDB Atlas and provides detailed status information.
"""

import sys
import os
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

def test_mongodb_connection():
    """Test MongoDB Atlas connection with detailed diagnostics"""
    
    print("=" * 60)
    print("🔍 MongoDB Atlas Connection Test")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Connection string from your database config (URL-encoded password)
    connection_string = "mongodb+srv://shashankgowda494_db_user:Atlas%401111@cluster0.xjpsgo5.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    database_name = "career_guidance_platform"
    
    print("📋 Connection Details:")
    print(f"   Database: {database_name}")
    print(f"   Cluster: cluster0.xjpsgo5.mongodb.net")
    print(f"   Username: shashankgowda494_db_user")
    print()
    
    try:
        print("🔄 Step 1: Creating MongoDB client...")
        client = MongoClient(
            connection_string,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=10000,         # 10 second connection timeout
            socketTimeoutMS=15000,          # 15 second socket timeout
        )
        print("✅ MongoDB client created successfully")
        
        print("\n🔄 Step 2: Testing server connection...")
        # Test the connection by pinging the server
        client.admin.command('ping')
        print("✅ Server ping successful - MongoDB Atlas is reachable")
        
        print("\n🔄 Step 3: Accessing database...")
        db = client[database_name]
        print(f"✅ Database '{database_name}' accessed successfully")
        
        print("\n🔄 Step 4: Testing database operations...")
        
        # List collections
        collections = db.list_collection_names()
        print(f"📊 Found {len(collections)} collections: {collections}")
        
        # Test users collection
        users_collection = db['users']
        user_count = users_collection.count_documents({})
        print(f"👥 Users collection: {user_count} documents")
        
        # Test sessions collection
        sessions_collection = db['sessions']
        session_count = sessions_collection.count_documents({})
        print(f"🔐 Sessions collection: {session_count} documents")
        
        print("\n🔄 Step 5: Testing write permissions...")
        # Test write operation with a temporary document
        test_collection = db['connection_test']
        test_doc = {
            'test': True,
            'timestamp': datetime.now(),
            'message': 'Connection test successful'
        }
        
        result = test_collection.insert_one(test_doc)
        print(f"✅ Write test successful - Document ID: {result.inserted_id}")
        
        # Clean up test document
        test_collection.delete_one({'_id': result.inserted_id})
        print("🧹 Test document cleaned up")
        
        print("\n" + "=" * 60)
        print("🎉 MongoDB Atlas Connection Status: CONNECTED")
        print("=" * 60)
        print("✅ All connection tests passed successfully!")
        print("✅ Database is fully operational")
        print("✅ Read/Write permissions confirmed")
        
        # Close connection
        client.close()
        return True
        
    except ServerSelectionTimeoutError as e:
        print("\n" + "=" * 60)
        print("❌ MongoDB Atlas Connection Status: TIMEOUT")
        print("=" * 60)
        print("🚨 Server selection timeout - possible causes:")
        print("   • Network connectivity issues")
        print("   • Firewall blocking connection")
        print("   • MongoDB Atlas cluster is down")
        print("   • IP address not whitelisted")
        print(f"   • Error details: {e}")
        return False
        
    except ConnectionFailure as e:
        print("\n" + "=" * 60)
        print("❌ MongoDB Atlas Connection Status: FAILED")
        print("=" * 60)
        print("🚨 Connection failure - possible causes:")
        print("   • Invalid credentials")
        print("   • Database/cluster doesn't exist")
        print("   • Network issues")
        print(f"   • Error details: {e}")
        return False
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ MongoDB Atlas Connection Status: ERROR")
        print("=" * 60)
        print("🚨 Unexpected error occurred:")
        print(f"   • Error type: {type(e).__name__}")
        print(f"   • Error details: {e}")
        return False

def test_local_fallback():
    """Test local JSON fallback system"""
    print("\n" + "=" * 60)
    print("🔍 Testing Local JSON Fallback System")
    print("=" * 60)
    
    try:
        # Import the database config
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from config.database import get_db_config, get_users_collection, get_sessions_collection
        
        print("🔄 Initializing database config...")
        db_config = get_db_config()
        
        # Force connection attempt
        success = db_config.connect()
        
        if db_config.use_local_fallback:
            print("📁 Using local JSON storage (fallback mode)")
            
            # Test local collections
            users_collection = get_users_collection()
            sessions_collection = get_sessions_collection()
            
            user_count = users_collection.count_documents({})
            session_count = sessions_collection.count_documents({})
            
            print(f"👥 Local users: {user_count}")
            print(f"🔐 Local sessions: {session_count}")
            print("✅ Local fallback system is working")
            
        else:
            print("🌐 Using MongoDB Atlas (cloud database)")
            print("✅ Cloud database connection successful")
            
        return True
        
    except Exception as e:
        print(f"❌ Local fallback test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting MongoDB Atlas connection diagnostics...\n")
    
    # Test direct MongoDB connection
    mongo_success = test_mongodb_connection()
    
    # Test application's database configuration
    fallback_success = test_local_fallback()
    
    print("\n" + "=" * 60)
    print("📊 FINAL SUMMARY")
    print("=" * 60)
    
    if mongo_success:
        print("✅ MongoDB Atlas: CONNECTED")
        print("   Your application can connect to the cloud database")
    else:
        print("❌ MongoDB Atlas: NOT CONNECTED")
        print("   Your application will use local JSON storage")
    
    if fallback_success:
        print("✅ Application Database: WORKING")
        print("   Your app's database system is functional")
    else:
        print("❌ Application Database: ERROR")
        print("   There may be issues with your app's database setup")
    
    print("\n🔧 Recommendations:")
    if not mongo_success:
        print("   • Check your internet connection")
        print("   • Verify MongoDB Atlas cluster is running")
        print("   • Ensure IP address is whitelisted in Atlas")
        print("   • Verify credentials are correct")
    else:
        print("   • Your MongoDB Atlas connection is working perfectly!")
        print("   • No action needed - database is operational")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
