#!/usr/bin/env python3
"""
Simple test for role-specific questions
"""

import requests
import json

def test_questions():
    """Simple test for question generation"""
    url = "http://127.0.0.1:5000/interview/questions"
    
    # Test fullstack developer questions
    payload = {
        'skills': ['React', 'Node.js', 'JavaScript'],
        'role_hint': 'fullstack developer',
        'num_questions': 2
    }
    
    print("Testing fullstack developer questions...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            
            if data.get('success'):
                questions = data.get('questions', [])
                print(f"Number of questions: {len(questions)}")
                
                for i, q in enumerate(questions, 1):
                    print(f"\nQuestion {i}:")
                    print(f"  Text: {q.get('text', 'N/A')}")
                    print(f"  Skills: {q.get('skills_tested', [])}")
                    print(f"  Difficulty: {q.get('difficulty', 'N/A')}")
            else:
                print(f"Error: {data.get('error', 'Unknown')}")
        else:
            print(f"HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_questions()
