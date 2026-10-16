#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

import requests
import json

print("Testing Flask signin endpoint...")

# Test data
signin_data = {
    'email': 'debugtest@example.com',
    'password': 'DebugTest123'  
}

# Test on port 5000 (main server)
print("\nTesting on main server (port 5000):")
try:
    response = requests.post('http://localhost:5000/auth/signin', json=signin_data, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Signin successful!")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Signin failed")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"Error: {e}")