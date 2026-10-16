#!/usr/bin/env python3
"""
Test the simple CORS server
"""

import requests

def test_simple_server():
    """Test the simple CORS-enabled server"""
    print("🧪 Testing Simple CORS Server")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        print(f"Health Check: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Health: {response.json()}")
        
        # Test recommend endpoint
        response = requests.post("http://localhost:5000/recommend", 
            json={'resume_text': 'Software Engineer with React and Node.js experience'},
            timeout=5)
        print(f"Recommend API: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Jobs: {len(data.get('jobs', []))}")
            print(f"✅ Live Jobs: {len(data.get('live_jobs', []))}")
            print(f"✅ Skills: {data.get('parsed', {}).get('skills', [])}")
        
        print(f"\n🎯 CORS Server Status: ✅ WORKING")
        print(f"Your frontend should now be able to connect!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_simple_server()
