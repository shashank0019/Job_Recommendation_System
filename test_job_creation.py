import requests
import json

def test_job_creation():
    """Test job posting creation with and without authentication"""
    base_url = "http://localhost:5000"
    
    # Sample job data (similar to what's shown in the screenshot)
    job_data = {
        "title": "Software Engineer",
        "company": "CVCCV",
        "description": "Test job posting description",
        "requirements": ["react", "java"],
        "location": "chikkabalapur",
        "salary_range": "1000000",
        "job_type": "full-time",
        "experience_level": "entry",
        "contact_email": "shashikingmaker19@gmail.com",
        "application_url": "https://company.com/careers/job-id",
        "application_deadline": "2025-10-30",
        "remote_allowed": False,
        "tags": ["react", "java"]
    }
    
    print("🧪 Testing Job Creation")
    print("=" * 40)
    
    # Test 1: Without authentication (should fail with 401)
    print("1. Testing without authentication...")
    try:
        response = requests.post(f"{base_url}/api/jobs", json=job_data, timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Test 2: Check what tokens exist in the database
    print("2. Checking available sessions...")
    try:
        # We need to check what sessions exist
        from config.database import get_db_config
        from auth.models import Session, User
        
        config = get_db_config()
        config.connect()  # Ensure connection is established
        if config.db is not None:
            sessions_collection = config.db.sessions
            sessions = list(sessions_collection.find({}))
            print(f"   Found {len(sessions)} sessions in database")
            
            if sessions:
                # Try with the first available session token
                session = sessions[0]
                print(f"   Session data: {session}")
                session_token = session.get('session_token')
                
                if session_token:
                    print(f"   Using session token: {session_token[:20]}...")
                    
                    headers = {
                        'Authorization': f'Bearer {session_token}',
                        'Content-Type': 'application/json'
                    }
                    
                    print("3. Testing with authentication...")
                    response = requests.post(f"{base_url}/api/jobs", json=job_data, headers=headers, timeout=5)
                    print(f"   Status: {response.status_code}")
                    print(f"   Response: {response.json()}")
                else:
                    print("   Session token is None")
            else:
                print("   No sessions found - user needs to sign in first")
        else:
            print("   Database not available")
            
    except Exception as e:
        print(f"   Error checking sessions: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_job_creation()
