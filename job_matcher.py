import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import joblib
import os
from typing import List, Dict, Tuple, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobMatcher:
    """
    A class to match job seekers with job opportunities using TF-IDF and cosine similarity.
    Supports both offline CSV data and live API data.
    """
    
    def __init__(self, model_path: str = "data/trained_model.joblib", 
                 vectorizer_path: str = "data/tfidf_vectorizer.joblib",
                 csv_data_path: str = "data/job_dataset.csv",
                 max_jobs: int = 5000):
        """
        Initialize the JobMatcher.
        
        Args:
            model_path (str): Path to save/load the trained model
            vectorizer_path (str): Path to save/load the TF-IDF vectorizer
            csv_data_path (str): Path to the CSV job dataset
            max_jobs (int): Maximum number of jobs to load for performance
        """
        self.model_path = model_path
        self.vectorizer_path = vectorizer_path
        self.csv_data_path = csv_data_path
        self.max_jobs = max_jobs
        
        self.vectorizer = None
        self.job_data = None
        self.job_vectors = None
        self.is_trained = False
        
        # Load existing model if available
        self._load_model()
    
    def _load_model(self):
        """Load existing trained model and vectorizer if available."""
        try:
            if os.path.exists(self.vectorizer_path):
                self.vectorizer = joblib.load(self.vectorizer_path)
                logger.info("Loaded existing TF-IDF vectorizer")
                
            if os.path.exists(self.model_path):
                self.job_vectors = joblib.load(self.model_path)
                logger.info("Loaded existing job vectors")
                
            if os.path.exists(self.csv_data_path):
                # Load with row limit for performance
                self.job_data = pd.read_csv(self.csv_data_path, nrows=self.max_jobs)
                logger.info(f"Loaded {len(self.job_data)} jobs from dataset (max: {self.max_jobs})")
                
            if self.vectorizer is not None and self.job_vectors is not None:
                self.is_trained = True
                logger.info("Model is ready for job matching")
                
        except Exception as e:
            logger.warning(f"Could not load existing model: {e}")
            self.is_trained = False
    
    def _prepare_job_text(self, job_data: pd.DataFrame) -> List[str]:
        """
        Prepare job text for vectorization by combining relevant fields.
        
        Args:
            job_data (pd.DataFrame): DataFrame containing job information
            
        Returns:
            List[str]: List of combined job text strings
        """
        job_texts = []
        
        for _, job in job_data.iterrows():
            # Combine title, description, requirements, skills, industry, and benefits
            text_parts = []
            
            if pd.notna(job.get('title')):
                text_parts.append(str(job['title']))
            
            if pd.notna(job.get('description')):
                text_parts.append(str(job['description']))
            
            if pd.notna(job.get('requirements')):
                text_parts.append(str(job['requirements']))
            
            if pd.notna(job.get('skills')):
                text_parts.append(str(job['skills']))
            
            if pd.notna(job.get('industry')):
                text_parts.append(str(job['industry']))
            
            if pd.notna(job.get('benefits')):
                text_parts.append(str(job['benefits']))
            
            if pd.notna(job.get('company')):
                text_parts.append(str(job['company']))
            
            if pd.notna(job.get('work_type')):
                text_parts.append(str(job['work_type']))
            
            if pd.notna(job.get('experience_level')):
                text_parts.append(str(job['experience_level']))
            
            # Join all parts with spaces
            combined_text = ' '.join(text_parts)
            job_texts.append(combined_text)
        
        return job_texts
    
    def train_model(self, job_data: pd.DataFrame = None) -> bool:
        """
        Train the TF-IDF model on job data.
        
        Args:
            job_data (pd.DataFrame): Job data to train on. If None, uses CSV data.
            
        Returns:
            bool: True if training successful, False otherwise
        """
        try:
            # Use provided data or load from CSV
            if job_data is None:
                if not os.path.exists(self.csv_data_path):
                    logger.error(f"CSV data file not found: {self.csv_data_path}")
                    return False
                job_data = pd.read_csv(self.csv_data_path)
            
            self.job_data = job_data
            logger.info(f"Training model on {len(job_data)} jobs")
            
            # Prepare job text for vectorization
            job_texts = self._prepare_job_text(job_data)
            
            # Create and fit TF-IDF vectorizer
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.95
            )
            
            # Fit and transform the job texts
            self.job_vectors = self.vectorizer.fit_transform(job_texts)
            
            # Save the trained model and vectorizer
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.job_vectors, self.model_path)
            joblib.dump(self.vectorizer, self.vectorizer_path)
            
            self.is_trained = True
            logger.info("Model training completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return False
    
    def _vectorize_text(self, text: str) -> np.ndarray:
        """
        Vectorize input text using the trained TF-IDF vectorizer.
        
        Args:
            text (str): Text to vectorize
            
        Returns:
            np.ndarray: Vectorized text
        """
        if not self.is_trained or self.vectorizer is None:
            raise ValueError("Model must be trained before vectorizing text")
        
        return self.vectorizer.transform([text])
    
    def calculate_similarity(self, resume_text: str, job_text: str) -> float:
        """
        Calculate cosine similarity between resume and job text.
        
        Args:
            resume_text (str): Resume text
            job_text (str): Job description text
            
        Returns:
            float: Similarity score between 0 and 1
        """
        try:
            # Vectorize both texts
            resume_vector = self._vectorize_text(resume_text)
            job_vector = self._vectorize_text(job_text)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(resume_vector, job_vector)[0][0]
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def find_matching_jobs(self, resume_text: str, top_k: int = 10, 
                          min_similarity: float = 0.1) -> List[Dict[str, Any]]:
        """
        Find the most similar jobs for a given resume.
        
        Args:
            resume_text (str): Resume text to match against
            top_k (int): Number of top matches to return
            min_similarity (float): Minimum similarity threshold
            
        Returns:
            List[Dict[str, Any]]: List of matching jobs with similarity scores
        """
        if not self.is_trained:
            logger.error("Model must be trained before finding matches")
            return []
        
        try:
            # Check if job vectors and job data are in sync
            if len(self.job_data) != self.job_vectors.shape[0]:
                logger.warning(f"Mismatch: job_data has {len(self.job_data)} rows but job_vectors has {self.job_vectors.shape[0]} rows")
                logger.info("Retraining model to fix mismatch...")
                if not self.train_model():
                    logger.error("Failed to retrain model")
                    return []
            
            # Vectorize the resume
            try:
                resume_vector = self._vectorize_text(resume_text)
            except ValueError as ve:
                logger.warning(f"Vectorizer dimension mismatch: {ve}")
                logger.info("Retraining model to fix vectorizer mismatch...")
                if not self.train_model():
                    logger.error("Failed to retrain model")
                    return []
                resume_vector = self._vectorize_text(resume_text)
            
            # Calculate similarities with all jobs
            similarities = cosine_similarity(resume_vector, self.job_vectors).flatten()
            
            # Create list of (job_index, similarity_score) tuples
            job_scores = list(enumerate(similarities))
            
            # Sort by similarity score (descending)
            job_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Filter by minimum similarity and get top k
            matching_jobs = []
            for job_idx, score in job_scores:
                if score >= min_similarity and len(matching_jobs) < top_k:
                    # Add bounds checking to prevent indexing errors
                    if job_idx < len(self.job_data):
                        job_info = self.job_data.iloc[job_idx].to_dict()
                        job_info['similarity_score'] = round(score, 4)
                        job_info['job_index'] = job_idx
                        matching_jobs.append(job_info)
                    else:
                        logger.warning(f"Job index {job_idx} out of bounds (dataset size: {len(self.job_data)})")
            
            logger.info(f"Found {len(matching_jobs)} matching jobs")
            return matching_jobs
            
        except Exception as e:
            logger.error(f"Error finding matching jobs: {e}")
            return []
    
    def add_live_jobs(self, live_jobs: List[Dict[str, Any]]) -> bool:
        """
        Add live jobs from API to the existing dataset for matching.
        
        Args:
            live_jobs (List[Dict[str, Any]]): List of live job postings
            
        Returns:
            bool: True if jobs added successfully, False otherwise
        """
        try:
            if not self.is_trained:
                logger.error("Model must be trained before adding live jobs")
                return False
            
            # Convert live jobs to DataFrame format
            live_df = pd.DataFrame(live_jobs)
            
            # Ensure required columns exist
            required_columns = ['title', 'description', 'company', 'location']
            for col in required_columns:
                if col not in live_df.columns:
                    live_df[col] = ''
            
            # Add missing columns to match existing format
            if 'requirements' not in live_df.columns:
                live_df['requirements'] = ''
            if 'skills' not in live_df.columns:
                live_df['skills'] = ''
            if 'experience_level' not in live_df.columns:
                live_df['experience_level'] = ''
            if 'salary_range' not in live_df.columns:
                live_df['salary_range'] = ''
            if 'industry' not in live_df.columns:
                live_df['industry'] = ''
            if 'benefits' not in live_df.columns:
                live_df['benefits'] = ''
            if 'work_type' not in live_df.columns:
                live_df['work_type'] = ''
            if 'remote_allowed' not in live_df.columns:
                live_df['remote_allowed'] = ''
            
            # Prepare text for new jobs
            new_job_texts = self._prepare_job_text(live_df)
            
            # Vectorize new jobs using existing vectorizer
            new_job_vectors = self.vectorizer.transform(new_job_texts)
            
            # Combine with existing vectors
            self.job_vectors = np.vstack([self.job_vectors.toarray(), new_job_vectors.toarray()])
            
            # Combine datasets
            self.job_data = pd.concat([self.job_data, live_df], ignore_index=True)
            
            # Save updated model
            joblib.dump(self.job_vectors, self.model_path)
            
            logger.info(f"Added {len(live_jobs)} live jobs to the dataset")
            return True
            
        except Exception as e:
            logger.error(f"Error adding live jobs: {e}")
            return False
    
    def get_job_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the current job dataset.
        
        Returns:
            Dict[str, Any]: Dictionary containing dataset statistics
        """
        if self.job_data is None:
            return {"error": "No job data loaded"}
        
        try:
            stats = {
                "total_jobs": len(self.job_data),
                "columns": list(self.job_data.columns),
                "is_trained": self.is_trained,
                "vectorizer_features": self.vectorizer.get_feature_names_out().shape[0] if self.vectorizer else 0
            }
            
            # Add column-specific statistics
            if 'experience_level' in self.job_data.columns:
                stats['experience_levels'] = self.job_data['experience_level'].value_counts().to_dict()
            
            if 'location' in self.job_data.columns:
                stats['top_locations'] = self.job_data['location'].value_counts().head(10).to_dict()
            
            if 'industry' in self.job_data.columns:
                stats['top_industries'] = self.job_data['industry'].value_counts().head(10).to_dict()
            
            if 'work_type' in self.job_data.columns:
                stats['work_types'] = self.job_data['work_type'].value_counts().to_dict()
            
            if 'remote_allowed' in self.job_data.columns:
                stats['remote_jobs'] = self.job_data['remote_allowed'].value_counts().to_dict()
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting job statistics: {e}")
            return {"error": str(e)}
    
    def retrain_model(self) -> bool:
        """
        Retrain the model with current data.
        
        Returns:
            bool: True if retraining successful, False otherwise
        """
        if self.job_data is None:
            logger.error("No job data available for retraining")
            return False
        
        return self.train_model(self.job_data)


# Example usage and testing
if __name__ == "__main__":
    # Initialize the job matcher
    matcher = JobMatcher()
    
    # Train the model if not already trained
    if not matcher.is_trained:
        print("Training model...")
        success = matcher.train_model()
        if not success:
            print("Failed to train model")
            exit(1)
    
    # Sample resume text
    sample_resume = """
    I am a software engineer with 5 years of experience in Python development.
    I have worked with Django, React, and AWS. I am proficient in SQL and have
    experience with Docker and Kubernetes. I have led teams and implemented
    CI/CD pipelines.
    """
    
    # Find matching jobs
    print("Finding matching jobs...")
    matches = matcher.find_matching_jobs(sample_resume, top_k=5)
    
    print(f"\nTop {len(matches)} Job Matches:")
    print("=" * 50)
    
    for i, job in enumerate(matches, 1):
        print(f"{i}. {job['title']} at {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   Similarity Score: {job['similarity_score']}")
        print(f"   Skills: {job['skills']}")
        print()
    
    # Get statistics
    stats = matcher.get_job_statistics()
    print("Dataset Statistics:")
    print(f"Total Jobs: {stats['total_jobs']}")
    print(f"Model Trained: {stats['is_trained']}")
    print(f"Vectorizer Features: {stats['vectorizer_features']}") 