"""
Force collections to be visible in MongoDB Atlas UI
"""
from config.database import get_db_config
from datetime import datetime
from bson import ObjectId

def force_atlas_visibility():
    """Force collections to appear in Atlas UI by creating indexes and more data"""
    print("Force Atlas UI Visibility")
    print("=" * 30)
    
    config = get_db_config()
    config.connect()
    
    if config.db is not None:
        print("Connected to MongoDB Atlas")
        print(f"Database: {config.database_name}")
        print()
        
        # Force job_postings collection visibility
        print("Making job_postings visible...")
        jobs_collection = config.db.job_postings
        
        # Drop and recreate with more obvious data
        jobs_collection.drop()
        
        # Insert multiple jobs with clear, obvious data
        obvious_jobs = []
        companies = ["Google", "Microsoft", "Amazon", "Facebook", "Apple"]
        positions = ["Software Engineer", "Frontend Developer", "Backend Developer", "Full Stack Developer", "Data Scientist"]
        
        for i, (company, position) in enumerate(zip(companies, positions)):
            job = {
                "_id": ObjectId(),
                "title": position,
                "company": company,
                "description": f"Join {company} as a {position}. Great opportunity for career growth.",
                "requirements": ["Programming", "Problem Solving", "Communication"],
                "location": f"City {i+1}, India",
                "salary_range": f"{(i+1)*5}-{(i+1)*8} LPA",
                "job_type": "full-time",
                "posted_by": ObjectId(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "status": "active",
                "contact_email": f"hr@{company.lower()}.com",
                "application_url": f"https://{company.lower()}.com/careers",
                "tags": ["Tech", "Software"],
                "experience_level": "mid",
                "remote_allowed": True,
                "applications_count": i * 5
            }
            obvious_jobs.append(job)
        
        result = jobs_collection.insert_many(obvious_jobs)
        print(f"   Inserted {len(result.inserted_ids)} job postings")
        
        # Create index to make it more visible
        jobs_collection.create_index("company")
        jobs_collection.create_index("title")
        print("   Created indexes on job_postings")
        
        # Force interview_experiences collection visibility
        print("Making interview_experiences visible...")
        exp_collection = config.db.interview_experiences
        
        # Drop and recreate
        exp_collection.drop()
        
        # Insert obvious interview experiences
        obvious_experiences = []
        for i, company in enumerate(companies):
            exp = {
                "_id": ObjectId(),
                "company": company,
                "position": f"Software Engineer at {company}",
                "experience_text": f"Had a great interview experience at {company}. The process was smooth and professional.",
                "interview_type": "technical",
                "difficulty_rating": i + 1,
                "shared_by": ObjectId(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "interview_date": datetime.utcnow(),
                "outcome": "selected" if i % 2 == 0 else "rejected",
                "questions_asked": [
                    f"Technical question about {company}",
                    "Coding challenge",
                    "System design"
                ],
                "tips": [
                    f"Prepare well for {company}",
                    "Practice coding",
                    "Be confident"
                ],
                "tags": ["Technical", "Coding"],
                "location": f"{company} Office",
                "interview_rounds": i + 2,
                "preparation_time": f"{i+1} weeks",
                "anonymous": False,
                "status": "active",
                "helpful_votes": i * 3,
                "total_votes": i * 4
            }
            obvious_experiences.append(exp)
        
        result = exp_collection.insert_many(obvious_experiences)
        print(f"   Inserted {len(result.inserted_ids)} interview experiences")
        
        # Create indexes
        exp_collection.create_index("company")
        exp_collection.create_index("position")
        print("   Created indexes on interview_experiences")
        
        print()
        print("Verification:")
        
        # Verify all collections
        all_collections = config.db.list_collection_names()
        print(f"All collections: {all_collections}")
        
        for collection_name in all_collections:
            count = config.db[collection_name].count_documents({})
            print(f"   {collection_name}: {count} documents")
        
        print()
        print("SUCCESS!")
        print("Collections should now be visible in Atlas UI:")
        print("1. Go to MongoDB Atlas")
        print("2. Browse Collections")
        print("3. Select career_guidance_platform database")
        print("4. You should see all 4 collections with data")
        print()
        print("If still not visible:")
        print("- Hard refresh browser (Ctrl+Shift+R)")
        print("- Try different browser")
        print("- Check you're in correct project/organization")
        
    else:
        print("Database connection failed")

if __name__ == "__main__":
    force_atlas_visibility()
