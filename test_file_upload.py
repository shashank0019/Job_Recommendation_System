#!/usr/bin/env python3
"""Test file upload functionality"""

import requests
import tempfile
import os

def test_file_upload():
    """Test uploading a resume file to the server"""
    
    # Create a temporary test resume file
    test_resume_content = """
    John Doe
    Software Developer
    
    Skills: Python, JavaScript, React, Node.js, SQL, Git
    Experience: 3 years in web development
    
    Previous roles:
    - Full Stack Developer at Tech Corp (2021-2024)
    - Junior Developer at StartupXYZ (2020-2021)
    
    Education: Computer Science Degree
    """
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
            tmp_file.write(test_resume_content)
            tmp_file_path = tmp_file.name
        
        print("🧪 Testing file upload endpoint...")
        print(f"📄 Created test resume file: {os.path.basename(tmp_file_path)}")
        
        # Upload file to server
        with open(tmp_file_path, 'rb') as file:
            files = {'resume_file': ('test_resume.txt', file, 'text/plain')}
            
            print(f"📤 Uploading file with field name: resume_file")
            print(f"📄 File size: {os.path.getsize(tmp_file_path)} bytes")
            
            response = requests.post(
                'http://localhost:5000/upload',
                files=files,
                timeout=15
            )
        
        print(f"🔍 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('success')}")
            
            if data.get('success'):
                print(f"📁 File saved as: {data.get('filename')}")
                
                # Check recommendations
                recommendations = data.get('recommendations', [])
                print(f"📊 Got {len(recommendations)} recommendations")
                
                if recommendations:
                    print("\n📋 Sample recommendations:")
                    for i, job in enumerate(recommendations[:3]):
                        print(f"  {i+1}. {job.get('title')} at {job.get('company')} ({job.get('match_percentage')}% match)")
                
                # Check skill analysis
                skill_gap = data.get('skill_gap_analysis', {})
                if skill_gap:
                    print(f"\n🎯 Skill Gap Analysis:")
                    user_skills = skill_gap.get('user_skills', [])
                    print(f"  - User skills detected: {len(user_skills)} ({', '.join(user_skills[:5])})")
                    print(f"  - Missing skills: {len(skill_gap.get('missing_skills', []))}")
                    print(f"  - Coverage: {skill_gap.get('coverage_percentage', 0)}%")
                
                parsed = data.get('parsed_resume', {})
                if parsed:
                    print(f"\n📄 Parsed Resume:")
                    print(f"  - Skills extracted: {len(parsed.get('skills', []))}")
                    print(f"  - Text length: {parsed.get('text_length', 0)} characters")
                
                print("\n🎉 File upload test PASSED!")
            else:
                print(f"❌ Upload failed: {data.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
        
        # Clean up
        os.unlink(tmp_file_path)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        # Clean up on error
        if 'tmp_file_path' in locals():
            try:
                os.unlink(tmp_file_path)
            except:
                pass

if __name__ == "__main__":
    test_file_upload()