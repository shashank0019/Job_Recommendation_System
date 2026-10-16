#!/usr/bin/env python3
"""Test the recommend endpoint"""

import requests
import json

base_url = "http://localhost:5000"

print("Testing /recommend endpoint...\n")

try:
    response = requests.post(
        f"{base_url}/recommend",
        json={"resume_text": "Software Engineer with Python, React, Node.js, AWS experience. 5 years of full-stack development."},
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
