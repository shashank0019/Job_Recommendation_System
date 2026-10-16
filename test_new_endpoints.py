#!/usr/bin/env python3

import requests
import json

API_BASE = "http://localhost:5000"

def test_endpoints():
    print("🧪 Testing new API endpoints...")
    
    # Test job postings endpoint
    try:
        response = requests.get(f"{API_BASE}/api/jobs")
        print(f"✅ GET /api/jobs - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ GET /api/jobs - Error: {e}")
    
    # Test interview experiences endpoint
    try:
        response = requests.get(f"{API_BASE}/api/experiences")
        print(f"✅ GET /api/experiences - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ GET /api/experiences - Error: {e}")
    
    # Test health endpoint
    try:
        response = requests.get(f"{API_BASE}/health")
        print(f"✅ GET /health - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
    except Exception as e:
        print(f"❌ GET /health - Error: {e}")

if __name__ == "__main__":
    test_endpoints()
