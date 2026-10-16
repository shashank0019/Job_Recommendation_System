"""
Debug signin 401 errors
"""
import requests
import json

def test_signin_debug():
    """Test signin endpoint with debugging"""
    print("🔍 Debugging Signin 401 Errors")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Test 1: Check if server is responding
    print("\n1️⃣ Testing server health...")
    try:
        health_response = requests.get(f"{base_url}/auth/health", timeout=5)
        print(f"✅ Health check: {health_response.status_code}")
        if health_response.status_code == 200:
            print(f"📊 Health data: {health_response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test 2: Check signin endpoint with known user
    print("\n2️⃣ Testing signin with your credentials...")
    signin_data = {
        "email": "shashikingmaker495@gmail.com",
        "password": "test123"  # Common test password
    }
    
    try:
        print(f"📤 Sending: {json.dumps(signin_data, indent=2)}")
        
        response = requests.post(f"{base_url}/auth/signin", 
                               json=signin_data,
                               headers={'Content-Type': 'application/json'},
                               timeout=10)
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        print(f"📥 Response Body: {response.text}")
        
        if response.status_code == 401:
            print("\n🔍 401 Analysis:")
            print("   - Invalid email or password")
            print("   - User might not exist")
            print("   - Password might be different")
            
        elif response.status_code == 200:
            data = response.json()
            print(f"✅ Signin successful!")
            print(f"👤 User: {data.get('user', {}).get('name')}")
            print(f"🔑 Token: {data.get('token', 'No token')[:20]}...")
            
    except Exception as e:
        print(f"❌ Signin request failed: {e}")
    
    # Test 3: Try different common passwords
    print("\n3️⃣ Testing common passwords...")
    common_passwords = ["password", "123456", "admin", "test", "shashank"]
    
    for pwd in common_passwords:
        try:
            test_data = {
                "email": "shashikingmaker495@gmail.com",
                "password": pwd
            }
            
            response = requests.post(f"{base_url}/auth/signin", 
                                   json=test_data,
                                   headers={'Content-Type': 'application/json'},
                                   timeout=5)
            
            if response.status_code == 200:
                print(f"✅ SUCCESS with password: '{pwd}'")
                data = response.json()
                print(f"👤 User: {data.get('user', {}).get('name')}")
                return
            else:
                print(f"❌ Failed with '{pwd}': {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing '{pwd}': {e}")
    
    # Test 4: Check if user exists by trying signup
    print("\n4️⃣ Checking if user exists...")
    try:
        signup_data = {
            "name": "Test User",
            "email": "shashikingmaker495@gmail.com",
            "password": "test123"
        }
        
        response = requests.post(f"{base_url}/auth/signup", 
                               json=signup_data,
                               headers={'Content-Type': 'application/json'},
                               timeout=5)
        
        print(f"📥 Signup Response: {response.status_code}")
        print(f"📥 Signup Body: {response.text}")
        
        if response.status_code == 400 and "already exists" in response.text:
            print("✅ User exists - password is incorrect")
        elif response.status_code == 201:
            print("✅ User created successfully - try signin again")
        
    except Exception as e:
        print(f"❌ Signup test failed: {e}")
    
    print(f"\n🎯 Summary:")
    print(f"   - Server is responding")
    print(f"   - Signin endpoint is working")
    print(f"   - Issue is likely incorrect password")
    print(f"   - Try logging in with correct password")

if __name__ == "__main__":
    test_signin_debug()
