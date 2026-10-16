#!/usr/bin/env python3
"""
Test script to debug live job fetching functionality
"""

import requests
import json
import time

def test_arbeitnow_api():
    """Test the Arbeitnow API directly."""
    print("🔍 Testing Arbeitnow API...")
    
    try:
        # Test with a simple search
        response = requests.get(
            "https://arbeitnow.com/api/job-board-api",
            params={"search": "python", "page": 1},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response Type: {type(data)}")
                print(f"Response Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                if isinstance(data, dict) and 'data' in data:
                    jobs = data['data']
                    print(f"Jobs Found: {len(jobs)}")
                    if jobs:
                        print(f"First Job: {jobs[0]}")
                else:
                    print(f"Raw Response: {data[:500]}...")
                    
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}")
                print(f"Raw Response: {response.text[:500]}...")
        else:
            print(f"Error Response: {response.text[:500]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")

def test_custom_api():
    """Test custom API if configured."""
    print("\n🔍 Testing Custom API...")
    
    # Check environment variables
    import os
    custom_url = os.getenv("CUSTOM_JOBS_API_URL", "")
    custom_token = os.getenv("CUSTOM_JOBS_API_TOKEN", "")
    
    if not custom_url:
        print("❌ No custom API URL configured")
        return
    
    if not custom_token:
        print("❌ No custom API token configured")
        return
    
    print(f"✅ Custom API URL: {custom_url}")
    print(f"✅ Custom API Token: {custom_token[:10]}...")
    
    try:
        headers = {
            "Authorization": f"Bearer {custom_token}",
            "Accept": "application/json",
        }
        
        # Test with a simple request
        response = requests.get(
            custom_url,
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response Type: {type(data)}")
                print(f"Response Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}")
                print(f"Raw Response: {response.text[:500]}...")
        else:
            print(f"Error Response: {response.text[:500]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")

def test_skill_extraction():
    """Test skill extraction from text."""
    print("\n🔍 Testing Skill Extraction...")
    
    test_text = "We are looking for a Python developer with React experience and AWS knowledge"
    
    # Simple skill extraction
    skills = ["python", "react", "aws", "javascript", "node.js"]
    found_skills = []
    
    for skill in skills:
        if skill in test_text.lower():
            found_skills.append(skill)
    
    print(f"Test Text: {test_text}")
    print(f"Skills Found: {found_skills}")

def test_network_connectivity():
    """Test basic network connectivity."""
    print("\n🔍 Testing Network Connectivity...")
    
    test_urls = [
        "https://httpbin.org/get",
        "https://api.github.com",
        "https://arbeitnow.com"
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ {url}: {response.status_code}")
        except Exception as e:
            print(f"❌ {url}: {e}")

if __name__ == "__main__":
    print("🚀 Live Job Fetching Debug Test")
    print("=" * 50)
    
    test_network_connectivity()
    test_arbeitnow_api()
    test_custom_api()
    test_skill_extraction()
    
    print("\n" + "=" * 50)
    print("✅ Debug test completed!")
