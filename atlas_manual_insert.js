
// MongoDB Atlas Manual Insert Script
// Run this in your Atlas UI Query Console

// 1. First, create job_postings collection and insert sample data
db.job_postings.insertMany([
  {
    "title": "Frontend Developer",
    "company": "TechCorp",
    "description": "Build amazing user interfaces with React",
    "requirements": ["React", "JavaScript", "CSS", "HTML"],
    "location": "Mumbai, India",
    "salary_range": "6-10 LPA",
    "job_type": "full-time",
    "posted_by": ObjectId(),
    "created_at": new Date(),
    "updated_at": new Date(),
    "status": "active",
    "contact_email": "hr@techcorp.com",
    "application_url": "https://techcorp.com/careers",
    "tags": ["React", "Frontend"],
    "experience_level": "mid",
    "remote_allowed": true,
    "applications_count": 0
  },
  {
    "title": "Backend Developer",
    "company": "DataSoft",
    "description": "Build scalable backend systems",
    "requirements": ["Python", "Django", "PostgreSQL"],
    "location": "Bangalore, India",
    "salary_range": "8-12 LPA",
    "job_type": "full-time",
    "posted_by": ObjectId(),
    "created_at": new Date(),
    "updated_at": new Date(),
    "status": "active",
    "contact_email": "careers@datasoft.com",
    "application_url": "https://datasoft.com/jobs",
    "tags": ["Python", "Backend"],
    "experience_level": "senior",
    "remote_allowed": false,
    "applications_count": 0
  }
]);

// 2. Create interview_experiences collection and insert sample data
db.interview_experiences.insertMany([
  {
    "company": "Microsoft",
    "position": "Software Engineer",
    "experience_text": "Great interview process with focus on problem solving and teamwork",
    "interview_type": "technical",
    "difficulty_rating": 3,
    "shared_by": ObjectId(),
    "created_at": new Date(),
    "updated_at": new Date(),
    "interview_date": new Date(),
    "outcome": "selected",
    "questions_asked": ["Coding challenges", "System design basics", "Team collaboration"],
    "tips": ["Practice coding daily", "Understand system design", "Show teamwork skills"],
    "tags": ["Technical", "Teamwork"],
    "location": "Hyderabad, India",
    "interview_rounds": 3,
    "preparation_time": "1 month",
    "anonymous": false,
    "status": "active",
    "helpful_votes": 8,
    "total_votes": 10
  },
  {
    "company": "Amazon",
    "position": "SDE",
    "experience_text": "Challenging interview with focus on leadership principles and technical skills",
    "interview_type": "technical",
    "difficulty_rating": 4,
    "shared_by": ObjectId(),
    "created_at": new Date(),
    "updated_at": new Date(),
    "interview_date": new Date(),
    "outcome": "rejected",
    "questions_asked": ["Leadership principles", "Data structures", "System design"],
    "tips": ["Know Amazon principles", "Practice algorithms", "Think big"],
    "tags": ["Leadership", "Technical"],
    "location": "Chennai, India",
    "interview_rounds": 5,
    "preparation_time": "3 months",
    "anonymous": false,
    "status": "active",
    "helpful_votes": 12,
    "total_votes": 15
  }
]);
