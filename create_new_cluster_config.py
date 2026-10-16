"""
Create a new MongoDB Atlas cluster configuration that will be visible in UI
"""

def show_atlas_setup_instructions():
    """Show instructions to create a new visible cluster"""
    print("🆕 Create New MongoDB Atlas Cluster")
    print("=" * 50)
    
    print("Since your current cluster isn't showing properly in Atlas UI,")
    print("let's create a NEW cluster that will definitely be visible.")
    print()
    
    print("📋 STEP-BY-STEP INSTRUCTIONS:")
    print()
    
    print("1️⃣  CREATE NEW CLUSTER:")
    print("   - Go to https://cloud.mongodb.com/")
    print("   - Click 'Build a Database' or '+ Create'")
    print("   - Choose 'FREE' (M0 Sandbox)")
    print("   - Name it: 'career-platform' or similar")
    print("   - Choose any cloud provider/region")
    print("   - Click 'Create Cluster'")
    print()
    
    print("2️⃣  GET CONNECTION STRING:")
    print("   - Click 'Connect' on your new cluster")
    print("   - Choose 'Connect your application'")
    print("   - Select 'Python' and version '3.6 or later'")
    print("   - Copy the connection string")
    print("   - It should look like:")
    print("   mongodb+srv://<username>:<password>@career-platform.xxxxx.mongodb.net/")
    print()
    
    print("3️⃣  CREATE DATABASE USER:")
    print("   - In Atlas, go to 'Database Access'")
    print("   - Click 'Add New Database User'")
    print("   - Username: career_user")
    print("   - Password: (choose a strong password)")
    print("   - Role: 'Read and write to any database'")
    print("   - Click 'Add User'")
    print()
    
    print("4️⃣  UPDATE CONNECTION STRING:")
    print("   - Replace <username> with: career_user")
    print("   - Replace <password> with your chosen password")
    print("   - Add database name at the end: /career_guidance_platform")
    print()
    
    print("5️⃣  UPDATE CODE:")
    print("   - I'll help you update the database.py file")
    print("   - We'll use your new connection string")
    print("   - Then recreate all collections")
    print()
    
    print("🎯 BENEFITS OF NEW CLUSTER:")
    print("   ✅ Will definitely show in Atlas UI")
    print("   ✅ Fresh start with clean collections")
    print("   ✅ No confusion with multiple clusters")
    print("   ✅ Easy to manage and monitor")
    print()
    
    print("💡 Once you have the new connection string, run:")
    print("   python update_database_config.py")
    print("   (I'll create this script next)")

def create_update_script():
    """Create script to update database configuration"""
    update_script = '''"""
Update database configuration with new Atlas cluster
"""
from config.database import get_db_config
import re

def update_database_config():
    """Update database.py with new connection string"""
    
    print("🔧 Database Configuration Updater")
    print("=" * 40)
    
    # Get new connection string from user
    print("Please provide your NEW MongoDB Atlas connection string:")
    print("(It should look like: mongodb+srv://career_user:password@career-platform.xxxxx.mongodb.net/career_guidance_platform)")
    print()
    
    new_connection_string = input("Enter new connection string: ").strip()
    
    if not new_connection_string.startswith("mongodb+srv://"):
        print("❌ Invalid connection string format")
        return
    
    # Validate connection string
    if "career_guidance_platform" not in new_connection_string:
        if not new_connection_string.endswith("/"):
            new_connection_string += "/"
        new_connection_string += "career_guidance_platform"
    
    print(f"✅ Using connection string: {new_connection_string}")
    
    # Read current database.py
    try:
        with open('config/database.py', 'r') as f:
            content = f.read()
        
        # Replace connection string
        old_pattern = r'self\\.connection_string = "[^"]*"'
        new_line = f'self.connection_string = "{new_connection_string}"'
        
        updated_content = re.sub(old_pattern, new_line, content)
        
        # Write back to file
        with open('config/database.py', 'w') as f:
            f.write(updated_content)
        
        print("✅ Updated config/database.py")
        
        # Test new connection
        print("🧪 Testing new connection...")
        config = get_db_config()
        config.connect()
        
        if config.db is not None:
            print("✅ Connection successful!")
            print("🎯 Now run: python recreate_collections.py")
        else:
            print("❌ Connection failed - check your connection string")
            
    except Exception as e:
        print(f"❌ Error updating config: {e}")

if __name__ == "__main__":
    update_database_config()
'''
    
    with open('update_database_config.py', 'w') as f:
        f.write(update_script)
    
    print("📝 Created update_database_config.py")

