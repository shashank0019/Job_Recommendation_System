#!/usr/bin/env python3
"""Simple file upload test to debug field name issue"""

import requests

def test_simple_upload():
    """Test with a simple string file"""
    
    # Create simple text data 
    test_content = "John Doe - Python Developer with React and Node.js skills"
    
    try:
        print("🧪 Testing simple file upload...")
        
        # Try with the exact same method as frontend
        files = {'resume_file': ('resume.txt', test_content, 'text/plain')}
        
        print("📤 Sending POST request to /upload...")
        response = requests.post(
            'http://localhost:5000/upload',
            files=files,
            timeout=10
        )
        
        print(f"🔍 Response status: {response.status_code}")
        print(f"📄 Response text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('success')}")
            recommendations = data.get('recommendations', [])
            print(f"📊 Recommendations: {len(recommendations)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_simple_upload()