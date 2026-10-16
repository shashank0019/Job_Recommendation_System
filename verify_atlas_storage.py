"""
Verify that job posting and interview experience data is stored in MongoDB Atlas
"""
from config.database import get_db_config
from datetime import datetime
import json

def verify_atlas_storage():
    """Comprehensive verification of Atlas storage for job postings and interview experiences"""
    print("🔍 MongoDB Atlas Storage Verification")
    print("=" * 50)
    
    config = get_db_config()
    config.connect()
    
    if config.db is not None:
        print("✅ CONNECTED TO MONGODB ATLAS")
        print(f"🌐 Cluster: {config.client.address}")
        print(f"🗄️  Database: {config.database_name}")
        print(f"🔗 Connection: {config.connection_string[:50]}...")
        print(f"📍 Using Local Fallback: {config.use_local_fallback}")
        print()
        
        if config.use_local_fallback:
            print("❌ WARNING: Using local JSON fallback instead of Atlas!")
            return
        
        print("📊 ATLAS COLLECTIONS VERIFICATION:")
        collections = config.db.list_collection_names()
        
        for collection_name in collections:
            count = config.db[collection_name].count_documents({})
            print(f"   ✅ {collection_name}: {count} documents")
        
        print()
        
        # Detailed verification of job_postings
        print("💼 JOB POSTINGS VERIFICATION:")
        if 'job_postings' in collections:
            jobs_collection = config.db.job_postings
            job_count = jobs_collection.count_documents({})
            print(f"   📊 Total job postings in Atlas: {job_count}")
            
            if job_count > 0:
                print("   📋 Sample job postings from Atlas:")
                sample_jobs = list(jobs_collection.find({}).limit(3))
                for i, job in enumerate(sample_jobs, 1):
                    print(f"      {i}. {job.get('title', 'No Title')} at {job.get('company', 'No Company')}")
                    print(f"         Location: {job.get('location', 'No Location')}")
                    print(f"         Created: {job.get('created_at', 'No Date')}")
                    print(f"         Atlas ID: {job.get('_id')}")
                    print()
                
                # Test write operation to Atlas
                print("   🧪 Testing WRITE to Atlas (job_postings):")
                test_job = {
                    "title": "Test Job - Atlas Verification",
                    "company": "Atlas Test Company",
                    "description": "This is a test job to verify Atlas storage",
                    "requirements": ["Testing", "Verification"],
                    "location": "Atlas Cloud",
                    "salary_range": "Test Range",
                    "job_type": "full-time",
                    "posted_by": "test_user_id",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "status": "active",
                    "contact_email": "test@atlas.com",
                    "tags": ["Test", "Atlas"],
                    "experience_level": "entry",
                    "remote_allowed": True,
                    "applications_count": 0
                }
                
                try:
                    result = jobs_collection.insert_one(test_job)
                    print(f"      ✅ SUCCESS: Inserted test job with ID: {result.inserted_id}")
                    
                    # Verify it was actually stored
                    stored_job = jobs_collection.find_one({"_id": result.inserted_id})
                    if stored_job:
                        print(f"      ✅ VERIFIED: Test job retrieved from Atlas")
                        print(f"         Title: {stored_job.get('title')}")
                        print(f"         Company: {stored_job.get('company')}")
                    
                    # Clean up test data
                    jobs_collection.delete_one({"_id": result.inserted_id})
                    print(f"      🧹 Cleaned up test job")
                    
                except Exception as e:
                    print(f"      ❌ WRITE FAILED: {e}")
            else:
                print("   ⚠️  No job postings found in Atlas")
        else:
            print("   ❌ job_postings collection not found in Atlas")
        
        print()
        
        # Detailed verification of interview_experiences
        print("🎯 INTERVIEW EXPERIENCES VERIFICATION:")
        if 'interview_experiences' in collections:
            exp_collection = config.db.interview_experiences
            exp_count = exp_collection.count_documents({})
            print(f"   📊 Total interview experiences in Atlas: {exp_count}")
            
            if exp_count > 0:
                print("   📋 Sample interview experiences from Atlas:")
                sample_experiences = list(exp_collection.find({}).limit(3))
                for i, exp in enumerate(sample_experiences, 1):
                    print(f"      {i}. {exp.get('position', 'No Position')} at {exp.get('company', 'No Company')}")
                    print(f"         Type: {exp.get('interview_type', 'No Type')}")
                    print(f"         Difficulty: {exp.get('difficulty_rating', 'No Rating')}/5")
                    print(f"         Created: {exp.get('created_at', 'No Date')}")
                    print(f"         Atlas ID: {exp.get('_id')}")
                    print()
                
                # Test write operation to Atlas
                print("   🧪 Testing WRITE to Atlas (interview_experiences):")
                test_experience = {
                    "company": "Atlas Test Company",
                    "position": "Test Position - Atlas Verification",
                    "experience_text": "This is a test interview experience to verify Atlas storage",
                    "interview_type": "technical",
                    "difficulty_rating": 3,
                    "shared_by": "test_user_id",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "interview_date": datetime.utcnow(),
                    "outcome": "selected",
                    "questions_asked": ["Test question 1", "Test question 2"],
                    "tips": ["Test tip 1", "Test tip 2"],
                    "tags": ["Test", "Atlas"],
                    "location": "Atlas Cloud",
                    "interview_rounds": 2,
                    "preparation_time": "1 week",
                    "anonymous": False,
                    "status": "active",
                    "helpful_votes": 0,
                    "total_votes": 0
                }
                
                try:
                    result = exp_collection.insert_one(test_experience)
                    print(f"      ✅ SUCCESS: Inserted test experience with ID: {result.inserted_id}")
                    
                    # Verify it was actually stored
                    stored_exp = exp_collection.find_one({"_id": result.inserted_id})
                    if stored_exp:
                        print(f"      ✅ VERIFIED: Test experience retrieved from Atlas")
                        print(f"         Position: {stored_exp.get('position')}")
                        print(f"         Company: {stored_exp.get('company')}")
                    
                    # Clean up test data
                    exp_collection.delete_one({"_id": result.inserted_id})
                    print(f"      🧹 Cleaned up test experience")
                    
                except Exception as e:
                    print(f"      ❌ WRITE FAILED: {e}")
            else:
                print("   ⚠️  No interview experiences found in Atlas")
        else:
            print("   ❌ interview_experiences collection not found in Atlas")
        
        print()
        print("🎯 FINAL VERIFICATION SUMMARY:")
        print("=" * 50)
        
        if not config.use_local_fallback:
            print("✅ DATA IS STORED IN MONGODB ATLAS")
            print("✅ Not using local JSON fallback")
            print(f"✅ Connected to Atlas cluster: {config.client.address}")
            print(f"✅ Database: {config.database_name}")
            
            job_exists = 'job_postings' in collections
            exp_exists = 'interview_experiences' in collections
            
            if job_exists and exp_exists:
                print("✅ Both job_postings and interview_experiences collections exist in Atlas")
                print("✅ Your application data is safely stored in MongoDB Atlas cloud")
            else:
                print("⚠️  Some collections may be missing")
        else:
            print("❌ WARNING: Using local storage instead of Atlas")
        
    else:
        print("❌ FAILED TO CONNECT TO DATABASE")

if __name__ == "__main__":
    verify_atlas_storage()
