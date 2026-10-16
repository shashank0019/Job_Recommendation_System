"""
Direct test of profile update functionality
"""
import requests
import json

def test_profile_update_direct():
    """Test profile update with hardcoded credentials"""
    base_url = "http://localhost:5000"
    
    print("🔍 Testing profile update directly...")
    
    # Step 1: Sign in to get token
    print("\n1️⃣ Signing in...")
    signin_data = {
        "email": "shashikingmaker495@gmail.com",
        "password": "test123"  # Replace with actual password
    }
    
    try:
        signin_response = requests.post(f"{base_url}/auth/signin", json=signin_data)
        print(f"📊 Signin status: {signin_response.status_code}")
        
        if signin_response.status_code != 200:
            print(f"❌ Signin failed: {signin_response.text}")
            print("\n🔧 Try these common passwords:")
            print("- test123")
            print("- password")  
            print("- 123456")
            print("- your_actual_password")
            return False
            
        signin_result = signin_response.json()
        token = signin_result.get('token')
        print(f"✅ Signin successful, got token: {token[:20]}...")
        
        # Step 2: Get current profile
        print("\n2️⃣ Getting current profile...")
        headers = {"Authorization": f"Bearer {token}"}
        
        profile_response = requests.get(f"{base_url}/auth/profile", headers=headers)
        print(f"📊 Profile get status: {profile_response.status_code}")
        
        if profile_response.status_code == 200:
            current_profile = profile_response.json()
            print(f"📋 Current profile: {json.dumps(current_profile, indent=2)}")
        
        # Step 3: Update profile
        print("\n3️⃣ Updating profile...")
        update_data = {
            "name": "Shashank C A",
            "mobile": "1234567890",
            "gender": "male",
            "state": "Karnataka", 
            "skills": ["javascript", "python", "react", "testing"],
            "employment_status": "working"
        }
        
        print(f"📝 Sending update data: {json.dumps(update_data, indent=2)}")
        
        update_response = requests.put(f"{base_url}/auth/profile", json=update_data, headers=headers)
        print(f"📊 Update status: {update_response.status_code}")
        print(f"📄 Update response: {update_response.text}")
        
        if update_response.status_code == 200:
            update_result = update_response.json()
            print(f"✅ Update successful!")
            print(f"📋 Updated profile: {json.dumps(update_result.get('user', {}), indent=2)}")
            return True
        else:
            print(f"❌ Update failed: {update_response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server")
        print("Make sure the backend is running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_profile_update_direct()
    if success:
        print("\n🎉 Profile update test PASSED!")
    else:
        print("\n💥 Profile update test FAILED!")
        print("\nNext steps:")
        print("1. Make sure backend server is running")
        print("2. Use correct password for signin")
        print("3. Check browser console for frontend errors")
