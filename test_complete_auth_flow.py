#!/usr/bin/env python3

"""
Test complete authentication flow from signup to signin with refresh simulation
"""

import requests
import json
import time

API_BASE = "http://localhost:5000"

def test_complete_auth_flow():
    print("🧪 Testing complete authentication flow...")
    
    # Create unique user
    timestamp = int(time.time())
    test_user = {
        "name": "Flow Test User",
        "email": f"flowtest{timestamp}@example.com",
        "password": "FlowTestPassword123!"
    }
    
    print(f"👤 Testing with: {test_user['email']}")
    
    try:
        # Step 1: Create user
        print("\n1️⃣ Creating new user...")
        signup_response = requests.post(f"{API_BASE}/auth/signup", json=test_user)
        print(f"   Signup status: {signup_response.status_code}")
        
        if signup_response.status_code in [200, 201]:
            signup_data = signup_response.json()
            print(f"   ✅ Signup successful: {signup_data.get('success')}")
            
            # Step 2: Sign in immediately
            print("\n2️⃣ Signing in immediately after signup...")
            signin_response = requests.post(f"{API_BASE}/auth/signin", json={
                "email": test_user["email"],
                "password": test_user["password"]
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
                    
                    # Step 3: Verify token (simulating localStorage restore)
                    print("\n3️⃣ Verifying token (localStorage restore simulation)...")
                    verify_headers = {"Authorization": f"Bearer {token}"}
                    verify_response = requests.get(f"{API_BASE}/auth/verify", headers=verify_headers)
                    print(f"   Verify status: {verify_response.status_code}")
                    
                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        print(f"   ✅ Token valid: {verify_data.get('valid')}")
                        print(f"   ✅ User from verify: {verify_data.get('user', {}).get('name')}")
                        
                        # Step 4: Simulate page refresh - wait and verify again
                        print("\n4️⃣ Simulating page refresh (wait + verify)...")
                        time.sleep(2)  # Simulate page load time
                        
                        verify_refresh = requests.get(f"{API_BASE}/auth/verify", headers=verify_headers)
                        print(f"   Verify after refresh status: {verify_refresh.status_code}")
                        
                        if verify_refresh.status_code == 200:
                            verify_refresh_data = verify_refresh.json()
                            print(f"   ✅ Token still valid after refresh: {verify_refresh_data.get('valid')}")
                            
                            # Step 5: Try signup again (should fail - user exists)
                            print("\n5️⃣ Trying signup again (should fail)...")
                            signup_again = requests.post(f"{API_BASE}/auth/signup", json=test_user)
                            print(f"   Second signup status: {signup_again.status_code}")
                            
                            if signup_again.status_code == 409:  # Conflict - user exists
                                print(f"   ✅ Expected failure: {signup_again.json()}")
                                
                                # Step 6: Try signin again (should work)
                                print("\n6️⃣ Trying signin again (should work)...")
                                signin_again = requests.post(f"{API_BASE}/auth/signin", json={
                                    "email": test_user["email"],
                                    "password": test_user["password"]
                                })
                                print(f"   Second signin status: {signin_again.status_code}")
                                
                                if signin_again.status_code == 200:
                                    signin_again_data = signin_again.json()
                                    print(f"   ✅ Second signin successful: {signin_again_data.get('success')}")
                                    
                                    if signin_again_data.get('success'):
                                        new_token = signin_again_data.get('token')
                                        print(f"   ✅ New token: {new_token[:20]}...")
                                        print(f"   🔍 Same token? {token == new_token}")
                                        
                                        # Verify new token
                                        new_verify_headers = {"Authorization": f"Bearer {new_token}"}
                                        verify_new = requests.get(f"{API_BASE}/auth/verify", headers=new_verify_headers)
                                        print(f"   New token verify status: {verify_new.status_code}")
                                        
                                        if verify_new.status_code == 200:
                                            print(f"   ✅ New token is valid")
                                            print(f"\n🎉 AUTHENTICATION FLOW WORKING CORRECTLY!")
                                            print(f"   - Signup: ✅ Working")
                                            print(f"   - Signin: ✅ Working") 
                                            print(f"   - Token verification: ✅ Working")
                                            print(f"   - Refresh simulation: ✅ Working")
                                            print(f"   - Duplicate signup prevention: ✅ Working")
                                            print(f"   - Repeat signin: ✅ Working")
                                            
                                            print(f"\n💡 The issue is likely in the FRONTEND, not backend!")
                                            print(f"   Check:")
                                            print(f"   - localStorage token storage/retrieval")
                                            print(f"   - AuthContext initialization timing")
                                            print(f"   - Token format in Authorization header")
                                            print(f"   - Error handling in frontend")
                                        else:
                                            print(f"   ❌ New token verification failed: {verify_new.text}")
                                    else:
                                        print(f"   ❌ Second signin failed: {signin_again_data}")
                                        print(f"   🚨 BACKEND ISSUE: Signin failing after refresh!")
                                else:
                                    print(f"   ❌ Second signin error: {signin_again.text}")
                                    print(f"   🚨 BACKEND ISSUE: Signin API failing!")
                            else:
                                print(f"   ❌ Unexpected signup success: {signup_again.json()}")
                        else:
                            print(f"   ❌ Token invalid after refresh: {verify_refresh.text}")
                            print(f"   🚨 BACKEND ISSUE: Token expiring too quickly!")
                    else:
                        print(f"   ❌ Token verification failed: {verify_response.text}")
                        print(f"   🚨 BACKEND ISSUE: Token verification not working!")
                else:
                    print(f"   ❌ Signin failed: {signin_data}")
            else:
                print(f"   ❌ Signin error: {signin_response.text}")
                print(f"   🚨 BACKEND ISSUE: Cannot signin after signup!")
        else:
            print(f"   ❌ Signup error: {signup_response.text}")
            print(f"   🚨 BACKEND ISSUE: Signup not working!")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_auth_flow()
