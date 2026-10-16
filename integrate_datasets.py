#!/usr/bin/env python3
"""
Dataset Integration Script for Career Guidance Platform

This script integrates multiple datasets from the archive folder:
- postings.csv: Main job postings
- companies/: Company information
- jobs/: Job details, skills, benefits
- mappings/: Skills and industries mapping

Creates a unified, enriched job dataset for training the platform.
"""

import pandas as pd
import numpy as np
import os
import logging
from pathlib import Path
from typing import Dict, List, Any
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatasetIntegrator:
    """Integrates multiple job-related datasets into a unified format."""
    
    def __init__(self, archive_path: str = "data/archive (5)"):
        self.archive_path = Path(archive_path)
        self.output_path = Path("data")
        
        # Data storage
        self.postings_df = None
        self.companies_df = None
        self.job_skills_df = None
        self.job_industries_df = None
        self.benefits_df = None
        self.skills_mapping = None
        self.industries_mapping = None
        
    def load_all_datasets(self) -> bool:
        """Load all datasets from the archive folder."""
        try:
            logger.info("📊 Loading all datasets...")
            
            # Load main postings dataset
            logger.info("Loading postings dataset...")
            self.postings_df = pd.read_csv(self.archive_path / "postings.csv", low_memory=False)
            logger.info(f"✅ Loaded {len(self.postings_df)} job postings")
            
            # Load companies dataset
            logger.info("Loading companies dataset...")
            self.companies_df = pd.read_csv(self.archive_path / "companies" / "companies.csv")
            logger.info(f"✅ Loaded {len(self.companies_df)} companies")
            
            # Load job skills
            logger.info("Loading job skills dataset...")
            self.job_skills_df = pd.read_csv(self.archive_path / "jobs" / "job_skills.csv")
            logger.info(f"✅ Loaded {len(self.job_skills_df)} job-skill mappings")
            
            # Load job industries
            logger.info("Loading job industries dataset...")
            self.job_industries_df = pd.read_csv(self.archive_path / "jobs" / "job_industries.csv")
            logger.info(f"✅ Loaded {len(self.job_industries_df)} job-industry mappings")
            
            # Load benefits
            logger.info("Loading benefits dataset...")
            self.benefits_df = pd.read_csv(self.archive_path / "jobs" / "benefits.csv")
            logger.info(f"✅ Loaded {len(self.benefits_df)} job benefits")
            
            # Load mappings
            logger.info("Loading skill and industry mappings...")
            self.skills_mapping = pd.read_csv(self.archive_path / "mappings" / "skills.csv")
            self.industries_mapping = pd.read_csv(self.archive_path / "mappings" / "industries.csv")
            logger.info(f"✅ Loaded {len(self.skills_mapping)} skills and {len(self.industries_mapping)} industries")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading datasets: {e}")
            return False
    
    def clean_and_preprocess(self) -> bool:
        """Clean and preprocess the datasets."""
        try:
            logger.info("🧹 Cleaning and preprocessing datasets...")
            
            # Clean postings dataset
            if self.postings_df is not None:
                # Remove rows with missing essential data
                initial_count = len(self.postings_df)
                self.postings_df = self.postings_df.dropna(subset=['title', 'description'])
                
                # Clean text fields
                self.postings_df['title'] = self.postings_df['title'].astype(str).str.strip()
                self.postings_df['description'] = self.postings_df['description'].astype(str).str.strip()
                
                # Convert salary to numeric, handling missing values
                self.postings_df['min_salary'] = pd.to_numeric(self.postings_df['min_salary'], errors='coerce')
                self.postings_df['max_salary'] = pd.to_numeric(self.postings_df['max_salary'], errors='coerce')
                self.postings_df['med_salary'] = pd.to_numeric(self.postings_df['med_salary'], errors='coerce')
                
                # Create salary range
                self.postings_df['salary_range'] = self.postings_df.apply(
                    lambda row: self._create_salary_range(row), axis=1
                )
                
                logger.info(f"✅ Cleaned postings: {initial_count} -> {len(self.postings_df)}")
            
            # Clean companies dataset
            if self.companies_df is not None:
                self.companies_df = self.companies_df.dropna(subset=['name'])
                self.companies_df['name'] = self.companies_df['name'].astype(str).str.strip()
                logger.info(f"✅ Cleaned companies: {len(self.companies_df)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cleaning datasets: {e}")
            return False
    
    def _create_salary_range(self, row: pd.Series) -> str:
        """Create a salary range string from min, max, and median salaries."""
        min_sal = row.get('min_salary')
        max_sal = row.get('max_salary')
        med_sal = row.get('med_salary')
        
        if pd.notna(min_sal) and pd.notna(max_sal):
            return f"{int(min_sal):,}-{int(max_sal):,}"
        elif pd.notna(med_sal):
            return f"{int(med_sal):,}"
        else:
            return "N/A"
    
    def enrich_job_data(self) -> bool:
        """Enrich job data with company, skills, and industry information."""
        try:
            logger.info("🔗 Enriching job data with related information...")
            
            if self.postings_df is None:
                logger.error("Postings dataset not loaded")
                return False
            
            # Merge with companies
            if self.companies_df is not None:
                logger.info("Merging company information...")
                self.postings_df = self.postings_df.merge(
                    self.companies_df[['company_id', 'name', 'company_size', 'state', 'city', 'country']],
                    on='company_id',
                    how='left'
                )
                
                # Rename columns for consistency
                self.postings_df = self.postings_df.rename(columns={
                    'name': 'company',
                    'title': 'job_title'
                })
            
            # Add skills information
            if self.job_skills_df is not None and self.skills_mapping is not None:
                logger.info("Adding skills information...")
                self.postings_df = self._add_skills_to_jobs()
            
            # Add industry information
            if self.job_industries_df is not None and self.industries_mapping is not None:
                logger.info("Adding industry information...")
                self.postings_df = self._add_industries_to_jobs()
            
            # Add benefits information
            if self.benefits_df is not None:
                logger.info("Adding benefits information...")
                self.postings_df = self._add_benefits_to_jobs()
            
            logger.info("✅ Job data enrichment completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error enriching job data: {e}")
            return False
    
    def _add_skills_to_jobs(self) -> pd.DataFrame:
        """Add skills information to jobs."""
        # Merge job skills with skills mapping
        enriched_skills = self.job_skills_df.merge(
            self.skills_mapping,
            left_on='skill_abr',
            right_on='skill_abr',
            how='left'
        )
        
        # Group skills by job_id
        job_skills = enriched_skills.groupby('job_id')['skill_name'].apply(
            lambda x: ', '.join(x.dropna().unique())
        ).reset_index()
        job_skills.columns = ['job_id', 'skills']
        
        # Merge back to postings
        return self.postings_df.merge(job_skills, on='job_id', how='left')
    
    def _add_industries_to_jobs(self) -> pd.DataFrame:
        """Add industry information to jobs."""
        # Merge job industries with industry mapping
        enriched_industries = self.job_industries_df.merge(
            self.industries_mapping,
            on='industry_id',
            how='left'
        )
        
        # Group industries by job_id
        job_industries = enriched_industries.groupby('job_id')['industry_name'].apply(
            lambda x: ', '.join(x.dropna().unique())
        ).reset_index()
        job_industries.columns = ['job_id', 'industry']
        
        # Merge back to postings
        return self.postings_df.merge(job_industries, on='job_id', how='left')
    
    def _add_benefits_to_jobs(self) -> pd.DataFrame:
        """Add benefits information to jobs."""
        # Group benefits by job_id, combining both inferred and type
        job_benefits = self.benefits_df.groupby('job_id').apply(
            lambda x: ', '.join([
                str(val) for val in x[['inferred', 'type']].values.flatten() 
                if pd.notna(val) and str(val).strip() != ''
            ])
        ).reset_index()
        job_benefits.columns = ['job_id', 'benefits']
        
        # Merge back to postings
        return self.postings_df.merge(job_benefits, on='job_id', how='left')
    
    def create_unified_dataset(self) -> pd.DataFrame:
        """Create the final unified dataset in the format expected by our platform."""
        try:
            logger.info("🎯 Creating unified dataset...")
            
            if self.postings_df is None:
                logger.error("No enriched data available")
                return None
            
            # Select and rename columns to match our expected format
            unified_df = self.postings_df[[
                'job_id',
                'job_title',
                'company',
                'city',
                'description',
                'skills',
                'industry',
                'benefits',
                'salary_range',
                'formatted_experience_level',
                'formatted_work_type',
                'remote_allowed'
            ]].copy()
            
            # Rename columns to match our expected format
            unified_df.columns = [
                'job_id',
                'title',
                'company',
                'location',
                'description',
                'skills',
                'industry',
                'benefits',
                'salary_range',
                'experience_level',
                'work_type',
                'remote_allowed'
            ]
            
            # Clean up location (combine city and state if available)
            if 'state' in self.postings_df.columns:
                unified_df['location'] = unified_df.apply(
                    lambda row: self._format_location(row, self.postings_df), axis=1
                )
            
            # Create requirements field from skills and experience
            unified_df['requirements'] = unified_df.apply(
                lambda row: self._create_requirements(row), axis=1
            )
            
            # Fill missing values
            unified_df = unified_df.fillna({
                'skills': 'N/A',
                'industry': 'N/A',
                'benefits': 'N/A',
                'experience_level': 'N/A',
                'work_type': 'N/A',
                'remote_allowed': 'N/A'
            })
            
            # Remove rows with missing essential data
            unified_df = unified_df.dropna(subset=['title', 'description'])
            
            logger.info(f"✅ Created unified dataset with {len(unified_df)} jobs")
            return unified_df
            
        except Exception as e:
            logger.error(f"❌ Error creating unified dataset: {e}")
            return None
    
    def _format_location(self, row: pd.Series, source_df: pd.DataFrame) -> str:
        """Format location from city and state."""
        job_id = row['job_id']
        source_row = source_df[source_df['job_id'] == job_id].iloc[0] if len(source_df[source_df['job_id'] == job_id]) > 0 else None
        
        if source_row is not None:
            city = source_row.get('city', '')
            state = source_row.get('state', '')
            
            if pd.notna(city) and pd.notna(state):
                return f"{city}, {state}"
            elif pd.notna(city):
                return str(city)
            elif pd.notna(state):
                return str(state)
        
        return row['location']
    
    def _create_requirements(self, row: pd.Series) -> str:
        """Create requirements field from available data."""
        requirements = []
        
        if pd.notna(row['skills']) and row['skills'] != 'N/A':
            requirements.append(f"Skills: {row['skills']}")
        
        if pd.notna(row['experience_level']) and row['experience_level'] != 'N/A':
            requirements.append(f"Experience: {row['experience_level']}")
        
        if pd.notna(row['work_type']) and row['work_type'] != 'N/A':
            requirements.append(f"Work Type: {row['work_type']}")
        
        return '; '.join(requirements) if requirements else 'Requirements not specified'
    
    def save_unified_dataset(self, unified_df: pd.DataFrame) -> bool:
        """Save the unified dataset."""
        try:
            # Save full dataset
            full_path = self.output_path / "unified_job_dataset.csv"
            unified_df.to_csv(full_path, index=False)
            logger.info(f"✅ Saved full dataset to {full_path}")
            
            # Create a sample dataset for testing (first 1000 jobs)
            sample_df = unified_df.head(1000)
            sample_path = self.output_path / "job_dataset_sample.csv"
            sample_df.to_csv(sample_path, index=False)
            logger.info(f"✅ Saved sample dataset to {sample_path}")
            
            # Create a medium dataset for development (first 5000 jobs)
            medium_df = unified_df.head(5000)
            medium_path = self.output_path / "job_dataset_medium.csv"
            medium_df.to_csv(medium_path, index=False)
            logger.info(f"✅ Saved medium dataset to {medium_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving datasets: {e}")
            return False
    
    def generate_statistics(self, unified_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate statistics about the unified dataset."""
        try:
            logger.info("📊 Generating dataset statistics...")
            
            stats = {
                'total_jobs': len(unified_df),
                'unique_companies': unified_df['company'].nunique(),
                'unique_locations': unified_df['location'].nunique(),
                'experience_levels': unified_df['experience_level'].value_counts().to_dict(),
                'work_types': unified_df['work_type'].value_counts().to_dict(),
                'remote_jobs': unified_df['remote_allowed'].value_counts().to_dict(),
                'jobs_with_skills': unified_df['skills'].ne('N/A').sum(),
                'jobs_with_industry': unified_df['industry'].ne('N/A').sum(),
                'jobs_with_benefits': unified_df['benefits'].ne('N/A').sum(),
                'jobs_with_salary': unified_df['salary_range'].ne('N/A').sum()
            }
            
            # Top locations
            top_locations = unified_df['location'].value_counts().head(10).to_dict()
            stats['top_locations'] = top_locations
            
            # Top industries
            if 'industry' in unified_df.columns:
                top_industries = unified_df['industry'].value_counts().head(10).to_dict()
                stats['top_industries'] = top_industries
            
            logger.info("✅ Statistics generated")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error generating statistics: {e}")
            return {}
    
    def run_integration(self) -> bool:
        """Run the complete integration process."""
        try:
            logger.info("🚀 Starting dataset integration process...")
            
            # Step 1: Load all datasets
            if not self.load_all_datasets():
                return False
            
            # Step 2: Clean and preprocess
            if not self.clean_and_preprocess():
                return False
            
            # Step 3: Enrich job data
            if not self.enrich_job_data():
                return False
            
            # Step 4: Create unified dataset
            unified_df = self.create_unified_dataset()
            if unified_df is None:
                return False
            
            # Step 5: Save datasets
            if not self.save_unified_dataset(unified_df):
                return False
            
            # Step 6: Generate statistics
            stats = self.generate_statistics(unified_df)
            
            # Display summary
            logger.info("\n" + "="*60)
            logger.info("🎉 DATASET INTEGRATION COMPLETED SUCCESSFULLY!")
            logger.info("="*60)
            logger.info(f"📊 Total Jobs: {stats.get('total_jobs', 0):,}")
            logger.info(f"🏢 Unique Companies: {stats.get('unique_companies', 0):,}")
            logger.info(f"🌍 Unique Locations: {stats.get('unique_locations', 0):,}")
            logger.info(f"💼 Jobs with Skills: {stats.get('jobs_with_skills', 0):,}")
            logger.info(f"🏭 Jobs with Industry: {stats.get('jobs_with_industry', 0):,}")
            logger.info(f"💰 Jobs with Salary: {stats.get('jobs_with_salary', 0):,}")
            
            logger.info("\n📁 Generated Files:")
            logger.info("   - data/unified_job_dataset.csv (Full dataset)")
            logger.info("   - data/job_dataset_medium.csv (5K jobs for development)")
            logger.info("   - data/job_dataset_sample.csv (1K jobs for testing)")
            
            logger.info("\n🚀 Next Steps:")
            logger.info("   1. Update the job_matcher.py to use the new dataset")
            logger.info("   2. Run: python train_model.py")
            logger.info("   3. Test the system: python test_system.py")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Integration process failed: {e}")
            return False


def main():
    """Main function to run the integration."""
    logger.info("🎯 Career Guidance Platform - Dataset Integration")
    logger.info("=" * 60)
    
    integrator = DatasetIntegrator()
    
    if integrator.run_integration():
        logger.info("\n🎉 Integration completed successfully!")
        return True
    else:
        logger.error("\n❌ Integration failed!")
        return False


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⏹️  Integration interrupted by user")
        exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        exit(1) 