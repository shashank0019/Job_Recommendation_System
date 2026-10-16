#!/usr/bin/env python3

import sys
sys.path.append('.')

from config.database import get_db_config
from auth.models import User

# Connect to database
db_config = get_db_config()
db_config.connect()

# List all users
collection = db_config.db.users
all_users = list(collection.find())

print(f'Total users in database: {len(all_users)}')
print()

for user in all_users:
    name = user.get('name')
    email = user.get('email')
    created = user.get('created_at')
    has_pass = user.get('password_hash') is not None
    
    print(f'Name: {name}')
    print(f'Email: {email}')
    print(f'Created: {created}')
    print(f'Has password: {has_pass}')
    print('---')