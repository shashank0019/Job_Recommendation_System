#!/usr/bin/env python3
import requests

try:
    # Test the problems list endpoint
    response = requests.get('http://localhost:5000/api/problems')
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Total problems: {data.get('total')}")
        print(f"Filtered count: {data.get('filtered_count')}")
        print(f"Items count: {len(data.get('items', []))}")
        if data.get('items'):
            print(f"First problem: {data['items'][0].get('title')}")
    else:
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"Error: {e}")
