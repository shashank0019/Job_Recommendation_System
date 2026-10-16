"""
Database configuration for MongoDB Atlas connection
"""
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration and connection management"""
    
    def __init__(self):
        # MongoDB Atlas connection string from environment variables
        self.connection_string = os.getenv('MONGODB_URI', 
            "mongodb+srv://Final_project:Atlas11924@cluster0.xseglna.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        self.database_name = os.getenv('MONGODB_DB_NAME', 'career_guidance_platform')
        self.client = None
        self.db = None
        self.use_local_fallback = False
        self.local_data_dir = None
        
        # Log which connection is being used
        if os.getenv('MONGODB_URI'):
            logger.info(f"📍 Using MongoDB URI from .env file")
            logger.info(f"📊 Database: {self.database_name}")
        else:
            logger.warning("⚠️  MONGODB_URI not found in .env, using fallback connection")
        
    def connect(self):
        """Establish connection to MongoDB Atlas with fallback to local storage"""
        if os.getenv('USE_LOCAL_DATABASE', '').lower() in ('1', 'true', 'yes'):
            self._use_local_storage("Local database mode enabled by USE_LOCAL_DATABASE")
            return True

        try:
            # Try MongoDB Atlas first
            logger.info("Attempting to connect to MongoDB Atlas...")
            logger.info(f"Connection string: {self.connection_string[:60]}...")
            logger.info(f"Database name: {self.database_name}")
            
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=2000,   # Fast failover if database is unreachable
                connectTimeoutMS=2000,
                socketTimeoutMS=2000,
            )
            
            # Test the connection
            logger.info("Testing connection with ping...")
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            
            logger.info("✅ Successfully connected to MongoDB Atlas")
            logger.info(f"✅ Database: {self.database_name}")
            self.use_local_fallback = False
            return True
            
        except Exception as e:
            logger.warning(f"⚠️  MongoDB Atlas connection failed: {e}")
            logger.warning(f"   Error type: {type(e).__name__}")
            logger.warning(f"   Connection string used: {self.connection_string[:60]}...")
            self._use_local_storage("MongoDB unavailable; using local JSON storage")
            return True

    def _use_local_storage(self, reason):
        """Configure the same collection interface over local JSON files."""
        self._setup_local_storage()
        self.db = LocalDatabase(self.users_file, self.sessions_file)
        self.use_local_fallback = True
        logger.warning(f"⚠️  {reason}")
        logger.warning(f"   Local data directory: {self.local_data_dir}")
    
    def get_database(self):
        """Get database instance"""
        if self.db is None:
            if not self.connect():
                raise Exception("Failed to connect to database")
        return self.db
    
    def get_collection(self, collection_name):
        """Get a specific collection"""
        db = self.get_database()
        return db[collection_name]
    
    def _setup_local_storage(self):
        """Setup local JSON file storage as fallback"""
        import json
        from pathlib import Path
        
        # Create data directory if not exists
        self.local_data_dir = Path("data/auth")
        self.local_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize storage files
        self.users_file = self.local_data_dir / "users.json"
        self.sessions_file = self.local_data_dir / "sessions.json"
        self.collection_files = {
            'users': self.users_file,
            'sessions': self.sessions_file,
            'job_postings': self.local_data_dir / "job_postings.json",
            'interview_experiences': self.local_data_dir / "interview_experiences.json",
        }
        
        # Create empty files if they don't exist
        for file_path in self.collection_files.values():
            if not file_path.exists():
                with open(file_path, 'w') as f:
                    json.dump([], f)
    
    def close_connection(self):
        """Close database connection"""
        if self.client and not self.use_local_fallback:
            self.client.close()
            logger.info("Database connection closed")

class LocalCollection:
    """Local JSON file-based collection for fallback"""
    
    def __init__(self, file_path):
        self.file_path = file_path
        
    def _load_data(self):
        """Load data from JSON file"""
        import json
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def _save_data(self, data):
        """Save data to JSON file"""
        import json
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def find_one(self, filter_dict):
        """Find one document matching the filter"""
        data = self._load_data()
        for item in data:
            match = True
            for key, value in filter_dict.items():
                if not self._matches(item.get(key), value):
                    match = False
                    break
            if match:
                return item
        return None

    def find(self, filter_dict=None):
        items = self._load_data()
        matches = [item for item in items if self._matches_filter(item, filter_dict or {})]
        return LocalCursor(matches)
    
    def insert_one(self, document):
        """Insert one document"""
        import uuid
        from datetime import datetime
        
        data = self._load_data()
        
        # Add ID if not present
        if '_id' not in document:
            document['_id'] = str(uuid.uuid4())
        
        # Convert datetime objects to strings
        for key, value in document.items():
            if isinstance(value, datetime):
                document[key] = value.isoformat()
        
        data.append(document)
        self._save_data(data)
        
        # Return a Mongo-like result object.
        class MockResult:
            def __init__(self, inserted_id):
                self.inserted_id = inserted_id
        
        return MockResult(document['_id'])
    
    def update_one(self, filter_dict, update_dict):
        """Update one document"""
        from datetime import datetime
        
        data = self._load_data()
        for i, item in enumerate(data):
            match = True
            for key, value in filter_dict.items():
                if not self._matches(item.get(key), value):
                    match = False
                    break
            if match:
                # Apply $set operations
                if '$set' in update_dict:
                    for key, value in update_dict['$set'].items():
                        if isinstance(value, datetime):
                            value = value.isoformat()
                        item[key] = value
                data[i] = item
                self._save_data(data)
                return MockUpdateResult(1)
        return MockUpdateResult(0)
    
    def delete_one(self, filter_dict):
        """Delete one document"""
        data = self._load_data()
        for i, item in enumerate(data):
            match = True
            for key, value in filter_dict.items():
                if not self._matches(item.get(key), value):
                    match = False
                    break
            if match:
                data.pop(i)
                self._save_data(data)
                return MockDeleteResult(1)
        return MockDeleteResult(0)
    
    def count_documents(self, filter_dict):
        """Count documents matching filter"""
        data = self._load_data()
        count = 0
        for item in data:
            match = True
            for key, value in filter_dict.items():
                if not self._matches(item.get(key), value):
                    match = False
                    break
            if match:
                count += 1
        return count

    @staticmethod
    def _matches(actual, expected):
        """Match equality and the limited comparison operators used by the app."""
        if isinstance(expected, dict):
            for operator, value in expected.items():
                if operator == '$regex':
                    import re
                    if not re.search(str(value), str(actual or ''), re.IGNORECASE):
                        return False
                elif operator == '$options':
                    continue
                elif operator == '$in' and actual not in value:
                    return False
                if operator == '$gt' and not (actual and LocalCollection._comparable(actual) > value):
                    return False
                if operator == '$lt' and not (actual and LocalCollection._comparable(actual) < value):
                    return False
            return True
        return str(actual) == str(expected)

    @classmethod
    def _matches_filter(cls, item, filters):
        for key, expected in filters.items():
            if key == '$or':
                if not any(cls._matches_filter(item, option) for option in expected):
                    return False
            elif not cls._matches(item.get(key), expected):
                return False
        return True

    @staticmethod
    def _comparable(value):
        from datetime import datetime
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return value


class MockUpdateResult:
    def __init__(self, modified_count):
        self.modified_count = modified_count


class MockDeleteResult:
    def __init__(self, deleted_count):
        self.deleted_count = deleted_count


class LocalDatabase:
    """Database facade exposing local collections like a Mongo database."""

    def __init__(self, users_file, sessions_file):
        self._files = {
            'users': users_file,
            'sessions': sessions_file,
            'job_postings': users_file.parent / "job_postings.json",
            'interview_experiences': users_file.parent / "interview_experiences.json",
        }
        for path in self._files.values():
            if not path.exists():
                path.write_text('[]', encoding='utf-8')

    def __getattr__(self, name):
        if name in self._files:
            return LocalCollection(self._files[name])
        raise AttributeError(f"Unknown local collection: {name}")


class LocalCursor:
    def __init__(self, items):
        self.items = items

    def sort(self, field, direction):
        reverse = direction < 0
        self.items.sort(key=lambda item: item.get(field, ''), reverse=reverse)
        return self

    def skip(self, count):
        self.items = self.items[count:]
        return self

    def limit(self, count):
        self.items = self.items[:count]
        return self

    def __iter__(self):
        return iter(self.items)

# Global database instance - will be created lazily
db_config = None

def get_db_config():
    """Get database config instance - create if not exists"""
    global db_config
    if db_config is None:
        db_config = DatabaseConfig()
    return db_config

def get_db():
    """Get database instance - convenience function"""
    config = get_db_config()
    if config.use_local_fallback:
        return None  # Local storage doesn't need db instance
    return config.get_database()

def get_users_collection():
    """Get users collection"""
    config = get_db_config()
    if config.use_local_fallback:
        return LocalCollection(config.users_file)
    return config.get_collection('users')

def get_sessions_collection():
    """Get sessions collection"""
    config = get_db_config()
    if config.use_local_fallback:
        return LocalCollection(config.sessions_file)
    return config.get_collection('sessions')

# Test database connection
def test_connection():
    """Test database connection"""
    print("🔍 Testing MongoDB Atlas connection...")
    try:
        config = get_db_config()
        success = config.connect()
        if success:
            print("✅ Database connection successful!")
            
            # Test basic operations
            users_collection = get_users_collection()
            count = users_collection.count_documents({})
            print(f"📊 Current users in database: {count}")
            
            return True
        else:
            print("❌ Database connection failed!")
            return False
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False

if __name__ == "__main__":
    test_connection()