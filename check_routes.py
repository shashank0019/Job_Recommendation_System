#!/usr/bin/env python3
"""Check what routes are registered in the Flask app"""

from app import app

def check_routes():
    """Check all registered routes in the Flask app"""
    print("Registered Routes in Flask App:")
    print("=" * 50)
    
    for rule in app.url_map.iter_rules():
        methods = ', '.join(sorted(rule.methods))
        print(f"{rule.rule:<30} -> {rule.endpoint:<25} [{methods}]")
    
    print("\nLooking for job posting and interview experience routes...")
    
    job_routes = [rule for rule in app.url_map.iter_rules() if 'job' in rule.rule.lower()]
    interview_routes = [rule for rule in app.url_map.iter_rules() if 'experience' in rule.rule.lower()]
    
    print(f"\nJob-related routes found: {len(job_routes)}")
    for route in job_routes:
        print(f"  {route.rule} -> {route.endpoint}")
    
    print(f"\nInterview-related routes found: {len(interview_routes)}")
    for route in interview_routes:
        print(f"  {route.rule} -> {route.endpoint}")

if __name__ == "__main__":
    check_routes()
