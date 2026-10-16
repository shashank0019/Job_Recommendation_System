#!/usr/bin/env python3
"""
Test Script for Career Guidance Platform

This script tests all major components to ensure they're working correctly.
Run this after training the model to verify everything is set up properly.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from resume_parser import ResumeParser
from job_matcher import JobMatcher
from api_client import JobAPIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_resume_parser():
    """Test the resume parser functionality."""
    logger.info("🧪 Testing Resume Parser...")
    
    try:
        parser = ResumeParser()
        
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

def test_job_matcher():
    """Test the job matcher functionality."""
    logger.info("\n🧪 Testing Job Matcher...")
    
    try:
        matcher = JobMatcher()
        
        # Check if model is trained
        if not matcher.is_trained:
            logger.error("❌ Job matcher model is not trained. Please run train_model.py first.")
            return False
        
        logger.info("✅ Job matcher model is trained and ready!")
        
        # Test with sample resume
        test_resume = """
        I am a software engineer with 5 years of experience in Python development.
        I have worked with Django, React, and AWS. I am proficient in SQL and have
        experience with Docker and Kubernetes. I have led teams and implemented
        CI/CD pipelines.
        """
        
        # Find matching jobs
        matches = matcher.find_matching_jobs(test_resume, top_k=5)
        
        if matches:
            logger.info(f"✅ Job matching successful! Found {len(matches)} matches:")
            for i, job in enumerate(matches[:3], 1):
                logger.info(f"   {i}. {job['title']} at {job['company']}")
                logger.info(f"      Location: {job['location']}")
                logger.info(f"      Similarity Score: {job['similarity_score']:.3f}")
                logger.info(f"      Skills: {job['skills']}")
                logger.info()
            
            return True
        else:
            logger.warning("⚠️  Job matching returned no results. This might indicate an issue.")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error testing job matcher: {e}")
        return False

def test_api_client():
    """Test the API client functionality."""
    logger.info("\n🧪 Testing API Client...")
    
    try:
        client = JobAPIClient()
        
        # Check API status
        status = client.get_api_status()
        logger.info(f"API Key Configured: {status['api_key_configured']}")
        logger.info(f"API Accessible: {status['api_accessible']}")
        
        if status['api_key_configured'] and status['api_accessible']:
            logger.info("✅ API client is working correctly!")
            
            # Test a simple search (optional)
            response = input("\n🔍 Do you want to test a live job search? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                logger.info("Searching for software engineering jobs...")
                jobs = client.search_jobs("software engineer", num_pages=1)
                logger.info(f"Found {len(jobs)} live jobs")
                
                if jobs:
                    logger.info("Sample job:")
                    job = jobs[0]
                    logger.info(f"   Title: {job['title']}")
                    logger.info(f"   Company: {job['company']}")
                    logger.info(f"   Location: {job['location']}")
            
            return True
        else:
            logger.warning("⚠️  API client is not fully configured, but this won't affect basic functionality.")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error testing API client: {e}")
        return False

def test_end_to_end():
    """Test the complete workflow from resume to job recommendations."""
    logger.info("\n🧪 Testing End-to-End Workflow...")
    
    try:
        # Initialize components
        parser = ResumeParser()
        matcher = JobMatcher()
        
        if not matcher.is_trained:
            logger.error("❌ Cannot test end-to-end: model not trained")
            return False
        
        # Sample resume
        test_resume = """
        I am a data scientist with 3 years of experience in machine learning.
        I have worked with Python, R, SQL, and various ML frameworks like TensorFlow.
        I have experience with data analysis, statistical modeling, and building
        predictive models. I have worked with cloud platforms like AWS and have
        experience with Docker and Git.
        """
        
        # Step 1: Parse resume
        logger.info("Step 1: Parsing resume...")
        parse_result = parser.parse_resume(test_resume)
        
        if not parse_result['success']:
            logger.error("❌ Resume parsing failed in end-to-end test")
            return False
        
        logger.info(f"✅ Resume parsed successfully. Extracted {parse_result['parsed_data']['total_skills']} skills.")
        
        # Step 2: Find job matches
        logger.info("Step 2: Finding job matches...")
        matches = matcher.find_matching_jobs(test_resume, top_k=3)
        
        if not matches:
            logger.error("❌ No job matches found in end-to-end test")
            return False
        
        logger.info(f"✅ Found {len(matches)} job matches:")
        for i, job in enumerate(matches, 1):
            logger.info(f"   {i}. {job['title']} at {job['company']} (Score: {job['similarity_score']:.3f})")
        
        logger.info("🎉 End-to-end test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in end-to-end test: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("🚀 Starting Career Guidance Platform System Tests")
    logger.info("=" * 60)
    
    tests = [
        ("Resume Parser", test_resume_parser),
        ("Job Matcher", test_job_matcher),
        ("API Client", test_api_client),
        ("End-to-End Workflow", test_end_to_end)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            logger.error(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}")
        if success:
            passed += 1
    
    logger.info(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! The Career Guidance Platform is ready to use.")
        logger.info("🚀 You can now start the application with: python app.py")
        return True
    else:
        logger.error(f"❌ {total - passed} test(s) failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⏹️  Testing interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1) 