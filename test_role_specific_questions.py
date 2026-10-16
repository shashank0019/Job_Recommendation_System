#!/usr/bin/env python3
"""
Test Role-Specific Question Generation
"""

import requests
import json
import time

def test_role_specific_questions():
    """Test that questions are generated based on specific roles"""
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testing Role-Specific Question Generation")
    print("=" * 60)
    
    test_cases = [
        {
            'name': 'Fullstack Developer',
            'payload': {
                'skills': ['React', 'Node.js', 'JavaScript'],
                'role_hint': 'fullstack developer',
                'num_questions': 3
            },
            'expected_keywords': ['fullstack', 'frontend', 'backend', 'architecture', 'authentication']
        },
        {
            'name': 'Data Scientist',
            'payload': {
                'skills': ['Python', 'Machine Learning', 'Pandas'],
                'role_hint': 'data scientist',
                'num_questions': 3
            },
            'expected_keywords': ['machine learning', 'data', 'model', 'classification', 'validation']
        },
        {
            'name': 'Software Engineer',
            'payload': {
                'skills': ['Python', 'Java'],
                'role_hint': 'software engineer',
                'num_questions': 3
            },
            'expected_keywords': ['caching', 'debugging', 'production', 'system', 'performance']
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📋 Testing: {test_case['name']}")
        print("-" * 40)
        
        try:
            response = requests.post(
                f"{base_url}/interview/questions",
                json=test_case['payload'],
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    questions = data.get('questions', [])
                    print(f"✅ Generated {len(questions)} questions")
                    
                    # Check if questions are role-specific
                    role_specific_count = 0
                    
                    for i, q in enumerate(questions, 1):
                        question_text = q.get('text', '').lower()
                        print(f"\nQ{i}: {q.get('text', 'N/A')}")
                        print(f"    Skills Tested: {q.get('skills_tested', [])}")
                        print(f"    Difficulty: {q.get('difficulty', 'N/A')}")
                        
                        # Check if question contains role-specific keywords
                        keyword_matches = []
                        for keyword in test_case['expected_keywords']:
                            if keyword.lower() in question_text:
                                keyword_matches.append(keyword)
                        
                        if keyword_matches:
                            role_specific_count += 1
                            print(f"    ✅ Role-specific keywords found: {keyword_matches}")
                        else:
                            print(f"    ⚠️ Generic question (no role-specific keywords)")
                    
                    # Evaluate role-specificity
                    specificity_ratio = role_specific_count / len(questions)
                    if specificity_ratio >= 0.6:
                        print(f"\n🎯 EXCELLENT: {role_specific_count}/{len(questions)} questions are role-specific ({specificity_ratio:.1%})")
                    elif specificity_ratio >= 0.3:
                        print(f"\n👍 GOOD: {role_specific_count}/{len(questions)} questions are role-specific ({specificity_ratio:.1%})")
                    else:
                        print(f"\n⚠️ NEEDS IMPROVEMENT: Only {role_specific_count}/{len(questions)} questions are role-specific ({specificity_ratio:.1%})")
                        
                else:
                    print(f"❌ API Error: {data.get('error', 'Unknown')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "=" * 60)
    print("🎉 Role-Specific Question Test Completed!")
    print("\n💡 Tips for improvement:")
    print("• Questions should mention specific technologies and scenarios")
    print("• Role-specific challenges and responsibilities should be addressed")
    print("• Technical depth should match the role requirements")
    print("• Questions should test both breadth and depth of knowledge")

if __name__ == "__main__":
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    test_role_specific_questions()
