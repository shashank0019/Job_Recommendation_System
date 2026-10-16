#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

# Test the authentication directly
print("Testing authentication logic directly...")

from auth.models import User

test_email = "debugtest@example.com"
test_password = "DebugTest123"

print(f"\n1. Finding user by email: {test_email}")
user = User.find_by_email(test_email)

if user:
    print("✅ User found")
    print(f"   Name: {user.name}")
    print(f"   Email: {user.email}")
    print(f"   Password hash: {user.password_hash[:30]}...")
    
    print(f"\n2. Testing password verification with: {test_password}")
    password_valid = user.verify_password(test_password)
    print(f"   Password valid: {password_valid}")
    
    if password_valid:
        print("\n3. Testing session creation...")
        from auth.models import Session
        session = Session.create(user_id=user._id)
        
        if session:
            print("✅ Session created successfully")
            print(f"   Session token: {session.session_token[:20]}...")
        else:
            print("❌ Failed to create session")
    else:
        print("❌ Password verification failed")
        
        # Test with raw bcrypt to see what's wrong
        print("\n   Testing with raw bcrypt...")
        import bcrypt
        try:
            raw_result = bcrypt.checkpw(test_password.encode('utf-8'), user.password_hash.encode('utf-8'))
            print(f"   Raw bcrypt result: {raw_result}")
        except Exception as e:
            print(f"   Raw bcrypt error: {e}")
else:
    print("❌ User not found")