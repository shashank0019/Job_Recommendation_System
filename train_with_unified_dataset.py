#!/usr/bin/env python3
"""
Training Script for Career Guidance Platform using Unified Dataset

This script trains the TF-IDF model on the unified job dataset created from
the archive datasets. It's optimized for handling large datasets efficiently.
"""

import os
import sys
import logging
import time
from pathlib import Path
import pandas as pd

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

class UnifiedDatasetTrainer:
    """Trains the Career Guidance Platform on the unified dataset."""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.unified_dataset_path = self.data_dir / "unified_job_dataset.csv"
        self.medium_dataset_path = self.data_dir / "job_dataset_medium.csv"
        self.sample_dataset_path = self.data_dir / "job_dataset_sample.csv"
        
        self.job_matcher = None
        self.resume_parser = None
        
    def check_datasets(self) -> bool:
        """Check which datasets are available."""
        logger.info("🔍 Checking available datasets...")
        
        available_datasets = []
        
        if self.unified_dataset_path.exists():
            size_mb = self.unified_dataset_path.stat().st_size / (1024 * 1024)
            available_datasets.append(("unified_job_dataset.csv", size_mb, "Full dataset"))
        
        if self.medium_dataset_path.exists():
            size_mb = self.medium_dataset_path.stat().st_size / (1024 * 1024)
            available_datasets.append(("job_dataset_medium.csv", size_mb, "Medium dataset (5K jobs)"))
        
        if self.sample_dataset_path.exists():
            size_mb = self.sample_dataset_path.stat().st_size / (1024 * 1024)
            available_datasets.append(("job_dataset_sample.csv", size_mb, "Sample dataset (1K jobs)"))
        
        if not available_datasets:
            logger.error("❌ No unified datasets found!")
            logger.error("Please run integrate_datasets.py first to create the unified dataset.")
            return False
        
        logger.info("✅ Available datasets:")
        for filename, size_mb, description in available_datasets:
            logger.info(f"   📁 {filename} ({size_mb:.1f} MB) - {description}")
        
        return True
    
    def select_dataset(self) -> str:
        """Let user select which dataset to use for training."""
        logger.info("\n🎯 Select dataset for training:")
        logger.info("   1. Sample dataset (1K jobs) - Fast training, good for testing")
        logger.info("   2. Medium dataset (5K jobs) - Balanced training, good for development")
        logger.info("   3. Full dataset - Complete training, best for production")
        
        while True:
            try:
                choice = input("\nEnter your choice (1-3): ").strip()
                if choice == "1":
                    return str(self.sample_dataset_path)
                elif choice == "2":
                    return str(self.medium_dataset_path)
                elif choice == "3":
                    return str(self.unified_dataset_path)
                else:
                    print("❌ Invalid choice. Please enter 1, 2, or 3.")
            except KeyboardInterrupt:
                logger.info("\n⏹️  Training interrupted by user")
                sys.exit(1)
    
    def load_dataset(self, dataset_path: str) -> pd.DataFrame:
        """Load the selected dataset."""
        try:
            logger.info(f"📊 Loading dataset: {Path(dataset_path).name}")
            start_time = time.time()
            
            # Load with optimized settings for large files
            df = pd.read_csv(
                dataset_path,
                low_memory=False,
                dtype={
                    'job_id': 'int64',
                    'title': 'string',
                    'company': 'string',
                    'location': 'string',
                    'description': 'string',
                    'skills': 'string',
                    'industry': 'string',
                    'benefits': 'string',
                    'salary_range': 'string',
                    'experience_level': 'string',
                    'work_type': 'string',
                    'remote_allowed': 'string',
                    'requirements': 'string'
                }
            )
            
            load_time = time.time() - start_time
            logger.info(f"✅ Dataset loaded in {load_time:.2f} seconds")
            logger.info(f"   📊 Total jobs: {len(df):,}")
            logger.info(f"   🏢 Unique companies: {df['company'].nunique():,}")
            logger.info(f"   🌍 Unique locations: {df['location'].nunique():,}")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Error loading dataset: {e}")
            return None
    
    def test_resume_parser(self) -> bool:
        """Test the resume parser functionality."""
        logger.info("\n🧪 Testing Resume Parser...")
        
        try:
            self.resume_parser = ResumeParser()
            
            # Test with sample resume
            test_resume = """
            EXPERIENCE
            Senior Software Engineer at TechCorp (2020-2023)
            - Developed web applications using Python, Django, and React
            - Managed AWS infrastructure and implemented CI/CD pipelines
            - Led a team of 5 developers in agile development process
            
            SKILLS
            Programming: Python, JavaScript, Java, SQL
            Frameworks: Django, React, Spring Boot
            Cloud: AWS, Docker, Kubernetes
            Tools: Git, Jenkins, Jira
            
            EDUCATION
            Bachelor's in Computer Science from University of Technology
            """
            
            result = self.resume_parser.parse_resume(test_resume)
            
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
    
    def train_model(self, dataset_path: str) -> bool:
        """Train the job matching model on the selected dataset."""
        try:
            logger.info(f"\n🤖 Training TF-IDF model on {Path(dataset_path).name}...")
            
            # Load dataset
            job_data = self.load_dataset(dataset_path)
            if job_data is None:
                return False
            
            # Initialize job matcher
            self.job_matcher = JobMatcher()
            
            # Train the model
            start_time = time.time()
            success = self.job_matcher.train_model(job_data)
            training_time = time.time() - start_time
            
            if success:
                logger.info(f"✅ Model training completed in {training_time:.2f} seconds!")
                
                # Get statistics
                stats = self.job_matcher.get_job_statistics()
                logger.info(f"📊 Training Statistics:")
                logger.info(f"   Total Jobs: {stats.get('total_jobs', 0):,}")
                logger.info(f"   Model Trained: {stats.get('is_trained', False)}")
                logger.info(f"   Vectorizer Features: {stats.get('vectorizer_features', 0):,}")
                
                if 'top_locations' in stats:
                    logger.info(f"   Top Locations: {len(stats['top_locations'])}")
                
                if 'top_industries' in stats:
                    logger.info(f"   Top Industries: {len(stats['top_industries'])}")
                
                return True
            else:
                logger.error("❌ Model training failed!")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during training: {e}")
            return False
    
    def test_model(self) -> bool:
        """Test the trained model with sample resumes."""
        logger.info("\n🧪 Testing trained model...")
        
        if not self.job_matcher or not self.job_matcher.is_trained:
            logger.error("❌ Model not trained. Cannot test.")
            return False
        
        # Test resumes for different job types
        test_resumes = [
            {
                "name": "Software Engineer",
                "text": """
                I am a software engineer with 5 years of experience in Python development.
                I have worked with Django, React, and AWS. I am proficient in SQL and have
                experience with Docker and Kubernetes. I have led teams and implemented
                CI/CD pipelines.
                """
            },
            {
                "name": "Data Scientist",
                "text": """
                I am a data scientist with 3 years of experience in machine learning.
                I have worked with Python, R, SQL, and various ML frameworks like TensorFlow.
                I have experience with data analysis, statistical modeling, and building
                predictive models. I have worked with cloud platforms like AWS.
                """
            },
            {
                "name": "Product Manager",
                "text": """
                I am a product manager with 4 years of experience in software products.
                I have worked with agile methodologies, user research, and data analysis.
                I have experience with product strategy, roadmap planning, and cross-functional
                team leadership. I have worked with engineering and design teams.
                """
            }
        ]
        
        all_tests_passed = True
        
        for test_case in test_resumes:
            logger.info(f"\n🔍 Testing: {test_case['name']}")
            
            try:
                # Find matching jobs
                matches = self.job_matcher.find_matching_jobs(
                    test_case['text'], 
                    top_k=3,
                    min_similarity=0.05
                )
                
                if matches:
                    logger.info(f"✅ Found {len(matches)} matches:")
                    for i, job in enumerate(matches[:2], 1):
                        logger.info(f"   {i}. {job['title']} at {job['company']}")
                        logger.info(f"      Location: {job['location']}")
                        logger.info(f"      Similarity: {job['similarity_score']:.3f}")
                        if 'industry' in job:
                            logger.info(f"      Industry: {job['industry']}")
                else:
                    logger.warning("⚠️  No matches found")
                    all_tests_passed = False
                    
            except Exception as e:
                logger.error(f"❌ Test failed: {e}")
                all_tests_passed = False
        
        return all_tests_passed
    
    def run_training(self) -> bool:
        """Run the complete training process."""
        try:
            logger.info("🚀 Starting Career Guidance Platform Training with Unified Dataset")
            logger.info("=" * 70)
            
            # Step 1: Check available datasets
            if not self.check_datasets():
                return False
            
            # Step 2: Test resume parser
            if not self.test_resume_parser():
                return False
            
            # Step 3: Select dataset
            dataset_path = self.select_dataset()
            
            # Step 4: Train model
            if not self.train_model(dataset_path):
                return False
            
            # Step 5: Test model
            if not self.test_model():
                logger.warning("⚠️  Model testing had some issues, but training completed")
            
            # Success summary
            logger.info("\n" + "=" * 70)
            logger.info("🎉 TRAINING COMPLETED SUCCESSFULLY!")
            logger.info("=" * 70)
            logger.info(f"📊 Dataset used: {Path(dataset_path).name}")
            logger.info(f"🤖 Model trained and ready for use")
            logger.info(f"🧪 Resume parser tested and working")
            
            logger.info("\n🚀 Next Steps:")
            logger.info("   1. Start the application: python app.py")
            logger.info("   2. Test the system: python test_system.py")
            logger.info("   3. Open http://localhost:5000 in your browser")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Training process failed: {e}")
            return False


def main():
    """Main function to run the training."""
    trainer = UnifiedDatasetTrainer()
    
    if trainer.run_training():
        logger.info("\n🎉 Training completed successfully!")
        return True
    else:
        logger.error("\n❌ Training failed!")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⏹️  Training interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1) 