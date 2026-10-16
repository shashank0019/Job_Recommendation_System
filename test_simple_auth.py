#!/usr/bin/env python3
"""Simple authentication test to debug login issues"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_simple_auth():
    """Test authentication with detailed output"""
    print("Simple Authentication Test")
    print("=" * 40)
    
    # Test with a simple new user first
    print("Creating a new test user...")
    
    new_user = {
        "name": "Simple Test User",
        "email": "simpletest@example.com",
        "password": "SimplePass123!"
    }
    
    try:
        # Create user
        signup_response = requests.post(f"{BASE_URL}/auth/signup", json=new_user)
        print(f"Signup Status: {signup_response.status_code}")
        
        if signup_response.status_code == 201:
            print("SUCCESS: User created successfully")
            signup_result = signup_response.json()
            print(f"User ID: {signup_result.get('user', {}).get('id', 'N/A')}")
            
            # Now try to login
            print("\nTesting login with new user...")
            login_data = {
                "email": new_user["email"],
                "password": new_user["password"]
            }
            
            signin_response = requests.post(f"{BASE_URL}/auth/signin", json=login_data)
            print(f"Signin Status: {signin_response.status_code}")
            
            if signin_response.status_code == 200:
                print("SUCCESS: Login successful")
                signin_result = signin_response.json()
                token = signin_result.get('token')
                print(f"Token received: {token[:20] if token else 'None'}...")
                
                # Test authenticated endpoint
                print("\nTesting authenticated endpoint...")
                headers = {'Authorization': f'Bearer {token}'}
                
                # Test creating a simple job posting
                job_data = {
                    "title": "Test Job",
                    "company": "Test Company",
                    "description": "A simple test job posting",
                    "location": "Remote",
                    "salary_range": "$50k-70k",
                    "job_type": "full-time"
                }
                
                job_response = requests.post(f"{BASE_URL}/api/jobs", json=job_data, headers=headers)
                print(f"Job Creation Status: {job_response.status_code}")
                
                if job_response.status_code == 201:
                    print("SUCCESS: Job posting created!")
                    job_result = job_response.json()
                    print(f"Job ID: {job_result.get('job', {}).get('id', 'N/A')}")
                else:
                    job_result = job_response.json()
                    print(f"ERROR: {job_result.get('message', 'Unknown error')}")
                
                # Test creating a simple interview experience
                print("\nTesting interview experience creation...")
                exp_data = {
                    "company": "Test Company",
                    "position": "Software Engineer",
                    "experience_text": "Simple test interview experience",
                    "interview_type": "technical",
                    "difficulty_rating": 3
                }
                
                exp_response = requests.post(f"{BASE_URL}/api/experiences", json=exp_data, headers=headers)
                print(f"Experience Creation Status: {exp_response.status_code}")
                
                if exp_response.status_code == 201:
                    print("SUCCESS: Interview experience created!")
                    exp_result = exp_response.json()
                    print(f"Experience ID: {exp_result.get('experience', {}).get('id', 'N/A')}")
                else:
                    exp_result = exp_response.json()
                    print(f"ERROR: {exp_result.get('message', 'Unknown error')}")
                
            else:
                signin_result = signin_response.json()
                print(f"ERROR: Login failed - {signin_result.get('error', 'Unknown error')}")
        
        elif signup_response.status_code == 409:
            print("User already exists, trying to login...")
            login_data = {
                "email": new_user["email"],
                "password": new_user["password"]
            }
            
            signin_response = requests.post(f"{BASE_URL}/auth/signin", json=login_data)
            print(f"Signin Status: {signin_response.status_code}")
            
            if signin_response.status_code == 200:
                print("SUCCESS: Login with existing user successful")
            else:
                signin_result = signin_response.json()
                print(f"ERROR: {signin_result.get('error', 'Unknown error')}")
        
        else:
            signup_result = signup_response.json()
            print(f"ERROR: Signup failed - {signup_result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"ERROR: Exception occurred - {e}")

if __name__ == "__main__":
    test_simple_auth()
