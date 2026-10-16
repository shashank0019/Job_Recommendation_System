"""
Test script to verify profile update API endpoint works
"""
import requests
import json

def test_profile_api():
    """Test the profile update API endpoint"""
    try:
        # First, let's test if the server is running
        base_url = "http://localhost:5000"
        
        print("🔍 Testing server connection...")
        response = requests.get(f"{base_url}/auth/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running")
            print(f"📊 Health check response: {response.json()}")
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
            
        # Test signin to get a valid token
        print("\n🔐 Testing user authentication...")
        signin_data = {
            "email": "shashikingmaker495@gmail.com",
            "password": "your_password_here"  # You'll need to provide the actual password
        }
        
        # Note: This will fail without the actual password, but we can check the endpoint
        signin_response = requests.post(f"{base_url}/auth/signin", json=signin_data)
        print(f"📋 Signin response status: {signin_response.status_code}")
        
        if signin_response.status_code == 200:
            signin_result = signin_response.json()
            token = signin_result.get('token')
            print("✅ Authentication successful")
            
            # Test profile update
            print("\n🔄 Testing profile update...")
            profile_data = {
                "name": "Shashank C A",
                "mobile": "9876543210",
                "gender": "male", 
                "state": "Karnataka",
                "skills": ["java", "python", "react"],
                "employment_status": "working"
            }
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            update_response = requests.put(f"{base_url}/auth/profile", json=profile_data, headers=headers)
            print(f"📊 Profile update response: {update_response.status_code}")
            
            if update_response.status_code == 200:
                result = update_response.json()
                print("✅ Profile update successful!")
                print(f"📋 Updated user: {result.get('user', {})}")
                return True
            else:
                print(f"❌ Profile update failed: {update_response.text}")
                return False
        else:
            print(f"❌ Authentication failed: {signin_response.text}")
            print("ℹ️  This is expected if you haven't provided the correct password")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server. Make sure it's running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing profile update API endpoint...")
    success = test_profile_api()
    
    if success:
        print("✅ API test completed successfully!")
    else:
        print("❌ API test failed!")
        print("\nℹ️  To complete this test, you need to:")
        print("1. Make sure the backend server is running")
        print("2. Provide the correct password in the signin_data")
        print("3. Or test manually through the frontend")
