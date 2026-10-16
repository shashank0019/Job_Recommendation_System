#!/usr/bin/env python3
"""
Test the profile update endpoint
"""
import requests
import json

def test_profile_update():
    """Test profile update functionality"""
    
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
    
    # Test profile update
    profile_url = "http://localhost:5000/auth/profile"
    headers = {"Authorization": f"Bearer {token}"}
    
    profile_data = {
        "name": "Shashank C A",
        "mobile": "7760219785",
        "gender": "Male",
        "state": "Karnataka", 
        "skills": ["Python", "JavaScript"],
        "experience": "2 years",
        "education": "Bachelor's"
    }
    
    print("📝 Testing profile update...")
    print(f"📋 Profile data: {json.dumps(profile_data, indent=2)}")
    
    profile_response = requests.put(profile_url, json=profile_data, headers=headers)
    
    print(f"Status Code: {profile_response.status_code}")
    print(f"Response: {json.dumps(profile_response.json(), indent=2)}")
    
    if profile_response.status_code == 200:
        data = profile_response.json()
        if data.get('success'):
            print("✅ PROFILE UPDATE SUCCESSFUL!")
            return True
    
    print("❌ PROFILE UPDATE FAILED!")
    return False

if __name__ == "__main__":
    test_profile_update()