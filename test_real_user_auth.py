#!/usr/bin/env python3

"""
Test authentication with existing user to debug refresh issue
"""

import requests
import json
import time

API_BASE = "http://localhost:5000"

def test_existing_user_auth():
    print("🧪 Testing authentication with existing user...")
    
    # Use existing user from database
    existing_user = {
        "email": "test@example.com",
        "password": "TestPassword123!"  # Try common password
    }
    
    session = requests.Session()
    
    try:
        # Step 1: Try signin with existing user
        print("\n1️⃣ Testing signin with existing user...")
        signin_response = session.post(f"{API_BASE}/auth/signin", json=existing_user)
        print(f"   Signin status: {signin_response.status_code}")
        
        if signin_response.status_code == 200:
            signin_data = signin_response.json()
            print(f"   Signin success: {signin_data.get('success')}")
            
            if signin_data.get('success'):
                token = signin_data.get('token')
                user_data = signin_data.get('user')
                print(f"   ✅ Token received: {token[:20]}..." if token else "   ❌ No token received")
                print(f"   ✅ User: {user_data.get('name')} ({user_data.get('email')})")
                
                # Step 2: Verify token immediately
                print("\n2️⃣ Testing immediate token verification...")
                verify_response = session.get(f"{API_BASE}/auth/verify", headers={
                    "Authorization": f"Bearer {token}"
                })
                print(f"   Verify status: {verify_response.status_code}")
                if verify_response.status_code == 200:
                    verify_data = verify_response.json()
                    print(f"   ✅ Verification successful: {verify_data.get('valid')}")
                    print(f"   ✅ User from verify: {verify_data.get('user', {}).get('name')}")
                else:
                    print(f"   ❌ Verify error: {verify_response.text}")
                
                # Step 3: Simulate page refresh - new session, same token
                print("\n3️⃣ Simulating page refresh (new session, same token)...")
                new_session = requests.Session()
                
                verify_response3 = new_session.get(f"{API_BASE}/auth/verify", headers={
                    "Authorization": f"Bearer {token}"
                })
                print(f"   Verify after refresh status: {verify_response3.status_code}")
                if verify_response3.status_code == 200:
                    verify_data3 = verify_response3.json()
                    print(f"   ✅ Verification after refresh: {verify_data3.get('valid')}")
                else:
                    print(f"   ❌ Verify after refresh error: {verify_response3.text}")
                
                # Step 4: Try signup with same email (should fail)
                print("\n4️⃣ Testing signup with existing email...")
                signup_response = new_session.post(f"{API_BASE}/auth/signup", json={
                    "name": "Test User 2",
                    "email": existing_user["email"],
                    "password": "NewPassword123!"
                })
                print(f"   Signup status: {signup_response.status_code}")
                if signup_response.status_code != 200:
                    print(f"   ✅ Expected error: {signup_response.text}")
                else:
                    signup_data = signup_response.json()
                    print(f"   ❌ Unexpected success: {signup_data}")
                
                # Step 5: Try signin again after "refresh"
                print("\n5️⃣ Testing signin again after refresh...")
                signin_response2 = new_session.post(f"{API_BASE}/auth/signin", json=existing_user)
                print(f"   Second signin status: {signin_response2.status_code}")
                if signin_response2.status_code == 200:
                    signin_data2 = signin_response2.json()
                    print(f"   ✅ Second signin success: {signin_data2.get('success')}")
                    if signin_data2.get('success'):
                        new_token = signin_data2.get('token')
                        print(f"   ✅ New token: {new_token[:20]}...")
                        print(f"   🔍 Same token? {token == new_token}")
                else:
                    print(f"   ❌ Second signin error: {signin_response2.text}")
                
            else:
                print(f"   ❌ Signin failed: {signin_data}")
        else:
            print(f"   ❌ Signin error: {signin_response.text}")
            
            # If signin failed, let's try different passwords
            print("\n🔑 Trying different passwords...")
            test_passwords = [
                "password123",
                "Password123",
                "Password123!",
                "TestPassword123",
                "testpassword"
            ]
            
            for pwd in test_passwords:
                test_signin = session.post(f"{API_BASE}/auth/signin", json={
                    "email": existing_user["email"],
                    "password": pwd
                })
                if test_signin.status_code == 200:
                    print(f"   ✅ Password '{pwd}' works!")
                    break
                else:
                    print(f"   ❌ Password '{pwd}' failed")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_existing_user_auth()
