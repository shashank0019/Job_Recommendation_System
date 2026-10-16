#!/usr/bin/env python3
"""
Direct test of authentication logic
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import get_users_collection
from auth.models import User
from auth.utils import verify_password
import json

def test_signin_logic():
    """Test the signin logic directly"""
    print("🔍 Testing signin logic...")
    
    # Load user data directly from JSON
    users_collection = get_users_collection()
    user_data = users_collection.find_one({'email': 'test@example.com'})
    
    print(f"User found: {user_data is not None}")
    if user_data:
        print(f"User email: {user_data.get('email')}")
        print(f"User name: {user_data.get('name')}")
        
        # Try to create User object
        try:
            user = User.from_dict(user_data)
            print(f"User object created successfully: {user.email}")
            
            # Test password verification
            test_password = "test123"
            password_hash = user.password_hash
            print(f"Password hash: {password_hash[:50]}...")
            
            result = verify_password(test_password, password_hash)
            print(f"Password verification result: {result}")
            
        except Exception as e:
            print(f"Error creating user object: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ User not found!")
        
        # List all users
        print("\n📋 All users in database:")
        data = users_collection._load_data()
        for i, user in enumerate(data):
            print(f"{i+1}. {user.get('email')} - {user.get('name')}")

if __name__ == "__main__":
    test_signin_logic()