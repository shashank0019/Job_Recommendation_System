import requests
import json

def test_recommend():
    try:
        url = "http://localhost:5000/recommend"
        payload = {"resume_text": "Python developer with 3 years experience"}
        
        print("Testing recommend endpoint...")
        response = requests.post(url, json=payload, timeout=5)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            jobs = data.get('jobs', [])
            print(f"Jobs found: {len(jobs)}")
            if jobs:
                print(f"First job title: {jobs[0].get('title', 'Unknown')}")
                print(f"First job company: {jobs[0].get('company', 'Unknown')}")
        else:
            print(f"Error response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Connection refused - server not running")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_recommend()