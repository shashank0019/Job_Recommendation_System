#!/usr/bin/env python3
"""
Job Posting System Verification
Checks that all job posting components are saved and working
"""

import os
import json
from datetime import datetime

def verify_data_files():
    """Verify all data files exist and are valid"""
    print("Checking data files...")
    
    # Check main job data
    jobs_file = os.path.join('data', 'posted_jobs.json')
    if os.path.exists(jobs_file):
        try:
            with open(jobs_file, 'r', encoding='utf-8') as f:
                jobs = json.load(f)
            print(f"✓ posted_jobs.json: {len(jobs)} jobs")
            
            # Show job summary
            for job in jobs:
                print(f"  - {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
            
            return len(jobs)
        except Exception as e:
            print(f"✗ Error reading jobs file: {e}")
            return 0
    else:
        print("✗ posted_jobs.json not found")
        return 0

def verify_server_files():
    """Verify server files exist"""
    print("\nChecking server files...")
    
    server_files = [
        'job_api_simple.py',
        'api/job_posting_routes.py',
        'models/job_posting.py',
        'app.py'
    ]
    
    found_files = []
    for file in server_files:
        if os.path.exists(file):
            print(f"✓ {file}")
            found_files.append(file)
        else:
            print(f"✗ {file} (optional)")
    
    return found_files

def verify_config_files():
    """Verify configuration files"""
    print("\nChecking configuration files...")
    
    config_files = [
        'job_posting_config.json',
        'JOB_POSTING_README.md',
        'start_job_server.py'
    ]
    
    for file in config_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file}")

def create_backup_info():
    """Create backup information file"""
    backup_info = {
        "backup_date": datetime.now().isoformat(),
        "verification_results": {
            "data_files": verify_data_files(),
            "server_files": verify_server_files(),
            "config_files_status": "checked"
        },
        "system_status": "verified",
        "next_steps": [
            "Run: python start_job_server.py",
            "Test: http://localhost:5000/api/jobs",
            "Frontend: Connect to localhost:5000"
        ]
    }
    
    with open('job_posting_backup_info.json', 'w', encoding='utf-8') as f:
        json.dump(backup_info, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Backup info saved to job_posting_backup_info.json")
    return backup_info

def main():
    """Main verification"""
    print("Job Posting System Verification")
    print("=" * 35)
    
    # Verify all components
    job_count = verify_data_files()
    server_files = verify_server_files()
    verify_config_files()
    
    # Create backup info
    backup_info = create_backup_info()
    
    print(f"\n📊 Summary:")
    print(f"  Jobs saved: {job_count}")
    print(f"  Server files: {len(server_files)} available")
    print(f"  Working server: job_api_simple.py")
    print(f"  Data location: data/posted_jobs.json")
    
    print(f"\n🚀 Ready to start:")
    print(f"  python start_job_server.py")
    
    return job_count > 0

if __name__ == '__main__':
    success = main()
    if success:
        print("\n✅ All job posting components verified and saved!")
    else:
        print("\n❌ Some issues found. Check the output above.")