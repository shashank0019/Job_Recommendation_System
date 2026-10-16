#!/usr/bin/env python3
"""
Simple test script for live job fetching functionality
"""

import requests
import json

def test_live_jobs_endpoint():
    """Test the live jobs endpoint on the running Flask server."""
    try:
        print("🧪 Testing live jobs endpoint...")
        
        # Test the endpoint
        response = requests.get("http://127.0.0.1:5000/test-live-jobs", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Live jobs test successful!")
            print(f"📊 Test Results:")
            print(f"   - Keywords tested: {data['test_data']['keywords']}")
            print(f"   - Arbeitnow jobs: {data['test_data']['arbeitnow_jobs_count']}")
            print(f"   - Custom API jobs: {data['test_data']['custom_api_jobs_count']}")
            print(f"   - Fallback jobs: {data['test_data']['fallback_jobs_count']}")
            print(f"   - Total live jobs: {data['test_data']['total_live_jobs']}")
            
            if data['fallback_sample']:
                print(f"\n🔄 Fallback Job Sample:")
                for job in data['fallback_sample']:
                    print(f"   - {job['title']} at {job['company']} ({job['location']})")
                    
        else:
            print(f"❌ Test failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask server. Make sure it's running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Test error: {e}")

def test_job_recommendation():
    """Test the job recommendation endpoint with live jobs."""
    try:
        print("\n🧪 Testing job recommendation with live jobs...")
        
        # Test data
        test_resume = """
        I am a Python developer with 3 years of experience in web development.
        I have worked with React, JavaScript, and AWS. I am proficient in Django
        and Flask frameworks. I have experience with databases like MySQL and MongoDB.
        """
        
        response = requests.post(
            "http://127.0.0.1:5000/recommend",
            json={"resume_text": test_resume},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Job recommendation successful!")
            print(f"📊 Results:")
            print(f"   - Dataset jobs: {len(data.get('jobs', []))}")
            print(f"   - Live jobs: {len(data.get('live_jobs', []))}")
            print(f"   - Skills parsed: {data.get('parsed', {}).get('skills', [])}")
            
            if data.get('live_jobs'):
                print(f"\n🌐 Live Jobs Found:")
                for i, job in enumerate(data['live_jobs'][:3]):
                    print(f"   {i+1}. {job['title']} at {job['company']}")
                    print(f"      Location: {job['location']}")
                    print(f"      Source: {job.get('source', 'unknown')}")
                    print(f"      Score: {job.get('final_score', 'N/A')}")
            else:
                print("⚠️ No live jobs found in response")
                
        else:
            print(f"❌ Recommendation failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask server. Make sure it's running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    print("🚀 Live Job Fetching Test Suite")
    print("=" * 50)
    
    test_live_jobs_endpoint()
    test_job_recommendation()
    
    print("\n" + "=" * 50)
    print("✅ Test suite completed!")
