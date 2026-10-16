#!/usr/bin/env python3
"""List users in the database to find valid credentials"""

from config.database import get_db_config

def list_users():
    """List all users in the database"""
    print("Users in Database:")
    print("=" * 30)
    
    config = get_db_config()
    config.connect()
    
    if config.db is not None and not config.use_local_fallback:
        users_collection = config.db.users
        users = users_collection.find({})
        
        for user in users:
            print(f"Name: {user.get('name', 'N/A')}")
            print(f"Email: {user.get('email', 'N/A')}")
            print(f"ID: {user.get('_id', 'N/A')}")
            print("-" * 20)
    else:
        print("Not connected to database")

if __name__ == "__main__":
    list_users()
