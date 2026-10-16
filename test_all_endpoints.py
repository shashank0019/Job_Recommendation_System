#!/usr/bin/env python3
"""
Test all endpoints in the comprehensive local server
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_all_endpoints():
    """Test all server endpoints"""
    print("🧪 Testing All Endpoints")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1️⃣ Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print("❌ Health check failed")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: Sign in
    print("\n2️⃣ Testing Sign In...")
    try:
        signin_data = {
            "email": "shashikingmaker495@gmail.com", 
            "password": "password123"
        }
        response = requests.post(f"{BASE_URL}/auth/signin", json=signin_data, timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"✅ Sign in successful, got token: {token[:20]}...")
            return token
        else:
            print(f"❌ Sign in failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Sign in error: {e}")
        return None

def test_authenticated_endpoints(token):
    """Test endpoints that require authentication"""
    if not token:
        print("⚠️ No token available, skipping authenticated tests")
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 3: Token verification
    print("\n3️⃣ Testing Token Verification...")
    try:
        response = requests.get(f"{BASE_URL}/auth/verify", headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Token verification passed")
        else:
            print("❌ Token verification failed")
    except Exception as e:
        print(f"❌ Token verification error: {e}")

def test_public_endpoints():
    """Test public endpoints"""
    
    # Test 4: Problems API
    print("\n4️⃣ Testing Problems API...")
    try:
        response = requests.get(f"{BASE_URL}/api/problems?limit=5", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Problems API works, got {len(data.get('items', []))} problems")
            if data.get('items'):
                print(f"   Sample: {data['items'][0].get('title')}")
        else:
            print("❌ Problems API failed")
    except Exception as e:
        print(f"❌ Problems API error: {e}")
    
    # Test 5: Recommend API
    print("\n5️⃣ Testing Recommend API...")
    try:
        recommend_data = {"resume_text": "Software developer with Python experience"}
        response = requests.post(f"{BASE_URL}/recommend", json=recommend_data, timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Recommend API works, got {len(data.get('jobs', []))} jobs")
        else:
            print("❌ Recommend API failed")
    except Exception as e:
        print(f"❌ Recommend API error: {e}")
    
    # Test 6: Interview Questions
    print("\n6️⃣ Testing Interview Questions...")
    try:
        response = requests.get(f"{BASE_URL}/interview/questions", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Interview API works, got {len(data.get('questions', []))} questions")
        else:
            print("❌ Interview API failed")
    except Exception as e:
        print(f"❌ Interview API error: {e}")

if __name__ == "__main__":
    token = test_all_endpoints()
    test_authenticated_endpoints(token)
    test_public_endpoints()
    
    print(f"\n🎯 Server Test Summary:")
    print(f"   - Server running at: {BASE_URL}")
    print(f"   - All React endpoints should work now!")
    print(f"   - Clear browser localStorage if you have old tokens")