#!/usr/bin/env python3

import requests
import json
import time

print("Testing authentication endpoints...")

# Wait a moment for server to be ready
time.sleep(2)

# Test signup
print("\n1. Testing signup...")
signup_data = {
    "name": "Test User",
    "email": "test@example.com", 
    "password": "TestPass123"
}

try:
    response = requests.post('http://localhost:5000/auth/signup', 
                           json=signup_data, 
                           timeout=10)
    print(f"Signup Status: {response.status_code}")
    print(f"Signup Response: {response.text}")
except Exception as e:
    print(f"Signup Error: {e}")

# Test signin
print("\n2. Testing signin...")
signin_data = {
    "email": "test@example.com",
    "password": "TestPass123"
}

try:
    response = requests.post('http://localhost:5000/auth/signin',
                           json=signin_data,
                           timeout=10)
    print(f"Signin Status: {response.status_code}")
    print(f"Signin Response: {response.text}")
except Exception as e:
    print(f"Signin Error: {e}")

# Test with existing user (debugtest@example.com)
print("\n3. Testing signin with existing user...")
existing_signin_data = {
    "email": "debugtest@example.com",
    "password": "DebugTest123"
}

try:
    response = requests.post('http://localhost:5000/auth/signin',
                           json=existing_signin_data,
                           timeout=10)
    print(f"Existing User Signin Status: {response.status_code}")
    print(f"Existing User Signin Response: {response.text}")
except Exception as e:
    print(f"Existing User Signin Error: {e}")