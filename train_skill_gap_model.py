#!/usr/bin/env python3
"""
Skill Gap Analysis Model Training Script

This script trains a model to analyze skill gaps between candidate skills and job requirements.
It uses job descriptions and skill requirements to create a comprehensive skill matching system.
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import joblib
import json
import re
import os
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SkillGapTrainer:
    def __init__(self):
        self.skill_vectorizer = None
        self.job_vectorizer = None
        self.skill_clusters = None
        self.skill_importance = {}
        self.skill_categories = {}
        
    def load_data(self):
        """Load job datasets for training."""
        datasets = []
        
        # Try to load different dataset files
        data_files = [
            "data/unified_job_dataset.csv",
            "data/job_dataset_medium.csv", 
            "data/job_dataset_sample.csv"
        ]
        
        for file_path in data_files:
            if os.path.exists(file_path):
                try:
                    df = pd.read_csv(file_path)
                    datasets.append(df)
                    logger.info(f"Loaded {len(df)} jobs from {file_path}")
                except Exception as e:
                    logger.warning(f"Could not load {file_path}: {e}")
        
        if not datasets:
            raise ValueError("No job datasets found!")
        
        # Combine datasets
        self.job_data = pd.concat(datasets, ignore_index=True)
        logger.info(f"Total jobs loaded: {len(self.job_data)}")
        
        return self.job_data
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from job description text."""
        if not text or pd.isna(text):
            return []
        
        text = str(text).lower()
        
        # Comprehensive skill dictionary
        skill_patterns = {
            'Programming Languages': [
                r'\bpython\b', r'\bjava\b', r'\bjavascript\b', r'\btypescript\b',
                r'\bc\+\+\b', r'\bc#\b', r'\bgo\b', r'\brust\b', r'\bphp\b', r'\bruby\b',
                r'\bswift\b', r'\bkotlin\b', r'\bscala\b', r'\bperl\b', r'\br\b'
            ],
            'Frameworks & Libraries': [
                r'\breact\b', r'\bangular\b', r'\bvue\b', r'\bnode\.js\b', r'\bexpress\b',
                r'\bdjango\b', r'\bflask\b', r'\bspring\b', r'\blaravel\b', r'\basp\.net\b',
                r'\bjquery\b', r'\bbootstrap\b', r'\btailwind\b', r'\bnext\.js\b', r'\bnuxt\b'
            ],
            'Databases': [
                r'\bmysql\b', r'\bpostgresql\b', r'\bmongodb\b', r'\bredis\b',
                r'\belasticsearch\b', r'\boracle\b', r'\bsql server\b', r'\bdynamodb\b',
                r'\bcassandra\b', r'\bneo4j\b', r'\bsqlite\b'
            ],
            'Cloud & DevOps': [
                r'\baws\b', r'\bazure\b', r'\bgcp\b', r'\bdocker\b', r'\bkubernetes\b',
                r'\bjenkins\b', r'\bgit\b', r'\bterraform\b', r'\bansible\b', r'\bci/cd\b',
                r'\bgithub actions\b', r'\bgitlab\b', r'\bcircleci\b', r'\btravis\b'
            ],
            'Data & AI': [
                r'\bmachine learning\b', r'\bdata science\b', r'\btensorflow\b', r'\bpytorch\b',
                r'\bpandas\b', r'\bnumpy\b', r'\bscikit-learn\b', r'\bnlp\b', r'\bai\b',
                r'\bdeep learning\b', r'\bneural networks\b', r'\bopencv\b'
            ],
            'Tools & Platforms': [
                r'\bjira\b', r'\bconfluence\b', r'\bslack\b', r'\bfigma\b', r'\bpostman\b',
                r'\bswagger\b', r'\bkafka\b', r'\brabbitmq\b', r'\bapache\b', r'\bnginx\b'
            ]
        }
        
        extracted_skills = []
        for category, patterns in skill_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    skill = re.search(pattern, text).group(0)
                    extracted_skills.append(skill)
                    if category not in self.skill_categories:
                        self.skill_categories[category] = []
                    if skill not in self.skill_categories[category]:
                        self.skill_categories[category].append(skill)
        
        return list(set(extracted_skills))
    
    def prepare_training_data(self):
        """Prepare training data for skill gap analysis."""
        logger.info("Preparing training data...")
        
        # Extract skills from job descriptions
        self.job_data['extracted_skills'] = self.job_data['description'].apply(
            self.extract_skills_from_text
        )
        
        # Create skill importance based on frequency
        all_skills = []
        for skills in self.job_data['extracted_skills']:
            all_skills.extend(skills)
        
        skill_counts = pd.Series(all_skills).value_counts()
        total_jobs = len(self.job_data)
        
        for skill, count in skill_counts.items():
            self.skill_importance[skill] = {
                'frequency': count,
                'percentage': (count / total_jobs) * 100,
                'importance_score': min(10, (count / total_jobs) * 100)
            }
        
        logger.info(f"Extracted {len(self.skill_importance)} unique skills")
        
        # Create skill vectors for clustering
        skill_texts = [' '.join(skills) for skills in self.job_data['extracted_skills']]
        self.skill_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        skill_vectors = self.skill_vectorizer.fit_transform(skill_texts)
        
        # Cluster skills to find skill groups
        n_clusters = min(20, len(skill_vectors))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.skill_clusters = kmeans.fit_predict(skill_vectors)
        
        # Create job vectors for matching
        job_texts = self.job_data['description'].fillna('').astype(str)
        self.job_vectorizer = TfidfVectorizer(
            max_features=2000,
            stop_words='english',
            ngram_range=(1, 3)
        )
        
        self.job_vectors = self.job_vectorizer.fit_transform(job_texts)
        
        logger.info("Training data preparation completed")
        
        return skill_vectors, self.job_vectors
    
    def train_model(self):
        """Train the skill gap analysis model."""
        logger.info("Starting model training...")
        
        try:
            # Load and prepare data
            self.load_data()
            skill_vectors, job_vectors = self.prepare_training_data()
            
            # Save the trained model components
            model_data = {
                'skill_vectorizer': self.skill_vectorizer,
                'job_vectorizer': self.job_vectorizer,
                'skill_clusters': self.skill_clusters,
                'skill_importance': self.skill_importance,
                'skill_categories': self.skill_categories,
                'job_vectors': job_vectors,
                'job_data': self.job_data
            }
            
            # Save model
            joblib.dump(model_data, 'data/skill_gap_model.joblib')
            
            # Save skill importance as JSON for easy access
            with open('data/skill_importance.json', 'w') as f:
                json.dump(self.skill_importance, f, indent=2)
            
            # Save skill categories
            with open('data/skill_categories.json', 'w') as f:
                json.dump(self.skill_categories, f, indent=2)
            
            logger.info("Model training completed successfully!")
            logger.info(f"Saved model to data/skill_gap_model.joblib")
            logger.info(f"Saved skill importance to data/skill_importance.json")
            logger.info(f"Saved skill categories to data/skill_categories.json")
            
            return True
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return False
    
    def analyze_skill_gap(self, user_skills: List[str], job_description: str) -> Dict[str, Any]:
        """Analyze skill gap between user skills and job requirements."""
        if not hasattr(self, 'skill_vectorizer') or not hasattr(self, 'job_vectorizer'):
            raise ValueError("Model not trained. Please run train_model() first.")
        
        # Extract required skills from job description
        required_skills = self.extract_skills_from_text(job_description)
        
        # Calculate skill match
        user_skill_set = set([s.lower() for s in user_skills])
        required_skill_set = set([s.lower() for s in required_skills])
        
        matching_skills = user_skill_set.intersection(required_skill_set)
        missing_skills = required_skill_set - user_skill_set
        extra_skills = user_skill_set - required_skill_set
        
        # Calculate scores
        match_percentage = len(matching_skills) / max(1, len(required_skill_set)) * 100
        
        # Calculate importance-weighted score
        importance_score = 0
        total_importance = 0
        
        for skill in matching_skills:
            if skill in self.skill_importance:
                importance_score += self.skill_importance[skill]['importance_score']
                total_importance += self.skill_importance[skill]['importance_score']
        
        weighted_score = (importance_score / max(1, total_importance)) * 100 if total_importance > 0 else 0
        
        # Get skill recommendations
        recommendations = []
        for skill in missing_skills:
            if skill in self.skill_importance:
                recommendations.append({
                    'skill': skill,
                    'importance': self.skill_importance[skill]['importance_score'],
                    'frequency': self.skill_importance[skill]['frequency']
                })
        
        # Sort recommendations by importance
        recommendations.sort(key=lambda x: x['importance'], reverse=True)
        
        return {
            'match_percentage': round(match_percentage, 1),
            'weighted_score': round(weighted_score, 1),
            'matching_skills': list(matching_skills),
            'missing_skills': list(missing_skills),
            'extra_skills': list(extra_skills),
            'required_skills': list(required_skill_set),
            'recommendations': recommendations[:10],  # Top 10 recommendations
            'skill_categories': self.skill_categories
        }

def main():
    """Main training function."""
    print("🚀 Starting Skill Gap Analysis Model Training...")
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Initialize trainer
    trainer = SkillGapTrainer()
    
    # Train model
    success = trainer.train_model()
    
    if success:
        print("✅ Skill Gap Analysis Model trained successfully!")
        print("📊 Model components saved:")
        print("   - data/skill_gap_model.joblib (main model)")
        print("   - data/skill_importance.json (skill importance data)")
        print("   - data/skill_categories.json (skill categories)")
        
        # Test the model
        print("\n🧪 Testing the model...")
        test_skills = ['python', 'javascript', 'react']
        test_job = "We are looking for a Python developer with experience in Django, React, and AWS. Knowledge of Docker and Kubernetes is a plus."
        
        try:
            result = trainer.analyze_skill_gap(test_skills, test_job)
            print(f"✅ Test successful! Match: {result['match_percentage']}%")
            print(f"   Missing skills: {result['missing_skills']}")
        except Exception as e:
            print(f"⚠️ Test failed: {e}")
    else:
        print("❌ Model training failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
