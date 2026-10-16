#!/usr/bin/env python3
"""
Test script to check and fix job matching model training issues.
"""

import os
import sys
import pandas as pd
import logging

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_data_files():
    """Check if required data files exist."""
    print("🔍 Checking data files...")
    
    data_dir = "data"
    required_files = [
        "job_dataset.csv",
        "unified_job_dataset.csv"
    ]
    
    existing_files = []
    for file in required_files:
        file_path = os.path.join(data_dir, file)
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file} exists ({size:,} bytes)")
            existing_files.append(file_path)
        else:
            print(f"❌ {file} not found")
    
    return existing_files

def test_job_matcher():
    """Test the job matcher functionality."""
    print("\n🧪 Testing JobMatcher...")
    
    try:
        from job_matcher import JobMatcher
        
        # Initialize with small dataset first
        matcher = JobMatcher(csv_data_path="data/job_dataset.csv")
        
        print(f"Model trained: {matcher.is_trained}")
        
        if not matcher.is_trained:
            print("Training model...")
            success = matcher.train_model()
            if success:
                print("✅ Model training successful")
            else:
                print("❌ Model training failed")
                return False
        
        # Test with sample resume
        sample_resume = "Software Engineer with Python, React, and AWS experience"
        matches = matcher.find_matching_jobs(sample_resume, top_k=3)
        
        print(f"✅ Found {len(matches)} job matches")
        for i, job in enumerate(matches, 1):
            print(f"  {i}. {job.get('title', 'N/A')} - Score: {job.get('similarity_score', 0):.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ JobMatcher test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_resume_parser():
    """Test the resume parser functionality."""
    print("\n🧪 Testing ResumeParser...")
    
    try:
        from resume_parser import ResumeParser
        
        parser = ResumeParser()
        sample_resume = """
        Senior Software Engineer with 5+ years experience.
        Skills: Python, JavaScript, React, AWS, Docker, PostgreSQL
        Experience with microservices and cloud deployment.
        """
        
        result = parser.parse_resume(sample_resume)
        
        if result['success']:
            print("✅ Resume parsing successful")
            skills = result['parsed_data']['skills']
            print(f"  Found skills in {len(skills)} categories")
            for category, skill_list in skills.items():
                if skill_list:
                    print(f"    {category}: {', '.join(skill_list[:3])}")
        else:
            print(f"❌ Resume parsing failed: {result.get('error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ ResumeParser test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_sample_dataset():
    """Create a sample dataset if none exists."""
    print("\n📝 Creating sample job dataset...")
    
    sample_jobs = [
        {
            "job_id": 1,
            "title": "Senior Software Engineer",
            "company": "TechCorp",
            "location": "San Francisco, CA",
            "description": "Develop scalable web applications using modern technologies. Work with React, Node.js, and cloud platforms.",
            "requirements": "5+ years experience, Bachelor's degree in CS",
            "skills": "React, Node.js, Python, AWS, Docker, JavaScript",
            "experience_level": "Senior",
            "salary_range": "120000-160000",
            "industry": "Technology",
            "benefits": "Health insurance, 401k, flexible hours",
            "work_type": "Full-time",
            "remote_allowed": "Yes"
        },
        {
            "job_id": 2,
            "title": "Frontend Developer",
            "company": "WebSolutions",
            "location": "Remote",
            "description": "Create responsive user interfaces using React and modern CSS. Collaborate with design team.",
            "requirements": "3+ years frontend experience",
            "skills": "React, JavaScript, HTML, CSS, TypeScript, Redux",
            "experience_level": "Mid-level",
            "salary_range": "80000-110000",
            "industry": "Technology",
            "benefits": "Health insurance, remote work",
            "work_type": "Full-time",
            "remote_allowed": "Yes"
        },
        {
            "job_id": 3,
            "title": "Python Developer",
            "company": "DataTech",
            "location": "New York, NY",
            "description": "Build data processing pipelines and APIs using Python, Django, and PostgreSQL.",
            "requirements": "4+ years Python experience",
            "skills": "Python, Django, PostgreSQL, REST APIs, Docker",
            "experience_level": "Mid-level",
            "salary_range": "90000-130000",
            "industry": "Technology",
            "benefits": "Health insurance, 401k",
            "work_type": "Full-time",
            "remote_allowed": "Hybrid"
        },
        {
            "job_id": 4,
            "title": "DevOps Engineer",
            "company": "CloudTech",
            "location": "Austin, TX",
            "description": "Manage cloud infrastructure, implement CI/CD pipelines, monitor system performance.",
            "requirements": "3+ years DevOps experience",
            "skills": "AWS, Docker, Kubernetes, Jenkins, Linux, Python",
            "experience_level": "Mid-level",
            "salary_range": "95000-135000",
            "industry": "Technology",
            "benefits": "Health insurance, stock options",
            "work_type": "Full-time",
            "remote_allowed": "No"
        },
        {
            "job_id": 5,
            "title": "Full Stack Developer",
            "company": "StartupXYZ",
            "location": "Seattle, WA",
            "description": "Work on both frontend and backend development using React, Node.js, and MongoDB.",
            "requirements": "2+ years full stack experience",
            "skills": "React, Node.js, MongoDB, JavaScript, Express.js",
            "experience_level": "Junior",
            "salary_range": "70000-100000",
            "industry": "Technology",
            "benefits": "Equity, flexible hours",
            "work_type": "Full-time",
            "remote_allowed": "Yes"
        }
    ]
    
    try:
        df = pd.DataFrame(sample_jobs)
        os.makedirs("data", exist_ok=True)
        df.to_csv("data/job_dataset.csv", index=False)
        print("✅ Sample dataset created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create sample dataset: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Starting Job Recommendation System Tests\n")
    
    # Check data files
    existing_files = check_data_files()
    
    # Create sample dataset if needed
    if not existing_files:
        if not create_sample_dataset():
            return
    
    # Test resume parser
    if not test_resume_parser():
        print("❌ Resume parser tests failed")
        return
    
    # Test job matcher
    if not test_job_matcher():
        print("❌ Job matcher tests failed")
        return
    
    print("\n✅ All tests passed! Job recommendation system is working.")

if __name__ == "__main__":
    main()
