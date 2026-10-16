#!/usr/bin/env python3
"""Test the text recommendation endpoint directly"""

import requests
import json

def test_text_recommendation():
    """Test sending text directly to the recommendation endpoint"""
    
    test_text = "Software Developer with 3 years experience in Python, JavaScript, React, and Node.js. Worked on web applications and APIs."
    
    try:
        print("🧪 Testing text recommendation endpoint...")
        print(f"📝 Test text: {test_text[:50]}...")
        
        response = requests.post(
            'http://localhost:5000/recommend',
            json={'resume_text': test_text},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"🔍 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('success')}")
            
            if data.get('success'):
                recommendations = data.get('recommendations', [])
                print(f"📊 Got {len(recommendations)} recommendations")
                
                if recommendations:
                    print("\n📋 Sample recommendations:")
                    for i, job in enumerate(recommendations[:3]):
                        print(f"  {i+1}. {job.get('title')} at {job.get('company')} ({job.get('match_percentage')}% match)")
                
                skill_gap = data.get('skill_gap_analysis', {})
                if skill_gap:
                    print(f"\n🎯 Skill Gap Analysis:")
                    print(f"  - Missing skills: {len(skill_gap.get('missing_skills', []))}")
                    print(f"  - Coverage: {skill_gap.get('coverage_percentage', 0)}%")
                
                print("\n🎉 Text recommendation test PASSED!")
            else:
                print(f"❌ API returned error: {data.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_text_recommendation()