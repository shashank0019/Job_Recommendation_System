#!/usr/bin/env python3
"""
Test the complete job posting flow with the correct server
"""
import requests
import json

API_BASE = "http://localhost:5001"

def test_job_posting_flow():
    """Test the complete job posting flow"""
    print("🧪 Testing job posting flow on correct server (port 5001)...")
    
    # Step 1: Create a test user and get auth token
    test_user = {
        "name": "Job Poster",
        "email": "jobposter@example.com",
        "password": "JobPoster123"
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
    
    # Step 2: Create a job posting
    print("\n2️⃣ Creating job posting...")
    
    job_data = {
        "title": "Senior Python Developer",
        "company": "Tech Innovations Inc",
        "description": "We are looking for an experienced Python developer to join our team and work on cutting-edge projects.",
        "requirements": ["Python", "Django", "PostgreSQL", "Docker"],
        "location": "San Francisco, CA",
        "salary_range": "$120,000 - $150,000",
        "job_type": "full-time",
        "experience_level": "senior",
        "contact_email": "hr@techinnovations.com",
        "application_url": "https://techinnovations.com/careers",
        "tags": ["python", "backend", "api"],
        "remote_allowed": True
    }
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        response = requests.post(f"{API_BASE}/api/jobs", json=job_data, headers=headers)
        
        print(f"Job creation status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            job_id = result['job']['id']
            print(f"✅ Job created successfully: {job_id}")
        else:
            print(f"❌ Job creation failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Job creation error: {e}")
        return False
    
    # Step 3: Fetch jobs to verify it appears
    print("\n3️⃣ Fetching jobs to verify...")
    
    try:
        response = requests.get(f"{API_BASE}/api/jobs")
        
        if response.status_code == 200:
            result = response.json()
            jobs = result.get('jobs', [])
            print(f"✅ Found {len(jobs)} jobs total")
            
            # Look for our job
            our_job = next((job for job in jobs if job.get('id') == job_id), None)
            if our_job:
                print(f"✅ Our job is visible: '{our_job['title']}'")
                print(f"   - Company: {our_job['company']}")
                print(f"   - Posted by: {our_job['posted_by']}")
                print(f"   - User ID: {user_id}")
                return True
            else:
                print(f"❌ Our job is not visible in the list")
                print(f"   - Looking for job ID: {job_id}")
                print(f"   - Available job IDs: {[job.get('id') for job in jobs]}")
                return False
        else:
            print(f"❌ Failed to fetch jobs: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Job fetching error: {e}")
        return False

def cleanup():
    """Clean up test data"""
    print("\n🧹 Cleaning up...")
    try:
        requests.delete(f"{API_BASE}/auth/cleanup/jobposter@example.com")
        print("✅ Test user cleaned up")
    except:
        pass

if __name__ == "__main__":
    print("🚀 Testing Job Posting Flow")
    print("=" * 50)
    
    success = test_job_posting_flow()
    cleanup()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Job posting flow is working correctly!")
        print("✅ Users can create jobs and they appear in the list")
    else:
        print("❌ Job posting flow has issues")
        print("🔧 Check server logs and database connection")
    
    print(f"\n📋 Server status:")
    print(f"- Correct server running on port 5001")
    print(f"- Frontend should use VITE_API_BASE=http://localhost:5001")
    print(f"- Frontend needs to be restarted to pick up new env var")
