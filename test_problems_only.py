#!/usr/bin/env python3
"""
Test the problems endpoint specifically
"""
import requests
import json

def test_problems():
    """Test problems endpoint"""
    url = "http://localhost:5000/api/problems"
    
    print(f"Testing problems endpoint: {url}")
    
    try:
        # Test with limit parameter like the React app uses
        response = requests.get(f"{url}?limit=1000", timeout=10)
        
        print(f"\n--- Response ---")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            print(f"\n✅ PROBLEMS ENDPOINT WORKING!")
            print(f"📊 Found {len(data.get('items', []))} problems")
            print(f"🎯 Total available: {data.get('total', 0)}")
            return True
        else:
            print(f"Response: {response.text}")
            print(f"\n❌ PROBLEMS ENDPOINT FAILED!")
            return False
            
    except Exception as e:
        print(f"\n❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    test_problems()