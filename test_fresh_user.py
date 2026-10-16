#!/usr/bin/env python3

"""
Test with a completely fresh user to isolate the authentication issue
"""

import requests
import json
import time
from datetime import datetime

API_BASE = "http://localhost:5000"

def test_fresh_user():
    print("🧪 Testing with fresh user...")
    
    # Create unique user
    timestamp = int(time.time())
    fresh_user = {
        "name": "Fresh Test User",
        "email": f"fresh{timestamp}@example.com",
        "password": "FreshPassword123!"
    }
    
    print(f"👤 Creating user: {fresh_user['email']}")
    
    session = requests.Session()
    
    try:
        # Step 1: Create fresh user
        print("\n1️⃣ Creating fresh user...")
        signup_response = session.post(f"{API_BASE}/auth/signup", json=fresh_user)
        print(f"   Signup status: {signup_response.status_code}")
        
        if signup_response.status_code == 200:
            signup_data = signup_response.json()
            print(f"   ✅ Signup successful: {signup_data}")
            
            # Step 2: Sign in immediately
            print("\n2️⃣ Signing in immediately...")
            signin_response = session.post(f"{API_BASE}/auth/signin", json={
                "email": fresh_user["email"],
                "password": fresh_user["password"]
            })
            print(f"   Signin status: {signin_response.status_code}")
            
            if signin_response.status_code == 200:
                signin_data = signin_response.json()
                print(f"   ✅ Signin successful: {signin_data.get('success')}")
                
                if signin_data.get('success'):
                    token = signin_data.get('token')
                    user_data = signin_data.get('user')
                    print(f"   ✅ Token: {token[:20]}...")
                    print(f"   ✅ User: {user_data.get('name')}")
                    
                    # Step 3: Verify token
                    print("\n3️⃣ Verifying token...")
                    verify_response = session.get(f"{API_BASE}/auth/verify", headers={
                        "Authorization": f"Bearer {token}"
                    })
                    print(f"   Verify status: {verify_response.status_code}")
                    
                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        print(f"   ✅ Token valid: {verify_data.get('valid')}")
                        
                        # Step 4: Simulate refresh - new session with same token
                        print("\n4️⃣ Simulating page refresh...")
                        refresh_session = requests.Session()
                        
                        verify_refresh = refresh_session.get(f"{API_BASE}/auth/verify", headers={
                            "Authorization": f"Bearer {token}"
                        })
                        print(f"   Verify after refresh status: {verify_refresh.status_code}")
                        
                        if verify_refresh.status_code == 200:
                            verify_refresh_data = verify_refresh.json()
                            print(f"   ✅ Token still valid after refresh: {verify_refresh_data.get('valid')}")
                            
                            # Step 5: Try signup again (should fail)
                            print("\n5️⃣ Trying signup again (should fail)...")
                            signup_again = refresh_session.post(f"{API_BASE}/auth/signup", json=fresh_user)
                            print(f"   Second signup status: {signup_again.status_code}")
                            
                            if signup_again.status_code != 200:
                                print(f"   ✅ Expected failure: {signup_again.json()}")
                            else:
                                print(f"   ❌ Unexpected success: {signup_again.json()}")
                            
                            # Step 6: Try signin again (should work)
                            print("\n6️⃣ Trying signin again (should work)...")
                            signin_again = refresh_session.post(f"{API_BASE}/auth/signin", json={
                                "email": fresh_user["email"],
                                "password": fresh_user["password"]
                            })
                            print(f"   Second signin status: {signin_again.status_code}")
                            
                            if signin_again.status_code == 200:
                                signin_again_data = signin_again.json()
                                print(f"   ✅ Second signin successful: {signin_again_data.get('success')}")
                                
                                if signin_again_data.get('success'):
                                    new_token = signin_again_data.get('token')
                                    print(f"   ✅ New token: {new_token[:20]}...")
                                    print(f"   🔍 Same token as before? {token == new_token}")
                                    
                                    # Step 7: Verify new token
                                    print("\n7️⃣ Verifying new token...")
                                    verify_new = refresh_session.get(f"{API_BASE}/auth/verify", headers={
                                        "Authorization": f"Bearer {new_token}"
                                    })
                                    print(f"   New token verify status: {verify_new.status_code}")
                                    
                                    if verify_new.status_code == 200:
                                        verify_new_data = verify_new.json()
                                        print(f"   ✅ New token valid: {verify_new_data.get('valid')}")
                                        print(f"   🎉 Authentication flow working correctly!")
                                    else:
                                        print(f"   ❌ New token verification failed: {verify_new.text}")
                                else:
                                    print(f"   ❌ Second signin failed: {signin_again_data}")
                            else:
                                print(f"   ❌ Second signin error: {signin_again.text}")
                                print("   🚨 THIS IS THE ISSUE - signin failing after refresh!")
                        else:
                            print(f"   ❌ Token invalid after refresh: {verify_refresh.text}")
                            print("   🚨 THIS IS THE ISSUE - token becoming invalid after refresh!")
                    else:
                        print(f"   ❌ Token verification failed: {verify_response.text}")
                else:
                    print(f"   ❌ Signin failed: {signin_data}")
            else:
                print(f"   ❌ Signin error: {signin_response.text}")
        else:
            print(f"   ❌ Signup error: {signup_response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fresh_user()
