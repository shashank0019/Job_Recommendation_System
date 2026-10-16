#!/usr/bin/env python3
"""
Debug job matching with detailed output
"""

import requests
import json

def debug_job_matching():
    """Debug job matching with detailed logging"""
    url = "http://127.0.0.1:5000/recommend"
    
    # Sample resume with very specific skills
    sample_resume = """
    Senior Software Engineer
    
    Experience:
    - 5+ years of experience in full-stack web development
    - Expert in React.js, Node.js, JavaScript, TypeScript
    - Proficient in Python, Django, Flask
    - Experience with MongoDB, PostgreSQL, MySQL
    - Cloud platforms: AWS, Docker, Kubernetes
    - Strong experience in software engineering best practices
    
    Skills:
    React, Node.js, JavaScript, TypeScript, Python, Django, Flask, MongoDB, PostgreSQL, MySQL, AWS, Docker, Kubernetes, Git, HTML, CSS, REST APIs, GraphQL, Microservices, Agile, Scrum
    
    Education:
    Master's in Computer Science
    
    Looking for: Senior Software Engineer, Full Stack Developer, Backend Developer positions
    """
    
    print("🔍 Debug Job Matching")
    print("=" * 60)
    print(f"Resume Skills: React, Node.js, JavaScript, Python, AWS, etc.")
    
    try:
        response = requests.post(url, json={
            'resume_text': sample_resume
        }, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"API Success: {data.get('success')}")
            
            if data.get('success'):
                # Detailed analysis
                parsed = data.get('parsed', {})
                jobs = data.get('jobs', [])
                live_jobs = data.get('live_jobs', [])
                
                print(f"\n📄 Resume Analysis:")
                print(f"  Extracted Skills: {len(parsed.get('skills', []))} skills")
                print(f"  Skills: {parsed.get('skills', [])[:10]}...")  # Show first 10
                print(f"  Experience: {parsed.get('years_experience', 0)} years")
                
                print(f"\n🎯 Model Job Matches:")
                print(f"  Total Matches: {len(jobs)}")
                
                if jobs:
                    print(f"  Top Matches:")
                    for i, job in enumerate(jobs, 1):
                        score = job.get('similarity_score', 0)
                        print(f"    {i}. {job.get('title', 'N/A')}")
                        print(f"       Company: {job.get('company', 'N/A')}")
                        print(f"       Location: {job.get('location', 'N/A')}")
                        print(f"       Similarity: {score:.4f} ({score*100:.2f}%)")
                        print()
                else:
                    print(f"  ❌ No model matches found!")
                    print(f"  This could indicate:")
                    print(f"    - Similarity threshold too high (>0.01)")
                    print(f"    - Vocabulary mismatch between resume and jobs")
                    print(f"    - TF-IDF vectorization issues")
                
                print(f"\n🌐 Live Job Matches:")
                print(f"  Total Live Jobs: {len(live_jobs)}")
                
                if live_jobs:
                    print(f"  Sample Live Jobs:")
                    for i, job in enumerate(live_jobs[:3], 1):
                        print(f"    {i}. {job.get('title', 'N/A')}")
                        print(f"       Company: {job.get('company', 'N/A')}")
                        print(f"       Location: {job.get('location', 'N/A')}")
                
                # Diagnosis
                print(f"\n🔧 Diagnosis:")
                if parsed.get('skills'):
                    print(f"  ✅ Resume parsing: Working")
                else:
                    print(f"  ❌ Resume parsing: Failed")
                
                if jobs:
                    print(f"  ✅ Model matching: Working")
                else:
                    print(f"  ❌ Model matching: Not working")
                    print(f"     Possible fixes:")
                    print(f"     - Lower similarity threshold")
                    print(f"     - Check job dataset content")
                    print(f"     - Verify TF-IDF vectorization")
                
                if live_jobs:
                    print(f"  ✅ Live job fetching: Working")
                else:
                    print(f"  ⚠️ Live job fetching: No results")
                
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_job_matching()
