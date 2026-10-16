#!/usr/bin/env python3
"""
Interview-Only Server for Testing Enhanced Question Generation
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# Enhanced interview system with OpenAI
try:
    from interview_openai import initialize_openai_generator, generate_enhanced_interview_questions, openai_interview_generator
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False
    initialize_openai_generator = None
    generate_enhanced_interview_questions = None
    openai_interview_generator = None

# Enhanced fallback interview system
try:
    from enhanced_interview_fallback import get_enhanced_questions, get_enhanced_evaluation
    ENHANCED_FALLBACK_AVAILABLE = True
    print("✅ Enhanced fallback system loaded successfully")
except Exception as e:
    ENHANCED_FALLBACK_AVAILABLE = False
    get_enhanced_questions = None
    get_enhanced_evaluation = None
    print(f"⚠️ Enhanced fallback system failed to load: {e}")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174", "http://localhost:3000", "http://127.0.0.1:3000"]}})

def generate_interview_questions(skills: list[str], role_hint: str = "", level_hint: str = "any", num_questions: int = 6) -> list[dict]:
    """Generate interview questions using enhanced systems."""
    
    # First try OpenAI for enhanced questions (temporarily disabled for testing)
    if False and OPENAI_AVAILABLE and openai_interview_generator:
        try:
            print(f"🤖 Generating questions with OpenAI for role: {role_hint}, skills: {skills}")
            
            # Determine category based on role hint
            category = "technical"  # Default to technical
            role_lower = role_hint.lower()
            if "behavioral" in role_lower:
                category = "behavioral"
            elif "hr" in role_lower or "personality" in role_lower:
                category = "behavioral"
            elif "communication" in role_lower:
                category = "behavioral"
            elif "case" in role_lower or "situational" in role_lower:
                category = "problem_solving"
            elif "system" in role_lower or "design" in role_lower:
                category = "system_design"
            
            print(f"🎯 Determined category: {category} for role: {role_hint}")
            
            openai_questions = generate_enhanced_interview_questions(skills, role_hint, category, num_questions)
            if openai_questions and len(openai_questions) > 0:
                print(f"✅ Generated {len(openai_questions)} questions using OpenAI")
                return openai_questions
            else:
                print("⚠️ OpenAI returned no questions, falling back to enhanced method")
        except Exception as e:
            print(f"⚠️ OpenAI question generation failed: {e}, falling back to enhanced method")
    
    # Try enhanced fallback system
    if ENHANCED_FALLBACK_AVAILABLE and get_enhanced_questions:
        try:
            # Determine category for fallback (same logic as OpenAI)
            category = "technical"  # Default to technical
            role_lower = role_hint.lower() if role_hint else ""
            if "behavioral" in role_lower:
                category = "behavioral"
            elif "hr" in role_lower or "personality" in role_lower:
                category = "behavioral"
            elif "communication" in role_lower:
                category = "behavioral"
            elif "case" in role_lower or "situational" in role_lower:
                category = "problem_solving"
            elif "system" in role_lower or "design" in role_lower:
                category = "system_design"
            
            print(f"🎯 Using enhanced fallback for role: {role_hint}, category: {category}, skills: {skills}")
            enhanced_questions = get_enhanced_questions(skills, role_hint, category, num_questions)
            if enhanced_questions and len(enhanced_questions) > 0:
                print(f"✅ Generated {len(enhanced_questions)} questions using enhanced fallback")
                return enhanced_questions
        except Exception as e:
            print(f"⚠️ Enhanced fallback failed: {e}, using basic fallback")
    
    # Basic fallback questions
    print(f"⚠️ Using basic fallback questions for role: {role_hint}")
    basic_questions = []
    for i in range(num_questions):
        skill = skills[i % len(skills)] if skills else "your technical skills"
        basic_questions.append({
            'id': i + 1,
            'text': f"Describe your experience with {skill} and how you've applied it in real projects.",
            'category': 'technical',
            'difficulty': 'medium',
            'time_limit_sec': 90,
            'skills_tested': [skill] if skills else [],
            'evaluation_criteria': ['technical_accuracy', 'communication']
        })
    
    return basic_questions

@app.route('/api/interview/questions', methods=['POST', 'OPTIONS'])
@app.route('/interview/questions', methods=['POST', 'OPTIONS'])
def interview_questions():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
    
    try:
        payload = request.get_json() or {}
        skills = payload.get('skills') or []
        role_hint = payload.get('role_hint') or ''
        level_hint = payload.get('level_hint') or 'any'
        num_questions = int(payload.get('num_questions') or 6)
        
        print(f"\n📝 Question Request:")
        print(f"   Role: {role_hint}")
        print(f"   Skills: {skills}")
        print(f"   Questions: {num_questions}")
        
        qs = generate_interview_questions(skills, role_hint, level_hint, num_questions)
        
        print(f"\n📋 Generated Questions:")
        for i, q in enumerate(qs, 1):
            print(f"   Q{i}: {q.get('text', 'N/A')[:80]}...")
        
        return jsonify({'success': True, 'questions': qs})
    except Exception as e:
        print(f"❌ Error in interview_questions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/interview/submit', methods=['POST', 'OPTIONS'])
@app.route('/interview/submit', methods=['POST', 'OPTIONS'])
def interview_submit():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
    
    try:
        payload = request.get_json() or {}
        qs = payload.get('questions') or []
        answers = payload.get('answers') or []
        skills = payload.get('skills') or []
        role_hint = payload.get('role_hint') or ''
        
        if not qs or not answers:
            return jsonify({'success': False, 'error': 'Missing questions or answers'}), 400
        
        # Use enhanced evaluation if available
        if ENHANCED_FALLBACK_AVAILABLE and get_enhanced_evaluation:
            try:
                print("🎯 Using enhanced fallback evaluation")
                per = []
                total = 0.0
                for q, a in zip(qs, answers):
                    fb = get_enhanced_evaluation(
                        question=q.get('text', ''),
                        answer=a or '',
                        skills=skills,
                        role_hint=role_hint
                    )
                    per.append({
                        'question_id': q.get('id'),
                        'score': fb.get('score', 70),
                        'strengths': fb.get('strengths', []),
                        'improvements': fb.get('improvements', []),
                        'technical_accuracy': fb.get('technical_accuracy', 70),
                        'communication': fb.get('communication', 70),
                        'problem_solving': fb.get('problem_solving', 70),
                        'overall_feedback': fb.get('overall_feedback', ''),
                        'follow_up_suggestions': fb.get('follow_up_suggestions', [])
                    })
                    total += float(fb.get('score', 70))
                
                total_norm = round((total / max(1, len(per))), 1)
                result = {'total_score': total_norm, 'per_answer': per, 'evaluation_method': 'Enhanced Fallback'}
            except Exception as e:
                print(f"⚠️ Enhanced evaluation failed: {e}")
                result = {'total_score': 75, 'per_answer': [], 'evaluation_method': 'Basic'}
        else:
            # Basic evaluation
            result = {'total_score': 75, 'per_answer': [], 'evaluation_method': 'Basic'}
        
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        print(f"❌ Error in interview_submit: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET', 'OPTIONS'])
def health():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
    return jsonify({
        'status': 'healthy',
        'enhanced_fallback': ENHANCED_FALLBACK_AVAILABLE,
        'openai_available': OPENAI_AVAILABLE
    })

if __name__ == '__main__':
    print("🚀 Starting Interview-Only Server...")
    print("=" * 50)
    
    # Initialize OpenAI if available
    if OPENAI_AVAILABLE:
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key and initialize_openai_generator:
            try:
                if initialize_openai_generator(openai_key):
                    print("✅ OpenAI interview generator initialized")
                else:
                    print("⚠️ Failed to initialize OpenAI interview generator")
            except Exception as e:
                print(f"⚠️ OpenAI initialization error: {e}")
    
    print("✅ Interview system ready!")
    print("🌐 Server running on: http://127.0.0.1:5000")
    print("📋 Available endpoints:")
    print("   POST /interview/questions - Generate questions")
    print("   POST /interview/submit - Submit answers")
    print("   GET  /health - System status")
    print("=" * 50)
    
    app.run(host='127.0.0.1', port=5000, debug=True)
