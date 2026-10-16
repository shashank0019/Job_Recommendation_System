"""
Job Posting model for MongoDB operations
"""
from datetime import datetime
from bson import ObjectId
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class JobPosting:
    """Job Posting model for MongoDB operations"""
    
    def __init__(self, title: str, company: str, description: str, requirements: List[str], 
                 location: str, salary_range: str, job_type: str, posted_by: str, **kwargs):
        self.title = title
        self.company = company
        self.description = description
        self.requirements = requirements  # List of required skills
        self.location = location
        self.salary_range = salary_range
        self.job_type = job_type  # 'full-time', 'part-time', 'contract', 'internship'
        self.posted_by = posted_by  # User ID who posted the job
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
        self.status = kwargs.get('status', 'active')  # 'active', 'closed', 'draft'
        self.application_deadline = kwargs.get('application_deadline', None)
        self.contact_email = kwargs.get('contact_email', '')
        self.application_url = kwargs.get('application_url', '')
        self.tags = kwargs.get('tags', [])  # Technology tags
        self.experience_level = kwargs.get('experience_level', 'entry')  # 'entry', 'mid', 'senior'
        self.remote_allowed = kwargs.get('remote_allowed', False)
        self.applications_count = kwargs.get('applications_count', 0)
        self._id = kwargs.get('_id', None)
    
    @staticmethod
    def create(title: str, company: str, description: str, requirements: List[str],
               location: str, salary_range: str, job_type: str, posted_by: str, **kwargs) -> Optional['JobPosting']:
        """Create a new job posting"""
        try:
            from config.database import get_db_config
            
            db_config = get_db_config()
            
            if db_config.db is None:
                logger.error("Database connection not available")
                return None
            
            # Create job posting object
            job_posting = JobPosting(
                title=title,
                company=company,
                description=description,
                requirements=requirements,
                location=location,
                salary_range=salary_range,
                job_type=job_type,
                posted_by=posted_by,
                **kwargs
            )
            
            # Insert into database
            jobs_collection = db_config.db.job_postings
            result = jobs_collection.insert_one(job_posting.to_dict())
            
            if result.inserted_id:
                job_posting._id = result.inserted_id
                logger.info(f"Job posting created successfully: {title}")
                return job_posting
            else:
                logger.error("Failed to insert job posting into database")
                return None
                
        except Exception as e:
            logger.error(f"Error creating job posting: {e}")
            return None
    
    @staticmethod
    def find_all(filters: Dict[str, Any] = None, limit: int = 50, skip: int = 0) -> List['JobPosting']:
        """Find all job postings with optional filters"""
        try:
            from config.database import get_db_config
            
            db_config = get_db_config()
            
            if db_config.db is None:
                logger.error("Database connection not available")
                return []
            
            jobs_collection = db_config.db.job_postings
            
            # Build query
            query = filters or {}
            
            # Default to active jobs only
            if 'status' not in query:
                query['status'] = 'active'
            
            # Sort by creation date (newest first)
            cursor = jobs_collection.find(query).sort('created_at', -1).skip(skip).limit(limit)
            
            job_postings = []
            for job_data in cursor:
                job_postings.append(JobPosting.from_dict(job_data))
            
            return job_postings
            
        except Exception as e:
            logger.error(f"Error finding job postings: {e}")
            return []
    
    @staticmethod
    def find_by_id(job_id) -> Optional['JobPosting']:
        """Find job posting by ID"""
        try:
            from config.database import get_db_config
            
            db_config = get_db_config()
            
            if db_config.db is None:
                logger.error("Database connection not available")
                return None
            
            # Handle both string and ObjectId types
            if isinstance(job_id, str):
                job_id = ObjectId(job_id) if len(job_id) == 24 else job_id
            
            jobs_collection = db_config.db.job_postings
            job_data = jobs_collection.find_one({'_id': job_id})
            
            if job_data:
                return JobPosting.from_dict(job_data)
            return None
            
        except Exception as e:
            logger.error(f"Error finding job posting by ID: {e}")
            return None
    
    @staticmethod
    def find_by_user(user_id, limit: int = 20) -> List['JobPosting']:
        """Find job postings by user ID"""
        try:
            from config.database import get_db_config
            
            db_config = get_db_config()
            
            if db_config.db is None:
                logger.error("Database connection not available")
                return []
            
            # Handle both string and ObjectId types
            if isinstance(user_id, str):
                user_id = ObjectId(user_id) if len(user_id) == 24 else user_id
            
            jobs_collection = db_config.db.job_postings
            cursor = jobs_collection.find({'posted_by': user_id}).sort('created_at', -1).limit(limit)
            
            job_postings = []
            for job_data in cursor:
                job_postings.append(JobPosting.from_dict(job_data))
            
            return job_postings
            
        except Exception as e:
            logger.error(f"Error finding job postings by user: {e}")
            return []
    
    def save(self) -> bool:
        """Save job posting to database"""
        try:
            from config.database import get_db_config
            db_config = get_db_config()
            
            if db_config.db is None:
                logger.error("Database connection not available")
                return False
            
            jobs_collection = db_config.db.job_postings
            self.updated_at = datetime.utcnow()
            
            if self._id:
                # Update existing job posting
                result = jobs_collection.update_one(
                    {'_id': self._id},
                    {'$set': self.to_dict()}
                )
                return result.modified_count > 0
            else:
                # Insert new job posting
                result = jobs_collection.insert_one(self.to_dict())
                if result.inserted_id:
                    self._id = result.inserted_id
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error saving job posting: {e}")
            return False
    
    def delete(self) -> bool:
        """Delete job posting from database"""
        try:
            from config.database import get_db_config
            db_config = get_db_config()
            
            if db_config.db is None:
                logger.error("Database connection not available")
                return False
            
            jobs_collection = db_config.db.job_postings
            
            if self._id:
                result = jobs_collection.delete_one({'_id': self._id})
                return result.deleted_count > 0
            return False
                
        except Exception as e:
            logger.error(f"Error deleting job posting: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job posting object to dictionary for MongoDB"""
        job_dict = {
            'title': self.title,
            'company': self.company,
            'description': self.description,
            'requirements': self.requirements,
            'location': self.location,
            'salary_range': self.salary_range,
            'job_type': self.job_type,
            'posted_by': self.posted_by,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'status': self.status,
            'application_deadline': self.application_deadline,
            'contact_email': self.contact_email,
            'application_url': self.application_url,
            'tags': self.tags,
            'experience_level': self.experience_level,
            'remote_allowed': self.remote_allowed,
            'applications_count': self.applications_count
        }
        if self._id:
            job_dict['_id'] = self._id
        return job_dict
    
    def to_public_dict(self) -> Dict[str, Any]:
        """Convert job posting object to public dictionary"""
        return {
            'id': str(self._id) if self._id else None,
            'title': self.title,
            'company': self.company,
            'description': self.description,
            'requirements': self.requirements,
            'location': self.location,
            'salary_range': self.salary_range,
            'job_type': self.job_type,
            'posted_by': str(self.posted_by) if self.posted_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'status': self.status,
            'application_deadline': self.application_deadline.isoformat() if self.application_deadline else None,
            'contact_email': self.contact_email,
            'application_url': self.application_url,
            'tags': self.tags,
            'experience_level': self.experience_level,
            'remote_allowed': self.remote_allowed,
            'applications_count': self.applications_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JobPosting':
        """Create JobPosting object from dictionary"""
        
        # Parse datetime strings if they exist
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at)
            except:
                created_at = datetime.utcnow()
        
        updated_at = data.get('updated_at')
        if isinstance(updated_at, str):
            try:
                updated_at = datetime.fromisoformat(updated_at)
            except:
                updated_at = datetime.utcnow()
        
        application_deadline = data.get('application_deadline')
        if isinstance(application_deadline, str):
            try:
                application_deadline = datetime.fromisoformat(application_deadline)
            except:
                application_deadline = None
        
        return cls(
            title=data['title'],
            company=data['company'],
            description=data['description'],
            requirements=data.get('requirements', []),
            location=data['location'],
            salary_range=data['salary_range'],
            job_type=data['job_type'],
            posted_by=data['posted_by'],
            created_at=created_at,
            updated_at=updated_at,
            status=data.get('status', 'active'),
            application_deadline=application_deadline,
            contact_email=data.get('contact_email', ''),
            application_url=data.get('application_url', ''),
            tags=data.get('tags', []),
            experience_level=data.get('experience_level', 'entry'),
            remote_allowed=data.get('remote_allowed', False),
            applications_count=data.get('applications_count', 0),
            _id=data.get('_id')
        )