def create_recreate_script():
    """Create script to recreate collections in new cluster"""
    recreate_script = '''"""
Recreate all collections in the new MongoDB Atlas cluster
"""
from config.database import get_db_config
from datetime import datetime
from bson import ObjectId

def recreate_collections():
    """Recreate all collections with sample data in new cluster"""
    print("🔄 Recreating Collections in New Cluster")
    print("=" * 50)
    
    config = get_db_config()
    config.connect()
    
    if config.db is not None:
        print(f"✅ Connected to: {config.database_name}")
        
        # Create users collection with sample user
        print("👥 Creating users collection...")
        users_data = [{
            "_id": ObjectId(),
            "name": "Sample User",
            "email": "user@example.com",
            "password_hash": "hashed_password",
            "created_at": datetime.utcnow(),
            "profile": {}
        }]
        config.db.users.insert_many(users_data)
        print(f"   ✅ Created {len(users_data)} users")
        
        # Create sessions collection
        print("🔐 Creating sessions collection...")
        sessions_data = [{
            "_id": ObjectId(),
            "user_id": users_data[0]["_id"],
            "session_token": "sample_token_123",
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow()
        }]
        config.db.sessions.insert_many(sessions_data)
        print(f"   ✅ Created {len(sessions_data)} sessions")
        
        # Create job_postings collection
        print("💼 Creating job_postings collection...")
        jobs_data = [
            {
                "_id": ObjectId(),
                "title": "React Developer",
                "company": "TechCorp",
                "description": "Build amazing React applications",
                "requirements": ["React", "JavaScript", "CSS"],
                "location": "Bangalore, India",
                "salary_range": "₹8-12 LPA",
                "job_type": "full-time",
                "posted_by": users_data[0]["_id"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "status": "active",
                "contact_email": "hr@techcorp.com",
                "tags": ["React", "Frontend"],
                "experience_level": "mid",
                "remote_allowed": True,
                "applications_count": 0
            },
            {
                "_id": ObjectId(),
                "title": "Python Backend Developer",
                "company": "DataSoft",
                "description": "Build scalable backend systems",
                "requirements": ["Python", "Django", "PostgreSQL"],
                "location": "Mumbai, India",
                "salary_range": "₹10-15 LPA",
                "job_type": "full-time",
                "posted_by": users_data[0]["_id"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "status": "active",
                "contact_email": "careers@datasoft.com",
                "tags": ["Python", "Backend"],
                "experience_level": "senior",
                "remote_allowed": False,
                "applications_count": 0
            }
        ]
        config.db.job_postings.insert_many(jobs_data)
        print(f"   ✅ Created {len(jobs_data)} job postings")
        
        # Create interview_experiences collection
        print("🎯 Creating interview_experiences collection...")
        experiences_data = [
            {
                "_id": ObjectId(),
                "company": "Google",
                "position": "Software Engineer",
                "experience_text": "Great interview experience with 4 rounds covering algorithms and system design.",
                "interview_type": "technical",
                "difficulty_rating": 4,
                "shared_by": users_data[0]["_id"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "interview_date": datetime.utcnow(),
                "outcome": "selected",
                "questions_asked": ["Binary search", "System design", "Behavioral"],
                "tips": ["Practice algorithms", "Know system design", "Be confident"],
                "tags": ["Algorithms", "System Design"],
                "location": "Bangalore, India",
                "interview_rounds": 4,
                "preparation_time": "3 months",
                "anonymous": False,
                "status": "active",
                "helpful_votes": 10,
                "total_votes": 12
            },
            {
                "_id": ObjectId(),
                "company": "Microsoft",
                "position": "Frontend Developer",
                "experience_text": "Focused on React and JavaScript fundamentals. Very friendly interviewers.",
                "interview_type": "technical",
                "difficulty_rating": 3,
                "shared_by": users_data[0]["_id"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "interview_date": datetime.utcnow(),
                "outcome": "selected",
                "questions_asked": ["React hooks", "JavaScript closures", "CSS flexbox"],
                "tips": ["Know React well", "Practice coding", "Ask questions"],
                "tags": ["React", "JavaScript", "CSS"],
                "location": "Hyderabad, India",
                "interview_rounds": 3,
                "preparation_time": "2 months",
                "anonymous": False,
                "status": "active",
                "helpful_votes": 8,
                "total_votes": 10
            }
        ]
        config.db.interview_experiences.insert_many(experiences_data)
        print(f"   ✅ Created {len(experiences_data)} interview experiences")
        
        print()
        print("🎉 All Collections Created Successfully!")
        
        # Verify collections
        collections = config.db.list_collection_names()
        print(f"📋 Collections in database: {collections}")
        
        for collection_name in collections:
            count = config.db[collection_name].count_documents({})
            print(f"   📊 {collection_name}: {count} documents")
        
        print()
        print("🌟 Your collections should now be visible in MongoDB Atlas UI!")
        print("   Go to Atlas → Browse Collections → career_guidance_platform")
        
    else:
        print("❌ Database connection failed")

if __name__ == "__main__":
    recreate_collections()
'''
    
    with open('recreate_collections.py', 'w') as f:
        f.write(recreate_script)
    
    print("📝 Created recreate_collections.py")

if __name__ == "__main__":
    show_atlas_setup_instructions()
    print()
    create_update_script()
    create_recreate_script()
    print()
    print("🎯 NEXT STEPS:")
    print("1. Create new cluster in Atlas (follow instructions above)")
    print("2. Run: python update_database_config.py")
    print("3. Run: python recreate_collections.py")
    print("4. Check Atlas UI - collections will be visible!")
