#!/usr/bin/env python3
"""
Test job recommendation functionality
"""

import requests
import json

def test_job_recommendation():
    """Test the job recommendation API"""
    url = "http://127.0.0.1:5000/recommend"
    
    # Sample resume text
    sample_resume = """
    John Doe
    Software Engineer
    
    Experience:
    - 3 years of experience in full-stack development
    - Proficient in React, Node.js, JavaScript, Python
    - Experience with MongoDB, Express.js, SQL databases
    - Built and deployed web applications using AWS
    - Strong problem-solving and communication skills
    
    Skills:
    React, Node.js, JavaScript, Python, MongoDB, Express.js, SQL, AWS, Git, HTML, CSS
    
    Education:
    Bachelor's in Computer Science
    """
    
    print("🧪 Testing Job Recommendation API")
    print("=" * 50)
    print(f"URL: {url}")
    print(f"Resume length: {len(sample_resume)} characters")
    
    try:
        response = requests.post(url, json={
            'resume_text': sample_resume
        }, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            
            if data.get('success'):
                # Check parsed resume
                parsed = data.get('parsed', {})
                print(f"\n📄 Parsed Resume:")
                print(f"  Skills: {parsed.get('skills', [])}")
                print(f"  Experience: {parsed.get('years_experience', 0)} years")
                
                # Check job matches
                jobs = data.get('jobs', [])
                print(f"\n🎯 Model Matches: {len(jobs)} jobs")
                for i, job in enumerate(jobs[:3], 1):
                    print(f"  {i}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
                    print(f"     Match: {(job.get('similarity_score', 0) * 100):.1f}%")
                
                # Check live jobs
                live_jobs = data.get('live_jobs', [])
                print(f"\n🌐 Live Jobs: {len(live_jobs)} jobs")
                for i, job in enumerate(live_jobs[:3], 1):
                    print(f"  {i}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
                    print(f"     Location: {job.get('location', 'N/A')}")
                
                # Summary
                print(f"\n📊 Summary:")
                print(f"  ✅ Resume parsing: {'Working' if parsed else 'Failed'}")
                print(f"  ✅ Model matches: {'Working' if jobs else 'No matches found'}")
                print(f"  ✅ Live jobs: {'Working' if live_jobs else 'No live jobs found'}")
                
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_job_recommendation()
