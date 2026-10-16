#!/usr/bin/env python3
"""
Debug the live jobs function directly
"""

def debug_fetch_live_jobs():
    """Debug the fetch_live_jobs function step by step"""
    print("🔍 Debugging fetch_live_jobs function...")
    
    # Import the function
    try:
        from clean_cors_server import fetch_live_jobs, api_client
        print("✅ Successfully imported fetch_live_jobs and api_client")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return
    
    # Check api_client status
    print(f"API Client: {api_client}")
    if api_client:
        try:
            status = api_client.get_api_status()
            print(f"API Status: {status}")
        except Exception as e:
            print(f"API Status Error: {e}")
    
    # Test with sample skills
    test_skills = ["python", "react", "javascript"]
    print(f"\nTesting with skills: {test_skills}")
    
    try:
        live_jobs = fetch_live_jobs(test_skills, max_jobs=3)
        print(f"✅ Function returned {len(live_jobs)} jobs")
        
        if live_jobs:
            print("\n📋 Jobs returned:")
            for i, job in enumerate(live_jobs, 1):
                print(f"{i}. Title: {job.get('title', 'N/A')}")
                print(f"   Company: {job.get('company', 'N/A')}")
                print(f"   Location: {job.get('location', 'N/A')}")
                print(f"   Skills: {job.get('skills', 'N/A')}")
                print(f"   Source: {job.get('source', 'N/A')}")
                print(f"   All keys: {list(job.keys())}")
                print()
        else:
            print("❌ No jobs returned")
            
    except Exception as e:
        print(f"❌ Error calling fetch_live_jobs: {e}")
        import traceback
        traceback.print_exc()

def test_server_response():
    """Test what the server actually returns"""
    print("\n🔍 Testing server response format...")
    
    # Simulate what the server does
    try:
        from clean_cors_server import extract_skills, fetch_live_jobs, find_matching_jobs
        
        resume_text = "Software Engineer with 5 years experience in React, Python, and AWS"
        
        # Extract skills
        skills = extract_skills(resume_text)
        print(f"Extracted skills: {skills}")
        
        # Get live jobs
        live_jobs = fetch_live_jobs(skills, max_jobs=5)
        print(f"Live jobs count: {len(live_jobs)}")
        
        # Get matching jobs
        matching_jobs = find_matching_jobs(skills, max_jobs=5)
        print(f"Matching jobs count: {len(matching_jobs)}")
        
        # Simulate response
        response = {
            'success': True,
            'jobs': matching_jobs,
            'live_jobs': live_jobs,
            'parsed': {
                'skills': skills,
                'years_experience': 5
            }
        }
        
        print(f"\nResponse structure:")
        print(f"- success: {response['success']}")
        print(f"- jobs: {len(response['jobs'])} items")
        print(f"- live_jobs: {len(response['live_jobs'])} items")
        print(f"- parsed.skills: {response['parsed']['skills']}")
        
        if response['live_jobs']:
            print(f"\nFirst live job:")
            first_job = response['live_jobs'][0]
            for key, value in first_job.items():
                print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"❌ Error in server simulation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Live Jobs Debug")
    print("=" * 40)
    
    debug_fetch_live_jobs()
    test_server_response()
    
    print("\n" + "=" * 40)
    print("✅ Debug completed!")
