#!/usr/bin/env python3
"""
Enhanced Interview Question Generation using OpenAI API
"""

import os
import json
import random
from typing import List, Dict, Any, Optional
import openai
from openai import OpenAI

class OpenAIInterviewGenerator:
    def __init__(self, api_key: str = None):
        """Initialize OpenAI Interview Generator"""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Question templates for different categories
        self.question_templates = {
            'technical': [
                "Explain how you would implement {skill} in a production environment. What are the key considerations?",
                "Describe a challenging problem you solved using {skill}. What was your approach?",
                "How would you optimize performance when working with {skill}? Give specific examples.",
                "What are the common pitfalls when using {skill} and how do you avoid them?",
                "Compare {skill} with alternative technologies. When would you choose each?"
            ],
            'behavioral': [
                "Tell me about a time when you had to learn {skill} quickly for a project. How did you approach it?",
                "Describe a situation where you had to collaborate with others on a {skill} project. What challenges did you face?",
                "How do you stay updated with the latest developments in {skill}?",
                "Tell me about a time when you had to debug a complex issue related to {skill}.",
                "Describe how you would mentor a junior developer in {skill}."
            ],
            'system_design': [
                "How would you design a scalable system using {skill}? Walk me through your architecture.",
                "Explain how you would handle high traffic loads in a {skill} application.",
                "Describe the security considerations when implementing {skill} in a production system.",
                "How would you monitor and maintain a {skill} based system?",
                "What database design would you use for a {skill} application and why?"
            ],
            'problem_solving': [
                "Given a performance bottleneck in a {skill} application, how would you identify and resolve it?",
                "How would you approach migrating a legacy system to {skill}?",
                "Describe how you would implement error handling and logging in a {skill} project.",
                "How would you ensure code quality and maintainability in a {skill} codebase?",
                "What testing strategies would you use for a {skill} application?"
            ]
        }

    def generate_questions_with_openai(self, skills: List[str], role_hint: str, category: str, num_questions: int = 6) -> List[Dict[str, Any]]:
        """Generate interview questions using OpenAI API"""
        try:
            # Create a comprehensive prompt
            skills_text = ", ".join(skills) if skills else "general software development"
            
            prompt = f"""
            Generate {num_questions} professional interview questions for a {role_hint} position.
            
            Requirements:
            - Focus on these skills/technologies: {skills_text}
            - Category: {category}
            - Questions should be practical and scenario-based
            - Include a mix of technical depth and real-world application
            - Each question should be answerable in 60-90 seconds
            - Avoid yes/no questions
            - Make questions specific to the role and skills mentioned
            
            Format the response as a JSON array with this structure:
            [
                {{
                    "id": 1,
                    "text": "Question text here",
                    "category": "{category}",
                    "difficulty": "medium",
                    "time_limit_sec": 90,
                    "skills_tested": ["skill1", "skill2"],
                    "evaluation_criteria": ["criteria1", "criteria2"]
                }}
            ]
            
            Make the questions challenging but fair, focusing on practical experience and problem-solving skills.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert technical interviewer with experience in software engineering, data science, and various technology stacks. Generate high-quality, practical interview questions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            # Parse the response
            content = response.choices[0].message.content.strip()
            
            # Try to extract JSON from the response
            try:
                # Remove any markdown formatting
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                
                questions = json.loads(content)
                
                # Validate and clean the questions
                validated_questions = []
                for i, q in enumerate(questions):
                    if isinstance(q, dict) and 'text' in q:
                        validated_q = {
                            'id': q.get('id', i + 1),
                            'text': q['text'],
                            'category': q.get('category', category),
                            'difficulty': q.get('difficulty', 'medium'),
                            'time_limit_sec': q.get('time_limit_sec', 90),
                            'skills_tested': q.get('skills_tested', skills[:2]),
                            'evaluation_criteria': q.get('evaluation_criteria', ['technical_accuracy', 'communication'])
                        }
                        validated_questions.append(validated_q)
                
                return validated_questions[:num_questions]
                
            except json.JSONDecodeError:
                # Fallback: extract questions from text
                return self._extract_questions_from_text(content, category, num_questions)
                
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._generate_fallback_questions(skills, role_hint, category, num_questions)

    def _extract_questions_from_text(self, text: str, category: str, num_questions: int) -> List[Dict[str, Any]]:
        """Extract questions from plain text response"""
        lines = text.split('\n')
        questions = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line and ('?' in line or 'describe' in line.lower() or 'explain' in line.lower()):
                # Clean up the line
                line = line.lstrip('0123456789.- ')
                if len(line) > 20:  # Reasonable question length
                    questions.append({
                        'id': len(questions) + 1,
                        'text': line,
                        'category': category,
                        'difficulty': 'medium',
                        'time_limit_sec': 90,
                        'skills_tested': [],
                        'evaluation_criteria': ['technical_accuracy', 'communication']
                    })
                    
                    if len(questions) >= num_questions:
                        break
        
        return questions

    def _generate_fallback_questions(self, skills: List[str], role_hint: str, category: str, num_questions: int) -> List[Dict[str, Any]]:
        """Generate fallback questions when OpenAI API fails"""
        templates = self.question_templates.get(category, self.question_templates['technical'])
        questions = []
        
        # Use skills to generate questions
        available_skills = skills if skills else ['Python', 'JavaScript', 'SQL', 'React', 'Node.js']
        
        for i in range(num_questions):
            skill = available_skills[i % len(available_skills)]
            template = templates[i % len(templates)]
            
            questions.append({
                'id': i + 1,
                'text': template.format(skill=skill),
                'category': category,
                'difficulty': 'medium',
                'time_limit_sec': 90,
                'skills_tested': [skill],
                'evaluation_criteria': ['technical_accuracy', 'communication', 'problem_solving']
            })
        
        return questions

    def generate_adaptive_questions(self, skills: List[str], role_hint: str, previous_answers: List[str] = None, num_questions: int = 6) -> List[Dict[str, Any]]:
        """Generate adaptive questions based on previous answers"""
        if not previous_answers:
            # First round - mix of categories
            categories = ['technical', 'behavioral', 'problem_solving']
            questions = []
            
            for i, category in enumerate(categories):
                q_count = num_questions // len(categories)
                if i == len(categories) - 1:  # Last category gets remaining questions
                    q_count = num_questions - len(questions)
                
                cat_questions = self.generate_questions_with_openai(skills, role_hint, category, q_count)
                questions.extend(cat_questions)
            
            return questions
        else:
            # Adaptive round - analyze previous answers and generate follow-ups
            return self._generate_followup_questions(skills, role_hint, previous_answers, num_questions)

    def _generate_followup_questions(self, skills: List[str], role_hint: str, previous_answers: List[str], num_questions: int) -> List[Dict[str, Any]]:
        """Generate follow-up questions based on previous answers"""
        try:
            answers_summary = "\n".join([f"Answer {i+1}: {ans[:200]}..." for i, ans in enumerate(previous_answers)])
            
            prompt = f"""
            Based on the candidate's previous answers for a {role_hint} position, generate {num_questions} follow-up interview questions.
            
            Previous answers summary:
            {answers_summary}
            
            Skills being evaluated: {", ".join(skills)}
            
            Generate questions that:
            - Dive deeper into areas where the candidate showed strength
            - Explore gaps or areas that need clarification
            - Test practical application of concepts mentioned
            - Are progressively more challenging
            
            Format as JSON array with the same structure as before.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert interviewer conducting a follow-up round. Generate insightful questions based on previous responses."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.6
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            questions = json.loads(content)
            return questions[:num_questions]
            
        except Exception as e:
            print(f"Follow-up question generation error: {e}")
            return self._generate_fallback_questions(skills, role_hint, 'technical', num_questions)

    def evaluate_answer(self, question: str, answer: str, skills: List[str], role_hint: str) -> Dict[str, Any]:
        """Evaluate an interview answer using OpenAI"""
        try:
            prompt = f"""
            Evaluate this interview answer for a {role_hint} position:
            
            Question: {question}
            Answer: {answer}
            Expected skills: {", ".join(skills)}
            
            Provide evaluation in this JSON format:
            {{
                "score": 85,
                "strengths": ["strength1", "strength2"],
                "improvements": ["improvement1", "improvement2"],
                "technical_accuracy": 80,
                "communication": 90,
                "problem_solving": 85,
                "overall_feedback": "Detailed feedback here",
                "follow_up_suggestions": ["suggestion1", "suggestion2"]
            }}
            
            Score should be 0-100. Be constructive but honest in feedback.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert technical interviewer providing detailed, constructive feedback on interview answers."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            evaluation = json.loads(content)
            return evaluation
            
        except Exception as e:
            print(f"Answer evaluation error: {e}")
            return {
                "score": 70,
                "strengths": ["Provided a response"],
                "improvements": ["Could provide more specific examples"],
                "technical_accuracy": 70,
                "communication": 70,
                "problem_solving": 70,
                "overall_feedback": "Answer received but detailed evaluation unavailable.",
                "follow_up_suggestions": ["Practice explaining technical concepts clearly"]
            }

# Global instance
openai_interview_generator = None

def initialize_openai_generator(api_key: str):
    """Initialize the global OpenAI interview generator"""
    global openai_interview_generator
    try:
        openai_interview_generator = OpenAIInterviewGenerator(api_key)
        return True
    except Exception as e:
        print(f"Failed to initialize OpenAI generator: {e}")
        return False

def generate_enhanced_interview_questions(skills: List[str], role_hint: str = "", category: str = "technical", num_questions: int = 6) -> List[Dict[str, Any]]:
    """Generate enhanced interview questions using OpenAI or fallback"""
    global openai_interview_generator
    
    if openai_interview_generator:
        try:
            return openai_interview_generator.generate_questions_with_openai(skills, role_hint, category, num_questions)
        except Exception as e:
            print(f"OpenAI generation failed, using fallback: {e}")
    
    # Fallback to template-based generation
    return openai_interview_generator._generate_fallback_questions(skills, role_hint, category, num_questions) if openai_interview_generator else []
