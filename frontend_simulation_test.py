#!/usr/bin/env python3
"""
Simulate exactly what your frontend is doing to debug the issue
"""

import requests
import json

def simulate_frontend():
    """Simulate the exact requests your frontend makes"""
    print("🎯 SIMULATING FRONTEND REQUESTS")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    # Test 1: Check if server is responding
    print("1. Testing server health...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   ✅ Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Server is running and responding")
        else:
            print(f"   ❌ Server health check failed")
            return
    except Exception as e:
        print(f"   ❌ Cannot connect to server: {e}")
        return
    
    # Test 2: Test the exact resume upload your frontend does
    print("\n2. Testing resume upload (simulating frontend)...")
    
    # This simulates what happens when you paste text in the frontend
    sample_resume_text = """
Software Engineer
React, JavaScript, Node.js, Python, AWS
5 years experience in web development
Built scalable applications using modern technologies
    """.strip()
    
    try:
        # Test the /recommend endpoint (for text input)
        response = requests.post(f"{base_url}/recommend",
            json={'resume_text': sample_resume_text},
            headers={
                'Content-Type': 'application/json',
                'Origin': 'http://localhost:5174'  # Your frontend origin
            },
            timeout=10)
        
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                parsed = data.get('parsed', {})
                jobs = data.get('jobs', [])
                live_jobs = data.get('live_jobs', [])
                
                print(f"   ✅ SUCCESS! API is working")
                print(f"   📊 Skills extracted: {parsed.get('skills', [])}")
                print(f"   📅 Experience: {parsed.get('years_experience')} years")
                print(f"   🎯 Job matches: {len(jobs)}")
                print(f"   🌐 Live jobs: {len(live_jobs)}")
                
                if jobs:
                    print(f"   📋 Top job matches:")
                    for i, job in enumerate(jobs[:3], 1):
                        title = job.get('title', 'N/A')
                        company = job.get('company', 'N/A')
                        score = job.get('similarity_score', 0)
                        print(f"      {i}. {title} at {company} - {score:.1%} match")
                
                # Check if this is really dynamic
                if len(jobs) > 0 and jobs[0].get('similarity_score', 0) != 0.95:
                    print(f"   🎉 DYNAMIC MATCHING CONFIRMED! Scores are not static")
                else:
                    print(f"   ⚠️ Might still be showing static data")
                    
            else:
                print(f"   ❌ API returned error: {data.get('error')}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test 3: Test file upload
    print("\n3. Testing file upload (simulating frontend file upload)...")
    try:
        # Simulate file upload
        files = {'resume_file': ('test_resume.txt', sample_resume_text, 'text/plain')}
        
        response = requests.post(f"{base_url}/upload",
            files=files,
            headers={'Origin': 'http://localhost:5174'},
            timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ File upload working!")
                parsed = data.get('parsed', {})
                print(f"   📁 Filename: {parsed.get('filename')}")
                print(f"   📊 Skills: {parsed.get('skills', [])}")
            else:
                print(f"   ❌ Upload error: {data.get('error')}")
        else:
            print(f"   ❌ Upload failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Upload test failed: {e}")
    
    # Test 4: Test missing endpoints
    print("\n4. Testing interview/problems endpoints...")
    try:
        # Test interview questions
        interview_response = requests.post(f"{base_url}/api/interview/questions",
            json={'skills': ['react', 'javascript'], 'num_questions': 2},
            timeout=5)
        print(f"   Interview API: {interview_response.status_code}")
        
        # Test problems
        problems_response = requests.get(f"{base_url}/api/problems", timeout=5)
        print(f"   Problems API: {problems_response.status_code}")
        
        if interview_response.status_code == 200 and problems_response.status_code == 200:
            print(f"   ✅ All APIs working - no more 404 errors!")
        
    except Exception as e:
        print(f"   ❌ API test failed: {e}")
    
    print(f"\n🎯 DIAGNOSIS:")
    print(f"If you see '✅ SUCCESS! API is working' above, then:")
    print(f"  1. The server is working correctly")
    print(f"  2. Dynamic matching is functional") 
    print(f"  3. The issue might be browser cache or frontend configuration")
    print(f"")
    print(f"💡 SOLUTIONS TO TRY:")
    print(f"  1. Hard refresh your browser (Ctrl+F5 or Cmd+Shift+R)")
    print(f"  2. Clear browser cache and cookies")
    print(f"  3. Try in incognito/private browsing mode")
    print(f"  4. Check browser console for any JavaScript errors")

if __name__ == "__main__":
    simulate_frontend()
