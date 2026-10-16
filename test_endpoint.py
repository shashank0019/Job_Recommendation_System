#!/usr/bin/env python3
"""
Test the actual endpoint to see what's being returned
"""

import requests
import json

def test_upload_endpoint():
    """Test the /upload endpoint"""
    print("🔍 Testing /upload endpoint...")
    
    try:
        url = "http://localhost:5000/upload"
        data = {
            "resume_text": "Software Engineer with 5 years experience in React, Python, JavaScript, and AWS. Worked on web applications and cloud infrastructure."
        }
        
        response = requests.post(
            url,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success', False)}")
            
            # Check live jobs specifically
            live_jobs = result.get('live_jobs', [])
            print(f"Live Jobs Count: {len(live_jobs)}")
            
            if live_jobs:
                print("\n📋 Live Jobs Found:")
                for i, job in enumerate(live_jobs[:3], 1):
                    print(f"{i}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
                    print(f"   Location: {job.get('location', 'N/A')}")
                    print(f"   Source: {job.get('source', 'N/A')}")
                    if 'job_url' in job:
                        print(f"   URL: {job['job_url']}")
                    print()
            else:
                print("❌ No live jobs returned")
            
            # Check other data
            jobs = result.get('jobs', [])
            print(f"Regular Jobs Count: {len(jobs)}")
            
            parsed = result.get('parsed', {})
            print(f"Parsed Skills: {parsed.get('skills', [])}")
            
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        import traceback
        traceback.print_exc()

def test_recommend_endpoint():
    """Test the /recommend endpoint"""
    print("\n🔍 Testing /recommend endpoint...")
    
    try:
        url = "http://localhost:5000/recommend"
        data = {
            "resume_text": "Senior Python Developer with React and AWS experience. 7 years in web development."
        }
        
        response = requests.post(
            url,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success', False)}")
            
            # Check live jobs
            live_jobs = result.get('live_jobs', [])
            print(f"Live Jobs Count: {len(live_jobs)}")
            
            if live_jobs:
                print("\n📋 Live Jobs Found:")
                for i, job in enumerate(live_jobs[:2], 1):
                    print(f"{i}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
                    print(f"   Source: {job.get('source', 'N/A')}")
            else:
                print("❌ No live jobs returned")
                
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing recommend endpoint: {e}")

if __name__ == "__main__":
    print("🚀 Testing Live Jobs Endpoints")
    print("=" * 50)
    
    test_upload_endpoint()
    test_recommend_endpoint()
    
    print("\n" + "=" * 50)
    print("✅ Endpoint testing completed!")
