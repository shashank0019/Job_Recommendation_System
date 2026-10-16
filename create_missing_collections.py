from config.database import get_db_config
from datetime import datetime
from bson import ObjectId

def create_missing_collections():
    """Create the missing job_postings and interview_experiences collections"""
    print("🔧 Creating Missing Collections in MongoDB Atlas")
    print("=" * 50)
    
    config = get_db_config()
    config.connect()
    
    if config.db is not None:
        # Check current collections
        existing_collections = config.db.list_collection_names()
        print(f"📋 Current collections: {existing_collections}")
        print()
        
        # Create job_postings collection with sample data
        if 'job_postings' not in existing_collections:
            print("📝 Creating job_postings collection...")
            
            sample_job = {
                "_id": ObjectId(),
                "title": "Senior React Developer",
                "company": "TechCorp Inc",
                "description": "We are looking for an experienced React developer to join our frontend team.",
                "requirements": ["React", "JavaScript", "TypeScript", "Redux", "CSS"],
                "location": "San Francisco, CA",
                "salary_range": "$120,000 - $150,000",
                "job_type": "full-time",
                "posted_by": ObjectId("507f1f77bcf86cd799439011"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "status": "active",
                "contact_email": "hr@techcorp.com",
                "application_url": "https://techcorp.com/careers/react-dev",
                "tags": ["React", "Frontend", "JavaScript"],
                "experience_level": "senior",
                "remote_allowed": True,
                "applications_count": 0
            }
            
            jobs_collection = config.db.job_postings
            result = jobs_collection.insert_one(sample_job)
            print(f"✅ Created job_postings collection with sample job: {result.inserted_id}")
        else:
            print("✅ job_postings collection already exists")
        
        # Create interview_experiences collection with sample data
        if 'interview_experiences' not in existing_collections:
            print("📝 Creating interview_experiences collection...")
            
            sample_experience = {
                "_id": ObjectId(),
                "company": "Google",
                "position": "Software Engineer",
                "experience_text": "The interview process was thorough with 4 rounds. Started with a phone screening, followed by 3 technical rounds covering algorithms, system design, and behavioral questions.",
                "interview_type": "technical",
                "difficulty_rating": 4,
                "shared_by": ObjectId("507f1f77bcf86cd799439014"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "interview_date": datetime.utcnow(),
                "outcome": "selected",
                "questions_asked": [
                    "Implement a binary search algorithm",
                    "Design a URL shortener like bit.ly",
                    "Tell me about a challenging project you worked on"
                ],
                "tips": [
                    "Practice coding problems daily",
                    "Understand system design fundamentals",
                    "Prepare STAR format answers for behavioral questions"
                ],
                "tags": ["Algorithms", "System Design", "Behavioral"],
                "location": "Mountain View, CA",
                "interview_rounds": 4,
                "preparation_time": "3 months",
                "anonymous": False,
                "status": "active",
                "helpful_votes": 15,
                "total_votes": 18
            }
            
            experiences_collection = config.db.interview_experiences
            result = experiences_collection.insert_one(sample_experience)
            print(f"✅ Created interview_experiences collection with sample experience: {result.inserted_id}")
        else:
            print("✅ interview_experiences collection already exists")
        
        print()
        
        # Verify collections were created
        updated_collections = config.db.list_collection_names()
        print(f"📋 Updated collections: {updated_collections}")
        
        # Count documents in each collection
        for collection_name in ['users', 'sessions', 'job_postings', 'interview_experiences']:
            if collection_name in updated_collections:
                count = config.db[collection_name].count_documents({})
                print(f"📊 {collection_name}: {count} documents")
        
        print("\n🎉 Collections setup complete!")
        
    else:
        print("❌ Database connection failed")

if __name__ == "__main__":
    create_missing_collections()
