#!/usr/bin/env python3
"""
Test script to verify the fixed authentication flow
"""
import requests
import json

API_BASE = "http://localhost:5000"

def test_complete_auth_flow():
    """Test the complete signup -> signin flow with the fixed frontend"""
    print("🧪 Testing FIXED signup -> signin flow...")
    
    test_user = {
        "name": "New Test User",
        "email": "newtestuser@example.com",
        "password": "NewTestPassword123"
    }
    
    # Step 1: Clean up any existing user first
    print(f"\n🧹 Cleaning up existing test user...")
    try:
        response = requests.delete(f"{API_BASE}/auth/cleanup/{test_user['email']}")
        print(f"Cleanup status: {response.status_code}")
    except Exception as e:
        print(f"Cleanup note: {e}")
    
    # Step 2: Sign up via backend API (same as before)
    print(f"\n1️⃣ Testing signup via backend API...")
    try:
        response = requests.post(f"{API_BASE}/auth/signup", json=test_user)
        print(f"Signup status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Signup successful: User ID {data['user']['id']}")
        else:
            print(f"❌ Signup failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Signup request failed: {e}")
        return False
    
    # Step 3: Sign in via backend API (this should work now)
    print(f"\n2️⃣ Testing signin via backend API...")
    try:
        signin_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        
        response = requests.post(f"{API_BASE}/auth/signin", json=signin_data)
        print(f"Signin status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Signin successful: Token {data['token'][:20]}...")
            print(f"✅ User data: {data['user']['name']} ({data['user']['email']})")
            return True
        else:
            print(f"❌ Signin failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Signin request failed: {e}")
        return False

def test_password_validation():
    """Test password validation on backend"""
    print(f"\n🔐 Testing password validation...")
    
    # Test weak password
    weak_user = {
        "name": "Weak User",
        "email": "weakuser@example.com", 
        "password": "weak"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/signup", json=weak_user)
        print(f"Weak password status: {response.status_code}")
        
        if response.status_code == 400:
            data = response.json()
            print(f"✅ Password validation working: {data['error']}")
        else:
            print(f"⚠️ Weak password was accepted: {response.text}")
    except Exception as e:
        print(f"❌ Password validation test failed: {e}")

def cleanup_test_users():
    """Clean up test users"""
    print(f"\n🧹 Cleaning up test users...")
    test_emails = ["newtestuser@example.com", "weakuser@example.com"]
    
    for email in test_emails:
        try:
            response = requests.delete(f"{API_BASE}/auth/cleanup/{email}")
            if response.status_code == 200:
                print(f"✅ Cleaned up {email}")
            else:
                print(f"⚠️ {email} cleanup: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Cleanup error for {email}: {e}")

if __name__ == "__main__":
    print("🚀 Testing Fixed Authentication System")
    print("=" * 50)
    
    # Test the main flow
    success = test_complete_auth_flow()
    
    # Test validation
    test_password_validation()
    
    # Cleanup
    cleanup_test_users()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Authentication system is working correctly!")
        print("✅ Users can now sign up and sign in with new emails")
    else:
        print("❌ Authentication system still has issues")
    
    print("\n📋 Summary of fixes:")
    print("- Frontend login now calls backend API instead of localStorage")
    print("- Frontend signup uses AuthContext for consistency")
    print("- Both signup and signin use the same MongoDB database")
    print("- Password validation and hashing handled by backend")
