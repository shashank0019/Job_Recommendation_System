#!/usr/bin/env python3
"""
Simple test for live job functionality
"""

def test_fetch_live_jobs():
    """Test the fetch_live_jobs function from clean_cors_server"""
    print("🔍 Testing fetch_live_jobs function...")
    
    try:
        # Import the function from clean_cors_server
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))
        
        from clean_cors_server import fetch_live_jobs
        
        # Test with sample skills
        test_skills = ["python", "react", "javascript"]
        print(f"Testing with skills: {test_skills}")
        
        live_jobs = fetch_live_jobs(test_skills, max_jobs=3)
        
        print(f"✅ Found {len(live_jobs)} live jobs")
        
        for i, job in enumerate(live_jobs, 1):
            print(f"{i}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
            print(f"   Location: {job.get('location', 'N/A')}")
            print(f"   Skills: {job.get('skills', 'N/A')}")
            print(f"   Source: {job.get('source', 'N/A')}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing fetch_live_jobs: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_client():
    """Test the API client directly"""
    print("\n🔍 Testing API Client...")
    
    try:
        from api_client import JobAPIClient
        
        client = JobAPIClient()
        status = client.get_api_status()
        
        print(f"API Key Configured: {status['api_key_configured']}")
        print(f"API Host: {status['api_host']}")
        print(f"API Accessible: {status.get('api_accessible', False)}")
        
        if status.get('error'):
            print(f"Error: {status['error']}")
        
        return status['api_key_configured']
        
    except Exception as e:
        print(f"❌ Error testing API client: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Simple Live Jobs Test")
    print("=" * 40)
    
    # Test API client first
    api_works = test_api_client()
    
    # Test fetch function
    fetch_works = test_fetch_live_jobs()
    
    print("=" * 40)
    if fetch_works:
        print("✅ Live jobs functionality is working!")
        if not api_works:
            print("ℹ️  Using fallback data (no API key configured)")
    else:
        print("❌ Live jobs functionality has issues")
