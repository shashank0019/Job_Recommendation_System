#!/usr/bin/env python3
"""
Test script for the correct job posting server on port 5001
"""
import requests
import json

API_BASE = "http://localhost:5001"

def test_correct_server():
    """Test the correct server endpoints"""
    print("🔍 Testing correct server on port 5001...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print(f"✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    # Test jobs endpoint
    try:
        response = requests.get(f"{API_BASE}/api/jobs")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Jobs endpoint working")
            print(f"   - Jobs found: {len(data.get('jobs', []))}")
            print(f"   - Response structure: {list(data.keys())}")
        else:
            print(f"❌ Jobs endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Jobs endpoint error: {e}")
    
    # Test POST endpoint (should require auth)
    try:
        test_job = {
            "title": "Test Job",
            "company": "Test Company",
            "description": "Test Description",
            "location": "Test Location",
            "salary_range": "$50,000",
            "job_type": "full-time"
        }
        
        response = requests.post(f"{API_BASE}/api/jobs", json=test_job)
        print(f"✅ POST /api/jobs response: {response.status_code}")
        
        if response.status_code == 401:
            print("   - ✅ Correctly requires authentication")
        elif response.status_code == 200:
            print("   - ⚠️ No authentication required (wrong server)")
        else:
            print(f"   - Response: {response.text}")
    except Exception as e:
        print(f"❌ POST jobs endpoint error: {e}")

if __name__ == "__main__":
    test_correct_server()
