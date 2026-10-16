#!/usr/bin/env python3
"""
Debug script to test the upload endpoint and identify the exact error.
"""

import requests
import json
import sys
import os
from pathlib import Path

def test_upload_endpoint():
    """Test the upload endpoint with different scenarios."""
    base_url = "http://localhost:5000"
    
    print("🔍 Testing upload endpoint...")
    
    # Test 1: Simple JSON upload
    print("\n1. Testing JSON upload...")
    try:
        response = requests.post(
            f"{base_url}/upload",
            json={"resume_text": "Software Engineer with Python and React experience"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text}")
        else:
            print("✅ JSON upload successful")
    except Exception as e:
        print(f"❌ JSON upload failed: {e}")
    
    # Test 2: File upload (if test PDF exists)
    print("\n2. Testing PDF file upload...")
    try:
        # Create a simple test text file if it doesn't exist
        test_file_path = Path("test_resume.txt")
        if not test_file_path.exists():
            with open(test_file_path, "w") as f:
                f.write("John Doe\nSoftware Engineer\nPython, JavaScript, React, Node.js\n5 years experience")
        
        with open(test_file_path, "rb") as f:
            files = {"resume_file": ("test_resume.txt", f, "text/plain")}
            response = requests.post(
                f"{base_url}/upload",
                files=files,
                timeout=30
            )
        
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text}")
        else:
            print("✅ File upload successful")
            
        # Clean up
        if test_file_path.exists():
            test_file_path.unlink()
            
    except Exception as e:
        print(f"❌ File upload failed: {e}")
    
    # Test 3: Check if server is responding
    print("\n3. Testing server health...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"Server health status: {response.status_code}")
    except Exception as e:
        print(f"❌ Server not responding: {e}")

if __name__ == "__main__":
    test_upload_endpoint()