#!/usr/bin/env python3
"""
Simple Skill Gap Analysis Data Generator
Creates basic skill importance and categories data for immediate use.
"""

import json
import os

def create_simple_skill_data():
    """Create basic skill importance and categories data."""
    
    # Skill importance based on industry knowledge
    skill_importance = {
        "python": {"frequency": 15000, "percentage": 45.2, "importance_score": 9.5},
        "javascript": {"frequency": 18000, "percentage": 54.3, "importance_score": 9.8},
        "java": {"frequency": 12000, "percentage": 36.2, "importance_score": 8.7},
        "react": {"frequency": 14000, "percentage": 42.3, "importance_score": 9.2},
        "aws": {"frequency": 11000, "percentage": 33.2, "importance_score": 8.5},
        "docker": {"frequency": 9000, "percentage": 27.1, "importance_score": 7.8},
        "kubernetes": {"frequency": 7000, "percentage": 21.1, "importance_score": 7.2},
        "sql": {"frequency": 16000, "percentage": 48.2, "importance_score": 9.0},
        "mongodb": {"frequency": 6000, "percentage": 18.1, "importance_score": 6.8},
        "node.js": {"frequency": 10000, "percentage": 30.2, "importance_score": 8.2},
        "django": {"frequency": 5000, "percentage": 15.1, "importance_score": 6.5},
        "flask": {"frequency": 4000, "percentage": 12.1, "importance_score": 6.0},
        "spring": {"frequency": 8000, "percentage": 24.2, "importance_score": 7.5},
        "git": {"frequency": 20000, "percentage": 60.3, "importance_score": 10.0},
        "jenkins": {"frequency": 5000, "percentage": 15.1, "importance_score": 6.5},
        "machine learning": {"frequency": 6000, "percentage": 18.1, "importance_score": 6.8},
        "data science": {"frequency": 7000, "percentage": 21.1, "importance_score": 7.2},
        "tensorflow": {"frequency": 3000, "percentage": 9.1, "importance_score": 5.5},
        "pandas": {"frequency": 4000, "percentage": 12.1, "importance_score": 6.0},
        "numpy": {"frequency": 3500, "percentage": 10.6, "importance_score": 5.8},
        "angular": {"frequency": 8000, "percentage": 24.2, "importance_score": 7.5},
        "vue": {"frequency": 6000, "percentage": 18.1, "importance_score": 6.8},
        "typescript": {"frequency": 9000, "percentage": 27.1, "importance_score": 7.8},
        "c++": {"frequency": 7000, "percentage": 21.1, "importance_score": 7.2},
        "c#": {"frequency": 8000, "percentage": 24.2, "importance_score": 7.5},
        "php": {"frequency": 6000, "percentage": 18.1, "importance_score": 6.8},
        "ruby": {"frequency": 4000, "percentage": 12.1, "importance_score": 6.0},
        "go": {"frequency": 3000, "percentage": 9.1, "importance_score": 5.5},
        "rust": {"frequency": 2000, "percentage": 6.0, "importance_score": 4.8},
        "mysql": {"frequency": 12000, "percentage": 36.2, "importance_score": 8.7},
        "postgresql": {"frequency": 9000, "percentage": 27.1, "importance_score": 7.8},
        "redis": {"frequency": 5000, "percentage": 15.1, "importance_score": 6.5},
        "elasticsearch": {"frequency": 4000, "percentage": 12.1, "importance_score": 6.0},
        "azure": {"frequency": 8000, "percentage": 24.2, "importance_score": 7.5},
        "gcp": {"frequency": 6000, "percentage": 18.1, "importance_score": 6.8},
        "terraform": {"frequency": 4000, "percentage": 12.1, "importance_score": 6.0},
        "ansible": {"frequency": 3000, "percentage": 9.1, "importance_score": 5.5},
        "jira": {"frequency": 15000, "percentage": 45.2, "importance_score": 9.5},
        "confluence": {"frequency": 8000, "percentage": 24.2, "importance_score": 7.5},
        "slack": {"frequency": 10000, "percentage": 30.2, "importance_score": 8.2},
        "figma": {"frequency": 5000, "percentage": 15.1, "importance_score": 6.5},
        "postman": {"frequency": 7000, "percentage": 21.1, "importance_score": 7.2}
    }
    
    # Skill categories
    skill_categories = {
        "Programming Languages": ["python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "php", "ruby"],
        "Frameworks & Libraries": ["react", "angular", "vue", "node.js", "django", "flask", "spring", "express", "laravel", "asp.net"],
        "Databases": ["mysql", "postgresql", "mongodb", "redis", "elasticsearch", "oracle", "sql server", "dynamodb"],
        "Cloud & DevOps": ["aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git", "terraform", "ansible", "ci/cd"],
        "Data & AI": ["machine learning", "data science", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn", "nlp", "ai"],
        "Tools & Platforms": ["jira", "confluence", "slack", "figma", "postman", "swagger", "kafka", "rabbitmq"]
    }
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # Save skill importance
    with open('data/skill_importance.json', 'w') as f:
        json.dump(skill_importance, f, indent=2)
    
    # Save skill categories
    with open('data/skill_categories.json', 'w') as f:
        json.dump(skill_categories, f, indent=2)
    
    print("✅ Simple skill data created successfully!")
    print("📊 Files saved:")
    print("   - data/skill_importance.json")
    print("   - data/skill_categories.json")
    
    return True

if __name__ == "__main__":
    create_simple_skill_data()
