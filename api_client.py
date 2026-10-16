import requests
import os
import time
from typing import List, Dict, Any, Optional
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobAPIClient:
    """
    A client for fetching live job data from various job search APIs.
    Currently supports RapidAPI JSearch, but can be extended for other APIs.
    """
    
    def __init__(self, api_key: str = None, api_host: str = None):
        """
        Initialize the Job API client.
        
        Args:
            api_key (str): API key for the job search service
            api_host (str): API host URL
        """
        self.api_key = api_key or os.getenv('RAPIDAPI_KEY')
        self.api_host = api_host or os.getenv('RAPIDAPI_HOST', 'jsearch.p.rapidapi.com')
        
        if not self.api_key:
            logger.warning("No API key provided. Live job fetching will be disabled.")
        
        self.base_url = f"https://{self.api_host}"
        self.headers = {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': self.api_host
        } if self.api_key else {}
    
    def search_jobs(self, query: str, location: str = "", 
                    page: int = 1, num_pages: int = 1) -> List[Dict[str, Any]]:
        """
        Search for jobs using the JSearch API.
        
        Args:
            query (str): Job search query (e.g., "software engineer", "data scientist")
            location (str): Location for job search
            page (int): Starting page number
            num_pages (int): Number of pages to fetch
            
        Returns:
            List[Dict[str, Any]]: List of job postings
        """
        if not self.api_key:
            logger.error("No API key available for job search")
            return []
        
        all_jobs = []
        
        try:
            for current_page in range(page, page + num_pages):
                logger.info(f"Fetching page {current_page} for query: {query}")
                
                # Prepare query parameters
                params = {
                    'query': query,
                    'page': str(current_page),
                    'num_pages': '1'
                }
                
                if location:
                    params['location'] = location
                
                # Make API request
                response = requests.get(
                    f"{self.base_url}/search",
                    headers=self.headers,
                    params=params,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'data' in data and data['data']:
                        jobs = self._parse_jsearch_response(data['data'])
                        all_jobs.extend(jobs)
                        logger.info(f"Retrieved {len(jobs)} jobs from page {current_page}")
                    else:
                        logger.info(f"No jobs found on page {current_page}")
                        break
                        
                else:
                    logger.error(f"API request failed with status {response.status_code}: {response.text}")
                    break
                
                # Rate limiting - wait between requests
                if current_page < page + num_pages - 1:
                    time.sleep(1)
            
            logger.info(f"Total jobs retrieved: {len(all_jobs)}")
            return all_jobs
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return []
    
    def _parse_jsearch_response(self, jobs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parse the JSearch API response into a standardized format.
        
        Args:
            jobs_data (List[Dict[str, Any]]): Raw job data from API
            
        Returns:
            List[Dict[str, Any]]: Standardized job data
        """
        standardized_jobs = []
        
        for job in jobs_data:
            try:
                standardized_job = {
                    'title': job.get('job_title', ''),
                    'company': job.get('employer_name', ''),
                    'location': job.get('job_city', ''),
                    'description': job.get('job_description', ''),
                    'requirements': job.get('job_required_skills', ''),
                    'skills': job.get('job_required_skills', ''),
                    'experience_level': self._extract_experience_level(job.get('job_description', '')),
                    'salary_range': job.get('job_salary', ''),
                    'job_url': job.get('job_apply_link', ''),
                    'posted_date': job.get('job_posted_at_datetime_utc', ''),
                    'source': 'jsearch_api'
                }
                
                # Clean up empty strings
                for key, value in standardized_job.items():
                    if value == '':
                        standardized_job[key] = 'N/A'
                
                standardized_jobs.append(standardized_job)
                
            except Exception as e:
                logger.warning(f"Error parsing job data: {e}")
                continue
        
        return standardized_jobs
    
    def _extract_experience_level(self, description: str) -> str:
        """
        Extract experience level from job description.
        
        Args:
            description (str): Job description text
            
        Returns:
            str: Extracted experience level
        """
        if not description:
            return 'N/A'
        
        description_lower = description.lower()
        
        # Define experience level patterns
        experience_patterns = {
            'entry_level': ['entry level', 'entry-level', 'junior', '0-1 years', '0-2 years'],
            'mid_level': ['mid level', 'mid-level', 'intermediate', '2-5 years', '3-5 years'],
            'senior_level': ['senior', 'senior level', 'senior-level', '5+ years', '7+ years'],
            'lead_level': ['lead', 'principal', 'staff', 'architect', 'manager']
        }
        
        for level, patterns in experience_patterns.items():
            for pattern in patterns:
                if pattern in description_lower:
                    return level.replace('_', '-')
        
        return 'N/A'
    
    def get_job_details(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific job.
        
        Args:
            job_id (str): Job identifier
            
        Returns:
            Optional[Dict[str, Any]]: Detailed job information or None if not found
        """
        if not self.api_key:
            logger.error("No API key available for job details")
            return None
        
        try:
            params = {'job_id': job_id}
            
            response = requests.get(
                f"{self.base_url}/job-details",
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    return self._parse_jsearch_response([data['data']])[0]
            
            logger.error(f"Failed to get job details: {response.status_code}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting job details: {e}")
            return None
    
    def search_jobs_by_skills(self, skills: List[str], location: str = "", 
                             max_jobs: int = 50) -> List[Dict[str, Any]]:
        """
        Search for jobs based on specific skills.
        
        Args:
            skills (List[str]): List of skills to search for
            location (str): Location for job search
            max_jobs (int): Maximum number of jobs to return
            
        Returns:
            List[Dict[str, Any]]: List of matching jobs
        """
        if not skills:
            return []
        
        # Create search query from skills
        query = ' OR '.join(skills)
        
        # Search for jobs
        jobs = self.search_jobs(query, location, num_pages=5)  # Fetch more pages to get variety
        
        # Filter jobs by skill relevance
        relevant_jobs = []
        for job in jobs:
            if len(relevant_jobs) >= max_jobs:
                break
            
            # Check if job contains any of the required skills
            job_text = f"{job['title']} {job['description']} {job['skills']}".lower()
            skill_matches = sum(1 for skill in skills if skill.lower() in job_text)
            
            if skill_matches > 0:
                job['skill_matches'] = skill_matches
                relevant_jobs.append(job)
        
        # Sort by skill matches (descending)
        relevant_jobs.sort(key=lambda x: x.get('skill_matches', 0), reverse=True)
        
        return relevant_jobs[:max_jobs]
    
    def get_api_status(self) -> Dict[str, Any]:
        """
        Check the status of the API connection.
        
        Returns:
            Dict[str, Any]: API status information
        """
        status = {
            'api_key_configured': bool(self.api_key),
            'api_host': self.api_host,
            'base_url': self.base_url
        }
        
        if self.api_key:
            try:
                # Test API connection with a simple search
                test_response = requests.get(
                    f"{self.base_url}/search",
                    headers=self.headers,
                    params={'query': 'test', 'page': '1'},
                    timeout=10
                )
                
                status['api_accessible'] = test_response.status_code == 200
                status['last_test_status'] = test_response.status_code
                
            except Exception as e:
                status['api_accessible'] = False
                status['error'] = str(e)
        else:
            status['api_accessible'] = False
            status['error'] = 'No API key configured'
        
        return status


# Example usage and testing
if __name__ == "__main__":
    # Initialize the API client
    client = JobAPIClient()
    
    # Check API status
    status = client.get_api_status()
    print("API Status:")
    print(f"API Key Configured: {status['api_key_configured']}")
    print(f"API Accessible: {status['api_accessible']}")
    
    if status['api_accessible']:
        # Search for jobs
        print("\nSearching for software engineering jobs...")
        jobs = client.search_jobs("software engineer", "San Francisco", num_pages=2)
        
        print(f"\nFound {len(jobs)} jobs:")
        for i, job in enumerate(jobs[:5], 1):  # Show first 5 jobs
            print(f"{i}. {job['title']} at {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   Skills: {job['skills']}")
            print()
        
        # Search by skills
        print("Searching for jobs with Python and React skills...")
        skill_jobs = client.search_jobs_by_skills(['Python', 'React'], max_jobs=10)
        
        print(f"\nFound {len(skill_jobs)} relevant jobs:")
        for i, job in enumerate(skill_jobs[:3], 1):  # Show first 3 jobs
            print(f"{i}. {job['title']} at {job['company']}")
            print(f"   Skill Matches: {job.get('skill_matches', 0)}")
            print()
    
    else:
        print("API is not accessible. Please check your API key and configuration.") 