#!/usr/bin/env python3
"""
Very simple test to verify authentication is working
"""

def test_authentication_api():
    """Test authentication endpoints directly"""
    import requests
    import json
    
    base_url = "http://localhost:5000"
    
    # Test data
    test_user = {
        'name': 'Frontend Test',
        'email': 'frontend@test.com',
        'password': 'Frontend123'
    }
    
    print("🔧 Testing Authentication API...")
    
    try:
        # Test 1: Server health
        print("\n1. Testing server connection...")
        try:
            r = requests.get(f"{base_url}/auth/health", timeout=5)
            print(f"   Health Status: {r.status_code}")
            if r.status_code == 200:
                print("   ✅ Server is responding")
            else:
                print("   ❌ Server health check failed")
                return False
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Cannot connect to server: {e}")
            return False
        
        # Test 2: Signup
        print("\n2. Testing user signup...")
        r = requests.post(f"{base_url}/auth/signup", json=test_user, timeout=10)
        print(f"   Signup Status: {r.status_code}")
        
        if r.status_code == 201:
            print("   ✅ Signup successful")
        elif r.status_code == 409:
            print("   ℹ️ User already exists (409)")
        else:
            print(f"   ❌ Signup failed: {r.json()}")
            return False
        
        # Test 3: Signin  
        print("\n3. Testing user signin...")
        signin_data = {
            'email': test_user['email'],
            'password': test_user['password']
        }
        
        r = requests.post(f"{base_url}/auth/signin", json=signin_data, timeout=10)
        print(f"   Signin Status: {r.status_code}")
        
        if r.status_code == 200:
            response_data = r.json()
            print("   ✅ Signin successful!")
            print(f"   Token: {response_data.get('token', 'No token')[:20]}...")
            print(f"   User: {response_data.get('user', {}).get('name', 'No name')}")
            return True
        else:
            print(f"   ❌ Signin failed: {r.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_authentication_api()
    if success:
        print("\n🎉 Authentication API is working!")
        print("   Your React frontend should be able to authenticate users.")
        print("   The 500 errors should be resolved.")
    else:
        print("\n❌ Authentication API test failed.")
        print("   Please ensure the Flask server is running on port 5000.")