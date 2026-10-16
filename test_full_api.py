import requests
import json

def test_api_endpoints():
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Career Guidance Platform API Endpoints")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Health Check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
    
    print()
    
    # Test jobs endpoint
    try:
        response = requests.get(f"{base_url}/api/jobs", timeout=5)
        print(f"✅ Jobs Endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data['jobs'])} jobs")
            for job in data['jobs']:
                print(f"   - {job['title']} at {job['company']} ({job['location']})")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Jobs Endpoint Failed: {e}")
    
    print()
    
    # Test experiences endpoint
    try:
        response = requests.get(f"{base_url}/api/experiences", timeout=5)
        print(f"✅ Experiences Endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data['experiences'])} experiences")
            for exp in data['experiences']:
                print(f"   - {exp['position']} at {exp['company']} (Rating: {exp['difficulty_rating']}/5)")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Experiences Endpoint Failed: {e}")
    
    print()
    print("🎉 API Testing Complete!")

if __name__ == "__main__":
    test_api_endpoints()
