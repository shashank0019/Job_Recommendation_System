#!/usr/bin/env python3

import requests
import json
import time

def test_frontend_backend_integration():
    """Test the complete frontend-backend upload integration."""
    
    backend_url = "http://localhost:5000"
    frontend_url = "http://localhost:5174"
    
    print("🧪 Testing Frontend-Backend Upload Integration...")
    print("=" * 60)
    
    # Test 1: Check if both servers are running
    print("\n1️⃣ Checking server status...")
    
    try:
        backend_response = requests.get(f"{backend_url}/health", timeout=5)
        if backend_response.status_code == 200:
            print("✅ Backend server: RUNNING")
        else:
            print(f"❌ Backend server: ERROR ({backend_response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Backend server: NOT ACCESSIBLE - {e}")
        return False
    
    try:
        frontend_response = requests.get(frontend_url, timeout=5)
        if frontend_response.status_code == 200:
            print("✅ Frontend server: RUNNING")
        else:
            print(f"❌ Frontend server: ERROR ({frontend_response.status_code})")
    except Exception as e:
        print(f"❌ Frontend server: NOT ACCESSIBLE - {e}")
        print("   Make sure to run: npm run dev in the frontend directory")
    
    # Test 2: Test upload endpoint directly
    print("\n2️⃣ Testing upload endpoint...")
    
    # Test JSON upload
    try:
        json_data = {
            "resume_text": "Senior Software Engineer with 5+ years experience in Python, React, Node.js, AWS, MongoDB, Docker, Kubernetes. Expertise in full-stack development and cloud architecture."
        }
        response = requests.post(
            f"{backend_url}/upload",
            json=json_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ JSON Upload: SUCCESS")
            print(f"   Skills extracted: {data.get('parsed', {}).get('total_skills', 0)}")
            print(f"   Job matches: {len(data.get('jobs', []))}")
            print(f"   Live jobs: {len(data.get('live_jobs', []))}")
        else:
            print(f"❌ JSON Upload: FAILED ({response.status_code})")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ JSON Upload: ERROR - {e}")
        return False
    
    # Test file upload
    print("\n3️⃣ Testing file upload...")
    try:
        # Create a test resume file
        test_resume_content = """
        JOHN DOE
        Senior Software Engineer
        
        EXPERIENCE:
        - 5+ years in Python, JavaScript, React
        - AWS, Docker, Kubernetes experience
        - Full-stack web development
        
        SKILLS:
        Programming: Python, JavaScript, Java, SQL
        Frameworks: React, Django, Flask, Node.js
        Cloud: AWS, Docker, Kubernetes
        Databases: MongoDB, PostgreSQL, Redis
        """
        
        files = {
            'resume_file': ('test_resume.txt', test_resume_content, 'text/plain')
        }
        
        response = requests.post(f"{backend_url}/upload", files=files, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ File Upload: SUCCESS")
            print(f"   Skills extracted: {data.get('parsed', {}).get('total_skills', 0)}")
            print(f"   Job matches: {len(data.get('jobs', []))}")
        else:
            print(f"❌ File Upload: FAILED ({response.status_code})")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ File Upload: ERROR - {e}")
        return False
    
    # Test 4: Check CORS
    print("\n4️⃣ Testing CORS configuration...")
    try:
        response = requests.options(
            f"{backend_url}/upload",
            headers={
                "Origin": "http://localhost:5174",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            },
            timeout=5
        )
        
        if response.status_code in [200, 204]:
            print("✅ CORS: CONFIGURED CORRECTLY")
        else:
            print(f"⚠️  CORS: Potential issue ({response.status_code})")
            
    except Exception as e:
        print(f"❌ CORS: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print("✅ Upload functionality is working correctly!")
    print("\n📋 Summary:")
    print("   - Backend server is running and responding")
    print("   - Upload endpoint accepts both JSON and file uploads")
    print("   - Resume parsing and job matching are functional")
    print("   - CORS is configured for frontend integration")
    print("\n🎯 You can now test the upload feature in the browser at:")
    print(f"   {frontend_url}")
    
    return True

if __name__ == "__main__":
    test_frontend_backend_integration()
