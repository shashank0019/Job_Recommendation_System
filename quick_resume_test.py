#!/usr/bin/env python3
"""
Quick test to verify resume processing is working correctly
"""

import requests

def quick_test():
    """Quick test with a simple resume"""
    print("🔍 QUICK RESUME TEST")
    print("=" * 40)
    
    # Simple test resume
    test_resume = """
John Smith
Software Developer

Skills: React, JavaScript, Node.js, Python, AWS, MongoDB
Experience: 4 years of web development
    """
    
    print(f"📝 Testing resume: {test_resume.strip()}")
    
    try:
        response = requests.post("http://localhost:5000/recommend",
            json={'resume_text': test_resume},
            timeout=10)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                parsed = data.get('parsed', {})
                jobs = data.get('jobs', [])
                
                print(f"✅ Skills: {parsed.get('skills', [])}")
                print(f"✅ Experience: {parsed.get('years_experience')} years")
                print(f"✅ Job Matches: {len(jobs)}")
                
                if jobs:
                    for i, job in enumerate(jobs[:2], 1):
                        score = job.get('similarity_score', 0)
                        print(f"   {i}. {job.get('title')} at {job.get('company')} - {score:.1%}")
                
                # Check if it's working dynamically
                expected_skills = ['react', 'javascript', 'node.js', 'python', 'aws', 'mongodb']
                found_skills = parsed.get('skills', [])
                matches = [s for s in expected_skills if s in found_skills]
                
                print(f"✅ Skill Detection: {len(matches)}/{len(expected_skills)} found")
                
                if len(matches) >= 4:
                    print("🎉 WORKING! Dynamic skill extraction is functioning")
                else:
                    print("⚠️ Skill extraction might need improvement")
                    
            else:
                print(f"❌ Error: {data.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    quick_test()
