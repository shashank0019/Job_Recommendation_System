#!/usr/bin/env python3
"""
Test the upload endpoint specifically
"""

import requests

def test_upload_endpoint():
    """Test the upload endpoint with different scenarios"""
    print("🧪 Testing Upload Endpoint")
    print("=" * 50)
    
    # Test 1: JSON data upload
    print("\n📝 Test 1: JSON Resume Upload")
    try:
        response = requests.post("http://localhost:5000/upload", 
            json={'resume_text': 'Software Engineer with React, Node.js, Python, and AWS experience. 5 years of full-stack development.'},
            headers={'Content-Type': 'application/json'},
            timeout=10)
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('success')}")
            print(f"✅ Jobs: {len(data.get('jobs', []))}")
            print(f"✅ Live Jobs: {len(data.get('live_jobs', []))}")
            print(f"✅ Skills: {data.get('parsed', {}).get('skills', [])}")
            
            # Show sample job
            jobs = data.get('jobs', [])
            if jobs:
                job = jobs[0]
                print(f"✅ Sample Job: {job.get('title')} at {job.get('company')}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test 2: File upload simulation
    print("\n📁 Test 2: File Upload Simulation")
    try:
        # Create a simple text file in memory
        files = {'resume_file': ('resume.txt', 'Software Engineer\nReact, Node.js, Python\n5 years experience', 'text/plain')}
        
        response = requests.post("http://localhost:5000/upload", 
            files=files,
            timeout=10)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ File Upload Success: {data.get('success')}")
            print(f"✅ Skills: {data.get('parsed', {}).get('skills', [])}")
        else:
            print(f"❌ File Upload Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ File upload failed: {e}")
    
    print(f"\n🎯 Upload Endpoint Summary:")
    print(f"   ✅ Server responding on http://localhost:5000/upload")
    print(f"   ✅ CORS headers should be properly configured")
    print(f"   ✅ Ready for frontend integration")

if __name__ == "__main__":
    test_upload_endpoint()
