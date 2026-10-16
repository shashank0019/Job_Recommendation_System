#!/usr/bin/env python3
"""
Model Training Script for Career Guidance Platform

This script trains the TF-IDF model on the job dataset and saves it for later use.
Run this script before starting the main application to ensure the model is ready.
"""

import os
import sys
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from job_matcher import JobMatcher
from resume_parser import ResumeParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main training function."""
    logger.info("🚀 Starting Career Guidance Platform Model Training")
    
    # Check if data directory exists
    data_dir = Path("data")
    if not data_dir.exists():
        logger.error("❌ Data directory not found. Please ensure the 'data' directory exists.")
        return False
    
    # Check if CSV dataset exists
    csv_path = data_dir / "job_dataset.csv"
    if not csv_path.exists():
        logger.error("❌ Job dataset CSV not found. Please ensure 'data/job_dataset.csv' exists.")
        return False
    
    try:
        # Initialize the job matcher
        logger.info("📊 Initializing Job Matcher...")
        matcher = JobMatcher()
        
        # Check if model is already trained
        if matcher.is_trained:
            logger.info("✅ Model is already trained and ready!")
            
            # Show statistics
            stats = matcher.get_job_statistics()
            logger.info(f"📈 Dataset Statistics:")
            logger.info(f"   Total Jobs: {stats.get('total_jobs', 0)}")
            logger.info(f"   Model Trained: {stats.get('is_trained', False)}")
            logger.info(f"   Vectorizer Features: {stats.get('vectorizer_features', 0)}")
            
            # Ask if user wants to retrain
            response = input("\n🔄 Do you want to retrain the model? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                logger.info("✅ Keeping existing model. No retraining needed.")
                return True
        
        # Train the model
        logger.info("🤖 Training TF-IDF model on job dataset...")
        success = matcher.train_model()
        
        if success:
            logger.info("✅ Model training completed successfully!")
            
            # Show final statistics
            stats = matcher.get_job_statistics()
            logger.info(f"📊 Final Statistics:")
            logger.info(f"   Total Jobs: {stats.get('total_jobs', 0)}")
            logger.info(f"   Model Trained: {stats.get('is_trained', False)}")
            logger.info(f"   Vectorizer Features: {stats.get('vectorizer_features', 0)}")
            
            # Test the model with a sample resume
            logger.info("\n🧪 Testing model with sample resume...")
            test_resume = """
            I am a software engineer with 3 years of experience in Python development.
            I have worked with Django, React, and AWS. I am proficient in SQL and have
            experience with Docker and Git. I have worked in agile teams and implemented
            CI/CD pipelines.
            """
            
            matches = matcher.find_matching_jobs(test_resume, top_k=3)
            
            if matches:
                logger.info("✅ Model test successful! Sample matches:")
                for i, job in enumerate(matches[:3], 1):
                    logger.info(f"   {i}. {job['title']} at {job['company']} (Score: {job['similarity_score']:.3f})")
            else:
                logger.warning("⚠️  Model test returned no matches. This might indicate an issue.")
            
            logger.info("\n🎉 Model training and testing completed successfully!")
            logger.info("🚀 You can now start the Career Guidance Platform with: python app.py")
            return True
            
        else:
            logger.error("❌ Model training failed!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Unexpected error during training: {e}")
        return False

def test_resume_parser():
    """Test the resume parser functionality."""
    logger.info("\n📝 Testing Resume Parser...")
    
    try:
        parser = ResumeParser()
        
        # Test with sample resume
        test_resume = """
        EXPERIENCE
        Software Engineer at TechCorp (2020-2023)
        - Developed web applications using Python, Django, and React
        - Managed AWS infrastructure and implemented CI/CD pipelines
        - Led a team of 3 developers in agile development process
        
        SKILLS
        Programming: Python, JavaScript, Java, SQL
        Frameworks: Django, React, Spring Boot
        Cloud: AWS, Docker, Kubernetes
        Tools: Git, Jenkins, Jira
        
        EDUCATION
        Bachelor's in Computer Science from University of Technology
        """
        
        result = parser.parse_resume(test_resume)
        
        if result['success']:
            logger.info("✅ Resume parsing successful!")
            logger.info(f"   Total Skills: {result['parsed_data']['total_skills']}")
            logger.info(f"   Keywords: {result['parsed_data']['keyword_count']}")
            
            # Show extracted skills
            for category, skills in result['parsed_data']['skills'].items():
                if skills:
                    logger.info(f"   {category}: {', '.join(skills[:5])}")
            
            return True
        else:
            logger.error(f"❌ Resume parsing failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error testing resume parser: {e}")
        return False

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🎯 Career Guidance Platform - Model Training")
    logger.info("=" * 60)
    
    # Test resume parser first
    if not test_resume_parser():
        logger.error("❌ Resume parser test failed. Exiting.")
        sys.exit(1)
    
    # Train the model
    if main():
        logger.info("\n🎉 All systems ready! The Career Guidance Platform is ready to use.")
        sys.exit(0)
    else:
        logger.error("\n❌ Training failed. Please check the errors above and try again.")
        sys.exit(1) 