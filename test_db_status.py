#!/usr/bin/env python3
"""
Test script to check database connection status
"""
from config.database import get_db_config

def test_db_status():
    print("🔍 Testing database connection status...")
    
    config = get_db_config()
    success = config.connect()
    
    print(f"Connection successful: {success}")
    print(f"Using local fallback: {config.use_local_fallback}")
    print(f"Database available: {config.db is not None}")
    
    if config.db is not None:
        print(f"Database name: {config.database_name}")
        # Test collection access
        try:
            users_collection = config.db.users
            count = users_collection.count_documents({})
            print(f"Users in MongoDB: {count}")
        except Exception as e:
            print(f"Error accessing users collection: {e}")
    
    # Test the helper functions
    try:
        from config.database import get_users_collection
        users_collection = get_users_collection()
        count = users_collection.count_documents({})
        print(f"Users via helper function: {count}")
    except Exception as e:
        print(f"Error with helper function: {e}")

if __name__ == "__main__":
    test_db_status()
