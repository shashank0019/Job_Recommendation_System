import requests
import json

def test_job_creation_with_active_token():
    """Test job posting creation with an active session token"""
    base_url = "http://localhost:5000"
    
    # Use one of the active session tokens we found
    # From the session check, we know there are active tokens like "CX6KUOPtkaI3pdLUKgdJ..."
    # Let's get a fresh one from the database
    
    from config.database import get_db_config
    from datetime import datetime
    
    config = get_db_config()
    config.connect()
    
    if config.db is not None:
        sessions_collection = config.db.sessions
        
        # Find an active session (not expired)
        current_time = datetime.utcnow()
        active_session = sessions_collection.find_one({
            "expires_at": {"$gt": current_time}
        })
        
        if active_session:
            session_token = active_session.get('session_token')
            print(f"✅ Found active session token: {session_token[:20]}...")
            
            # Sample job data (similar to what's shown in the screenshot)
            job_data = {
                "title": "Test Software Engineer",
                "company": "Test Company",
                "description": "This is a test job posting to verify the API is working",
                "requirements": ["react", "java", "python"],
                "location": "Test City",
                "salary_range": "50000-80000",
                "job_type": "full-time",
                "experience_level": "entry",
                "contact_email": "test@example.com",
                "application_url": "https://company.com/careers/test-job",
                "application_deadline": "2025-12-31",
                "remote_allowed": True,
                "tags": ["react", "java", "python"]
            }
            
            print("\n🧪 Testing Job Creation with Active Token")
            print("=" * 50)
            
            headers = {
                'Authorization': f'Bearer {session_token}',
                'Content-Type': 'application/json'
            }
            
            try:
                response = requests.post(f"{base_url}/api/jobs", json=job_data, headers=headers, timeout=10)
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 201:
                    result = response.json()
                    print("✅ SUCCESS! Job posting created successfully")
                    print(f"Job ID: {result.get('job', {}).get('id', 'N/A')}")
                    print(f"Job Title: {result.get('job', {}).get('title', 'N/A')}")
                    print(f"Company: {result.get('job', {}).get('company', 'N/A')}")
                elif response.status_code == 401:
                    result = response.json()
                    print(f"❌ Authentication Error: {result.get('error', 'Unknown error')}")
                else:
                    result = response.json()
                    print(f"❌ Error: {result.get('message', result.get('error', 'Unknown error'))}")
                    
            except Exception as e:
                print(f"❌ Request failed: {e}")
        else:
            print("❌ No active sessions found. User needs to sign in.")
    else:
        print("❌ Database connection failed")

if __name__ == "__main__":
    test_job_creation_with_active_token()
