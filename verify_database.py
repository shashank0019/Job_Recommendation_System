from config.database import get_db_config

def verify_database_details():
    """Verify exact database details and collections"""
    print("🔍 Database Verification Report")
    print("=" * 50)
    
    config = get_db_config()
    config.connect()
    
    if config.db is not None:
        # Show exact database and connection details
        print(f"🗄️  Database Name: {config.database_name}")
        print(f"🔗 Connection String: {config.connection_string}")
        print(f"📍 Client Address: {config.client.address}")
        print()
        
        # List all databases on the cluster
        print("🗂️  All Databases on Cluster:")
        try:
            db_list = config.client.list_database_names()
            for db_name in db_list:
                print(f"   - {db_name}")
        except Exception as e:
            print(f"   Error listing databases: {e}")
        print()
        
        # Show collections in our specific database
        print(f"📁 Collections in '{config.database_name}':")
        collections = config.db.list_collection_names()
        for collection_name in collections:
            count = config.db[collection_name].count_documents({})
            print(f"   ✅ {collection_name}: {count} documents")
        print()
        
        # Test if we can actually query the collections
        print("🧪 Testing Collection Access:")
        
        # Test job_postings
        try:
            jobs = list(config.db.job_postings.find({}).limit(1))
            if jobs:
                job = jobs[0]
                print(f"   ✅ job_postings: Can read data - Sample: {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
            else:
                print("   ⚠️  job_postings: Collection exists but empty")
        except Exception as e:
            print(f"   ❌ job_postings: Error - {e}")
        
        # Test interview_experiences
        try:
            experiences = list(config.db.interview_experiences.find({}).limit(1))
            if experiences:
                exp = experiences[0]
                print(f"   ✅ interview_experiences: Can read data - Sample: {exp.get('position', 'N/A')} at {exp.get('company', 'N/A')}")
            else:
                print("   ⚠️  interview_experiences: Collection exists but empty")
        except Exception as e:
            print(f"   ❌ interview_experiences: Error - {e}")
        
        print()
        print("💡 If collections don't appear in Atlas UI:")
        print("   1. Refresh the Atlas web interface")
        print("   2. Check you're viewing the correct database")
        print("   3. Collections appear after first document is inserted")
        
    else:
        print("❌ Database connection failed")

if __name__ == "__main__":
    verify_database_details()
