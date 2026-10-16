"""Test signup from command line"""
import requests
import json

def test_signup():
    """Test signup endpoint"""
    url = "http://localhost:5000/auth/signup"
    
    data = {
        "name": "Shashank C A",
        "email": "shashikingmaker495@gmail.com",
        "password": "MyPassword123!"
    }
    
    print(f"Testing signup at: {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
        
        print(f"\n--- Response ---")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("\n✅ SIGNUP SUCCESSFUL!")
            print("\nNow you can signin with:")
            print(f"  Email: {data['email']}")
            print(f"  Password: {data['password']}")
            return True
        else:
            print(f"\n❌ SIGNUP FAILED!")
            return False
            
    except Exception as e:
        print(f"\n❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    test_signup()
