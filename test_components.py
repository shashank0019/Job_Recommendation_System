#!/usr/bin/env python3
"""
Test the resume parser and job matcher components directly to identify the issue.
"""

import sys
import traceback
from pathlib import Path

# Add current directory to path
sys.path.append('.')

try:
    from resume_parser import ResumeParser
    from job_matcher import JobMatcher
    print("✅ Successfully imported modules")
except Exception as e:
    print(f"❌ Error importing modules: {e}")
    traceback.print_exc()
    sys.exit(1)

def test_resume_parser():
    """Test the resume parser component."""
    print("\n🔍 Testing ResumeParser...")
    try:
        parser = ResumeParser()
        
        # Test with simple text
        test_text = "John Doe, Software Engineer with 5 years experience in Python, React, JavaScript, AWS, MongoDB"
        
        result = parser.parse_resume(test_text)
        
        if result['success']:
            print("✅ Resume parsing successful")
            print(f"Skills found: {result['parsed_data'].get('skills', [])}")
        else:
            print(f"❌ Resume parsing failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Resume parser error: {e}")
        traceback.print_exc()

def test_job_matcher():
    """Test the job matcher component."""
    print("\n🔍 Testing JobMatcher...")
    try:
        matcher = JobMatcher()
        
        if not matcher.is_trained:
            print("⚠️  Model not trained, training now...")
            success = matcher.train_model()
            if not success:
                print("❌ Model training failed")
                return
            print("✅ Model training successful")
        
        # Test matching
        test_resume = "Software Engineer with Python, React, JavaScript experience"
        matches = matcher.find_matching_jobs(test_resume, top_k=5)
        
        print(f"✅ Found {len(matches)} job matches")
        
    except Exception as e:
        print(f"❌ Job matcher error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Testing backend components...")
    test_resume_parser()
    test_job_matcher()
    print("\n✨ Component testing complete!")