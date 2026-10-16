"""
Job Posting API routes
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
from auth.middleware import require_auth, get_current_user
from flask import g

logger = logging.getLogger(__name__)

job_posting_bp = Blueprint('job_posting', __name__)

@job_posting_bp.route('/jobs', methods=['GET'])
def get_jobs():
    """Get all job postings with optional filters"""
    try:
        from models.job_posting import JobPosting
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 50)  # Max 50 per page
        skip = (page - 1) * limit
        
        # Build filters
        filters = {}
        
        # Filter by job type
        job_type = request.args.get('job_type')
        if job_type:
            filters['job_type'] = job_type
        
        # Filter by experience level
        experience_level = request.args.get('experience_level')
        if experience_level:
            filters['experience_level'] = experience_level
        
        # Filter by location (case-insensitive search)
        location = request.args.get('location')
        if location:
            filters['location'] = {'$regex': location, '$options': 'i'}
        
        # Filter by company (case-insensitive search)
        company = request.args.get('company')
        if company:
            filters['company'] = {'$regex': company, '$options': 'i'}
        
        # Filter by tags
        tags = request.args.get('tags')
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            filters['tags'] = {'$in': tag_list}
        
        # Filter by remote allowed
        remote_allowed = request.args.get('remote_allowed')
        if remote_allowed and remote_allowed.lower() == 'true':
            filters['remote_allowed'] = True
        
        # Search in title and description
        search = request.args.get('search')
        if search:
            filters['$or'] = [
                {'title': {'$regex': search, '$options': 'i'}},
                {'description': {'$regex': search, '$options': 'i'}},
                {'company': {'$regex': search, '$options': 'i'}}
            ]
        
        # Get job postings
        job_postings = JobPosting.find_all(filters=filters, limit=limit, skip=skip)
        
        # Convert to public format
        jobs_data = [job.to_public_dict() for job in job_postings]
        
        return jsonify({
            'success': True,
            'jobs': jobs_data,
            'page': page,
            'limit': limit,
            'total': len(jobs_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting job postings: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get job postings'
        }), 500

@job_posting_bp.route('/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    """Get a specific job posting by ID"""
    try:
        from models.job_posting import JobPosting
        
        job_posting = JobPosting.find_by_id(job_id)
        
        if not job_posting:
            return jsonify({
                'success': False,
                'message': 'Job posting not found'
            }), 404
        
        return jsonify({
            'success': True,
            'job': job_posting.to_public_dict()
        })
        
    except Exception as e:
        logger.error(f"Error getting job posting: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get job posting'
        }), 500

@job_posting_bp.route('/jobs', methods=['POST'])
@require_auth
def create_job():
    """Create a new job posting"""
    try:
        from models.job_posting import JobPosting
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'company', 'description', 'location', 'salary_range', 'job_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Validate job type
        valid_job_types = ['full-time', 'part-time', 'contract', 'internship']
        if data['job_type'] not in valid_job_types:
            return jsonify({
                'success': False,
                'message': f'Invalid job type. Must be one of: {", ".join(valid_job_types)}'
            }), 400
        
        # Validate experience level
        experience_level = data.get('experience_level', 'entry')
        valid_experience_levels = ['entry', 'mid', 'senior']
        if experience_level not in valid_experience_levels:
            return jsonify({
                'success': False,
                'message': f'Invalid experience level. Must be one of: {", ".join(valid_experience_levels)}'
            }), 400
        
        # Parse application deadline if provided
        application_deadline = None
        if data.get('application_deadline'):
            try:
                application_deadline = datetime.fromisoformat(data['application_deadline'])
            except:
                return jsonify({
                    'success': False,
                    'message': 'Invalid application deadline format. Use ISO format (YYYY-MM-DD)'
                }), 400
        
        current_user = get_current_user()
        job_posting = JobPosting.create(
            title=data['title'],
            company=data['company'],
            description=data['description'],
            requirements=data.get('requirements', []),
            location=data['location'],
            salary_range=data['salary_range'],
            job_type=data['job_type'],
            posted_by=current_user._id,
            application_deadline=application_deadline,
            contact_email=data.get('contact_email', ''),
            application_url=data.get('application_url', ''),
            tags=data.get('tags', []),
            experience_level=experience_level,
            remote_allowed=data.get('remote_allowed', False)
        )
        
        if not job_posting:
            return jsonify({
                'success': False,
                'message': 'Failed to create job posting'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Job posting created successfully',
            'job': job_posting.to_public_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating job posting: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to create job posting'
        }), 500

@job_posting_bp.route('/jobs/<job_id>', methods=['PUT'])
@require_auth
def update_job(job_id):
    """Update a job posting"""
    try:
        from models.job_posting import JobPosting
        
        job_posting = JobPosting.find_by_id(job_id)
        
        if not job_posting:
            return jsonify({
                'success': False,
                'message': 'Job posting not found'
            }), 404
        
        current_user = get_current_user()
        if str(job_posting.posted_by) != str(current_user._id):
            return jsonify({
                'success': False,
                'message': 'You can only update your own job postings'
            }), 403
        
        data = request.get_json()
        
        # Update fields if provided
        if 'title' in data:
            job_posting.title = data['title']
        if 'company' in data:
            job_posting.company = data['company']
        if 'description' in data:
            job_posting.description = data['description']
        if 'requirements' in data:
            job_posting.requirements = data['requirements']
        if 'location' in data:
            job_posting.location = data['location']
        if 'salary_range' in data:
            job_posting.salary_range = data['salary_range']
        if 'job_type' in data:
            valid_job_types = ['full-time', 'part-time', 'contract', 'internship']
            if data['job_type'] not in valid_job_types:
                return jsonify({
                    'success': False,
                    'message': f'Invalid job type. Must be one of: {", ".join(valid_job_types)}'
                }), 400
            job_posting.job_type = data['job_type']
        if 'status' in data:
            valid_statuses = ['active', 'closed', 'draft']
            if data['status'] not in valid_statuses:
                return jsonify({
                    'success': False,
                    'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
                }), 400
            job_posting.status = data['status']
        if 'contact_email' in data:
            job_posting.contact_email = data['contact_email']
        if 'application_url' in data:
            job_posting.application_url = data['application_url']
        if 'tags' in data:
            job_posting.tags = data['tags']
        if 'experience_level' in data:
            valid_experience_levels = ['entry', 'mid', 'senior']
            if data['experience_level'] not in valid_experience_levels:
                return jsonify({
                    'success': False,
                    'message': f'Invalid experience level. Must be one of: {", ".join(valid_experience_levels)}'
                }), 400
            job_posting.experience_level = data['experience_level']
        if 'remote_allowed' in data:
            job_posting.remote_allowed = data['remote_allowed']
        if 'application_deadline' in data:
            if data['application_deadline']:
                try:
                    job_posting.application_deadline = datetime.fromisoformat(data['application_deadline'])
                except:
                    return jsonify({
                        'success': False,
                        'message': 'Invalid application deadline format. Use ISO format (YYYY-MM-DD)'
                    }), 400
            else:
                job_posting.application_deadline = None
        
        # Save changes
        if job_posting.save():
            return jsonify({
                'success': True,
                'message': 'Job posting updated successfully',
                'job': job_posting.to_public_dict()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to update job posting'
            }), 500
        
    except Exception as e:
        logger.error(f"Error updating job posting: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to update job posting'
        }), 500

@job_posting_bp.route('/jobs/<job_id>', methods=['DELETE'])
@require_auth
def delete_job(job_id):
    """Delete a job posting"""
    try:
        from models.job_posting import JobPosting
        
        job_posting = JobPosting.find_by_id(job_id)
        
        if not job_posting:
            return jsonify({
                'success': False,
                'message': 'Job posting not found'
            }), 404
        
        current_user = get_current_user()
        if str(job_posting.posted_by) != str(current_user._id):
            return jsonify({
                'success': False,
                'message': 'You can only delete your own job postings'
            }), 403
        
        # Delete job posting
        if job_posting.delete():
            return jsonify({
                'success': True,
                'message': 'Job posting deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to delete job posting'
            }), 500
        
    except Exception as e:
        logger.error(f"Error deleting job posting: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to delete job posting'
        }), 500

@job_posting_bp.route('/my-jobs', methods=['GET'])
# @require_auth  # Disabled - using localStorage auth
def get_my_jobs():
    """Get current user's job postings"""
    try:
        from models.job_posting import JobPosting
        from bson import ObjectId
        
        # Use dummy user ID since we're using localStorage auth
        dummy_user_id = ObjectId('507f1f77bcf86cd799439011')  # Static dummy ID
        limit = min(int(request.args.get('limit', 20)), 50)
        job_postings = JobPosting.find_by_user(dummy_user_id, limit=limit)
        
        # Convert to public format
        jobs_data = [job.to_public_dict() for job in job_postings]
        
        return jsonify({
            'success': True,
            'jobs': jobs_data,
            'total': len(jobs_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting user's job postings: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get your job postings'
        }), 500
