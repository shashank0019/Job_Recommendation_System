#!/usr/bin/env python3
"""
Debug with a real resume example to see what's happening
"""

import requests
import json

def debug_real_resume():
    """Test with a realistic resume to debug the issue"""
    print("🔍 DEBUGGING REAL RESUME PROCESSING")
    print("=" * 60)
    
    # Real resume example
    real_resume = """
Sarah Johnson
Senior Software Engineer
Email: sarah.johnson@email.com
Phone: (555) 123-4567

PROFESSIONAL SUMMARY
Experienced Full Stack Developer with 6+ years of expertise in modern web technologies.
Proven track record in React, Node.js, Python, and cloud platforms.

TECHNICAL SKILLS
• Frontend: React, JavaScript, TypeScript, HTML5, CSS3, Vue.js
• Backend: Node.js, Python, Django, Flask, Express.js
• Databases: MongoDB, PostgreSQL, MySQL, Redis
• Cloud & DevOps: AWS, Docker, Kubernetes, CI/CD
• Tools: Git, Jenkins, Jira, VS Code

WORK EXPERIENCE
Senior Software Engineer | TechCorp Inc. | 2021 - Present
• Developed scalable web applications using React and Node.js
• Implemented microservices architecture with Docker and Kubernetes
• Managed AWS infrastructure and CI/CD pipelines
• Led a team of 4 developers on multiple projects

Software Engineer | StartupXYZ | 2019 - 2021  
• Built full-stack applications with Python Django and React
• Optimized database queries reducing response time by 40%
• Integrated third-party APIs and payment systems

Junior Developer | WebSolutions | 2018 - 2019
• Developed responsive websites using JavaScript and CSS
• Collaborated with designers to implement UI/UX designs

EDUCATION
Bachelor of Science in Computer Science
University of Technology | 2014 - 2018

PROJECTS
E-commerce Platform: Built with React, Node.js, MongoDB
Task Management App: Developed using Python Flask and PostgreSQL
    """.strip()
    
    print(f"📝 Testing with realistic resume ({len(real_resume)} characters)")
    print(f"Expected skills: React, Node.js, Python, JavaScript, AWS, Docker, etc.")
    
    # Test 1: Direct API call
    print(f"\n1. Testing /recommend endpoint...")
    try:
        response = requests.post("http://localhost:5000/recommend",
            json={'resume_text': real_resume},
            headers={'Content-Type': 'application/json'},
            timeout=15)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                parsed = data.get('parsed', {})
                jobs = data.get('jobs', [])
                live_jobs = data.get('live_jobs', [])
                
                print(f"   ✅ Success: {data.get('success')}")
                print(f"   📊 Skills Found: {len(parsed.get('skills', []))} - {parsed.get('skills', [])}")
                print(f"   📅 Experience: {parsed.get('years_experience')} years")
                print(f"   🎯 Job Matches: {len(jobs)}")
                
                if jobs:
                    print(f"   📋 Top 3 Matches:")
                    for i, job in enumerate(jobs[:3], 1):
                        score = job.get('similarity_score', 0)
                        matched_skills = job.get('matched_skills', [])
                        print(f"      {i}. {job.get('title')} at {job.get('company')}")
                        print(f"         Match: {score:.1%}, Skills: {matched_skills}")
                
                print(f"   🌐 Live Jobs: {len(live_jobs)}")
                
                # Check if this looks like real dynamic data
                if jobs and len(jobs) > 0:
                    first_job = jobs[0]
                    if first_job.get('similarity_score', 0) > 0.5:
                        print(f"   ✅ DYNAMIC MATCHING: Working! High similarity scores detected")
                    else:
                        print(f"   ⚠️ LOW SCORES: Similarity scores seem low")
                else:
                    print(f"   ❌ NO MATCHES: No job matches found")
                    
            else:
                print(f"   ❌ API Error: {data.get('error')}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test 2: File upload simulation
    print(f"\n2. Testing /upload endpoint...")
    try:
        files = {'resume_file': ('sarah_resume.txt', real_resume, 'text/plain')}
        
        response = requests.post("http://localhost:5000/upload",
            files=files,
            timeout=15)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                parsed = data.get('parsed', {})
                jobs = data.get('jobs', [])
                
                print(f"   ✅ File Upload Success")
                print(f"   📊 Skills: {parsed.get('skills', [])}")
                print(f"   📅 Experience: {parsed.get('years_experience')} years")
                print(f"   📁 Filename: {parsed.get('filename')}")
                print(f"   🎯 Job Matches: {len(jobs)}")
                
                if jobs:
                    best_match = jobs[0]
                    print(f"   🏆 Best Match: {best_match.get('title')} at {best_match.get('company')}")
                    print(f"      Score: {best_match.get('similarity_score', 0):.1%}")
                
            else:
                print(f"   ❌ Upload Error: {data.get('error')}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Upload test failed: {e}")
    
    print(f"\n🎯 DIAGNOSIS:")
    print(f"✅ If you see high similarity scores (>50%) and relevant job matches,")
    print(f"   the dynamic matching is working correctly!")
    print(f"⚠️ If you see low scores or no matches, there might be an issue")
    print(f"   with skill extraction or job matching logic.")
    print(f"❌ If you get errors, the server might not be running properly.")

if __name__ == "__main__":
    debug_real_resume()
