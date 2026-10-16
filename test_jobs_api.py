#!/usr/bin/env python3
"""
Test script for job posting API endpoints
"""
import requests
import json

API_BASE = "http://localhost:5000"

def test_get_jobs():
    """Test getting job postings"""
    print("🔍 Testing GET /api/jobs...")
    
    try:
        response = requests.get(f"{API_BASE}/api/jobs")
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {len(data.get('jobs', []))} jobs")
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_health_check():
    """Test health endpoint"""
    print("\n🏥 Testing health check...")
    
    try:
        response = requests.get(f"{API_BASE}/health")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
        else:
            print(f"❌ Health check failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Health check request failed: {e}")

if __name__ == "__main__":
    test_health_check()
    test_get_jobs()
