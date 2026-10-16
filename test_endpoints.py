#!/usr/bin/env python3
"""Test script to check job posting and interview experience endpoints"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_endpoint(method, endpoint, data=None, headers=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        print(f"Testing {method} {endpoint}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code < 400:
            print(f"   SUCCESS")
        else:
            print(f"   ERROR")
            
        # Try to parse JSON response
        try:
            result = response.json()
            if 'message' in result:
                print(f"   Message: {result['message']}")
            if 'error' in result:
                print(f"   Error: {result['error']}")
        except:
            print(f"   Raw Response: {response.text[:200]}...")
        
        print()
        return response
        
    except Exception as e:
        print(f"Testing {method} {endpoint}")
        print(f"   CONNECTION ERROR: {e}")
        print()
        return None

def main():
    print("Testing Job Posting and Interview Experience Endpoints")
    print("=" * 60)
    
    # Test basic health check
    test_endpoint('GET', '/health')
    
    # Test job posting endpoints
    print("JOB POSTING TESTS")
    print("-" * 30)
    
    # Test GET jobs (should work without auth)
    test_endpoint('GET', '/api/jobs')
    
    # Test POST job (should fail without auth)
    job_data = {
        "title": "Test Job",
        "company": "Test Company",
        "description": "Test Description",
        "location": "Remote",
        "salary_range": "$50k-70k",
        "job_type": "full-time"
    }
    test_endpoint('POST', '/api/jobs', data=job_data)
    
    # Test interview experience endpoints
    print("INTERVIEW EXPERIENCE TESTS")
    print("-" * 30)
    
    # Test GET experiences (should work without auth)
    test_endpoint('GET', '/api/experiences')
    
    # Test POST experience (should fail without auth)
    experience_data = {
        "company": "Test Company",
        "position": "Software Engineer",
        "experience_text": "Great interview experience",
        "interview_type": "technical",
        "difficulty_rating": 3
    }
    test_endpoint('POST', '/api/experiences', data=experience_data)
    
    # Test authentication endpoint
    print("AUTHENTICATION TESTS")
    print("-" * 30)
    
    # Test signin (should work if user exists)
    auth_data = {
        "email": "direct@test.com",
        "password": "test123"
    }
    auth_response = test_endpoint('POST', '/auth/signin', data=auth_data)
    
    # If authentication successful, test authenticated endpoints
    if auth_response and auth_response.status_code == 200:
        try:
            auth_result = auth_response.json()
            token = auth_result.get('token')
            
            if token:
                print("AUTHENTICATED TESTS")
                print("-" * 30)
                
                headers = {'Authorization': f'Bearer {token}'}
                
                # Test authenticated job posting
                test_endpoint('POST', '/api/jobs', data=job_data, headers=headers)
                
                # Test authenticated interview experience
                test_endpoint('POST', '/api/experiences', data=experience_data, headers=headers)
                
                # Test user's own posts
                test_endpoint('GET', '/api/my-jobs', headers=headers)
                test_endpoint('GET', '/api/my-experiences', headers=headers)
        
        except Exception as e:
            print(f"Error processing auth response: {e}")

if __name__ == "__main__":
    main()
