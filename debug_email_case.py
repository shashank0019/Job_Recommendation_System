#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

from config.database import DatabaseConfig
from pprint import pprint

print("Checking user data in database...")

db_config = DatabaseConfig()
users_collection = db_config.db.users

# Find all users with debugtest email (case variations)
users = list(users_collection.find({'email': {'$regex': 'debugtest', '$options': 'i'}}))

print(f"Found {len(users)} matching users:")
for user in users:
    print(f"Email: '{user['email']}'")
    print(f"Name: {user['name']}")
    print("---")

print("\nTesting exact lookup:")
user1 = users_collection.find_one({'email': 'debugtest@example.com'})
user2 = users_collection.find_one({'email': 'DEBUGTEST@EXAMPLE.COM'})

print(f"Lowercase lookup: {'Found' if user1 else 'Not found'}")
print(f"Uppercase lookup: {'Found' if user2 else 'Not found'}")

# Test the Flask route email processing
test_email = "DebugTest@Example.com"
processed_email = test_email.strip().lower()
print(f"\nOriginal: {test_email}")
print(f"Processed: {processed_email}")

user3 = users_collection.find_one({'email': processed_email})
print(f"Processed lookup: {'Found' if user3 else 'Not found'}")