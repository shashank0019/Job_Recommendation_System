"""Quick MongoDB Atlas Connection Test"""
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

mongodb_uri = os.getenv('MONGODB_URI')
db_name = os.getenv('MONGODB_DB_NAME', 'career_guidance_db')

print(f"Testing connection to: {db_name}")
print(f"URI: {mongodb_uri[:50]}...")

try:
    client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("SUCCESS: Connected to MongoDB Atlas!")
    
    db = client[db_name]
    collections = db.list_collection_names()
    print(f"Collections found: {collections}")
    
    # Write results to file
    with open('mongodb_test_result.txt', 'w') as f:
        f.write("MongoDB Atlas Connection Test - SUCCESS\n")
        f.write(f"Database: {db_name}\n")
        f.write(f"Collections: {collections}\n")
        f.write("Status: READY TO USE\n")
    
    client.close()
    print("\nResults saved to: mongodb_test_result.txt")
    
except Exception as e:
    print(f"ERROR: {e}")
    with open('mongodb_test_result.txt', 'w') as f:
        f.write(f"MongoDB Atlas Connection Test - FAILED\n")
        f.write(f"Error: {e}\n")
