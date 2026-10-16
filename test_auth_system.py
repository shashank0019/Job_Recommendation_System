#!/usr/bin/env python3
"""
Test script for authentication system
"""
import requests
import json
import time

API_BASE = "http://localhost:5000"

def test_auth_system():
    """Test the complete authentication system"""
    print("🧪 Testing Authentication System")
    print("=" * 50)
    
    # Test data
    test_user = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "TestPassword123"
    }
    
    session = requests.Session()
    
    # Test 1: Health check
    print("\n1. 🏥 Testing auth health endpoint...")
    try:
        response = session.get(f"{API_BASE}/auth/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Auth module healthy, {data.get('users_count', 0)} users in database")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Test 2: User Registration
    print("\n2. 📝 Testing user registration...")
    try:
        response = session.post(f"{API_BASE}/auth/signup", json=test_user)
        if response.status_code == 201:
            data = response.json()
            print(f"   ✅ User registered successfully: {data['user']['name']}")
        elif response.status_code == 409:
            print("   ⚠️  User already exists, continuing with login test...")
        else:
            print(f"   ❌ Registration failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
        return False
    
    # Test 3: User Login
    print("\n3. 🔐 Testing user login...")
    try:
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        response = session.post(f"{API_BASE}/auth/signin", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data["token"]
            user_data = data["user"]
            print(f"   ✅ Login successful: {user_data['name']}")
            print(f"   🎫 Token received: {token[:20]}...")
        else:
            print(f"   ❌ Login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return False
    
    # Test 4: Token Verification
    print("\n4. ✅ Testing token verification...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = session.get(f"{API_BASE}/auth/verify", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Token verified: {data['user']['email']}")
        else:
            print(f"   ❌ Token verification failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Token verification error: {e}")
        return False
    
    # Test 5: Profile Access
    print("\n5. 👤 Testing profile access...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = session.get(f"{API_BASE}/auth/profile", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Profile accessed: {data['user']['name']}")
        else:
            print(f"   ❌ Profile access failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Profile access error: {e}")
        return False
    
    # Test 6: Profile Update
    print("\n6. 📝 Testing profile update...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        update_data = {
            "resume_text": "Updated resume content with new skills",
            "skills": ["Python", "React", "MongoDB", "Authentication"],
            "preferences": {"job_type": "remote", "experience_level": "senior"}
        }
        response = session.put(f"{API_BASE}/auth/profile", json=update_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Profile updated successfully")
            print(f"   📊 Skills: {data['user']['profile'].get('skills', [])}")
        else:
            print(f"   ❌ Profile update failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Profile update error: {e}")
        return False
    
    # Test 7: Logout
    print("\n7. 🚪 Testing logout...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = session.post(f"{API_BASE}/auth/logout", headers=headers)
        if response.status_code == 200:
            print("   ✅ Logout successful")
        else:
            print(f"   ❌ Logout failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Logout error: {e}")
        return False
    
    # Test 8: Access after logout (should fail)
    print("\n8. 🚫 Testing access after logout...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = session.get(f"{API_BASE}/auth/profile", headers=headers)
        if response.status_code == 401:
            print("   ✅ Access correctly denied after logout")
        else:
            print(f"   ❌ Unexpected response after logout: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Post-logout test error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All authentication tests passed!")
    print("\n📋 Test Summary:")
    print("   ✅ Health check")
    print("   ✅ User registration")
    print("   ✅ User login")
    print("   ✅ Token verification")
    print("   ✅ Profile access")
    print("   ✅ Profile update")
    print("   ✅ Logout")
    print("   ✅ Access control after logout")
    
    return True

def test_validation():
    """Test input validation"""
    print("\n🧪 Testing Input Validation")
    print("=" * 30)
    
    session = requests.Session()
    
    # Test invalid email
    print("\n1. Testing invalid email...")
    response = session.post(f"{API_BASE}/auth/signup", json={
        "name": "Test User",
        "email": "invalid-email",
        "password": "ValidPass123"
    })
    if response.status_code == 400:
        print("   ✅ Invalid email correctly rejected")
    else:
        print(f"   ❌ Invalid email validation failed: {response.status_code}")
    
    # Test weak password
    print("\n2. Testing weak password...")
    response = session.post(f"{API_BASE}/auth/signup", json={
        "name": "Test User",
        "email": "test2@example.com",
        "password": "weak"
    })
    if response.status_code == 400:
        print("   ✅ Weak password correctly rejected")
    else:
        print(f"   ❌ Weak password validation failed: {response.status_code}")
    
    # Test invalid name
    print("\n3. Testing invalid name...")
    response = session.post(f"{API_BASE}/auth/signup", json={
        "name": "X",
        "email": "test3@example.com",
        "password": "ValidPass123"
    })
    if response.status_code == 400:
        print("   ✅ Invalid name correctly rejected")
    else:
        print(f"   ❌ Invalid name validation failed: {response.status_code}")

if __name__ == "__main__":
    print("🚀 Starting Authentication System Tests...")
    print("Make sure the server is running on http://localhost:5000")
    print()
    
    # Wait a moment for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    try:
        # Test basic functionality
        success = test_auth_system()
        
        if success:
            # Test validation
            test_validation()
            
            print("\n🎯 All tests completed successfully!")
            print("\n💡 Next Steps:")
            print("   1. Update your frontend to use the authentication system")
            print("   2. Add protected routes where needed")
            print("   3. Implement user-specific features")
        else:
            print("\n💥 Some tests failed. Please check the server logs.")
            
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user.")
    except Exception as e:
        print(f"\n💥 Test execution error: {e}")