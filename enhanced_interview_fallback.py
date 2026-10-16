#!/usr/bin/env python3
"""
Enhanced Interview Fallback System
Provides high-quality questions even without OpenAI API
"""

import random
import json
from typing import List, Dict, Any

class EnhancedInterviewFallback:
    def __init__(self):
        """Initialize enhanced fallback system"""
        self.question_database = self._build_question_database()
        self.evaluation_templates = self._build_evaluation_templates()

    def _build_question_database(self) -> Dict[str, Dict[str, List[Dict]]]:
        """Build comprehensive question database"""
        return {
            'technical': {
                'python': [
                    {
                        'text': 'Explain the difference between list comprehensions and generator expressions in Python. When would you use each?',
                        'difficulty': 'medium',
                        'skills_tested': ['python', 'memory_management', 'performance'],
                        'evaluation_criteria': ['technical_accuracy', 'performance_understanding', 'use_cases']
                    },
                    {
                        'text': 'How would you implement a decorator in Python that logs function execution time? Provide a complete example.',
                        'difficulty': 'medium',
                        'skills_tested': ['python', 'decorators', 'logging'],
                        'evaluation_criteria': ['code_quality', 'decorator_understanding', 'practical_implementation']
                    },
                    {
                        'text': 'Describe how Python\'s GIL (Global Interpreter Lock) affects multithreading. How would you work around its limitations?',
                        'difficulty': 'hard',
                        'skills_tested': ['python', 'concurrency', 'performance'],
                        'evaluation_criteria': ['deep_understanding', 'concurrency_concepts', 'practical_solutions']
                    }
                ],
                'javascript': [
                    {
                        'text': 'Explain the event loop in JavaScript. How does it handle asynchronous operations?',
                        'difficulty': 'medium',
                        'skills_tested': ['javascript', 'async_programming', 'event_loop'],
                        'evaluation_criteria': ['conceptual_understanding', 'async_knowledge', 'examples']
                    },
                    {
                        'text': 'What are closures in JavaScript? Provide a practical example where closures solve a real problem.',
                        'difficulty': 'medium',
                        'skills_tested': ['javascript', 'closures', 'scope'],
                        'evaluation_criteria': ['closure_understanding', 'practical_application', 'code_examples']
                    },
                    {
                        'text': 'How would you implement debouncing in JavaScript? Explain when and why you would use it.',
                        'difficulty': 'medium',
                        'skills_tested': ['javascript', 'performance', 'user_experience'],
                        'evaluation_criteria': ['implementation_skills', 'performance_optimization', 'ux_understanding']
                    }
                ],
                'react': [
                    {
                        'text': 'Explain the difference between controlled and uncontrolled components in React. When would you use each approach?',
                        'difficulty': 'medium',
                        'skills_tested': ['react', 'component_design', 'state_management'],
                        'evaluation_criteria': ['react_concepts', 'design_decisions', 'best_practices']
                    },
                    {
                        'text': 'How would you optimize a React application that has performance issues with frequent re-renders?',
                        'difficulty': 'hard',
                        'skills_tested': ['react', 'performance', 'optimization'],
                        'evaluation_criteria': ['optimization_techniques', 'react_profiling', 'practical_solutions']
                    },
                    {
                        'text': 'Describe how you would implement error boundaries in React. What are their limitations?',
                        'difficulty': 'medium',
                        'skills_tested': ['react', 'error_handling', 'component_lifecycle'],
                        'evaluation_criteria': ['error_handling_knowledge', 'react_lifecycle', 'limitations_awareness']
                    }
                ],
                'node': [
                    {
                        'text': 'How would you handle file uploads in a Node.js application? Consider security and performance aspects.',
                        'difficulty': 'medium',
                        'skills_tested': ['nodejs', 'file_handling', 'security'],
                        'evaluation_criteria': ['security_awareness', 'performance_considerations', 'implementation_details']
                    },
                    {
                        'text': 'Explain how you would implement authentication and authorization in a Node.js REST API.',
                        'difficulty': 'medium',
                        'skills_tested': ['nodejs', 'authentication', 'security'],
                        'evaluation_criteria': ['security_best_practices', 'jwt_understanding', 'api_design']
                    },
                    {
                        'text': 'How would you handle database connections and connection pooling in a Node.js application?',
                        'difficulty': 'hard',
                        'skills_tested': ['nodejs', 'database', 'performance'],
                        'evaluation_criteria': ['database_knowledge', 'connection_management', 'scalability']
                    }
                ],
                'sql': [
                    {
                        'text': 'Explain the difference between INNER JOIN, LEFT JOIN, and RIGHT JOIN. Provide examples of when to use each.',
                        'difficulty': 'medium',
                        'skills_tested': ['sql', 'joins', 'database_design'],
                        'evaluation_criteria': ['join_understanding', 'practical_examples', 'use_cases']
                    },
                    {
                        'text': 'How would you optimize a slow-performing SQL query? Walk through your debugging process.',
                        'difficulty': 'hard',
                        'skills_tested': ['sql', 'performance', 'optimization'],
                        'evaluation_criteria': ['optimization_techniques', 'debugging_process', 'indexing_knowledge']
                    },
                    {
                        'text': 'Explain database normalization. What are the trade-offs between normalized and denormalized designs?',
                        'difficulty': 'medium',
                        'skills_tested': ['sql', 'database_design', 'normalization'],
                        'evaluation_criteria': ['normalization_understanding', 'trade_off_analysis', 'design_decisions']
                    }
                ],
                'fullstack': [
                    {
                        'text': 'Describe how you would architect a full-stack e-commerce application. What technologies would you choose for frontend, backend, and database layers?',
                        'difficulty': 'hard',
                        'skills_tested': ['system_design', 'fullstack_architecture', 'technology_selection'],
                        'evaluation_criteria': ['architectural_thinking', 'technology_choices', 'scalability_planning']
                    },
                    {
                        'text': 'How would you implement real-time features (like live chat or notifications) in a full-stack application? Discuss both frontend and backend considerations.',
                        'difficulty': 'medium',
                        'skills_tested': ['websockets', 'real_time_systems', 'fullstack_integration'],
                        'evaluation_criteria': ['real_time_understanding', 'integration_skills', 'performance_considerations']
                    },
                    {
                        'text': 'Walk me through how you would handle user authentication and authorization across a full-stack application. Include security best practices.',
                        'difficulty': 'medium',
                        'skills_tested': ['authentication', 'security', 'fullstack_security'],
                        'evaluation_criteria': ['security_knowledge', 'implementation_details', 'best_practices']
                    }
                ],
                'data_science': [
                    {
                        'text': 'Describe a machine learning project you worked on from data collection to model deployment. What challenges did you face at each stage?',
                        'difficulty': 'medium',
                        'skills_tested': ['ml_pipeline', 'data_science_workflow', 'problem_solving'],
                        'evaluation_criteria': ['end_to_end_thinking', 'practical_experience', 'challenge_handling']
                    },
                    {
                        'text': 'How would you approach a classification problem where you have highly imbalanced data? Discuss various techniques and their trade-offs.',
                        'difficulty': 'hard',
                        'skills_tested': ['imbalanced_data', 'classification', 'ml_techniques'],
                        'evaluation_criteria': ['technical_depth', 'technique_knowledge', 'trade_off_analysis']
                    },
                    {
                        'text': 'Explain how you would validate and interpret the results of a machine learning model. What metrics would you use and why?',
                        'difficulty': 'medium',
                        'skills_tested': ['model_validation', 'metrics', 'interpretation'],
                        'evaluation_criteria': ['validation_understanding', 'metrics_knowledge', 'interpretation_skills']
                    }
                ],
                'software_engineer': [
                    {
                        'text': 'Describe how you would design and implement a caching system for a high-traffic web application. Consider different caching strategies.',
                        'difficulty': 'hard',
                        'skills_tested': ['caching', 'performance', 'system_design'],
                        'evaluation_criteria': ['caching_strategies', 'performance_optimization', 'system_architecture']
                    },
                    {
                        'text': 'How would you approach debugging a production issue where users are experiencing intermittent failures? Walk me through your process.',
                        'difficulty': 'medium',
                        'skills_tested': ['debugging', 'production_issues', 'problem_solving'],
                        'evaluation_criteria': ['debugging_methodology', 'systematic_approach', 'production_experience']
                    },
                    {
                        'text': 'Explain how you would implement a feature flag system. What are the benefits and potential pitfalls?',
                        'difficulty': 'medium',
                        'skills_tested': ['feature_flags', 'deployment_strategies', 'system_design'],
                        'evaluation_criteria': ['feature_flag_understanding', 'deployment_knowledge', 'risk_assessment']
                    }
                ]
            },
            'behavioral': {
                'general': [
                    {
                        'text': 'Tell me about a time when you had to learn a new technology quickly for a project. How did you approach the learning process?',
                        'difficulty': 'medium',
                        'skills_tested': ['learning_agility', 'adaptability', 'time_management'],
                        'evaluation_criteria': ['learning_strategy', 'adaptability', 'time_management', 'results']
                    },
                    {
                        'text': 'Describe a situation where you disagreed with a technical decision made by your team. How did you handle it?',
                        'difficulty': 'medium',
                        'skills_tested': ['communication', 'teamwork', 'conflict_resolution'],
                        'evaluation_criteria': ['communication_skills', 'professionalism', 'problem_solving', 'collaboration']
                    },
                    {
                        'text': 'Tell me about a project where you had to balance technical debt with feature development. How did you make those decisions?',
                        'difficulty': 'hard',
                        'skills_tested': ['technical_leadership', 'decision_making', 'prioritization'],
                        'evaluation_criteria': ['strategic_thinking', 'technical_judgment', 'stakeholder_management']
                    }
                ]
            },
            'system_design': {
                'general': [
                    {
                        'text': 'How would you design a URL shortening service like bit.ly? Consider scalability and reliability.',
                        'difficulty': 'hard',
                        'skills_tested': ['system_design', 'scalability', 'databases'],
                        'evaluation_criteria': ['system_thinking', 'scalability_considerations', 'trade_offs']
                    },
                    {
                        'text': 'Design a real-time chat application. What technologies would you use and how would you handle message delivery?',
                        'difficulty': 'hard',
                        'skills_tested': ['system_design', 'real_time_systems', 'websockets'],
                        'evaluation_criteria': ['real_time_understanding', 'technology_choices', 'scalability']
                    },
                    {
                        'text': 'How would you design a caching layer for a high-traffic web application? Consider different caching strategies.',
                        'difficulty': 'hard',
                        'skills_tested': ['caching', 'performance', 'system_design'],
                        'evaluation_criteria': ['caching_strategies', 'performance_optimization', 'system_architecture']
                    }
                ]
            }
        }

    def _build_evaluation_templates(self) -> Dict[str, Any]:
        """Build evaluation templates for scoring"""
        return {
            'excellent': {
                'score_range': (85, 100),
                'strengths_templates': [
                    "Demonstrated deep understanding of {topic}",
                    "Provided excellent practical examples",
                    "Showed strong problem-solving approach",
                    "Explained concepts clearly and concisely",
                    "Considered edge cases and best practices"
                ],
                'improvements_templates': [
                    "Could elaborate more on {specific_area}",
                    "Consider mentioning {additional_concept}",
                    "Great answer overall, minor refinements possible"
                ]
            },
            'good': {
                'score_range': (70, 84),
                'strengths_templates': [
                    "Good understanding of {topic}",
                    "Provided relevant examples",
                    "Clear communication",
                    "Covered main concepts well"
                ],
                'improvements_templates': [
                    "Could provide more specific examples",
                    "Consider discussing {missing_aspect}",
                    "Explain the reasoning behind {decision}",
                    "Mention potential challenges or trade-offs"
                ]
            },
            'average': {
                'score_range': (50, 69),
                'strengths_templates': [
                    "Basic understanding demonstrated",
                    "Attempted to answer the question",
                    "Some relevant points mentioned"
                ],
                'improvements_templates': [
                    "Need to demonstrate deeper understanding of {topic}",
                    "Provide more concrete examples",
                    "Explain the 'why' behind your approach",
                    "Consider best practices and common pitfalls"
                ]
            },
            'needs_improvement': {
                'score_range': (0, 49),
                'strengths_templates': [
                    "Attempted to provide an answer",
                    "Showed willingness to engage"
                ],
                'improvements_templates': [
                    "Study {topic} fundamentals more thoroughly",
                    "Practice explaining technical concepts clearly",
                    "Gain more hands-on experience with {skill}",
                    "Focus on understanding core principles"
                ]
            }
        }

    def generate_questions(self, skills: List[str], role_hint: str, category: str = 'technical', num_questions: int = 6) -> List[Dict[str, Any]]:
        """Generate high-quality questions based on skills and role"""
        questions = []
        
        # Normalize skills
        normalized_skills = [skill.lower().replace('.js', '').replace('js', 'javascript') for skill in skills]
        
        # Get relevant question pools
        question_pools = []
        
        if category in self.question_database:
            category_questions = self.question_database[category]
            
            # First, try to match role-specific questions
            role_lower = role_hint.lower() if role_hint else ""
            
            # Map role hints to question pools
            role_mappings = {
                'fullstack': ['fullstack', 'javascript', 'node', 'react'],
                'full-stack': ['fullstack', 'javascript', 'node', 'react'],
                'data science': ['data_science', 'python'],
                'data scientist': ['data_science', 'python'],
                'software engineer': ['software_engineer', 'python', 'javascript'],
                'backend': ['node', 'python', 'software_engineer'],
                'frontend': ['javascript', 'react'],
                'devops': ['software_engineer'],
                'ml engineer': ['data_science', 'python']
            }
            
            # Find matching role questions
            matched_pools = []
            for role_key, pool_names in role_mappings.items():
                if role_key in role_lower:
                    print(f"🎯 Matched role '{role_key}' in '{role_lower}'")
                    for pool_name in pool_names:
                        if pool_name in category_questions:
                            pool_questions = category_questions[pool_name]
                            matched_pools.extend(pool_questions)
                            print(f"   Added {len(pool_questions)} questions from '{pool_name}' pool")
                    break
            
            if matched_pools:
                question_pools.extend(matched_pools)
                print(f"🎯 Found {len(matched_pools)} role-specific questions for '{role_hint}'")
            
            # Add questions for specific skills
            for skill in normalized_skills:
                if skill in category_questions:
                    question_pools.extend(category_questions[skill])
            
            # Add general questions if available and we don't have enough
            if len(question_pools) < num_questions and 'general' in category_questions:
                question_pools.extend(category_questions['general'])
        
        # If no specific questions found, use general technical questions
        if not question_pools and category == 'technical':
            for skill_questions in self.question_database['technical'].values():
                question_pools.extend(skill_questions)
        
        # Select diverse questions
        if question_pools:
            # Shuffle and select unique questions
            random.shuffle(question_pools)
            selected_questions = []
            used_texts = set()
            
            for q in question_pools:
                if len(selected_questions) >= num_questions:
                    break
                if q['text'] not in used_texts:
                    selected_questions.append(q)
                    used_texts.add(q['text'])
            
            # Format questions
            for i, q in enumerate(selected_questions):
                questions.append({
                    'id': i + 1,
                    'text': q['text'],
                    'category': category,
                    'difficulty': q.get('difficulty', 'medium'),
                    'time_limit_sec': 90,
                    'skills_tested': q.get('skills_tested', skills[:2]),
                    'evaluation_criteria': q.get('evaluation_criteria', ['technical_accuracy', 'communication'])
                })
        
        # Fill remaining slots with generated questions if needed
        while len(questions) < num_questions:
            questions.append(self._generate_template_question(skills, role_hint, len(questions) + 1))
        
        return questions[:num_questions]

    def _generate_template_question(self, skills: List[str], role_hint: str, question_id: int) -> Dict[str, Any]:
        """Generate a template-based question"""
        templates = [
            "Describe a challenging project where you used {skill}. What obstacles did you overcome?",
            "How would you explain {skill} to a junior developer? Include common pitfalls to avoid.",
            "What performance considerations are important when working with {skill}? Provide examples.",
            "How would you debug a complex issue in a {skill} application? Walk through your process.",
            "What are the best practices for {skill} that you follow in your development process?"
        ]
        
        skill = random.choice(skills) if skills else "your primary technology"
        template = random.choice(templates)
        
        return {
            'id': question_id,
            'text': template.format(skill=skill),
            'category': 'technical',
            'difficulty': 'medium',
            'time_limit_sec': 90,
            'skills_tested': [skill] if skills else [],
            'evaluation_criteria': ['technical_accuracy', 'communication', 'problem_solving']
        }

    def evaluate_answer(self, question: str, answer: str, skills: List[str], role_hint: str) -> Dict[str, Any]:
        """Evaluate an answer using rule-based scoring"""
        if not answer or not answer.strip():
            return {
                'score': 0,
                'strengths': [],
                'improvements': ['No answer provided'],
                'technical_accuracy': 0,
                'communication': 0,
                'problem_solving': 0,
                'overall_feedback': 'No response was provided for this question.',
                'follow_up_suggestions': ['Practice answering this type of question']
            }
        
        # Basic scoring based on answer characteristics
        score = self._calculate_score(answer, question, skills)
        
        # Determine evaluation level
        eval_level = self._get_evaluation_level(score)
        templates = self.evaluation_templates[eval_level]
        
        # Generate feedback
        strengths = self._generate_strengths(answer, templates['strengths_templates'], skills)
        improvements = self._generate_improvements(answer, templates['improvements_templates'], skills)
        
        return {
            'score': score,
            'strengths': strengths,
            'improvements': improvements,
            'technical_accuracy': max(score - 5, 0),
            'communication': min(score + 5, 100),
            'problem_solving': score,
            'overall_feedback': self._generate_overall_feedback(score, answer),
            'follow_up_suggestions': self._generate_follow_up_suggestions(skills, score)
        }

    def _calculate_score(self, answer: str, question: str, skills: List[str]) -> int:
        """Calculate score based on answer characteristics"""
        score = 50  # Base score
        
        # Length bonus (reasonable length indicates effort)
        word_count = len(answer.split())
        if word_count > 20:
            score += min(15, word_count // 10)
        
        # Technical keyword bonus
        technical_keywords = ['implement', 'design', 'optimize', 'debug', 'test', 'deploy', 'scale', 'performance', 'security']
        keyword_count = sum(1 for keyword in technical_keywords if keyword.lower() in answer.lower())
        score += min(10, keyword_count * 2)
        
        # Skill-specific bonus
        skill_mentions = sum(1 for skill in skills if skill.lower() in answer.lower())
        score += min(10, skill_mentions * 3)
        
        # Structure bonus (mentions examples, explains reasoning)
        structure_indicators = ['example', 'because', 'however', 'therefore', 'first', 'second', 'finally']
        structure_count = sum(1 for indicator in structure_indicators if indicator.lower() in answer.lower())
        score += min(10, structure_count * 2)
        
        # Cap at 100
        return min(100, score)

    def _get_evaluation_level(self, score: int) -> str:
        """Determine evaluation level based on score"""
        if score >= 85:
            return 'excellent'
        elif score >= 70:
            return 'good'
        elif score >= 50:
            return 'average'
        else:
            return 'needs_improvement'

    def _generate_strengths(self, answer: str, templates: List[str], skills: List[str]) -> List[str]:
        """Generate strengths based on answer analysis"""
        strengths = []
        
        # Select 2-3 relevant strength templates
        selected_templates = random.sample(templates, min(3, len(templates)))
        
        for template in selected_templates:
            if '{topic}' in template and skills:
                topic = random.choice(skills)
                strengths.append(template.format(topic=topic))
            elif '{topic}' not in template:
                strengths.append(template)
        
        return strengths

    def _generate_improvements(self, answer: str, templates: List[str], skills: List[str]) -> List[str]:
        """Generate improvements based on answer analysis"""
        improvements = []
        
        # Select 2-3 relevant improvement templates
        selected_templates = random.sample(templates, min(3, len(templates)))
        
        for template in selected_templates:
            if '{specific_area}' in template and skills:
                area = random.choice(skills)
                improvements.append(template.format(specific_area=area))
            elif '{missing_aspect}' in template:
                aspects = ['performance considerations', 'error handling', 'testing strategies', 'security implications']
                aspect = random.choice(aspects)
                improvements.append(template.format(missing_aspect=aspect))
            elif '{topic}' in template and skills:
                topic = random.choice(skills)
                improvements.append(template.format(topic=topic))
            elif '{skill}' in template and skills:
                skill = random.choice(skills)
                improvements.append(template.format(skill=skill))
            elif '{' not in template:
                improvements.append(template)
        
        return improvements

    def _generate_overall_feedback(self, score: int, answer: str) -> str:
        """Generate overall feedback based on score and answer"""
        if score >= 85:
            return "Excellent response! You demonstrated strong technical knowledge and provided clear explanations with good examples."
        elif score >= 70:
            return "Good answer! You covered the main points well. Consider adding more specific examples or discussing edge cases."
        elif score >= 50:
            return "Decent attempt. You touched on some key points but could provide more depth and specific examples."
        else:
            return "Your answer needs more development. Focus on providing specific examples and explaining your reasoning more clearly."

    def _generate_follow_up_suggestions(self, skills: List[str], score: int) -> List[str]:
        """Generate follow-up suggestions based on performance"""
        suggestions = []
        
        if score >= 85:
            suggestions = [
                "Great job! Continue practicing system design questions",
                "Consider exploring advanced topics in your tech stack",
                "Practice explaining complex concepts simply"
            ]
        elif score >= 70:
            suggestions = [
                "Practice providing more concrete examples",
                "Study common design patterns and best practices",
                "Work on explaining trade-offs in technical decisions"
            ]
        elif score >= 50:
            suggestions = [
                "Focus on understanding fundamental concepts deeply",
                "Practice coding problems related to your skills",
                "Study real-world applications of the technologies you use"
            ]
        else:
            suggestions = [
                "Spend time learning the basics of your chosen technologies",
                "Practice explaining technical concepts out loud",
                "Build small projects to gain hands-on experience"
            ]
        
        return suggestions[:3]

# Global instance
enhanced_fallback = EnhancedInterviewFallback()

def get_enhanced_questions(skills: List[str], role_hint: str, category: str = 'technical', num_questions: int = 6) -> List[Dict[str, Any]]:
    """Get enhanced questions using the fallback system"""
    return enhanced_fallback.generate_questions(skills, role_hint, category, num_questions)

def get_enhanced_evaluation(question: str, answer: str, skills: List[str], role_hint: str) -> Dict[str, Any]:
    """Get enhanced evaluation using the fallback system"""
    return enhanced_fallback.evaluate_answer(question, answer, skills, role_hint)
