#!/usr/bin/env python3
import requests

def test_cors(url, method='GET'):
    try:
        # Test preflight OPTIONS request
        print(f"Testing CORS for {url}")
        
        # First test OPTIONS request (preflight)
        options_response = requests.options(url, headers={
            'Origin': 'http://localhost:5174',
            'Access-Control-Request-Method': method,
            'Access-Control-Request-Headers': 'Content-Type'
        })
        
        print(f"OPTIONS Status: {options_response.status_code}")
        print(f"OPTIONS Headers: {dict(options_response.headers)}")
        
        # Then test actual request
        if method == 'GET':
            actual_response = requests.get(url, headers={
                'Origin': 'http://localhost:5174'
            })
        
        print(f"Actual {method} Status: {actual_response.status_code}")
        print(f"Actual {method} Headers: {dict(actual_response.headers)}")
        print()
        
    except Exception as e:
        print(f"Error testing {url}: {e}")
        print()

# Test the endpoints that were failing
test_cors('http://localhost:5000/api/problems')
test_cors('http://localhost:5000/api/problems/1')
test_cors('http://localhost:5000/api/jobs')
test_cors('http://localhost:5000/api/experiences')
