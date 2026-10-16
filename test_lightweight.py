#!/usr/bin/env python3
"""
Lightweight test to verify job recommendation API with smaller dataset
"""

import requests
import json
import os

# Test configuration
API_BASE = "http://localhost:5000"
TEST_RESUME = "Software Engineer with 3 years Python experience"

def test_lightweight_api():
    """Test the job recommendation API with minimal load"""
    print("🔍 Testing lightweight job recommendation API...")
    
    try:
        # Test 1: Simple GET request to problems
        print("\n1️⃣ Testing Problems API...")
        response = requests.get(f"{API_BASE}/problems", timeout=10)
        if response.status_code == 200:
            problems = response.json()
            print(f"✅ Problems API working: {len(problems)} problems loaded")
        else:
            print(f"❌ Problems API failed: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Problems API error: {e}")
    
    try:
        # Test 2: Job recommendations with minimal data
        print("\n2️⃣ Testing Job Recommendation API...")
        
        # Prepare minimal test data
        files = {'resume': ('test.txt', TEST_RESUME, 'text/plain')}
        
        response = requests.post(f"{API_BASE}/recommend", files=files, timeout=30)
        
        if response.status_code == 200:
            recommendations = response.json()
            print(f"✅ Recommendations API working!")
            print(f"📊 Received {len(recommendations.get('recommendations', []))} job recommendations")
            
            # Show sample recommendation
            if recommendations.get('recommendations'):
                sample = recommendations['recommendations'][0]
                print(f"📝 Sample job: {sample.get('title')} at {sample.get('company')} ({sample.get('match_percentage')}% match)")
            
            # Show skill gap analysis
            if recommendations.get('skill_gap_analysis'):
                gap = recommendations['skill_gap_analysis']
                print(f"🎯 Skill gap: {len(gap.get('missing_skills', []))} missing skills identified")
                
        else:
            print(f"❌ Recommendations API failed: {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Recommendations API error: {e}")
    
    try:
        # Test 3: Check server health
        print("\n3️⃣ Testing Server Health...")
        response = requests.get(f"{API_BASE}/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and responding")
        else:
            print(f"❌ Server health check failed: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Server health check error: {e}")

def check_data_size():
    """Check the size of data files"""
    print("\n📁 Checking data file sizes...")
    
    files_to_check = [
        "data/unified_job_dataset.csv",
        "data/posted_jobs.json",
        "data/trained_model.joblib",
        "data/tfidf_vectorizer.joblib"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            size_mb = size / (1024 * 1024)
            print(f"📊 {file_path}: {size_mb:.1f} MB")
        else:
            print(f"❌ {file_path}: Not found")

if __name__ == "__main__":
    print("🚀 Starting lightweight API test...")
    check_data_size()
    test_lightweight_api()
    print("\n✨ Test completed!")