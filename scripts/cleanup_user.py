"""
Utility script to delete a user by email from MongoDB Atlas
"""
from config.database import get_db_config

def delete_user_by_email(email):
    db_config = get_db_config()
    if db_config.db is None:
        print("Database connection not available")
        return False
    users_collection = db_config.db.users
    result = users_collection.delete_one({"email": email})
    if result.deleted_count > 0:
        print(f"✅ Deleted user: {email}")
        return True
    else:
        print(f"❌ No user found with email: {email}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python cleanup_user.py <email>")
    else:
        email = sys.argv[1].strip().lower()
        delete_user_by_email(email)
