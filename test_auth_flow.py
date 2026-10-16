#!/usr/bin/env python3

"""
Test authentication flow to debug sign-in issues after refresh
"""

import requests
import json
import time

API_BASE = "http://localhost:5000"

def test_auth_flow():
    print("🧪 Testing authentication flow...")
    
    # Test data
    test_user = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "TestPassword123!"
    }
    
    session = requests.Session()
    
    try:
        # Step 1: Sign up (if user doesn't exist)
        print("\n1️⃣ Testing signup...")
        signup_response = session.post(f"{API_BASE}/auth/signup", json=test_user)
        print(f"   Signup status: {signup_response.status_code}")
        if signup_response.status_code == 200:
            signup_data = signup_response.json()
            print(f"   Signup response: {signup_data}")
        else:
            print(f"   Signup error: {signup_response.text}")
        
        # Step 2: Sign in
        print("\n2️⃣ Testing signin...")
        signin_response = session.post(f"{API_BASE}/auth/signin", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        print(f"   Signin status: {signin_response.status_code}")
        
        if signin_response.status_code == 200:
            signin_data = signin_response.json()
            print(f"   Signin success: {signin_data.get('success')}")
            
            if signin_data.get('success'):
                token = signin_data.get('token')
                user_data = signin_data.get('user')
                print(f"   Token received: {token[:20]}..." if token else "   No token received")
                print(f"   User data: {user_data}")
                
                # Step 3: Verify token immediately
                print("\n3️⃣ Testing immediate token verification...")
                verify_response = session.get(f"{API_BASE}/auth/verify", headers={
                    "Authorization": f"Bearer {token}"
                })
                print(f"   Verify status: {verify_response.status_code}")
                if verify_response.status_code == 200:
                    verify_data = verify_response.json()
                    print(f"   Verify response: {verify_data}")
                else:
                    print(f"   Verify error: {verify_response.text}")
                
                # Step 4: Wait a moment and verify again (simulating refresh)
                print("\n4️⃣ Testing token verification after delay (simulating refresh)...")
                time.sleep(2)
                
                verify_response2 = session.get(f"{API_BASE}/auth/verify", headers={
                    "Authorization": f"Bearer {token}"
                })
                print(f"   Verify status: {verify_response2.status_code}")
                if verify_response2.status_code == 200:
                    verify_data2 = verify_response2.json()
                    print(f"   Verify response: {verify_data2}")
                else:
                    print(f"   Verify error: {verify_response2.text}")
                
                # Step 5: Test signup again (should fail if user exists)
                print("\n5️⃣ Testing signup again (should show user exists)...")
                signup_response2 = session.post(f"{API_BASE}/auth/signup", json=test_user)
                print(f"   Second signup status: {signup_response2.status_code}")
                if signup_response2.status_code != 200:
                    print(f"   Second signup error: {signup_response2.text}")
                else:
                    signup_data2 = signup_response2.json()
                    print(f"   Second signup response: {signup_data2}")
                
                # Step 6: Test signin again
                print("\n6️⃣ Testing signin again...")
                signin_response2 = session.post(f"{API_BASE}/auth/signin", json={
                    "email": test_user["email"],
                    "password": test_user["password"]
                })
                print(f"   Second signin status: {signin_response2.status_code}")
                if signin_response2.status_code == 200:
                    signin_data2 = signin_response2.json()
                    print(f"   Second signin response: {signin_data2}")
                else:
                    print(f"   Second signin error: {signin_response2.text}")
                
            else:
                print(f"   Signin failed: {signin_data}")
        else:
            print(f"   Signin error: {signin_response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_auth_flow()
