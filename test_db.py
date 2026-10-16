from config.database import test_connection, get_db_config

print("Testing database connection...")
test_connection()

print("\nChecking database config...")
config = get_db_config()
print(f"Using local fallback: {config.use_local_fallback}")
print(f"Database instance: {config.db}")

if config.db is not None:
    print("Database connected successfully!")
    # Try to list collections
    try:
        collections = config.db.list_collection_names()
        print(f"Available collections: {collections}")
    except Exception as e:
        print(f"Error listing collections: {e}")
else:
    print("No database connection - using local fallback")
