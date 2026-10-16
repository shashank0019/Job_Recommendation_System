"""Test signup and signin through HTTP requests"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_signin():
    """Test signin with the user we just created"""
    print("\n=== Testing Signin ===")
    
    signin_data = {
        "email": "shashikingmaker495@gmail.com",
        "password": "Test@123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/signin",
            json=signin_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Signin successful!")
            return response.json()
        else:
            print(f"❌ Signin failed: {response.json().get('error')}")
            return None
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def test_signup_existing_user():
    """Test signup with an existing user (should return 409)"""
    print("\n=== Testing Signup with Existing User ===")
    
    signup_data = {
        "name": "Shashank",
        "email": "shashikingmaker495@gmail.com",
        "password": "Test@123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/signup",
            json=signup_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 409:
            print("✅ Correctly returned 409 - user already exists")
        else:
            print(f"⚠️ Unexpected status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    # First test signin
    token_data = test_signin()
    
    # Then test signup with existing user
    test_signup_existing_user()
