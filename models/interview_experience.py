"""
Interview Experience model for MongoDB operations
"""
from datetime import datetime
from bson import ObjectId
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class InterviewExperience:
    """Interview Experience model for MongoDB operations"""
    
    def __init__(self, company: str, position: str, experience_text: str, 
                 interview_type: str, difficulty_rating: int, shared_by: str, **kwargs):
        self.company = company
        self.position = position
        self.experience_text = experience_text
        self.interview_type = interview_type  # 'technical', 'hr', 'behavioral', 'case-study', 'group'
        self.difficulty_rating = difficulty_rating  # 1-5 scale
        self.shared_by = shared_by  # User ID who shared the experience
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
        self.status = kwargs.get('status', 'active')  # 'active', 'hidden', 'reported'
        self.interview_date = kwargs.get('interview_date', None)
        self.outcome = kwargs.get('outcome', '')  # 'selected', 'rejected', 'pending', 'withdrawn'
        self.questions_asked = kwargs.get('questions_asked', [])  # List of questions
        self.tips = kwargs.get('tips', [])  # List of tips/advice
        self.tags = kwargs.get('tags', [])  # Technology/skill tags
        self.location = kwargs.get('location', '')
        self.interview_rounds = kwargs.get('interview_rounds', 1)
        self.preparation_time = kwargs.get('preparation_time', '')  # e.g., "2 weeks", "1 month"
        self.helpful_votes = kwargs.get('helpful_votes', 0)
        self.total_votes = kwargs.get('total_votes', 0)
        self.anonymous = kwargs.get('anonymous', False)
        self._id = kwargs.get('_id', None)
    
    @staticmethod
    def create(company: str, position: str, experience_text: str, interview_type: str,
               difficulty_rating: int, shared_by: str, **kwargs) -> Optional['InterviewExperience']:
        """Create a new interview experience"""
        try:
            from config.database import get_db_config
            
            db_config = get_db_config()
            
            if db_config.db is None:
                logger.error("Database connection not available")
                return None
            
            # Validate difficulty rating
            if difficulty_rating < 1 or difficulty_rating > 5:
                logger.error("Difficulty rating must be between 1 and 5")
                return None
            
            # Create interview experience object
            experience = InterviewExperience(
                company=company,
                position=position,
                experience_text=experience_text,
                interview_type=interview_type,
                difficulty_rating=difficulty_rating,
                shared_by=shared_by,
                **kwargs
            )
            
            # Insert into database
            experiences_collection = db_config.db.interview_experiences
            result = experiences_collection.insert_one(experience.to_dict())
            
            if result.inserted_id:
                experience._id = result.inserted_id
                logger.info(f"Interview experience created successfully: {company} - {position}")
                return experience
            else:
                logger.error("Failed to insert interview experience into database")
                return None
                
        except Exception as e:
            logger.error(f"Error creating interview experience: {e}")
            return None
    
    @staticmethod
    def find_all(filters: Dict[str, Any] = None, limit: int = 50, skip: int = 0) -> List['InterviewExperience']:
        """Find all interview experiences with optional filters"""
        try:
            from config.database import get_db_config
            
            db_config = get_db_config()
            
            if db_config.db is None:
                logger.error("Database connection not available")
                return []
            
            experiences_collection = db_config.db.interview_experiences
            
            # Build query
            query = filters or {}
            
            # Default to active experiences only
            if 'status' not in query:
                query['status'] = 'active'
            
            # Sort by creation date (newest first)
            cursor = experiences_collection.find(query).sort('created_at', -1).skip(skip).limit(limit)
            
            experiences = []
            for exp_data in cursor:
                experiences.append(InterviewExperience.from_dict(exp_data))
            
            return experiences
            
        except Exception as e:
            logger.error(f"Error finding interview experiences: {e}")
            return []
    
    @staticmethod
    def find_by_id(experience_id) -> Optional['InterviewExperience']:
        """Find interview experience by ID"""
        try:
            from config.database import get_db_config
            
            db_config = get_db_config()
            
            if db_config.db is None:
                logger.error("Database connection not available")
                return None
            
            # Handle both string and ObjectId types
            if isinstance(experience_id, str):
                experience_id = ObjectId(experience_id) if len(experience_id) == 24 else experience_id
            
            experiences_collection = db_config.db.interview_experiences
            exp_data = experiences_collection.find_one({'_id': experience_id})
            
            if exp_data:
                return InterviewExperience.from_dict(exp_data)
            return None
            
        except Exception as e:
            logger.error(f"Error finding interview experience by ID: {e}")
            return None
    
    @staticmethod
    def find_by_user(user_id, limit: int = 20) -> List['InterviewExperience']:
        """Find interview experiences by user ID"""
        try:
            from config.database import get_db_config
            
            db_config = get_db_config()
            
            if db_config.db is None:
                logger.error("Database connection not available")
                return []
            
            # Handle both string and ObjectId types
            if isinstance(user_id, str):
                user_id = ObjectId(user_id) if len(user_id) == 24 else user_id
            
            experiences_collection = db_config.db.interview_experiences
            cursor = experiences_collection.find({'shared_by': user_id}).sort('created_at', -1).limit(limit)
            
            experiences = []
            for exp_data in cursor:
                experiences.append(InterviewExperience.from_dict(exp_data))
            
            return experiences
            
        except Exception as e:
            logger.error(f"Error finding interview experiences by user: {e}")
            return []
    
    @staticmethod
    def find_by_company(company: str, limit: int = 20) -> List['InterviewExperience']:
        """Find interview experiences by company"""
        try:
            from config.database import get_db_config
            
            db_config = get_db_config()
            
            if db_config.db is None:
                logger.error("Database connection not available")
                return []
            
            experiences_collection = db_config.db.interview_experiences
            # Case-insensitive search
            query = {'company': {'$regex': company, '$options': 'i'}, 'status': 'active'}
            cursor = experiences_collection.find(query).sort('created_at', -1).limit(limit)
            
            experiences = []
            for exp_data in cursor:
                experiences.append(InterviewExperience.from_dict(exp_data))
            
            return experiences
            
        except Exception as e:
            logger.error(f"Error finding interview experiences by company: {e}")
            return []
    
    def save(self) -> bool:
        """Save interview experience to database"""
        try:
            from config.database import get_db_config
            db_config = get_db_config()
            
            if db_config.db is None:
                logger.error("Database connection not available")
                return False
            
            experiences_collection = db_config.db.interview_experiences
            self.updated_at = datetime.utcnow()
            
            if self._id:
                # Update existing experience
                result = experiences_collection.update_one(
                    {'_id': self._id},
                    {'$set': self.to_dict()}
                )
                return result.modified_count > 0
            else:
                # Insert new experience
                result = experiences_collection.insert_one(self.to_dict())
                if result.inserted_id:
                    self._id = result.inserted_id
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error saving interview experience: {e}")
            return False
    
    def delete(self) -> bool:
        """Delete interview experience from database"""
        try:
            from config.database import get_db_config
            db_config = get_db_config()
            
            if db_config.db is None:
                logger.error("Database connection not available")
                return False
            
            experiences_collection = db_config.db.interview_experiences
            
            if self._id:
                result = experiences_collection.delete_one({'_id': self._id})
                return result.deleted_count > 0
            return False
                
        except Exception as e:
            logger.error(f"Error deleting interview experience: {e}")
            return False
    
    def vote_helpful(self, is_helpful: bool) -> bool:
        """Vote on whether this experience is helpful"""
        try:
            self.total_votes += 1
            if is_helpful:
                self.helpful_votes += 1
            return self.save()
        except Exception as e:
            logger.error(f"Error voting on experience: {e}")
            return False
    
    def get_helpfulness_ratio(self) -> float:
        """Get the helpfulness ratio (0-1)"""
        if self.total_votes == 0:
            return 0.0
        return self.helpful_votes / self.total_votes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert interview experience object to dictionary for MongoDB"""
        exp_dict = {
            'company': self.company,
            'position': self.position,
            'experience_text': self.experience_text,
            'interview_type': self.interview_type,
            'difficulty_rating': self.difficulty_rating,
            'shared_by': self.shared_by,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'status': self.status,
            'interview_date': self.interview_date,
            'outcome': self.outcome,
            'questions_asked': self.questions_asked,
            'tips': self.tips,
            'tags': self.tags,
            'location': self.location,
            'interview_rounds': self.interview_rounds,
            'preparation_time': self.preparation_time,
            'helpful_votes': self.helpful_votes,
            'total_votes': self.total_votes,
            'anonymous': self.anonymous
        }
        if self._id:
            exp_dict['_id'] = self._id
        return exp_dict
    
    def to_public_dict(self) -> Dict[str, Any]:
        """Convert interview experience object to public dictionary"""
        return {
            'id': str(self._id) if self._id else None,
            'company': self.company,
            'position': self.position,
            'experience_text': self.experience_text,
            'interview_type': self.interview_type,
            'difficulty_rating': self.difficulty_rating,
            'shared_by': str(self.shared_by) if self.shared_by and not self.anonymous else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'status': self.status,
            'interview_date': self.interview_date.isoformat() if self.interview_date else None,
            'outcome': self.outcome,
            'questions_asked': self.questions_asked,
            'tips': self.tips,
            'tags': self.tags,
            'location': self.location,
            'interview_rounds': self.interview_rounds,
            'preparation_time': self.preparation_time,
            'helpful_votes': self.helpful_votes,
            'total_votes': self.total_votes,
            'helpfulness_ratio': self.get_helpfulness_ratio(),
            'anonymous': self.anonymous
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InterviewExperience':
        """Create InterviewExperience object from dictionary"""
        
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
        
        interview_date = data.get('interview_date')
        if isinstance(interview_date, str):
            try:
                interview_date = datetime.fromisoformat(interview_date)
            except:
                interview_date = None
        
        return cls(
            company=data['company'],
            position=data['position'],
            experience_text=data['experience_text'],
            interview_type=data['interview_type'],
            difficulty_rating=data['difficulty_rating'],
            shared_by=data['shared_by'],
            created_at=created_at,
            updated_at=updated_at,
            status=data.get('status', 'active'),
            interview_date=interview_date,
            outcome=data.get('outcome', ''),
            questions_asked=data.get('questions_asked', []),
            tips=data.get('tips', []),
            tags=data.get('tags', []),
            location=data.get('location', ''),
            interview_rounds=data.get('interview_rounds', 1),
            preparation_time=data.get('preparation_time', ''),
            helpful_votes=data.get('helpful_votes', 0),
            total_votes=data.get('total_votes', 0),
            anonymous=data.get('anonymous', False),
            _id=data.get('_id')
        )
