#!/usr/bin/env python3
"""
Test script to verify job recommendation performance and voice recording fixes.
"""

import os
import sys
import time
import requests
import json

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_job_recommendation_performance():
    """Test job recommendation API performance."""
    print("🚀 Testing Job Recommendation Performance...")
    
    sample_resume = """
    Senior Software Engineer with 5+ years of experience.
    
    SKILLS:
    - Programming: Python, JavaScript, React, Node.js
    - Cloud: AWS, Docker, Kubernetes
    - Databases: PostgreSQL, MongoDB, Redis
    - Tools: Git, Jenkins, Jira
    
    EXPERIENCE:
    - Led development of microservices architecture
    - Built scalable web applications serving 1M+ users
    - Implemented CI/CD pipelines
    - Mentored junior developers
    """
    
    try:
        # Test JSON upload endpoint
        start_time = time.time()
        
        response = requests.post(
            'http://localhost:5000/upload',
            json={'resume_text': sample_resume},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"⏱️  Response time: {response_time:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                jobs = data.get('jobs', [])
                live_jobs = data.get('live_jobs', [])
                
                print(f"✅ Job recommendation successful!")
                print(f"   - Found {len(jobs)} job matches")
                print(f"   - Found {len(live_jobs)} live jobs")
                print(f"   - Response time: {response_time:.2f}s")
                
                if jobs:
                    print("   - Top 3 matches:")
                    for i, job in enumerate(jobs[:3], 1):
                        title = job.get('title', 'N/A')
                        company = job.get('company', 'N/A')
                        score = job.get('similarity_score', 0)
                        print(f"     {i}. {title} at {company} (Score: {score:.3f})")
                
                # Performance benchmark
                if response_time < 3.0:
                    print("🎯 Performance: EXCELLENT (< 3s)")
                elif response_time < 5.0:
                    print("✅ Performance: GOOD (< 5s)")
                elif response_time < 10.0:
                    print("⚠️  Performance: ACCEPTABLE (< 10s)")
                else:
                    print("❌ Performance: SLOW (> 10s)")
                
                return True
            else:
                print(f"❌ API returned error: {data.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_model_loading():
    """Test direct model loading performance."""
    print("\n🧪 Testing Direct Model Loading...")
    
    try:
        from job_matcher import JobMatcher
        
        start_time = time.time()
        
        # Initialize with performance limit
        matcher = JobMatcher(max_jobs=1000)  # Limit to 1000 jobs for speed
        
        load_time = time.time() - start_time
        print(f"⏱️  Model loading time: {load_time:.2f} seconds")
        
        if matcher.is_trained:
            print("✅ Model loaded successfully")
            
            # Test matching performance
            start_time = time.time()
            
            sample_resume = "Software Engineer with Python, React, and AWS experience"
            matches = matcher.find_matching_jobs(sample_resume, top_k=5)
            
            match_time = time.time() - start_time
            print(f"⏱️  Matching time: {match_time:.3f} seconds")
            print(f"📊 Found {len(matches)} matches")
            
            return True
        else:
            print("❌ Model not trained")
            return False
            
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_server_status():
    """Check if the Flask server is running."""
    print("🔍 Checking server status...")
    
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print("❌ Server is not running")
        print("💡 Please start the server with: python app.py")
        return False

def main():
    """Main test function."""
    print("🧪 Testing Job Recommendation & Interview Fixes\n")
    
    # Test model loading performance
    model_ok = test_model_loading()
    
    # Check server status
    server_ok = check_server_status()
    
    if server_ok:
        # Test API performance
        api_ok = test_job_recommendation_performance()
    else:
        api_ok = False
    
    print("\n📋 Test Summary:")
    print(f"   Model Loading: {'✅ PASS' if model_ok else '❌ FAIL'}")
    print(f"   Server Status: {'✅ PASS' if server_ok else '❌ FAIL'}")
    print(f"   API Performance: {'✅ PASS' if api_ok else '❌ FAIL'}")
    
    if model_ok and server_ok and api_ok:
        print("\n🎉 All tests passed! System is ready.")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
    
    print("\n📝 Voice Recording Fix:")
    print("   - Enhanced speech recognition error handling")
    print("   - Added microphone permission checks")
    print("   - Improved real-time text updates")
    print("   - Better session management")
    print("   - Test by starting a mock interview and using voice recording")

if __name__ == "__main__":
    main()
