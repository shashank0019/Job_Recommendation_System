#!/usr/bin/env python3
"""
Debug the specific issue - test with exact resume content
"""

import requests
import json

def debug_specific_issue():
    """Test with specific resume content to debug the exact issue"""
    print("🔍 DEBUGGING SPECIFIC ISSUE")
    print("=" * 60)
    
    # Test with a very specific resume that should give clear results
    specific_resume = """
Sarah Johnson
Senior React Developer
Email: sarah@email.com

TECHNICAL SKILLS:
• Frontend: React, JavaScript, TypeScript, HTML5, CSS3
• Backend: Node.js, Express.js
• Database: MongoDB, PostgreSQL
• Cloud: AWS, Docker
• Tools: Git, VS Code, Webpack

PROFESSIONAL EXPERIENCE:
Senior Frontend Developer | TechCorp | 2019 - Present (5+ years)
• Developed responsive web applications using React and TypeScript
• Built RESTful APIs with Node.js and Express
• Managed AWS infrastructure and deployments
• Led a team of 3 junior developers

Software Engineer | StartupXYZ | 2017 - 2019 (2 years)
• Created interactive user interfaces with React
• Integrated third-party APIs and services
• Optimized application performance and loading times

EDUCATION:
Bachelor of Computer Science | University of Technology | 2017

PROJECTS:
E-commerce Platform: React, Node.js, MongoDB, AWS
Task Management App: TypeScript, React, PostgreSQL
    """
    
    print(f"📝 Testing with detailed resume ({len(specific_resume)} characters)")
    print(f"Expected skills: React, JavaScript, TypeScript, Node.js, MongoDB, AWS")
    print(f"Expected experience: 5+ years")
    
    try:
        # Test the recommend endpoint
        response = requests.post("http://localhost:5000/recommend",
            json={'resume_text': specific_resume},
            headers={'Content-Type': 'application/json'},
            timeout=15)
        
        print(f"\n📊 SERVER RESPONSE:")
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Print the complete raw response
            print(f"\n📋 RAW RESPONSE DATA:")
            print(json.dumps(data, indent=2))
            
            if data.get('success'):
                parsed = data.get('parsed', {})
                jobs = data.get('jobs', [])
                live_jobs = data.get('live_jobs', [])
                
                print(f"\n✅ PARSED RESUME DATA:")
                print(f"   Skills Found: {parsed.get('skills', [])}")
                print(f"   Experience: {parsed.get('years_experience')} years")
                print(f"   Filename: {parsed.get('filename', 'N/A')}")
                
                print(f"\n🎯 JOB MATCHES ({len(jobs)} total):")
                if jobs:
                    for i, job in enumerate(jobs, 1):
                        title = job.get('title', 'N/A')
                        company = job.get('company', 'N/A')
                        location = job.get('location', 'N/A')
                        score = job.get('similarity_score', 0)
                        matched_skills = job.get('matched_skills', [])
                        
                        print(f"   {i}. {title}")
                        print(f"      Company: {company}")
                        print(f"      Location: {location}")
                        print(f"      Match Score: {score:.3f} ({score:.1%})")
                        print(f"      Matched Skills: {matched_skills}")
                        print()
                        
                        # Analyze if this is really dynamic
                        if i == 1:  # Check first result
                            if score == 0.95:
                                print(f"      ⚠️ WARNING: This looks like static data (95% = old hardcoded)")
                            elif score > 0.8:
                                print(f"      ✅ GOOD: High dynamic match score detected")
                            elif score > 0.5:
                                print(f"      ✅ OK: Moderate dynamic match score")
                            else:
                                print(f"      ⚠️ LOW: Low match score - algorithm might need tuning")
                else:
                    print(f"   ❌ NO JOB MATCHES FOUND!")
                
                print(f"\n🌐 LIVE JOBS ({len(live_jobs)} total):")
                if live_jobs:
                    for i, job in enumerate(live_jobs[:3], 1):
                        print(f"   {i}. {job.get('title')} at {job.get('company')}")
                        print(f"      Location: {job.get('location')}")
                        print(f"      URL: {job.get('url', 'N/A')}")
                else:
                    print(f"   ❌ NO LIVE JOBS FOUND!")
                
                # Final analysis
                print(f"\n🎯 ANALYSIS:")
                expected_skills = ['react', 'javascript', 'typescript', 'node.js', 'mongodb', 'aws']
                found_skills = [s.lower() for s in parsed.get('skills', [])]
                matched_expected = [s for s in expected_skills if s in found_skills]
                
                print(f"   Expected Skills: {expected_skills}")
                print(f"   Found Skills: {found_skills}")
                print(f"   Matched: {matched_expected} ({len(matched_expected)}/{len(expected_skills)})")
                
                if len(matched_expected) >= 4:
                    print(f"   ✅ SKILL EXTRACTION: Working well")
                else:
                    print(f"   ⚠️ SKILL EXTRACTION: Needs improvement")
                
                if jobs and jobs[0].get('similarity_score', 0) > 0.7:
                    print(f"   ✅ JOB MATCHING: Working with high scores")
                elif jobs:
                    print(f"   ⚠️ JOB MATCHING: Working but low scores")
                else:
                    print(f"   ❌ JOB MATCHING: Not working")
                    
            else:
                print(f"❌ API ERROR: {data.get('error', 'Unknown error')}")
                
        else:
            print(f"❌ HTTP ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ REQUEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🎯 CONCLUSION:")
    print(f"If you see high match scores (>70%) and relevant skills extracted,")
    print(f"the backend is working correctly and the issue is frontend caching.")
    print(f"If you see low scores or wrong skills, the backend needs fixing.")

if __name__ == "__main__":
    debug_specific_issue()
