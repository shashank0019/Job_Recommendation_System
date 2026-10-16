"""
Simple signin test - Just test signin with valid credentials
"""
import requests
import json

# Test credentials that we know work
credentials = {
    "email": "shashikingmaker495@gmail.com",
    "password": "password123"
}

print("🔑 Testing signin with verified credentials...")
print(f"📧 Email: {credentials['email']}")

try:
    # Make signin request
    response = requests.post(
        'http://localhost:5000/auth/signin',
        json=credentials,
        headers={'Content-Type': 'application/json'},
        timeout=10
    )
    
    print(f"📊 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SIGNIN SUCCESSFUL!")
        data = response.json()
        print(f"👤 User: {data.get('user', {}).get('name', 'Unknown')}")
        print(f"📧 Email: {data.get('user', {}).get('email', 'Unknown')}")
    else:
        print(f"❌ SIGNIN FAILED: Status {response.status_code}")
        print(f"Error: {response.text}")

except requests.exceptions.ConnectionError:
    print("❌ CONNECTION ERROR: Server is not running on port 5000")
except requests.exceptions.Timeout:
    print("❌ TIMEOUT ERROR: Request took too long")
except Exception as e:
    print(f"❌ UNEXPECTED ERROR: {e}")