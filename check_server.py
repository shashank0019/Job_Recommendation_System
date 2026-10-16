#!/usr/bin/env python3
"""
Check which server is running on port 5000
"""
import requests
import json

API_BASE = "http://localhost:5000"

def check_server():
    """Check server endpoints to identify which server is running"""
    print("🔍 Checking server endpoints...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health endpoint: {data}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    # Test jobs endpoint
    try:
        response = requests.get(f"{API_BASE}/api/jobs?limit=1")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Jobs endpoint structure:")
            print(f"   - Success: {data.get('success')}")
            print(f"   - Jobs count: {len(data.get('jobs', []))}")
            print(f"   - Has pagination: {'pagination' in data}")
            print(f"   - Has total: {'total' in data}")
            
            if data.get('jobs'):
                job = data['jobs'][0]
                print(f"   - Job fields: {list(job.keys())}")
                print(f"   - Job ID type: {type(job.get('id'))}")
        else:
            print(f"❌ Jobs endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Jobs endpoint error: {e}")
    
    # Test if this is the MongoDB-based server
    try:
        # Try to create a test job (this should fail without auth)
        response = requests.post(f"{API_BASE}/api/jobs", json={
            "title": "Test Job",
            "company": "Test Company",
            "description": "Test Description",
            "location": "Test Location",
            "salary_range": "$50,000",
            "job_type": "full-time"
        })
        print(f"✅ POST /api/jobs response: {response.status_code}")
        if response.status_code == 401:
            print("   - This appears to be the MongoDB-based server (requires auth)")
        elif response.status_code == 200:
            print("   - This appears to be a different server (no auth required)")
    except Exception as e:
        print(f"❌ POST jobs endpoint error: {e}")

if __name__ == "__main__":
    check_server()
