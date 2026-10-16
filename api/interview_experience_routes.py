"""
Interview Experience API routes
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
from auth.middleware import require_auth
from flask import g

logger = logging.getLogger(__name__)

interview_experience_bp = Blueprint('interview_experience', __name__)

@interview_experience_bp.route('/experiences', methods=['GET'])
def get_experiences():
    """Get all interview experiences with optional filters"""
    try:
        from models.interview_experience import InterviewExperience
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 50)  # Max 50 per page
        skip = (page - 1) * limit
        
        # Build filters
        filters = {}
        
        # Filter by interview type
        interview_type = request.args.get('interview_type')
        if interview_type:
            filters['interview_type'] = interview_type
        
        # Filter by difficulty rating
        difficulty = request.args.get('difficulty')
        if difficulty:
            try:
                difficulty_int = int(difficulty)
                if 1 <= difficulty_int <= 5:
                    filters['difficulty_rating'] = difficulty_int
            except ValueError:
                pass
        
        # Filter by company (case-insensitive search)
        company = request.args.get('company')
        if company:
            filters['company'] = {'$regex': company, '$options': 'i'}
        
        # Filter by position (case-insensitive search)
        position = request.args.get('position')
        if position:
            filters['position'] = {'$regex': position, '$options': 'i'}
        
        # Filter by outcome
        outcome = request.args.get('outcome')
        if outcome:
            filters['outcome'] = outcome
        
        # Filter by tags
        tags = request.args.get('tags')
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            filters['tags'] = {'$in': tag_list}
        
        # Filter by location
        location = request.args.get('location')
        if location:
            filters['location'] = {'$regex': location, '$options': 'i'}
        
        # Search in experience text, company, and position
        search = request.args.get('search')
        if search:
            filters['$or'] = [
                {'experience_text': {'$regex': search, '$options': 'i'}},
                {'company': {'$regex': search, '$options': 'i'}},
                {'position': {'$regex': search, '$options': 'i'}},
                {'questions_asked': {'$regex': search, '$options': 'i'}},
                {'tips': {'$regex': search, '$options': 'i'}}
            ]
        
        # Get interview experiences
        experiences = InterviewExperience.find_all(filters=filters, limit=limit, skip=skip)
        
        # Convert to public format
        experiences_data = [exp.to_public_dict() for exp in experiences]
        
        return jsonify({
            'success': True,
            'experiences': experiences_data,
            'page': page,
            'limit': limit,
            'total': len(experiences_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting interview experiences: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get interview experiences'
        }), 500

@interview_experience_bp.route('/experiences/<experience_id>', methods=['GET'])
def get_experience(experience_id):
    """Get a specific interview experience by ID"""
    try:
        from models.interview_experience import InterviewExperience
        
        experience = InterviewExperience.find_by_id(experience_id)
        
        if not experience:
            return jsonify({
                'success': False,
                'message': 'Interview experience not found'
            }), 404
        
        return jsonify({
            'success': True,
            'experience': experience.to_public_dict()
        })
        
    except Exception as e:
        logger.error(f"Error getting interview experience: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get interview experience'
        }), 500

@interview_experience_bp.route('/experiences/company/<company>', methods=['GET'])
def get_experiences_by_company(company):
    """Get interview experiences for a specific company"""
    try:
        from models.interview_experience import InterviewExperience
        
        limit = min(int(request.args.get('limit', 20)), 50)
        experiences = InterviewExperience.find_by_company(company, limit=limit)
        
        # Convert to public format
        experiences_data = [exp.to_public_dict() for exp in experiences]
        
        return jsonify({
            'success': True,
            'experiences': experiences_data,
            'company': company,
            'total': len(experiences_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting experiences by company: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get interview experiences for company'
        }), 500

@interview_experience_bp.route('/experiences', methods=['POST'])
@require_auth
def create_experience():
    """Create a new interview experience"""
    try:
        from models.interview_experience import InterviewExperience
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['company', 'position', 'experience_text', 'interview_type', 'difficulty_rating']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Validate interview type
        valid_interview_types = ['technical', 'hr', 'behavioral', 'case-study', 'group']
        if data['interview_type'] not in valid_interview_types:
            return jsonify({
                'success': False,
                'message': f'Invalid interview type. Must be one of: {", ".join(valid_interview_types)}'
            }), 400
        
        # Validate difficulty rating
        try:
            difficulty_rating = int(data['difficulty_rating'])
            if difficulty_rating < 1 or difficulty_rating > 5:
                return jsonify({
                    'success': False,
                    'message': 'Difficulty rating must be between 1 and 5'
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'message': 'Difficulty rating must be a number between 1 and 5'
            }), 400
        
        # Validate outcome if provided
        outcome = data.get('outcome', '')
        if outcome:
            valid_outcomes = ['selected', 'rejected', 'pending', 'withdrawn']
            if outcome not in valid_outcomes:
                return jsonify({
                    'success': False,
                    'message': f'Invalid outcome. Must be one of: {", ".join(valid_outcomes)}'
                }), 400
        
        # Parse interview date if provided
        interview_date = None
        if data.get('interview_date'):
            try:
                interview_date = datetime.fromisoformat(data['interview_date'])
            except:
                return jsonify({
                    'success': False,
                    'message': 'Invalid interview date format. Use ISO format (YYYY-MM-DD)'
                }), 400
        
        # Validate interview rounds
        interview_rounds = data.get('interview_rounds', 1)
        try:
            interview_rounds = int(interview_rounds)
            if interview_rounds < 1:
                interview_rounds = 1
        except (ValueError, TypeError):
            interview_rounds = 1
        
        # Create interview experience
        current_user = g.current_user
        experience = InterviewExperience.create(
            company=data['company'],
            position=data['position'],
            experience_text=data['experience_text'],
            interview_type=data['interview_type'],
            difficulty_rating=difficulty_rating,
            shared_by=current_user._id,
            interview_date=interview_date,
            outcome=outcome,
            questions_asked=data.get('questions_asked', []),
            tips=data.get('tips', []),
            tags=data.get('tags', []),
            location=data.get('location', ''),
            interview_rounds=interview_rounds,
            preparation_time=data.get('preparation_time', ''),
            anonymous=data.get('anonymous', False)
        )
        
        if not experience:
            return jsonify({
                'success': False,
                'message': 'Failed to create interview experience'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Interview experience created successfully',
            'experience': experience.to_public_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating interview experience: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to create interview experience'
        }), 500

@interview_experience_bp.route('/experiences/<experience_id>', methods=['PUT'])
@require_auth
def update_experience(experience_id):
    """Update an interview experience"""
    try:
        from models.interview_experience import InterviewExperience
        
        experience = InterviewExperience.find_by_id(experience_id)
        
        if not experience:
            return jsonify({
                'success': False,
                'message': 'Interview experience not found'
            }), 404
        
        # Check if user owns this experience
        current_user = g.current_user
        if str(experience.shared_by) != str(current_user._id):
            return jsonify({
                'success': False,
                'message': 'You can only update your own interview experiences'
            }), 403
        
        data = request.get_json()
        
        # Update fields if provided
        if 'company' in data:
            experience.company = data['company']
        if 'position' in data:
            experience.position = data['position']
        if 'experience_text' in data:
            experience.experience_text = data['experience_text']
        if 'interview_type' in data:
            valid_interview_types = ['technical', 'hr', 'behavioral', 'case-study', 'group']
            if data['interview_type'] not in valid_interview_types:
                return jsonify({
                    'success': False,
                    'message': f'Invalid interview type. Must be one of: {", ".join(valid_interview_types)}'
                }), 400
            experience.interview_type = data['interview_type']
        if 'difficulty_rating' in data:
            try:
                difficulty_rating = int(data['difficulty_rating'])
                if difficulty_rating < 1 or difficulty_rating > 5:
                    return jsonify({
                        'success': False,
                        'message': 'Difficulty rating must be between 1 and 5'
                    }), 400
                experience.difficulty_rating = difficulty_rating
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'Difficulty rating must be a number between 1 and 5'
                }), 400
        if 'outcome' in data:
            outcome = data['outcome']
            if outcome:
                valid_outcomes = ['selected', 'rejected', 'pending', 'withdrawn']
                if outcome not in valid_outcomes:
                    return jsonify({
                        'success': False,
                        'message': f'Invalid outcome. Must be one of: {", ".join(valid_outcomes)}'
                    }), 400
            experience.outcome = outcome
        if 'questions_asked' in data:
            experience.questions_asked = data['questions_asked']
        if 'tips' in data:
            experience.tips = data['tips']
        if 'tags' in data:
            experience.tags = data['tags']
        if 'location' in data:
            experience.location = data['location']
        if 'interview_rounds' in data:
            try:
                interview_rounds = int(data['interview_rounds'])
                if interview_rounds < 1:
                    interview_rounds = 1
                experience.interview_rounds = interview_rounds
            except (ValueError, TypeError):
                pass
        if 'preparation_time' in data:
            experience.preparation_time = data['preparation_time']
        if 'anonymous' in data:
            experience.anonymous = data['anonymous']
        if 'status' in data:
            valid_statuses = ['active', 'hidden', 'reported']
            if data['status'] not in valid_statuses:
                return jsonify({
                    'success': False,
                    'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
                }), 400
            experience.status = data['status']
        if 'interview_date' in data:
            if data['interview_date']:
                try:
                    experience.interview_date = datetime.fromisoformat(data['interview_date'])
                except:
                    return jsonify({
                        'success': False,
                        'message': 'Invalid interview date format. Use ISO format (YYYY-MM-DD)'
                    }), 400
            else:
                experience.interview_date = None
        
        # Save changes
        if experience.save():
            return jsonify({
                'success': True,
                'message': 'Interview experience updated successfully',
                'experience': experience.to_public_dict()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to update interview experience'
            }), 500
        
    except Exception as e:
        logger.error(f"Error updating interview experience: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to update interview experience'
        }), 500

@interview_experience_bp.route('/experiences/<experience_id>', methods=['DELETE'])
@require_auth
def delete_experience(experience_id):
    """Delete an interview experience"""
    try:
        from models.interview_experience import InterviewExperience
        
        experience = InterviewExperience.find_by_id(experience_id)
        
        if not experience:
            return jsonify({
                'success': False,
                'message': 'Interview experience not found'
            }), 404
        
        # Check if user owns this experience
        current_user = g.current_user
        if str(experience.shared_by) != str(current_user._id):
            return jsonify({
                'success': False,
                'message': 'You can only delete your own interview experiences'
            }), 403
        
        # Delete experience
        if experience.delete():
            return jsonify({
                'success': True,
                'message': 'Interview experience deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to delete interview experience'
            }), 500
        
    except Exception as e:
        logger.error(f"Error deleting interview experience: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to delete interview experience'
        }), 500

@interview_experience_bp.route('/experiences/<experience_id>/vote', methods=['POST'])
@require_auth
def vote_experience(experience_id):
    """Vote on whether an interview experience is helpful"""
    try:
        from models.interview_experience import InterviewExperience
        
        experience = InterviewExperience.find_by_id(experience_id)
        
        if not experience:
            return jsonify({
                'success': False,
                'message': 'Interview experience not found'
            }), 404
        
        data = request.get_json()
        is_helpful = data.get('is_helpful', False)
        
        if experience.vote_helpful(is_helpful):
            return jsonify({
                'success': True,
                'message': 'Vote recorded successfully',
                'helpful_votes': experience.helpful_votes,
                'total_votes': experience.total_votes,
                'helpfulness_ratio': experience.get_helpfulness_ratio()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to record vote'
            }), 500
        
    except Exception as e:
        logger.error(f"Error voting on experience: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to record vote'
        }), 500

@interview_experience_bp.route('/my-experiences', methods=['GET'])
@require_auth
def get_my_experiences():
    """Get current user's interview experiences"""
    try:
        from models.interview_experience import InterviewExperience
        
        current_user = g.current_user
        limit = min(int(request.args.get('limit', 20)), 50)
        experiences = InterviewExperience.find_by_user(current_user._id, limit=limit)
        
        # Convert to public format
        experiences_data = [exp.to_public_dict() for exp in experiences]
        
        return jsonify({
            'success': True,
            'experiences': experiences_data,
            'total': len(experiences_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting user's interview experiences: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get your interview experiences'
        }), 500
