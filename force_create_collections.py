from config.database import get_db_config
from datetime import datetime
from bson import ObjectId

def force_create_collections():
    """Force create collections by inserting documents directly"""
    print("🔧 Force Creating Collections in MongoDB Atlas")
    print("=" * 60)
    
    config = get_db_config()
    config.connect()
    
    if config.db is not None:
        print(f"🗄️  Connected to Database: {config.database_name}")
        print(f"🌐 Cluster: {config.client.address}")
        print()
        
        # Force create job_postings collection
        print("📝 Force creating job_postings collection...")
        
        # Delete existing collection and recreate
        try:
            config.db.job_postings.drop()
            print("   🗑️  Dropped existing job_postings collection")
        except:
            print("   ℹ️  No existing job_postings to drop")
        
        # Create with multiple sample jobs
        sample_jobs = [
            {
                "_id": ObjectId(),
                "title": "Frontend Developer",
                "company": "Atlas Tech Solutions", 
                "description": "Join our team to build amazing user interfaces with React and modern web technologies.",
                "requirements": ["React", "JavaScript", "HTML", "CSS", "Git"],
                "location": "Bangalore, India",
                "salary_range": "₹8,00,000 - ₹12,00,000",
                "job_type": "full-time",
                "posted_by": ObjectId(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "status": "active",
                "contact_email": "hr@atlastech.com",
                "application_url": "https://atlastech.com/careers",
                "tags": ["React", "Frontend", "JavaScript"],
                "experience_level": "mid",
                "remote_allowed": True,
                "applications_count": 0
            },
            {
                "_id": ObjectId(),
                "title": "Python Backend Developer",
                "company": "DataCorp India",
                "description": "Build scalable backend systems using Python, Django, and cloud technologies.",
                "requirements": ["Python", "Django", "PostgreSQL", "AWS", "Docker"],
                "location": "Mumbai, India",
                "salary_range": "₹10,00,000 - ₹15,00,000",
                "job_type": "full-time", 
                "posted_by": ObjectId(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "status": "active",
                "contact_email": "careers@datacorp.in",
                "application_url": "https://datacorp.in/jobs",
                "tags": ["Python", "Backend", "Django"],
                "experience_level": "senior",
                "remote_allowed": False,
                "applications_count": 0
            }
        ]
        
        result = config.db.job_postings.insert_many(sample_jobs)
        print(f"   ✅ Inserted {len(result.inserted_ids)} job postings")
        
        # Force create interview_experiences collection
        print("📝 Force creating interview_experiences collection...")
        
        try:
            config.db.interview_experiences.drop()
            print("   🗑️  Dropped existing interview_experiences collection")
        except:
            print("   ℹ️  No existing interview_experiences to drop")
        
        sample_experiences = [
            {
                "_id": ObjectId(),
                "company": "Infosys",
                "position": "Software Engineer",
                "experience_text": "The interview had 3 rounds - technical screening, coding round, and HR discussion. Questions focused on Java, data structures, and problem-solving skills.",
                "interview_type": "technical",
                "difficulty_rating": 3,
                "shared_by": ObjectId(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "interview_date": datetime.utcnow(),
                "outcome": "selected",
                "questions_asked": [
                    "Explain OOP concepts in Java",
                    "Implement a linked list reversal",
                    "Why do you want to join Infosys?"
                ],
                "tips": [
                    "Practice basic data structures",
                    "Be confident in your answers",
                    "Research about the company"
                ],
                "tags": ["Java", "Data Structures", "OOP"],
                "location": "Bangalore, India",
                "interview_rounds": 3,
                "preparation_time": "2 weeks",
                "anonymous": False,
                "status": "active",
                "helpful_votes": 8,
                "total_votes": 10
            },
            {
                "_id": ObjectId(),
                "company": "TCS",
                "position": "Full Stack Developer",
                "experience_text": "Very structured interview process. Started with aptitude test, then technical interview covering both frontend and backend concepts.",
                "interview_type": "technical",
                "difficulty_rating": 2,
                "shared_by": ObjectId(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "interview_date": datetime.utcnow(),
                "outcome": "selected",
                "questions_asked": [
                    "Difference between React and Angular",
                    "SQL vs NoSQL databases",
                    "Explain REST API principles"
                ],
                "tips": [
                    "Know both frontend and backend basics",
                    "Practice SQL queries",
                    "Understand web development fundamentals"
                ],
                "tags": ["Full Stack", "React", "SQL"],
                "location": "Chennai, India",
                "interview_rounds": 2,
                "preparation_time": "1 month",
                "anonymous": False,
                "status": "active",
                "helpful_votes": 12,
                "total_votes": 15
            }
        ]
        
        result = config.db.interview_experiences.insert_many(sample_experiences)
        print(f"   ✅ Inserted {len(result.inserted_ids)} interview experiences")
        
        print()
        
        # Verify collections exist and have data
        print("🔍 Verifying Collections:")
        collections = config.db.list_collection_names()
        for collection_name in collections:
            count = config.db[collection_name].count_documents({})
            print(f"   ✅ {collection_name}: {count} documents")
        
        print()
        print("🎯 Collections should now be visible in MongoDB Atlas UI!")
        print("   1. Go to your MongoDB Atlas dashboard")
        print("   2. Navigate to 'Browse Collections'")
        print("   3. Select 'career_guidance_platform' database")
        print("   4. You should see job_postings and interview_experiences")
        
    else:
        print("❌ Database connection failed")

if __name__ == "__main__":
    force_create_collections()
