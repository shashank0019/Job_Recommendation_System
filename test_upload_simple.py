#!/usr/bin/env python3
"""Simple test for upload endpoint"""

import requests
import json

base_url = "http://localhost:5000"

print("Testing /upload endpoint...\n")

# Test 1: JSON upload
print("1. JSON Upload Test:")
try:
    response = requests.post(
        f"{base_url}/upload",
        json={"resume_text": "Software Engineer with Python, React, Node.js experience"},
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"   Error: {e}")

print("\n2. File Upload Test:")
try:
    files = {'resume_file': ('test.txt', 'Software Engineer with Python, React', 'text/plain')}
    response = requests.post(
        f"{base_url}/upload",
        files=files
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"   Error: {e}")
