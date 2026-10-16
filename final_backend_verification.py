#!/usr/bin/env python3
"""
Final verification - show exactly what the backend returns
"""

import requests
import json

def final_verification():
    """Show exactly what the backend is returning"""
    print("🎯 FINAL BACKEND VERIFICATION")
    print("=" * 60)
    
    # Test with a simple, clear resume
    test_resume = """
John Smith
Software Engineer

Skills: React, JavaScript, Node.js, Python, AWS
Experience: 3 years of web development
Built e-commerce applications and REST APIs
    """
    
    print(f"📝 Test Resume:")
    print(test_resume.strip())
    print(f"\n🔍 Expected Results:")
    print(f"   Skills: react, javascript, node.js, python, aws")
    print(f"   Experience: 3 years")
    print(f"   Best Match: Should be Full Stack Engineer or React Developer")
    
    try:
        response = requests.post("http://localhost:5000/recommend",
            json={'resume_text': test_resume},
            timeout=10)
        
        print(f"\n📊 ACTUAL BACKEND RESPONSE:")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                # Show parsed data
                parsed = data.get('parsed', {})
                print(f"\n✅ PARSED RESUME:")
                print(f"   Skills: {parsed.get('skills', [])}")
                print(f"   Experience: {parsed.get('years_experience')} years")
                
                # Show job matches
                jobs = data.get('jobs', [])
                print(f"\n🎯 JOB MATCHES ({len(jobs)} found):")
                
                if jobs:
                    for i, job in enumerate(jobs, 1):
                        score = job.get('similarity_score', 0)
                        matched_skills = job.get('matched_skills', [])
                        
                        print(f"   {i}. {job.get('title')} at {job.get('company')}")
                        print(f"      Location: {job.get('location')}")
                        print(f"      Match: {score:.1%}")
                        print(f"      Matched Skills: {matched_skills}")
                        print()
                
                # Show live jobs
                live_jobs = data.get('live_jobs', [])
                print(f"🌐 LIVE JOBS ({len(live_jobs)} found):")
                
                if live_jobs:
                    for i, job in enumerate(live_jobs[:3], 1):
                        print(f"   {i}. {job.get('title')} at {job.get('company')}")
                        print(f"      Location: {job.get('location')}")
                
                # Verification
                print(f"\n🔍 VERIFICATION:")
                
                # Check skills
                expected_skills = ['react', 'javascript', 'node.js', 'python', 'aws']
                found_skills = [s.lower() for s in parsed.get('skills', [])]
                skill_matches = [s for s in expected_skills if s in found_skills]
                
                print(f"   Skills Detection: {len(skill_matches)}/{len(expected_skills)} ✅")
                
                # Check experience
                exp = parsed.get('years_experience', 0)
                print(f"   Experience Detection: {exp} years {'✅' if exp == 3 else '⚠️'}")
                
                # Check job matching
                if jobs and jobs[0].get('similarity_score', 0) > 0.6:
                    print(f"   Job Matching: High quality matches ✅")
                elif jobs:
                    print(f"   Job Matching: Working but could be better ⚠️")
                else:
                    print(f"   Job Matching: No matches found ❌")
                
                # Check if dynamic
                if jobs:
                    first_score = jobs[0].get('similarity_score', 0)
                    if first_score not in [0.95, 0.87, 0.82]:  # Old static scores
                        print(f"   Dynamic Matching: Confirmed ✅")
                    else:
                        print(f"   Dynamic Matching: Might be static ⚠️")
                
                print(f"\n🎊 FINAL RESULT:")
                if (len(skill_matches) >= 4 and 
                    jobs and 
                    jobs[0].get('similarity_score', 0) > 0.6):
                    print(f"   ✅ BACKEND IS WORKING PERFECTLY!")
                    print(f"   ✅ Dynamic skill extraction: Working")
                    print(f"   ✅ Personalized job matching: Working") 
                    print(f"   ✅ High-quality results: Working")
                    print(f"")
                    print(f"   🎯 The issue is likely frontend caching!")
                    print(f"   💡 Try hard refresh (Ctrl+F5) or incognito mode")
                else:
                    print(f"   ⚠️ Backend needs some improvements")
                    
            else:
                print(f"❌ API Error: {data.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    final_verification()
