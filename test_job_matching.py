#!/usr/bin/env python3
"""
Test job matching functionality directly
"""

import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def test_job_matching():
    """Test job matching logic"""
    print("🧪 Testing Job Matching Logic")
    print("=" * 50)
    
    # Check if data files exist
    data_files = [
        "data/job_dataset_medium.csv",
        "data/job_dataset_sample.csv", 
        "data/unified_job_dataset.csv"
    ]
    
    job_data = None
    for file_path in data_files:
        if os.path.exists(file_path):
            try:
                if "unified" in file_path:
                    # Load only first 1000 rows to avoid memory issues
                    job_data = pd.read_csv(file_path, nrows=1000)
                else:
                    job_data = pd.read_csv(file_path)
                print(f"✅ Loaded {len(job_data)} jobs from {file_path}")
                break
            except Exception as e:
                print(f"❌ Failed to load {file_path}: {e}")
                continue
    
    if job_data is None:
        print("❌ No job data files found!")
        return
    
    # Check data structure
    print(f"\n📊 Data Structure:")
    print(f"  Columns: {list(job_data.columns)}")
    print(f"  Shape: {job_data.shape}")
    
    # Sample resume skills
    resume_skills = ['react', 'node.js', 'javascript', 'python', 'mongodb']
    resume_text = f"Software Engineer with experience in {', '.join(resume_skills)}"
    
    print(f"\n🔍 Testing with resume: {resume_text}")
    
    # Create job descriptions for matching
    job_descriptions = []
    for _, row in job_data.iterrows():
        desc_parts = []
        if 'title' in row and pd.notna(row['title']):
            desc_parts.append(str(row['title']))
        if 'description' in row and pd.notna(row['description']):
            desc_parts.append(str(row['description']))
        elif 'skills' in row and pd.notna(row['skills']):
            desc_parts.append(str(row['skills']))
        
        job_descriptions.append(' '.join(desc_parts))
    
    print(f"📝 Created {len(job_descriptions)} job descriptions")
    
    # Test TF-IDF matching
    try:
        vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
        all_texts = [resume_text] + job_descriptions
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        
        # Calculate similarities
        resume_vector = tfidf_matrix[0:1]
        job_vectors = tfidf_matrix[1:]
        similarities = cosine_similarity(resume_vector, job_vectors).flatten()
        
        # Get top matches
        top_indices = np.argsort(similarities)[::-1][:5]
        
        print(f"\n🎯 Top 5 Matches:")
        for i, idx in enumerate(top_indices, 1):
            score = similarities[idx]
            job = job_data.iloc[idx]
            title = job.get('title', 'N/A')
            company = job.get('company', 'N/A')
            print(f"  {i}. {title} at {company}")
            print(f"     Similarity: {score:.3f} ({score*100:.1f}%)")
        
        if similarities.max() > 0:
            print(f"\n✅ Job matching is working!")
            print(f"   Best match: {similarities.max():.3f}")
            print(f"   Average similarity: {similarities.mean():.3f}")
        else:
            print(f"\n⚠️ No meaningful matches found")
            print(f"   This might indicate vocabulary mismatch")
            
    except Exception as e:
        print(f"❌ TF-IDF matching failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_job_matching()
