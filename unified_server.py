#!/usr/bin/env python3
"""
Unified Server for Both Jobs and Interview Functionality
Handles all endpoints needed by the React frontend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

# Enhanced interview system
try:
    from enhanced_interview_fallback import get_enhanced_questions, get_enhanced_evaluation
    ENHANCED_FALLBACK_AVAILABLE = True
    print("✅ Enhanced fallback system loaded successfully")
except Exception as e:
    ENHANCED_FALLBACK_AVAILABLE = False
    print(f"⚠️ Enhanced fallback system failed to load: {e}")

app = Flask(__name__)

# Enable CORS for all origins including React dev server
CORS(app, 
     origins=["http://localhost:5173", "http://127.0.0.1:5173", 
              "http://localhost:5174", "http://127.0.0.1:5174", 
              "http://localhost:3000", "http://127.0.0.1:3000"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"])

# ==================== JOB POSTING FUNCTIONALITY ====================

JOBS_FILE = 'data/posted_jobs.json'

def load_jobs_from_file():
    """Load jobs from JSON file"""
    try:
        if os.path.exists(JOBS_FILE):
            with open(JOBS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading jobs: {e}")
        return []

def save_jobs_to_file(jobs):
    """Save jobs to JSON file"""
    try:
        os.makedirs(os.path.dirname(JOBS_FILE), exist_ok=True)
        with open(JOBS_FILE, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving jobs: {e}")
        return False

JOBS = load_jobs_from_file()

@app.route('/')
def index():
    """Health check"""
    return jsonify({
        'status': 'OK',
        'message': 'Unified Career Platform Server',
        'server_time': datetime.utcnow().isoformat(),
        'total_jobs': len(JOBS),
        'endpoints': {
            'jobs': 'GET/POST /api/jobs',
            'experiences': 'GET/POST /api/experiences',
            'interview_questions': 'POST /api/interview/questions',
            'interview_submit': 'POST /api/interview/submit'
        }
    })

@app.route('/api/jobs', methods=['GET', 'POST', 'OPTIONS'])
def api_jobs():
    """Handle job API requests"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
    
    if request.method == 'GET':
        return jsonify({'jobs': JOBS})
    
    elif request.method == 'POST':
        try:
            job_data = request.get_json()
            if not job_data:
                return jsonify({'error': 'No job data provided'}), 400
            
            # Add ID and timestamp
            new_job = {
                'id': len(JOBS) + 1,
                'created_at': datetime.utcnow().isoformat(),
                **job_data
            }
            
            JOBS.append(new_job)
            save_jobs_to_file(JOBS)
            
            return jsonify({'message': 'Job posted successfully', 'job': new_job})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# ==================== INTERVIEW EXPERIENCE FUNCTIONALITY ====================

EXPERIENCES_FILE = 'data/interview_experiences.json'

def load_experiences_from_file():
    """Load experiences from interview_experiences.json"""
    try:
        if os.path.exists(EXPERIENCES_FILE):
            with open(EXPERIENCES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading experiences: {e}")
        return []

def save_experiences_to_file(experiences):
    """Save experiences to interview_experiences.json"""
    try:
        os.makedirs(os.path.dirname(EXPERIENCES_FILE), exist_ok=True)
        with open(EXPERIENCES_FILE, 'w', encoding='utf-8') as f:
            json.dump(experiences, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving experiences: {e}")
        return False

@app.route('/api/experiences', methods=['GET', 'POST', 'OPTIONS'])
def api_experiences():
    """Handle interview experiences"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
    
    if request.method == 'GET':
        experiences = load_experiences_from_file()
        return jsonify({'experiences': experiences})
    
    elif request.method == 'POST':
        try:
            experience_data = request.get_json()
            if not experience_data:
                return jsonify({'error': 'No experience data provided'}), 400
            
            experiences = load_experiences_from_file()
            
            # Add ID and timestamp
            new_experience = {
                'id': len(experiences) + 1,
                'created_at': datetime.utcnow().isoformat(),
                **experience_data
            }
            
            experiences.append(new_experience)
            save_experiences_to_file(experiences)
            
            return jsonify({'message': 'Experience shared successfully', 'experience': new_experience})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# ==================== VIRTUAL INTERVIEW FUNCTIONALITY ====================

def generate_interview_questions(skills, role_hint="", category="technical", num_questions=6):
    """Generate interview questions using enhanced system"""
    
    # Try enhanced fallback system first
    if ENHANCED_FALLBACK_AVAILABLE and get_enhanced_questions:
        try:
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
            'category': category,
            'difficulty': 'medium',
            'time_limit_sec': 90,
            'skills_tested': [skill] if skills else [],
            'evaluation_criteria': ['technical_accuracy', 'communication']
        })
    
    return basic_questions

@app.route('/api/interview/questions', methods=['POST', 'OPTIONS'])
@app.route('/interview/questions', methods=['POST', 'OPTIONS'])
def interview_questions():
    """Generate interview questions"""
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
        
        # Determine category based on role hint
        category = "technical"  # Default to technical
        role_lower = role_hint.lower() if role_hint else ""
        if "behavioral" in role_lower:
            category = "behavioral"
        elif "hr" in role_lower or "personality" in role_lower:
            category = "behavioral"
        elif "communication" in role_lower:
            category = "behavioral"
        elif "case" in role_lower or "situational" in role_lower:
            category = "system_design"
        elif "system" in role_lower or "design" in role_lower:
            category = "system_design"
        
        qs = generate_interview_questions(skills, role_hint, category, num_questions)
        
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
    """Submit interview answers for evaluation"""
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
    """System health check"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
    
    return jsonify({
        'status': 'healthy',
        'enhanced_fallback': ENHANCED_FALLBACK_AVAILABLE,
        'jobs_count': len(JOBS),
        'server_type': 'unified_career_platform'
    })

@app.route('/test', methods=['GET'])
def test_route():
    """Test endpoint"""
    return jsonify({
        'message': 'Unified server test successful',
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Starting Unified Career Platform Server...")
    print("=" * 60)
    
    # Load initial data
    print(f"📊 Loaded {len(JOBS)} existing jobs")
    experiences = load_experiences_from_file()
    print(f"📋 Loaded {len(experiences)} interview experiences")
    
    if ENHANCED_FALLBACK_AVAILABLE:
        print("✅ Enhanced interview system ready!")
    else:
        print("⚠️ Using basic interview system")
    
    print("🌐 Server running on: http://127.0.0.1:5000")
    print("📋 Available endpoints:")
    print("   GET  / - Health check")
    print("   GET/POST /api/jobs - Job listings")
    print("   GET/POST /api/experiences - Interview experiences")
    print("   POST /api/interview/questions - Generate questions")
    print("   POST /api/interview/submit - Submit answers")
    print("   GET  /health - System status")
    print("   GET  /test - Test endpoint")
    print("=" * 60)
    
    app.run(host='127.0.0.1', port=5000, debug=True)