#!/usr/bin/env python3
"""
Test OpenAI Interview Integration
"""

import os
from interview_openai import initialize_openai_generator, generate_enhanced_interview_questions, openai_interview_generator

def test_openai_interview():
    """Test the OpenAI interview system"""
    
    # API key from environment variable
    api_key = os.getenv('OPENAI_API_KEY', 'your_openai_api_key_here')
    
    print("🧪 Testing OpenAI Interview Integration")
    print("=" * 50)
    
    # Test 1: Initialize OpenAI generator
    print("\n1. Initializing OpenAI generator...")
    try:
        success = initialize_openai_generator(api_key)
        if success:
            print("✅ OpenAI generator initialized successfully!")
        else:
            print("❌ Failed to initialize OpenAI generator")
            return False
    except Exception as e:
        print(f"❌ Error initializing OpenAI generator: {e}")
        return False
    
    # Test 2: Generate technical questions
    print("\n2. Generating technical interview questions...")
    try:
        skills = ['Python', 'React', 'Node.js', 'SQL']
        role_hint = 'fullstack developer'
        category = 'technical'
        
        questions = generate_enhanced_interview_questions(skills, role_hint, category, 3)
        
        if questions and len(questions) > 0:
            print(f"✅ Generated {len(questions)} questions successfully!")
            for i, q in enumerate(questions, 1):
                print(f"\nQuestion {i}:")
                print(f"Text: {q.get('text', 'N/A')}")
                print(f"Category: {q.get('category', 'N/A')}")
                print(f"Skills: {q.get('skills_tested', [])}")
        else:
            print("❌ No questions generated")
            return False
    except Exception as e:
        print(f"❌ Error generating questions: {e}")
        return False
    
    # Test 3: Evaluate an answer
    print("\n3. Testing answer evaluation...")
    try:
        if openai_interview_generator:
            question = "Explain how you would implement authentication in a React application."
            answer = "I would use JWT tokens stored in localStorage, implement login/logout functions, and create protected routes using React Router."
            skills = ['React', 'JavaScript', 'Authentication']
            role_hint = 'frontend developer'
            
            evaluation = openai_interview_generator.evaluate_answer(question, answer, skills, role_hint)
            
            if evaluation:
                print("✅ Answer evaluation successful!")
                print(f"Score: {evaluation.get('score', 'N/A')}")
                print(f"Strengths: {evaluation.get('strengths', [])}")
                print(f"Improvements: {evaluation.get('improvements', [])}")
            else:
                print("❌ Answer evaluation failed")
                return False
    except Exception as e:
        print(f"❌ Error evaluating answer: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! OpenAI interview integration is working correctly.")
    return True

if __name__ == "__main__":
    test_openai_interview()
