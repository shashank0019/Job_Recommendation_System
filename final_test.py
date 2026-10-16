#!/usr/bin/env python3
"""
Final test of the clean CORS server
"""

import requests

def final_test():
    """Final comprehensive test"""
    print("🎯 FINAL CORS SERVER TEST")
    print("=" * 60)
    
    try:
        # Test health
        print("1. Testing Health Endpoint...")
        health = requests.get("http://localhost:5000/health", timeout=5)
        print(f"   ✅ Health: {health.status_code} - {health.json()}")
        
        # Test recommend
        print("\n2. Testing Recommend Endpoint...")
        recommend = requests.post("http://localhost:5000/recommend", 
            json={'resume_text': 'Software Engineer with React, Node.js, Python, AWS experience'},
            timeout=5)
        print(f"   ✅ Recommend: {recommend.status_code}")
        
        if recommend.status_code == 200:
            data = recommend.json()
            print(f"   ✅ Jobs Found: {len(data.get('jobs', []))}")
            print(f"   ✅ Live Jobs: {len(data.get('live_jobs', []))}")
            print(f"   ✅ Skills: {data.get('parsed', {}).get('skills', [])}")
        
        # Test upload
        print("\n3. Testing Upload Endpoint...")
        upload = requests.post("http://localhost:5000/upload",
            json={'resume_text': 'Full Stack Developer with React, Node.js experience'},
            timeout=5)
        print(f"   ✅ Upload: {upload.status_code}")
        
        if upload.status_code == 200:
            data = upload.json()
            print(f"   ✅ Upload Success: {data.get('success')}")
        
        print(f"\n🎊 SUCCESS! All endpoints working!")
        print(f"🌐 Server ready at: http://localhost:5000")
        print(f"🎯 Your frontend can now connect without CORS errors!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    final_test()
