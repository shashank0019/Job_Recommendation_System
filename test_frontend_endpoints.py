#!/usr/bin/env python3
"""
Test all endpoints that the frontend will use after restart
"""
import requests
import json

API_BASE = "http://localhost:5001"

def test_all_frontend_endpoints():
    """Test all endpoints that frontend components use"""
    print("🧪 Testing all frontend endpoints on port 5001...")
    
    endpoints_to_test = [
        # Authentication endpoints
        {"method": "GET", "url": "/health", "auth": False, "description": "Health check"},
        
        # Job posting endpoints
        {"method": "GET", "url": "/api/jobs", "auth": False, "description": "Get job postings"},
        {"method": "POST", "url": "/api/jobs", "auth": True, "description": "Create job posting"},
        
        # Interview experience endpoints
        {"method": "GET", "url": "/api/experiences", "auth": False, "description": "Get interview experiences"},
        {"method": "POST", "url": "/api/experiences", "auth": True, "description": "Create interview experience"},
        
        # Authentication endpoints
        {"method": "POST", "url": "/auth/signup", "auth": False, "description": "User signup"},
        {"method": "POST", "url": "/auth/signin", "auth": False, "description": "User signin"},
    ]
    
    results = []
    
    for endpoint in endpoints_to_test:
        print(f"\n📡 Testing {endpoint['method']} {endpoint['url']} - {endpoint['description']}")
        
        try:
            url = f"{API_BASE}{endpoint['url']}"
            
            if endpoint['method'] == 'GET':
                response = requests.get(url)
            elif endpoint['method'] == 'POST':
                if endpoint['auth']:
                    # Test without auth (should fail)
                    response = requests.post(url, json={})
                else:
                    # Test with minimal valid data
                    if 'signup' in endpoint['url']:
                        test_data = {"name": "Test", "email": "test@test.com", "password": "Test123456"}
                    elif 'signin' in endpoint['url']:
                        test_data = {"email": "test@test.com", "password": "Test123456"}
                    else:
                        test_data = {}
                    response = requests.post(url, json=test_data)
            
            status = response.status_code
            
            if endpoint['auth'] and endpoint['method'] == 'POST':
                expected_status = 401  # Should require auth
                success = status == expected_status
                result_msg = f"✅ Correctly requires auth (401)" if success else f"❌ Expected 401, got {status}"
            elif 'signup' in endpoint['url']:
                expected_status = [201, 409]  # Created or already exists
                success = status in expected_status
                result_msg = f"✅ Signup working ({status})" if success else f"❌ Unexpected status {status}"
            elif 'signin' in endpoint['url']:
                expected_status = [200, 401]  # Success or invalid credentials
                success = status in expected_status
                result_msg = f"✅ Signin endpoint working ({status})" if success else f"❌ Unexpected status {status}"
            else:
                expected_status = 200
                success = status == expected_status
                result_msg = f"✅ Working ({status})" if success else f"❌ Failed ({status})"
            
            print(f"   Status: {status} - {result_msg}")
            
            results.append({
                "endpoint": f"{endpoint['method']} {endpoint['url']}",
                "status": status,
                "success": success,
                "description": endpoint['description']
            })
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                "endpoint": f"{endpoint['method']} {endpoint['url']}",
                "status": "ERROR",
                "success": False,
                "description": endpoint['description']
            })
    
    return results

def print_summary(results):
    """Print test summary"""
    print("\n" + "=" * 60)
    print("📊 ENDPOINT TEST SUMMARY")
    print("=" * 60)
    
    total = len(results)
    successful = sum(1 for r in results if r['success'])
    
    print(f"Total endpoints tested: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    
    print("\n📋 Detailed Results:")
    for result in results:
        status_icon = "✅" if result['success'] else "❌"
        print(f"{status_icon} {result['endpoint']} - {result['description']} ({result['status']})")
    
    print("\n🎯 Frontend Status:")
    if successful == total:
        print("✅ All endpoints working - Frontend will work correctly after restart!")
    else:
        print("⚠️ Some endpoints have issues - Check server logs")
    
    print(f"\n🔧 Instructions:")
    print(f"1. Restart the frontend development server:")
    print(f"   cd frontend")
    print(f"   npm run dev")
    print(f"2. Frontend will now use: {API_BASE}")
    print(f"3. Test job posting and interview experience features")

if __name__ == "__main__":
    print("🚀 Testing All Frontend Endpoints")
    print("=" * 60)
    
    results = test_all_frontend_endpoints()
    print_summary(results)
