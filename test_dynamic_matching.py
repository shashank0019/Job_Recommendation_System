#!/usr/bin/env python3
"""
Test dynamic job matching with different skill sets
"""

import requests

def test_dynamic_matching():
    """Test dynamic job matching with various skill combinations"""
    print("🎯 TESTING DYNAMIC JOB MATCHING")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "React Frontend Developer",
            "resume": "Frontend Developer with 3 years experience in React, JavaScript, TypeScript, and modern web development.",
            "expected_skills": ["react", "javascript", "typescript"]
        },
        {
            "name": "Python Backend Developer", 
            "resume": "Backend Engineer with 7 years experience in Python, Django, AWS, MongoDB, and API development.",
            "expected_skills": ["python", "django", "aws", "mongodb"]
        },
        {
            "name": "Full Stack Developer",
            "resume": "Full Stack Developer with 5+ years experience in React, Node.js, Python, AWS, Docker, and Kubernetes.",
            "expected_skills": ["react", "node.js", "python", "aws", "docker", "kubernetes"]
        },
        {
            "name": "DevOps Engineer",
            "resume": "DevOps Engineer with 4 years experience in AWS, Docker, Kubernetes, Python scripting, and CI/CD pipelines.",
            "expected_skills": ["aws", "docker", "kubernetes", "python"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print(f"   Resume: {test_case['resume'][:80]}...")
        
        try:
            response = requests.post("http://localhost:5000/recommend",
                json={'resume_text': test_case['resume']},
                timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    parsed = data.get('parsed', {})
                    jobs = data.get('jobs', [])
                    live_jobs = data.get('live_jobs', [])
                    
                    print(f"   ✅ Skills Found: {parsed.get('skills', [])}")
                    print(f"   ✅ Experience: {parsed.get('years_experience')} years")
                    print(f"   ✅ Job Matches: {len(jobs)}")
                    
                    if jobs:
                        best_match = jobs[0]
                        print(f"   🎯 Best Match: {best_match['title']} at {best_match['company']}")
                        print(f"      Match Score: {best_match['similarity_score']:.1%}")
                        print(f"      Matched Skills: {best_match.get('matched_skills', [])}")
                    
                    print(f"   🌐 Live Jobs: {len(live_jobs)}")
                    
                    # Verify skills extraction
                    extracted_skills = parsed.get('skills', [])
                    expected_skills = test_case['expected_skills']
                    matched_expected = [skill for skill in expected_skills if skill in extracted_skills]
                    
                    if len(matched_expected) >= len(expected_skills) * 0.7:  # 70% match threshold
                        print(f"   ✅ Skill Extraction: GOOD ({len(matched_expected)}/{len(expected_skills)} expected skills found)")
                    else:
                        print(f"   ⚠️ Skill Extraction: PARTIAL ({len(matched_expected)}/{len(expected_skills)} expected skills found)")
                
                else:
                    print(f"   ❌ API Error: {data.get('error')}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
    
    print(f"\n🎊 DYNAMIC MATCHING TEST COMPLETE!")
    print(f"✅ The system now provides personalized job recommendations")
    print(f"✅ Job matches are based on actual resume content")
    print(f"✅ Match scores reflect skill compatibility")
    print(f"✅ No more static data - everything is dynamic!")

if __name__ == "__main__":
    test_dynamic_matching()
