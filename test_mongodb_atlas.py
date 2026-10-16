"""
Test MongoDB Atlas Connection
Verifies that the connection string works and database is accessible
"""
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

# Load environment variables
load_dotenv()

def test_mongodb_connection():
    """Test MongoDB Atlas connection"""
    print("🔧 Testing MongoDB Atlas Connection...")
    print("=" * 60)
    
    # Get connection string from environment
    mongodb_uri = os.getenv('MONGODB_URI')
    db_name = os.getenv('MONGODB_DB_NAME', 'career_guidance_db')
    
    if not mongodb_uri:
        print("❌ ERROR: MONGODB_URI not found in .env file")
        return False
    
    print(f"📍 Database Name: {db_name}")
    print(f"🔗 Connection String: {mongodb_uri[:50]}...")
    print()
    
    try:
        # Create MongoDB client
        print("⏳ Connecting to MongoDB Atlas...")
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        
        # Test the connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")
        print()
        
        # Get database
        db = client[db_name]
        
        # List existing collections
        collections = db.list_collection_names()
        print(f"📊 Database: {db_name}")
        print(f"📁 Existing Collections: {len(collections)}")
        if collections:
            for col in collections:
                count = db[col].count_documents({})
                print(f"   - {col}: {count} documents")
        else:
            print("   (No collections yet - will be created automatically)")
        print()
        
        # Test write operation (create a test document)
        print("🧪 Testing write operation...")
        test_collection = db['connection_test']
        test_doc = {
            'test': 'MongoDB Atlas connection successful',
            'timestamp': '2026-01-07',
            'status': 'active'
        }
        result = test_collection.insert_one(test_doc)
        print(f"✅ Test document inserted with ID: {result.inserted_id}")
        
        # Clean up test document
        test_collection.delete_one({'_id': result.inserted_id})
        print("🧹 Test document cleaned up")
        print()
        
        # Display server info
        server_info = client.server_info()
        print(f"🖥️  MongoDB Version: {server_info.get('version', 'Unknown')}")
        print()
        
        print("=" * 60)
        print("✅ MongoDB Atlas is configured correctly!")
        print("✅ Your application is ready to use the database")
        print("=" * 60)
        
        client.close()
        return True
        
    except ConnectionFailure as e:
        print(f"❌ Connection Failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check your internet connection")
        print("   2. Verify the connection string in .env file")
        print("   3. Ensure your IP is whitelisted in MongoDB Atlas")
        print("   4. Check username and password are correct")
        return False
        
    except OperationFailure as e:
        print(f"❌ Authentication Failed: {e}")
        print("\n💡 Check your MongoDB Atlas credentials:")
        print("   - Username: shashank22ise_db_user")
        print("   - Password: (verify in MongoDB Atlas)")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print(f"   Error Type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_mongodb_connection()
    exit(0 if success else 1)
