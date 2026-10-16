from config.database import get_db_config
from datetime import datetime
from bson import ObjectId

def add_sample_data():
    """Add sample job postings and interview experiences"""
    config = get_db_config()
    config.connect()
    
    if config.db is None:
        print("❌ Database connection failed")
        return
    
    db = config.db
    
    # Sample job postings
    sample_jobs = [
        {
            "_id": ObjectId(),
            "title": "Senior React Developer",
            "company": "TechCorp Inc",
            "description": "We are looking for an experienced React developer to join our frontend team. You will be responsible for building user interfaces and ensuring great user experience.",
            "requirements": ["React", "JavaScript", "TypeScript", "Redux", "CSS"],
            "location": "San Francisco, CA",
            "salary_range": "$120,000 - $150,000",
            "job_type": "full-time",
            "posted_by": ObjectId("507f1f77bcf86cd799439011"),  # Sample user ID
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "status": "active",
            "contact_email": "hr@techcorp.com",
            "application_url": "https://techcorp.com/careers/react-dev",
            "tags": ["React", "Frontend", "JavaScript"],
            "experience_level": "senior",
            "remote_allowed": True,
            "applications_count": 0
        },
        {
            "_id": ObjectId(),
            "title": "Python Backend Engineer",
            "company": "DataFlow Solutions",
            "description": "Join our backend team to build scalable APIs and data processing systems using Python and Django.",
            "requirements": ["Python", "Django", "PostgreSQL", "Redis", "AWS"],
            "location": "New York, NY",
            "salary_range": "$100,000 - $130,000",
            "job_type": "full-time",
            "posted_by": ObjectId("507f1f77bcf86cd799439012"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "status": "active",
            "contact_email": "careers@dataflow.com",
            "application_url": "https://dataflow.com/jobs/python-engineer",
            "tags": ["Python", "Backend", "Django"],
            "experience_level": "mid",
            "remote_allowed": False,
            "applications_count": 0
        },
        {
            "_id": ObjectId(),
            "title": "Full Stack Developer Intern",
            "company": "StartupXYZ",
            "description": "Great opportunity for students to learn full stack development with modern technologies.",
            "requirements": ["JavaScript", "Node.js", "React", "MongoDB"],
            "location": "Remote",
            "salary_range": "$20 - $25 per hour",
            "job_type": "internship",
            "posted_by": ObjectId("507f1f77bcf86cd799439013"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "status": "active",
            "contact_email": "internships@startupxyz.com",
            "application_url": "https://startupxyz.com/internships",
            "tags": ["JavaScript", "Full Stack", "Internship"],
            "experience_level": "entry",
            "remote_allowed": True,
            "applications_count": 0
        }
    ]
    
    # Sample interview experiences
    sample_experiences = [
        {
            "_id": ObjectId(),
            "company": "Google",
            "position": "Software Engineer",
            "experience_text": "The interview process was thorough with 4 rounds. Started with a phone screening, followed by 3 technical rounds covering algorithms, system design, and behavioral questions. The interviewers were friendly and provided hints when needed.",
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
        },
        {
            "_id": ObjectId(),
            "company": "Microsoft",
            "position": "Frontend Developer",
            "experience_text": "Great experience overall. The team was welcoming and the questions were fair. They focused more on practical coding skills and less on theoretical computer science.",
            "interview_type": "technical",
            "difficulty_rating": 3,
            "shared_by": ObjectId("507f1f77bcf86cd799439015"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "interview_date": datetime.utcnow(),
            "outcome": "selected",
            "questions_asked": [
                "Build a React component with state management",
                "Optimize a slow-loading web page",
                "Explain the difference between var, let, and const"
            ],
            "tips": [
                "Know React hooks well",
                "Understand web performance optimization",
                "Be ready to code live during the interview"
            ],
            "tags": ["React", "JavaScript", "Frontend"],
            "location": "Seattle, WA",
            "interview_rounds": 3,
            "preparation_time": "2 months",
            "anonymous": False,
            "status": "active",
            "helpful_votes": 12,
            "total_votes": 14
        },
        {
            "_id": ObjectId(),
            "company": "Amazon",
            "position": "Software Development Engineer",
            "experience_text": "The interview was challenging but fair. Heavy focus on Amazon's leadership principles. Make sure to prepare examples that demonstrate each principle.",
            "interview_type": "behavioral",
            "difficulty_rating": 4,
            "shared_by": ObjectId("507f1f77bcf86cd799439016"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "interview_date": datetime.utcnow(),
            "outcome": "rejected",
            "questions_asked": [
                "Tell me about a time you had to work with a difficult team member",
                "Describe a situation where you had to learn something quickly",
                "Give an example of when you took ownership of a problem"
            ],
            "tips": [
                "Study Amazon's 14 leadership principles",
                "Prepare 2-3 examples for each principle",
                "Use the STAR method for all answers"
            ],
            "tags": ["Leadership Principles", "Behavioral", "STAR Method"],
            "location": "Austin, TX",
            "interview_rounds": 5,
            "preparation_time": "1 month",
            "anonymous": False,
            "status": "active",
            "helpful_votes": 8,
            "total_votes": 10
        }
    ]
    
    # Insert sample data
    try:
        # Insert job postings
        jobs_collection = db.job_postings
        result = jobs_collection.insert_many(sample_jobs)
        print(f"✅ Inserted {len(result.inserted_ids)} job postings")
        
        # Insert interview experiences
        experiences_collection = db.interview_experiences
        result = experiences_collection.insert_many(sample_experiences)
        print(f"✅ Inserted {len(result.inserted_ids)} interview experiences")
        
        print("\n🎉 Sample data added successfully!")
        
        # Verify the data
        job_count = jobs_collection.count_documents({})
        exp_count = experiences_collection.count_documents({})
        print(f"📊 Total job postings: {job_count}")
        print(f"📊 Total interview experiences: {exp_count}")
        
    except Exception as e:
        print(f"❌ Error inserting sample data: {e}")

if __name__ == "__main__":
    add_sample_data()
