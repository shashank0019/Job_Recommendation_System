#!/usr/bin/env python3
"""
Direct test of enhanced fallback system
"""

from enhanced_interview_fallback import get_enhanced_questions

def test_direct():
    """Test the enhanced fallback directly"""
    print("🧪 Testing Enhanced Fallback Directly")
    print("=" * 50)
    
    # Test fullstack developer questions
    skills = ['React', 'Node.js', 'JavaScript']
    role_hint = 'fullstack developer'
    category = 'technical'
    num_questions = 3
    
    print(f"Input:")
    print(f"  Skills: {skills}")
    print(f"  Role: {role_hint}")
    print(f"  Category: {category}")
    print(f"  Number: {num_questions}")
    
    try:
        questions = get_enhanced_questions(skills, role_hint, category, num_questions)
        
        print(f"\nOutput:")
        print(f"  Generated: {len(questions)} questions")
        
        for i, q in enumerate(questions, 1):
            print(f"\nQ{i}:")
            print(f"  Text: {q.get('text', 'N/A')}")
            print(f"  Skills: {q.get('skills_tested', [])}")
            print(f"  Difficulty: {q.get('difficulty', 'N/A')}")
            print(f"  Category: {q.get('category', 'N/A')}")
            
            # Check if question is role-specific
            text_lower = q.get('text', '').lower()
            if any(keyword in text_lower for keyword in ['fullstack', 'full-stack', 'frontend', 'backend', 'architecture', 'authentication']):
                print(f"  ✅ Role-specific question detected")
            else:
                print(f"  ⚠️ Generic question")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct()
