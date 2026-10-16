#!/usr/bin/env python3
"""
Test script to check authentication and session validity
"""
import requests
import json

API_BASE = "http://localhost:5001"

def test_auth():
    print("🔍 Testing Authentication System")
    print("=" * 50)
    
    # Test 1: Check if we can get jobs without auth (should work)
    print("\n1. Testing public endpoint (GET /api/jobs)...")
    try:
        response = requests.get(f"{API_BASE}/api/jobs")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Jobs found: {len(data.get('jobs', []))}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Try to delete a job without auth (should fail with 401)
    print("\n2. Testing protected endpoint without auth (DELETE /api/jobs/test)...")
    try:
        response = requests.delete(f"{API_BASE}/api/jobs/test")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Try to sign in with test credentials
    print("\n3. Testing sign-in...")
    try:
        signin_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        response = requests.post(f"{API_BASE}/auth/signin", json=signin_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success')}")
            print(f"   Token: {data.get('token', 'None')[:20]}..." if data.get('token') else "   Token: None")
            
            # Test 4: Try to delete with valid token
            if data.get('token'):
                print("\n4. Testing protected endpoint with auth token...")
                headers = {"Authorization": f"Bearer {data['token']}"}
                response = requests.delete(f"{API_BASE}/api/jobs/test", headers=headers)
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_auth()
