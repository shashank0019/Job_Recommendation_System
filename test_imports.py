#!/usr/bin/env python3

try:
    from api.job_posting_routes import job_posting_bp
    print("✅ Job posting routes imported successfully")
except ImportError as e:
    print(f"❌ Job posting routes import failed: {e}")

try:
    from api.interview_experience_routes import interview_experience_bp
    print("✅ Interview experience routes imported successfully")
except ImportError as e:
    print(f"❌ Interview experience routes import failed: {e}")

try:
    from models.job_posting import JobPosting
    print("✅ Job posting model imported successfully")
except ImportError as e:
    print(f"❌ Job posting model import failed: {e}")

try:
    from models.interview_experience import InterviewExperience
    print("✅ Interview experience model imported successfully")
except ImportError as e:
    print(f"❌ Interview experience model import failed: {e}")

print("\n🎉 All imports completed!")
