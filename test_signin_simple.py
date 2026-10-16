#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

from config.database import DatabaseConfig
from auth.models import User

# Initialize database
db_config = DatabaseConfig()
print(f"Database connection status: {db_config.db is not None}")

# Test finding a user by email
test_email = "debugtest@example.com"
print(f"\nTesting user lookup for: {test_email}")

try:
    user = User.find_by_email(test_email)
    if user:
        print(f"✅ User found: {user.name}")
        print(f"Email: {user.email}")
        print(f"Password hash: {user.password_hash[:20]}...")
        
        # Test password verification
        test_password = "DebugTest123"
        print(f"\nTesting password verification with: {test_password}")
        
        if user.verify_password(test_password):
            print("✅ Password verification successful")
        else:
            print("❌ Password verification failed")
            
    else:
        print("❌ User not found")
        
        # Create user for testing
        print("\nCreating test user...")
        new_user = User.create("Debug Test User", test_email, "DebugTest123")
        if new_user:
            print("✅ Test user created")
        else:
            print("❌ Failed to create test user")
            
except Exception as e:
    print(f"❌ Error during user lookup: {e}")
    import traceback
    traceback.print_exc()