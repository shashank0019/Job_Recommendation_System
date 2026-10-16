"""
Test the problems endpoint to debug CORS issues
"""
import requests

def test_problems_endpoint():
    """Test the problems endpoint"""
    print("🧪 Testing Problems Endpoint")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Test 1: OPTIONS request (preflight)
    print("\n1️⃣ Testing OPTIONS request (preflight)...")
    try:
        response = requests.options(f"{base_url}/api/problems", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ OPTIONS request successful")
        else:
            print(f"❌ OPTIONS request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ OPTIONS request error: {e}")
    
    # Test 2: GET request
    print("\n2️⃣ Testing GET request...")
    try:
        response = requests.get(f"{base_url}/api/problems?limit=10", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GET request successful")
            print(f"📊 Problems returned: {data.get('total', 0)}")
            print(f"📋 Sample problem: {data.get('items', [{}])[0].get('title', 'N/A')}")
        else:
            print(f"❌ GET request failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ GET request error: {e}")
    
    # Test 3: Simulate browser preflight + GET
    print("\n3️⃣ Testing browser-like CORS request...")
    try:
        # First, send preflight request
        preflight_headers = {
            'Origin': 'http://localhost:5174',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'content-type'
        }
        
        preflight_response = requests.options(f"{base_url}/api/problems", 
                                            headers=preflight_headers, 
                                            timeout=5)
        
        print(f"Preflight Status: {preflight_response.status_code}")
        print(f"Preflight Headers: {dict(preflight_response.headers)}")
        
        if preflight_response.status_code == 200:
            # Now send the actual GET request
            get_headers = {
                'Origin': 'http://localhost:5174',
                'Content-Type': 'application/json'
            }
            
            get_response = requests.get(f"{base_url}/api/problems?limit=5", 
                                      headers=get_headers, 
                                      timeout=5)
            
            print(f"GET Status: {get_response.status_code}")
            print(f"GET Headers: {dict(get_response.headers)}")
            
            if get_response.status_code == 200:
                print("✅ Browser-like CORS request successful!")
                data = get_response.json()
                print(f"📊 Problems: {data.get('total', 0)}")
            else:
                print(f"❌ GET after preflight failed: {get_response.status_code}")
        else:
            print(f"❌ Preflight failed: {preflight_response.status_code}")
            
    except Exception as e:
        print(f"❌ Browser-like CORS test error: {e}")
    
    print(f"\n🎯 Problems Endpoint Summary:")
    print(f"   - Endpoint: {base_url}/api/problems")
    print(f"   - CORS should be configured for localhost:5174")
    print(f"   - OPTIONS and GET methods should work")

if __name__ == "__main__":
    test_problems_endpoint()
