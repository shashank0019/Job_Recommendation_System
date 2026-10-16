#!/usr/bin/env python3
"""
Create a new TF-IDF model for job matching
"""

import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def create_tfidf_model():
    """Create and save a new TF-IDF model"""
    print("Creating new TF-IDF model...")
    
    try:
        # Load job data
        job_data = pd.read_csv('data/job_dataset_sample.csv')
        print(f"Loaded {len(job_data)} jobs")
        
        # Combine text fields for vectorization
        job_texts = []
        for idx, job in job_data.iterrows():
            text_parts = []
            
            # Add title
            if pd.notna(job.get('title')):
                text_parts.append(str(job['title']))
            
            # Add description
            if pd.notna(job.get('description')):
                text_parts.append(str(job['description']))
            
            # Add skills
            if pd.notna(job.get('skills')):
                text_parts.append(str(job['skills']))
            
            # Add requirements
            if pd.notna(job.get('requirements')):
                text_parts.append(str(job['requirements']))
            
            combined_text = ' '.join(text_parts)
            job_texts.append(combined_text)
        
        print(f"Prepared {len(job_texts)} job descriptions")
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            lowercase=True,
            ngram_range=(1, 2)
        )
        
        # Fit and transform job texts
        job_vectors = vectorizer.fit_transform(job_texts)
        print(f"Created TF-IDF vectors: {job_vectors.shape}")
        
        # Save vectorizer
        with open('data/tfidf_vectorizer.joblib', 'wb') as f:
            pickle.dump(vectorizer, f)
        print("✅ Saved TF-IDF vectorizer")
        
        # Save job vectors
        with open('data/trained_model.joblib', 'wb') as f:
            pickle.dump(job_vectors, f)
        print("✅ Saved job vectors")
        
        # Test the model
        test_resume = "Software Engineer with Python, React, Node.js experience"
        resume_vector = vectorizer.transform([test_resume])
        similarities = cosine_similarity(resume_vector, job_vectors).flatten()
        top_indices = similarities.argsort()[-5:][::-1]
        
        print("\nTest results:")
        for i, idx in enumerate(top_indices):
            if similarities[idx] > 0:
                job = job_data.iloc[idx]
                print(f"{i+1}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')} (score: {similarities[idx]:.3f})")
        
        return True
        
    except Exception as e:
        print(f"Error creating model: {e}")
        return False

if __name__ == '__main__':
    success = create_tfidf_model()
    if success:
        print("\n✅ TF-IDF model created successfully!")
    else:
        print("\n❌ Failed to create TF-IDF model")
