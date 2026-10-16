import requests

try:
    # Test health endpoint
    response = requests.get("http://localhost:5000/health", timeout=5)
    print(f"Health: {response.status_code} - {response.text}")
except Exception as e:
    print(f"Health failed: {e}")

try:
    # Test jobs endpoint
    response = requests.get("http://localhost:5000/api/jobs", timeout=5)
    print(f"Jobs: {response.status_code} - {response.text[:200]}")
except Exception as e:
    print(f"Jobs failed: {e}")
