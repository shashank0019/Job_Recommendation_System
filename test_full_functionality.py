#!/usr/bin/env python3
"""Comprehensive test of job posting and interview experience functionality"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_authenticated_functionality():
    """Test the full functionality with authentication"""
    print("Testing Job Posting and Interview Experience Save Functionality")
    print("=" * 70)
    
    # Step 1: Test authentication with a valid user
    print("STEP 1: Authentication")
    print("-" * 30)
    
    # Try different users until we find one that works
    test_users = [
        {"email": "shashank.22ise@cambridge.edu.in", "password": "password123"},
        {"email": "test@example.com", "password": "password123"},
        {"email": "debug@test.com", "password": "password123"},
        {"email": "shashikingmaker495@gmail.com", "password": "password123"}
    ]
    
    token = None
    user_info = None
    
    for user in test_users:
        try:
            auth_response = requests.post(f"{BASE_URL}/auth/signin", json=user)
            print(f"Testing login for {user['email']}: Status {auth_response.status_code}")
            
            if auth_response.status_code == 200:
                auth_result = auth_response.json()
                if auth_result.get('success') and auth_result.get('token'):
                    token = auth_result['token']
                    user_info = auth_result.get('user', {})
                    print(f"SUCCESS: Authenticated as {user_info.get('name', 'Unknown')}")
                    break
            else:
                try:
                    error = auth_response.json()
                    print(f"   Error: {error.get('error', 'Unknown error')}")
                except:
                    print(f"   Error: {auth_response.text}")
        except Exception as e:
            print(f"   Connection error: {e}")
    
    if not token:
        print("ERROR: Could not authenticate with any test user")
        print("Creating a new test user...")
        
        # Create a new user
        new_user = {
            "name": "Test User for Save",
            "email": f"test_save_{int(datetime.now().timestamp())}@example.com",
            "password": "password123"
        }
        
        try:
            signup_response = requests.post(f"{BASE_URL}/auth/signup", json=new_user)
            print(f"Signup response: {signup_response.status_code}")
            
            if signup_response.status_code == 201:
                # Try to login with new user
                auth_response = requests.post(f"{BASE_URL}/auth/signin", json={
                    "email": new_user["email"],
                    "password": new_user["password"]
                })
                
                if auth_response.status_code == 200:
                    auth_result = auth_response.json()
                    token = auth_result.get('token')
                    user_info = auth_result.get('user', {})
                    print(f"SUCCESS: Created and authenticated new user")
        except Exception as e:
            print(f"Error creating user: {e}")
    
    if not token:
        print("FATAL: Cannot proceed without authentication")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Step 2: Test Job Posting Creation
    print("\nSTEP 2: Job Posting Creation")
    print("-" * 30)
    
    job_data = {
        "title": "Senior Python Developer",
        "company": "Tech Solutions Inc",
        "description": "We are looking for an experienced Python developer to join our team. You will work on exciting projects using Django, Flask, and modern web technologies.",
        "requirements": ["Python", "Django", "Flask", "PostgreSQL", "Git"],
        "location": "San Francisco, CA",
        "salary_range": "$90,000 - $120,000",
        "job_type": "full-time",
        "experience_level": "senior",
        "remote_allowed": True,
        "contact_email": "hr@techsolutions.com",
        "tags": ["Python", "Django", "Flask", "Backend"]
    }
    
    try:
        job_response = requests.post(f"{BASE_URL}/api/jobs", json=job_data, headers=headers)
        print(f"Job creation response: {job_response.status_code}")
        
        if job_response.status_code == 201:
            job_result = job_response.json()
            print("SUCCESS: Job posting created successfully!")
            print(f"   Job ID: {job_result.get('job', {}).get('id', 'N/A')}")
            print(f"   Title: {job_result.get('job', {}).get('title', 'N/A')}")
        else:
            job_result = job_response.json()
            print(f"ERROR: {job_result.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"ERROR: Exception during job creation: {e}")
    
    # Step 3: Test Interview Experience Creation
    print("\nSTEP 3: Interview Experience Creation")
    print("-" * 30)
    
    experience_data = {
        "company": "Google",
        "position": "Software Engineer",
        "experience_text": "Had a great interview experience at Google. The process consisted of 4 rounds: phone screening, technical coding, system design, and behavioral. The interviewers were very friendly and the questions were challenging but fair.",
        "interview_type": "technical",
        "difficulty_rating": 4,
        "outcome": "selected",
        "questions_asked": [
            "Implement a LRU cache",
            "Design a URL shortener",
            "Tell me about a challenging project"
        ],
        "tips": [
            "Practice system design thoroughly",
            "Be ready to explain your thought process",
            "Ask clarifying questions"
        ],
        "tags": ["Python", "System Design", "Algorithms"],
        "location": "Mountain View, CA",
        "interview_rounds": 4,
        "preparation_time": "2 months"
    }
    
    try:
        exp_response = requests.post(f"{BASE_URL}/api/experiences", json=experience_data, headers=headers)
        print(f"Experience creation response: {exp_response.status_code}")
        
        if exp_response.status_code == 201:
            exp_result = exp_response.json()
            print("SUCCESS: Interview experience created successfully!")
            print(f"   Experience ID: {exp_result.get('experience', {}).get('id', 'N/A')}")
            print(f"   Company: {exp_result.get('experience', {}).get('company', 'N/A')}")
            print(f"   Position: {exp_result.get('experience', {}).get('position', 'N/A')}")
        else:
            exp_result = exp_response.json()
            print(f"ERROR: {exp_result.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"ERROR: Exception during experience creation: {e}")
    
    # Step 4: Verify data was saved by retrieving it
    print("\nSTEP 4: Data Verification")
    print("-" * 30)
    
    # Check user's job postings
    try:
        my_jobs_response = requests.get(f"{BASE_URL}/api/my-jobs", headers=headers)
        print(f"My jobs response: {my_jobs_response.status_code}")
        
        if my_jobs_response.status_code == 200:
            my_jobs_result = my_jobs_response.json()
            jobs_count = len(my_jobs_result.get('jobs', []))
            print(f"SUCCESS: Found {jobs_count} job posting(s) for user")
        else:
            print(f"ERROR: Could not retrieve user's jobs")
            
    except Exception as e:
        print(f"ERROR: Exception retrieving jobs: {e}")
    
    # Check user's interview experiences
    try:
        my_exp_response = requests.get(f"{BASE_URL}/api/my-experiences", headers=headers)
        print(f"My experiences response: {my_exp_response.status_code}")
        
        if my_exp_response.status_code == 200:
            my_exp_result = my_exp_response.json()
            exp_count = len(my_exp_result.get('experiences', []))
            print(f"SUCCESS: Found {exp_count} interview experience(s) for user")
        else:
            print(f"ERROR: Could not retrieve user's experiences")
            
    except Exception as e:
        print(f"ERROR: Exception retrieving experiences: {e}")
    
    print("\nTEST SUMMARY")
    print("=" * 30)
    print("If you see SUCCESS messages above, the save functionality is working correctly.")
    print("If you see ERROR messages, there are issues that need to be fixed.")

if __name__ == "__main__":
    test_authenticated_functionality()
