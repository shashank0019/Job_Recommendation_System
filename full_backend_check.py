#!/usr/bin/env python3
"""
Comprehensive backend check - test every endpoint and functionality
"""

import requests
import json

def full_backend_check():
    """Complete backend system check"""
    print("🔍 COMPREHENSIVE BACKEND CHECK")
    print("=" * 70)
    
    base_url = "http://localhost:5000"
    
    # Test 1: Server Health and Basic Info
    print("1. SERVER HEALTH CHECK")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Server: {data}")
        else:
            print(f"   ❌ Health check failed")
    except Exception as e:
        print(f"   ❌ Cannot connect: {e}")
        return
    
    # Test 2: Job Recommendation with Multiple Resumes
    print(f"\n2. JOB RECOMMENDATION TESTING")
    print("-" * 30)
    
    test_resumes = [
        {
            "name": "React Developer",
            "text": "Frontend Developer with 3 years experience in React, JavaScript, TypeScript, HTML, CSS. Built responsive web applications."
        },
        {
            "name": "Python Developer", 
            "text": "Backend Engineer with 5 years experience in Python, Django, Flask, PostgreSQL, AWS. Developed REST APIs and microservices."
        },
        {
            "name": "Full Stack Developer",
            "text": "Full Stack Developer with 7+ years experience in React, Node.js, Python, MongoDB, AWS, Docker. Led development teams."
        }
    ]
    
    for i, resume in enumerate(test_resumes, 1):
        print(f"\n   Test {i}: {resume['name']}")
        try:
            response = requests.post(f"{base_url}/recommend",
                json={'resume_text': resume['text']},
                timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    parsed = data.get('parsed', {})
                    jobs = data.get('jobs', [])
                    live_jobs = data.get('live_jobs', [])
                    
                    print(f"      ✅ Skills: {parsed.get('skills', [])}")
                    print(f"      ✅ Experience: {parsed.get('years_experience')} years")
                    print(f"      ✅ Job Matches: {len(jobs)}")
                    
                    if jobs:
                        best_job = jobs[0]
                        score = best_job.get('similarity_score', 0)
                        print(f"      🎯 Best Match: {best_job.get('title')} at {best_job.get('company')} ({score:.1%})")
                        
                        # Check if scores are dynamic
                        if score > 0 and score != 0.95:  # Not the old static 95%
                            print(f"      ✅ DYNAMIC: Real similarity calculation detected")
                        else:
                            print(f"      ⚠️ STATIC: Might be using hardcoded data")
                    
                    print(f"      ✅ Live Jobs: {len(live_jobs)}")
                else:
                    print(f"      ❌ API Error: {data.get('error')}")
            else:
                print(f"      ❌ HTTP Error: {response.status_code}")
        except Exception as e:
            print(f"      ❌ Request failed: {e}")
    
    # Test 3: File Upload
    print(f"\n3. FILE UPLOAD TESTING")
    print("-" * 30)
    
    test_file_content = """
John Smith
Senior Software Engineer

SKILLS:
• React, JavaScript, TypeScript
• Node.js, Express.js
• Python, Django
• AWS, Docker, Kubernetes
• MongoDB, PostgreSQL

EXPERIENCE:
Senior Software Engineer (2020-Present)
- 4+ years of full-stack development
- Led team of 5 developers
- Built scalable microservices architecture
    """
    
    try:
        files = {'resume_file': ('john_smith_resume.txt', test_file_content, 'text/plain')}
        response = requests.post(f"{base_url}/upload", files=files, timeout=10)
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                parsed = data.get('parsed', {})
                jobs = data.get('jobs', [])
                
                print(f"   ✅ File processed successfully")
                print(f"   📁 Filename: {parsed.get('filename')}")
                print(f"   📊 Skills: {parsed.get('skills', [])}")
                print(f"   📅 Experience: {parsed.get('years_experience')} years")
                print(f"   🎯 Job Matches: {len(jobs)}")
                
                if jobs:
                    print(f"   📋 Sample matches:")
                    for job in jobs[:2]:
                        score = job.get('similarity_score', 0)
                        print(f"      - {job.get('title')} at {job.get('company')} ({score:.1%})")
            else:
                print(f"   ❌ Upload failed: {data.get('error')}")
        else:
            print(f"   ❌ Upload error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Upload test failed: {e}")
    
    # Test 4: Interview Questions
    print(f"\n4. INTERVIEW SYSTEM TESTING")
    print("-" * 30)
    
    try:
        # Test both endpoints
        endpoints = ['/api/interview/questions', '/interview/questions']
        
        for endpoint in endpoints:
            response = requests.post(f"{base_url}{endpoint}",
                json={'skills': ['react', 'javascript', 'python'], 'num_questions': 2},
                timeout=5)
            print(f"   {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    questions = data.get('questions', [])
                    print(f"      ✅ Generated {len(questions)} questions")
                    if questions:
                        print(f"      📝 Sample: {questions[0].get('text', '')[:60]}...")
    except Exception as e:
        print(f"   ❌ Interview test failed: {e}")
    
    # Test 5: Problems API
    print(f"\n5. PROBLEMS API TESTING")
    print("-" * 30)
    
    try:
        endpoints = ['/api/problems', '/problems']
        
        for endpoint in endpoints:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"   {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    problems = data.get('problems', [])
                    print(f"      ✅ Found {len(problems)} problems")
                    if problems:
                        print(f"      💻 Sample: {problems[0].get('title', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Problems test failed: {e}")
    
    # Test 6: Check what the server is actually returning
    print(f"\n6. RAW SERVER RESPONSE ANALYSIS")
    print("-" * 30)
    
    try:
        test_text = "Software Engineer with React, Node.js, Python, 5 years experience"
        response = requests.post(f"{base_url}/recommend",
            json={'resume_text': test_text},
            timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 Raw Response Structure:")
            print(f"      Success: {data.get('success')}")
            print(f"      Jobs count: {len(data.get('jobs', []))}")
            print(f"      Live jobs count: {len(data.get('live_jobs', []))}")
            
            jobs = data.get('jobs', [])
            if jobs:
                print(f"   📋 Job Details:")
                for i, job in enumerate(jobs[:3], 1):
                    print(f"      {i}. Title: {job.get('title')}")
                    print(f"         Company: {job.get('company')}")
                    print(f"         Score: {job.get('similarity_score')}")
                    print(f"         Matched Skills: {job.get('matched_skills', [])}")
            
            parsed = data.get('parsed', {})
            print(f"   📊 Parsed Data:")
            print(f"      Skills: {parsed.get('skills', [])}")
            print(f"      Experience: {parsed.get('years_experience')}")
            
        else:
            print(f"   ❌ Failed to get response: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Raw response test failed: {e}")
    
    print(f"\n🎯 BACKEND ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"✅ If all tests show '✅' and dynamic scores, backend is working")
    print(f"⚠️ If you see static scores (like 95%, 87%, 82%), there's an issue")
    print(f"❌ If tests fail, the server has problems")

if __name__ == "__main__":
    full_backend_check()
