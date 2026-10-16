import requests
import json

def test_experience_api():
    base_url = "http://127.0.0.1:5003"
    
    print("🧪 Testing Interview Experience API...")
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test 2: GET experiences
    try:
        response = requests.get(f"{base_url}/api/experiences", timeout=5)
        data = response.json()
        print(f"✅ GET experiences: {response.status_code} - Found {data.get('total', 0)} experiences")
    except Exception as e:
        print(f"❌ GET experiences failed: {e}")
    
    # Test 3: POST new experience
    try:
        test_experience = {
            "company": "Test Company API",
            "position": "Test Position API", 
            "experience_text": "This is a test experience from API test script",
            "interview_type": "Technical",
            "difficulty_rating": "Medium",
            "outcome": "Pending"
        }
        
        response = requests.post(
            f"{base_url}/api/experiences", 
            json=test_experience,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ POST experience: {response.status_code} - Created ID {result['experience']['id']}")
            return result['experience']['id']
        else:
            print(f"❌ POST experience failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ POST experience failed: {e}")
    
    return None

if __name__ == "__main__":
    test_experience_api()
