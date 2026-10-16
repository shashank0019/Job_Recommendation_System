"""Test signin from command line"""
import requests
import json

def test_signin():
    """Test signin endpoint"""
    url = "http://localhost:5000/auth/signin"
    
    data = {
        "email": "shashikingmaker495@gmail.com",
        "password": "password123"
    }
    
    print(f"Testing signin at: {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
        
        print(f"\n--- Response ---")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n✅ SIGNIN SUCCESSFUL!")
            token = response.json().get('token')
            if token:
                print(f"\n🎟️  Your session token: {token[:50]}...")
            return True
        else:
            print(f"\n❌ SIGNIN FAILED!")
            return False
            
    except Exception as e:
        print(f"\n❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    test_signin()
