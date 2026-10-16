#!/usr/bin/env python3
"""
Test script to demonstrate the auth mismatch issue
"""
import requests
import json

API_BASE = "http://localhost:5000"

def test_signup_signin_flow():
    """Test the complete signup -> signin flow"""
    print("🧪 Testing signup -> signin flow...")
    
    test_user = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "TestPassword123"
    }
    
    # Step 1: Sign up via backend API
    print(f"\n1️⃣ Testing signup via backend API...")
    try:
        response = requests.post(f"{API_BASE}/auth/signup", json=test_user)
        print(f"Signup status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Signup successful: {data}")
        elif response.status_code == 409:
            print("⚠️ User already exists - continuing with signin test")
        else:
            print(f"❌ Signup failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Signup request failed: {e}")
        return
    
    # Step 2: Try to sign in via backend API
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
            print(f"✅ Signin successful: {data}")
        else:
            print(f"❌ Signin failed: {response.text}")
    except Exception as e:
        print(f"❌ Signin request failed: {e}")
    
    print(f"\n📋 Summary:")
    print(f"- Signup creates user in MongoDB database")
    print(f"- Frontend signin only checks localStorage")
    print(f"- This causes signin to fail for new users!")

def cleanup_test_user():
    """Clean up test user"""
    print(f"\n🧹 Cleaning up test user...")
    try:
        response = requests.delete(f"{API_BASE}/auth/cleanup/testuser@example.com")
        if response.status_code == 200:
            print("✅ Test user cleaned up")
        else:
            print(f"⚠️ Cleanup response: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")

if __name__ == "__main__":
    test_signup_signin_flow()
    cleanup_test_user()
