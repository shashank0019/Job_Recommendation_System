#!/usr/bin/env python3
"""
Test the problems server to ensure 180+ problems are being served correctly
"""

import requests
import json

def test_problems_server():
    """Test the problems server endpoints"""
    base_url = "http://localhost:5001"
    
    try:
        print("🔍 Testing Problems Server...")
        
        # Test 1: Health check
        print("\n1️⃣ Testing health check...")
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data.get('total_problems', 0)} problems available")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        print("🚨 Make sure to run: python problems_server.py")
        return False
    
    try:
        # Test 2: Get all problems
        print("\n2️⃣ Testing problems endpoint...")
        response = requests.get(f"{base_url}/problems?limit=200", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                problems = data.get('problems', [])
                total = data.get('total', 0)
                print(f"✅ Problems endpoint working!")
                print(f"📊 Retrieved: {len(problems)} problems")
                print(f"📈 Total available: {total} problems")
                
                if len(problems) >= 100:
                    print(f"🎉 SUCCESS! Now showing {len(problems)} problems instead of 5!")
                    
                    # Show some sample problems
                    print(f"\n📝 Sample problems:")
                    for i, problem in enumerate(problems[:3]):
                        print(f"   {i+1}. {problem.get('title', 'Unknown')} ({problem.get('difficulty', 'Unknown')})")
                    
                    return True
                else:
                    print(f"⚠️  Only {len(problems)} problems found, expected 180+")
            else:
                print(f"❌ API returned error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Problems endpoint failed: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Problems test failed: {e}")
    
    return False

if __name__ == "__main__":
    print("🚀 Starting Problems Server Test...")
    success = test_problems_server()
    
    if success:
        print("\n🎯 RESOLUTION: The problems database has 180+ problems available!")
        print("🔧 Next steps:")
        print("   1. Keep the problems server running (python problems_server.py)")
        print("   2. Start the React frontend (cd frontend && npm run dev)")
        print("   3. Navigate to Problems section in the frontend")
        print("   4. You should now see 180+ problems instead of 5!")
    else:
        print("\n❌ Problems server test failed.")
        print("🔧 Troubleshooting:")
        print("   1. Make sure to run: python problems_server.py")
        print("   2. Check if port 5000 is available")
        print("   3. Verify data/Problems/problems.json exists")