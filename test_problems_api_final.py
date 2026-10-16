import requests
import json

def test_problems_api():
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Problems API with 200 problems...")
    
    try:
        # Test GET all problems
        response = requests.get(f"{base_url}/api/problems", timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            print(f"✅ GET problems: {response.status_code}")
            print(f"   Total problems: {data.get('filtered_count', 0)}")
            print(f"   Available problems: {data.get('total', 0)}")
            
            if data.get('items'):
                print(f"   First problem: {data['items'][0]['title']}")
                print(f"   Last problem: {data['items'][-1]['title']}")
                
                # Check for duplicates
                titles = [p['title'] for p in data['items']]
                unique_titles = set(titles)
                if len(titles) == len(unique_titles):
                    print("   ✅ No duplicates found in API response!")
                else:
                    print(f"   ❌ Found {len(titles) - len(unique_titles)} duplicates in API response!")
            
        else:
            print(f"❌ GET problems failed: {response.status_code} - {data}")
            
    except Exception as e:
        print(f"❌ API test failed: {e}")

    # Test specific problem
    try:
        response = requests.get(f"{base_url}/api/problems/1", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GET problem by ID: {data['problem']['title']}")
        else:
            print(f"❌ GET problem by ID failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Problem by ID test failed: {e}")

if __name__ == "__main__":
    test_problems_api()
