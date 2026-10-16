#!/usr/bin/env python3

"""
Test script to create sample data and verify database collections are created
"""

def test_database_collections():
    print("🧪 Testing database collection creation...")
    
    try:
        # Test database connection
        from config.database import get_db_config
        db_config = get_db_config()
        
        if not db_config.connect():
            print("❌ Failed to connect to database")
            return False
            
        print("✅ Database connection successful")
        
        # Check current collections
        if db_config.use_local_fallback:
            print("📁 Using local storage fallback")
        else:
            collections = db_config.db.list_collection_names()
            print(f"📋 Current collections: {collections}")
        
        # Test JobPosting model
        print("\n🔧 Testing JobPosting model...")
        from models.job_posting import JobPosting
        
        # Create a sample job posting
        sample_job = JobPosting.create(
            title="Software Engineer",
            company="Test Company",
            description="A test job posting to verify database integration",
            requirements=["Python", "Flask", "MongoDB"],
            location="Remote",
            salary_range="50000-70000",
            job_type="full-time",
            posted_by="test_user_id",
            tags=["python", "backend", "remote"]
        )
        
        if sample_job:
            print("✅ Sample job posting created successfully")
            print(f"   Job ID: {sample_job._id}")
            print(f"   Title: {sample_job.title}")
            print(f"   Company: {sample_job.company}")
        else:
            print("❌ Failed to create sample job posting")
            
        # Test InterviewExperience model
        print("\n🔧 Testing InterviewExperience model...")
        from models.interview_experience import InterviewExperience
        
        # Create a sample interview experience
        sample_experience = InterviewExperience.create(
            company="Test Company",
            position="Software Engineer",
            experience_text="This is a test interview experience to verify database integration. The interview was conducted remotely and involved technical questions.",
            interview_type="technical",
            difficulty_rating=3,
            shared_by="test_user_id",
            outcome="selected",
            questions_asked=["What is your experience with Python?", "Explain REST APIs"],
            tips=["Practice coding problems", "Research the company"],
            tags=["python", "technical", "remote"]
        )
        
        if sample_experience:
            print("✅ Sample interview experience created successfully")
            print(f"   Experience ID: {sample_experience._id}")
            print(f"   Company: {sample_experience.company}")
            print(f"   Position: {sample_experience.position}")
        else:
            print("❌ Failed to create sample interview experience")
            
        # Check collections again
        print("\n📋 Checking collections after data creation...")
        if not db_config.use_local_fallback:
            collections = db_config.db.list_collection_names()
            print(f"   Collections now: {collections}")
            
            # Count documents
            if 'job_postings' in collections:
                job_count = db_config.db.job_postings.count_documents({})
                print(f"   📊 Job postings count: {job_count}")
                
            if 'interview_experiences' in collections:
                exp_count = db_config.db.interview_experiences.count_documents({})
                print(f"   📊 Interview experiences count: {exp_count}")
        
        print("\n🎉 Database integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_database_collections()
