#!/usr/bin/env python3

import requests
import json

def test_upload_endpoint():
    """Test the /upload endpoint to see what's causing the 500 error."""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Testing /upload endpoint...")
    
    # Test 1: JSON data upload
    print("\n1️⃣ Testing JSON upload...")
    try:
        response = requests.post(
            f"{base_url}/upload",
            json={"resume_text": "Python developer with React and Django experience"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ JSON upload: SUCCESS")
            data = response.json()
            print(f"   Parsed skills: {data.get('parsed', {}).get('total_skills', 0)}")
        else:
            print(f"❌ JSON upload: FAILED")
            print(f"   Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server at localhost:5000")
        print("   Make sure the backend server is running with: python app.py")
        return False
    except Exception as e:
        print(f"❌ JSON upload error: {e}")
    
    # Test 2: Health check
    print("\n2️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Health check: SUCCESS")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check: FAILED")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 3: File upload (simulate)
    print("\n3️⃣ Testing file upload...")
    try:
        # Create a simple text file content
        files = {'resume_file': ('test_resume.txt', 'Python developer with React experience', 'text/plain')}
        response = requests.post(f"{base_url}/upload", files=files, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ File upload: SUCCESS")
        else:
            print(f"❌ File upload: FAILED")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ File upload error: {e}")
    
    return True

if __name__ == "__main__":
    test_upload_endpoint()
