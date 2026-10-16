#!/usr/bin/env python3
"""
Test the recommendation server endpoints
"""

import requests
import json

def test_recommendation_server():
    """Test the recommendation server"""
    base_url = "http://localhost:5000"
    
    print("🔍 Testing Recommendation Server...")
    
    try:
        # Test 1: Health check
        print("\n1️⃣ Testing health check...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed!")
            print(f"📊 Jobs loaded: {data.get('jobs_loaded', 0)}")
            print(f"🔧 Available endpoints: {list(data.get('endpoints', {}).keys())}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        print("🚨 Make sure to run: python simple_recommendation_server.py")
        return False
    
    try:
        # Test 2: Job recommendation
        print("\n2️⃣ Testing job recommendation...")
        test_resume = "Software Engineer with 3 years Python experience. Skilled in JavaScript, React, and SQL."
        
        response = requests.post(f"{base_url}/recommend", 
                               json={"resume_text": test_resume},
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                recommendations = data.get('recommendations', [])
                skill_gap = data.get('skill_gap_analysis', {})
                
                print(f"✅ Recommendations endpoint working!")
                print(f"📊 Received {len(recommendations)} job recommendations")
                print(f"🎯 Average match: {skill_gap.get('avg_match_percentage', 0):.1f}%")
                
                if recommendations:
                    sample = recommendations[0]
                    print(f"📝 Sample job: {sample.get('title')} at {sample.get('company')} ({sample.get('match_percentage')}% match)")
                
                skills_found = skill_gap.get('skills_you_have', [])
                missing_skills = skill_gap.get('missing_skills', [])
                print(f"💪 Skills found: {skills_found[:3]}...")
                print(f"📚 Missing skills: {missing_skills[:3]}...")
                
                return True
            else:
                print(f"❌ Recommendation failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Recommendation endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Recommendation test failed: {e}")
    
    return False

if __name__ == "__main__":
    print("🚀 Testing Recommendation Server Endpoints...")
    success = test_recommendation_server()
    
    if success:
        print("\n🎉 SUCCESS! Recommendation server is working!")
        print("🔧 Next steps:")
        print("   1. React frontend should now connect successfully")
        print("   2. Job recommendations will work in the UI")
        print("   3. File uploads will work in the UI")
        print("   4. No more connection errors!")
    else:
        print("\n❌ Server test failed.")
        print("🔧 Troubleshooting:")
        print("   1. Make sure server is running: python simple_recommendation_server.py")
        print("   2. Check if port 5000 is available") 
        print("   3. Verify data files exist")