#!/usr/bin/env python3
import requests

try:
    # Test the specific endpoint that's failing in the frontend
    response = requests.get('http://localhost:5000/api/problems/1')
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
