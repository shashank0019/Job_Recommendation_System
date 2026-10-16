from config.database import get_db_config
from models.job_posting import JobPosting

print("Testing model database connection...")

# Test database config
config = get_db_config()
print(f"Database config: {config}")
print(f"Database instance: {config.db}")
print(f"Using local fallback: {config.use_local_fallback}")

# Force connection
config.connect()
print(f"After connect - Database instance: {config.db}")

# Test JobPosting.find_all()
print("\nTesting JobPosting.find_all()...")
try:
    jobs = JobPosting.find_all()
    print(f"Found {len(jobs)} jobs")
    for job in jobs:
        print(f"- {job.title} at {job.company}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# Test direct database query
print("\nTesting direct database query...")
try:
    if config.db is not None:
        jobs_collection = config.db.job_postings
        count = jobs_collection.count_documents({})
        print(f"Direct query - Total jobs in database: {count}")
        
        # Get all jobs directly
        jobs = list(jobs_collection.find({}))
        print(f"Direct query - Found {len(jobs)} jobs")
        for job in jobs:
            print(f"- {job.get('title', 'No title')} at {job.get('company', 'No company')}")
    else:
        print("No database connection available")
except Exception as e:
    print(f"Direct query error: {e}")
    import traceback
    traceback.print_exc()
