#!/usr/bin/env python3

"""
Test frontend-backend authentication flow to debug refresh issue
"""

import requests
import json

API_BASE = "http://localhost:5000"

def test_frontend_backend_auth():
    print("🧪 Testing frontend-backend authentication flow...")
    
    # Use an existing user that we know exists
    test_user = {
        "email": "shashikingmaker495@gmail.com",
        "password": "TestPassword123!"  # Try common password patterns
    }
    
    try:
        # Step 1: Signin (simulating frontend)
        print("\n1️⃣ Signing in (frontend simulation)...")
        signin_response = requests.post(f"{API_BASE}/auth/signin", json=test_user)
        print(f"   Status: {signin_response.status_code}")
        
        if signin_response.status_code == 200:
            signin_data = signin_response.json()
            print(f"   Success: {signin_data.get('success')}")
            
            if signin_data.get('success'):
                token = signin_data.get('token')
                user_data = signin_data.get('user')
                print(f"   ✅ Token: {token[:20]}...")
                print(f"   ✅ User: {user_data.get('name')}")
                
                # Step 2: Verify token immediately (simulating localStorage restore)
                print("\n2️⃣ Verifying token immediately...")
                verify_headers = {"Authorization": f"Bearer {token}"}
                verify_response = requests.get(f"{API_BASE}/auth/verify", headers=verify_headers)
                print(f"   Status: {verify_response.status_code}")
                
                if verify_response.status_code == 200:
                    verify_data = verify_response.json()
                    print(f"   ✅ Valid: {verify_data.get('valid')}")
                    print(f"   ✅ Success: {verify_data.get('success')}")
                else:
                    print(f"   ❌ Error: {verify_response.text}")
                    return
                
                # Step 3: Wait and verify again (simulating page refresh delay)
                print("\n3️⃣ Verifying token after delay...")
                import time
                time.sleep(1)
                
                verify_response2 = requests.get(f"{API_BASE}/auth/verify", headers=verify_headers)
                print(f"   Status: {verify_response2.status_code}")
                
                if verify_response2.status_code == 200:
                    verify_data2 = verify_response2.json()
                    print(f"   ✅ Valid: {verify_data2.get('valid')}")
                    print(f"   ✅ Success: {verify_data2.get('success')}")
                else:
                    print(f"   ❌ Error: {verify_response2.text}")
                
                # Step 4: Test with wrong token format (common frontend mistake)
                print("\n4️⃣ Testing with wrong token format...")
                wrong_headers = {"Authorization": token}  # Missing "Bearer "
                verify_wrong = requests.get(f"{API_BASE}/auth/verify", headers=wrong_headers)
                print(f"   Status: {verify_wrong.status_code}")
                print(f"   Expected error: {verify_wrong.text}")
                
                # Step 5: Test signup with same email (should fail)
                print("\n5️⃣ Testing signup with existing email...")
                signup_response = requests.post(f"{API_BASE}/auth/signup", json={
                    "name": "Another User",
                    "email": test_user["email"],
                    "password": "AnotherPassword123!"
                })
                print(f"   Status: {signup_response.status_code}")
                if signup_response.status_code != 200:
                    print(f"   ✅ Expected error: {signup_response.json()}")
                else:
                    print(f"   ❌ Unexpected success: {signup_response.json()}")
                
                # Step 6: Test signin again (should work)
                print("\n6️⃣ Testing signin again...")
                signin_response2 = requests.post(f"{API_BASE}/auth/signin", json=test_user)
                print(f"   Status: {signin_response2.status_code}")
                
                if signin_response2.status_code == 200:
                    signin_data2 = signin_response2.json()
                    print(f"   ✅ Success: {signin_data2.get('success')}")
                    
                    if signin_data2.get('success'):
                        new_token = signin_data2.get('token')
                        print(f"   ✅ New token: {new_token[:20]}...")
                        print(f"   🔍 Same token? {token == new_token}")
                        
                        # Verify new token
                        verify_new_headers = {"Authorization": f"Bearer {new_token}"}
                        verify_new = requests.get(f"{API_BASE}/auth/verify", headers=verify_new_headers)
                        print(f"   New token verify status: {verify_new.status_code}")
                        
                        if verify_new.status_code == 200:
                            print(f"   ✅ New token is valid")
                            print(f"   🎉 Backend authentication is working correctly!")
                        else:
                            print(f"   ❌ New token verification failed: {verify_new.text}")
                else:
                    print(f"   ❌ Second signin failed: {signin_response2.text}")
                    print(f"   🚨 This indicates a backend issue!")
            else:
                print(f"   ❌ Signin failed: {signin_data}")
        else:
            print(f"   ❌ Signin error: {signin_response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_frontend_backend_auth()
