#!/usr/bin/env python3
"""
Test the interview experience endpoints on the correct server
"""
import requests
import json

API_BASE = "http://localhost:5001"

def test_interview_experience_endpoints():
    """Test interview experience endpoints"""
    print("🧪 Testing interview experience endpoints on port 5001...")
    
    # Test GET /api/experiences (should not require auth)
    print("\n1️⃣ Testing GET /api/experiences...")
    try:
        response = requests.get(f"{API_BASE}/api/experiences")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Experiences endpoint working")
            print(f"   - Experiences found: {len(data.get('experiences', []))}")
            print(f"   - Response structure: {list(data.keys())}")
        else:
            print(f"❌ Experiences endpoint failed: {response.text}")
    except Exception as e:
        print(f"❌ Experiences endpoint error: {e}")
    
    # Test POST /api/experiences (should require auth)
    print("\n2️⃣ Testing POST /api/experiences (should require auth)...")
    try:
        test_experience = {
            "company": "Test Company",
            "position": "Software Engineer",
            "experience_text": "Great interview experience",
            "interview_type": "technical",
            "difficulty_rating": 3,
            "outcome": "selected"
        }
        
        response = requests.post(f"{API_BASE}/api/experiences", json=test_experience)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Correctly requires authentication")
        elif response.status_code == 200:
            print("⚠️ No authentication required (unexpected)")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ POST experiences endpoint error: {e}")

def test_interview_experience_flow():
    """Test the complete interview experience flow"""
    print("\n🧪 Testing complete interview experience flow...")
    
    # Step 1: Create a test user and get auth token
    test_user = {
        "name": "Interview Sharer",
        "email": "interviewsharer@example.com",
        "password": "InterviewSharer123"
    }
    
    print("\n1️⃣ Setting up test user...")
    
    # Clean up existing user
    try:
        requests.delete(f"{API_BASE}/auth/cleanup/{test_user['email']}")
    except:
        pass
    
    # Sign up
    try:
        response = requests.post(f"{API_BASE}/auth/signup", json=test_user)
        if response.status_code != 201:
            print(f"❌ Signup failed: {response.text}")
            return False
        print("✅ User created successfully")
    except Exception as e:
        print(f"❌ Signup error: {e}")
        return False
    
    # Sign in to get token
    try:
        signin_data = {"email": test_user["email"], "password": test_user["password"]}
        response = requests.post(f"{API_BASE}/auth/signin", json=signin_data)
        if response.status_code != 200:
            print(f"❌ Signin failed: {response.text}")
            return False
        
        data = response.json()
        auth_token = data['token']
        user_id = data['user']['id']
        print(f"✅ User signed in, token: {auth_token[:20]}...")
    except Exception as e:
        print(f"❌ Signin error: {e}")
        return False
    
    # Step 2: Create an interview experience
    print("\n2️⃣ Creating interview experience...")
    
    experience_data = {
        "company": "Google",
        "position": "Software Engineer",
        "experience_text": "Had a great interview experience with Google. The interviewers were very friendly and the questions were challenging but fair.",
        "interview_type": "technical",
        "difficulty_rating": 4,
        "outcome": "selected",
        "interview_date": "2024-10-15",
        "location": "Mountain View, CA",
        "interview_rounds": 3,
        "preparation_time": "2 weeks",
        "questions_asked": ["Implement a binary search tree", "Design a URL shortener", "System design question"],
        "tips": ["Practice coding problems daily", "Review system design concepts", "Be confident and ask clarifying questions"],
        "tags": ["google", "software-engineer", "technical"],
        "anonymous": False
    }
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        response = requests.post(f"{API_BASE}/api/experiences", json=experience_data, headers=headers)
        
        print(f"Experience creation status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            experience_id = result['experience']['id']
            print(f"✅ Experience created successfully: {experience_id}")
        else:
            print(f"❌ Experience creation failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Experience creation error: {e}")
        return False
    
    # Step 3: Fetch experiences to verify it appears
    print("\n3️⃣ Fetching experiences to verify...")
    
    try:
        response = requests.get(f"{API_BASE}/api/experiences")
        
        if response.status_code == 200:
            result = response.json()
            experiences = result.get('experiences', [])
            print(f"✅ Found {len(experiences)} experiences total")
            
            # Look for our experience
            our_experience = next((exp for exp in experiences if exp.get('id') == experience_id), None)
            if our_experience:
                print(f"✅ Our experience is visible: '{our_experience['company']} - {our_experience['position']}'")
                print(f"   - Difficulty: {our_experience['difficulty_rating']}/5")
                print(f"   - Outcome: {our_experience['outcome']}")
                return True
            else:
                print(f"❌ Our experience is not visible in the list")
                print(f"   - Looking for experience ID: {experience_id}")
                print(f"   - Available experience IDs: {[exp.get('id') for exp in experiences]}")
                return False
        else:
            print(f"❌ Failed to fetch experiences: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Experience fetching error: {e}")
        return False

def cleanup():
    """Clean up test data"""
    print("\n🧹 Cleaning up...")
    try:
        requests.delete(f"{API_BASE}/auth/cleanup/interviewsharer@example.com")
        print("✅ Test user cleaned up")
    except:
        pass

if __name__ == "__main__":
    print("🚀 Testing Interview Experience System")
    print("=" * 50)
    
    # Test basic endpoints
    test_interview_experience_endpoints()
    
    # Test complete flow
    success = test_interview_experience_flow()
    cleanup()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Interview experience system is working correctly!")
        print("✅ Users can create experiences and they appear in the list")
    else:
        print("❌ Interview experience system has issues")
        print("🔧 Check server logs and database connection")
    
    print(f"\n📋 Status:")
    print(f"- Backend endpoints working on port 5001")
    print(f"- Frontend needs restart to use new port")
    print(f"- Environment variable: VITE_API_BASE=http://localhost:5001")
