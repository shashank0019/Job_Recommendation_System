#!/usr/bin/env python3
"""
Quick test script to debug job recommendation issues
"""

import sys
import os
import json

# Add current directory to path
sys.path.append('.')

def test_basic_functionality():
    print("🔍 Testing basic functionality...")
    
    # Test 1: Check files exist
    print("\n1. Checking data files:")
    files = [
        'data/unified_job_dataset.csv',
        'data/posted_jobs.json',
        'data/job_dataset.csv'
    ]
    
    for file in files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"   ✅ {file} - {size} bytes")
        else:
            print(f"   ❌ {file} - Missing")
    
    # Test 2: Try loading job matcher
    print("\n2. Testing job matcher import:")
    try:
        from job_matcher import JobMatcher
        matcher = JobMatcher()
        print("   ✅ JobMatcher loaded successfully")
    except Exception as e:
        print(f"   ❌ JobMatcher error: {e}")
    
    # Test 3: Try loading resume parser  
    print("\n3. Testing resume parser import:")
    try:
        from resume_parser import ResumeParser
        parser = ResumeParser()
        print("   ✅ ResumeParser loaded successfully")
    except Exception as e:
        print(f"   ❌ ResumeParser error: {e}")
    
    # Test 4: Try basic CSV loading
    print("\n4. Testing CSV loading:")
    try:
        import pandas as pd
        df = pd.read_csv('data/unified_job_dataset.csv')
        print(f"   ✅ Loaded {len(df)} jobs from unified dataset")
        
        # Test a few rows
        for i in range(min(3, len(df))):
            row = df.iloc[i]
            skills = row.get('skills', '')
            print(f"   Job {i+1}: {row.get('title')} - Skills: {skills[:50]}...")
            
    except Exception as e:
        print(f"   ❌ CSV loading error: {e}")
    
    # Test 5: Test posted jobs JSON
    print("\n5. Testing posted jobs JSON:")
    try:
        with open('data/posted_jobs.json', 'r') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            print(f"   ✅ Loaded {len(data)} live jobs (array format)")
        elif isinstance(data, dict) and 'jobs' in data:
            print(f"   ✅ Loaded {len(data['jobs'])} live jobs (object format)")
        else:
            print(f"   ⚠️  Unknown format: {type(data)}")
            
    except Exception as e:
        print(f"   ❌ JSON loading error: {e}")

if __name__ == "__main__":
    test_basic_functionality()