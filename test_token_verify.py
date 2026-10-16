#!/usr/bin/env python3
"""
Test the verify token endpoint
"""
import requests
import json

def test_verify_token():
    """Test token verification"""
    
    # First, get a token by signing in
    signin_url = "http://localhost:5000/auth/signin"
    signin_data = {
        "email": "shashikingmaker495@gmail.com",
        "password": "password123"
    }
    
    print("🔐 Getting token via signin...")
    signin_response = requests.post(signin_url, json=signin_data)
    
    if signin_response.status_code != 200:
        print("❌ Failed to signin")
        return False
    
    token = signin_response.json().get('token')
    print(f"✅ Got token: {token[:20]}...")
    
    # Now test token verification
    verify_url = "http://localhost:5000/auth/verify"
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔍 Testing token verification...")
    verify_response = requests.get(verify_url, headers=headers)
    
    print(f"Status Code: {verify_response.status_code}")
    print(f"Response: {json.dumps(verify_response.json(), indent=2)}")
    
    if verify_response.status_code == 200:
        data = verify_response.json()
        if data.get('success') and data.get('valid'):
            print("✅ TOKEN VERIFICATION SUCCESSFUL!")
            return True
    
    print("❌ TOKEN VERIFICATION FAILED!")
    return False

if __name__ == "__main__":
    test_verify_token()