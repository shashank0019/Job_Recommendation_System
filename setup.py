#!/usr/bin/env python3
"""
Setup Script for Career Guidance Platform

This script helps set up the Career Guidance Platform by:
1. Installing required dependencies
2. Downloading spaCy model
3. Training the initial model
4. Testing the system
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a shell command and handle errors."""
    logger.info(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed:")
        logger.error(f"   Command: {command}")
        logger.error(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    logger.info("🐍 Checking Python version...")
    
    if sys.version_info < (3, 7):
        logger.error("❌ Python 3.7 or higher is required")
        logger.error(f"   Current version: {sys.version}")
        return False
    
    logger.info(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} is compatible")
    return True

def install_dependencies():
    """Install required Python packages."""
    logger.info("📦 Installing Python dependencies...")
    
    # Check if requirements.txt exists
    if not Path("requirements.txt").exists():
        logger.error("❌ requirements.txt not found")
        return False
    
    # Install packages
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python packages"
    )

def download_spacy_model():
    """Download the required spaCy model."""
    logger.info("🤖 Downloading spaCy model...")
    
    # Check if model is already downloaded
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        logger.info("✅ spaCy model 'en_core_web_sm' is already available")
        return True
    except OSError:
        pass
    
    # Download the model
    return run_command(
        f"{sys.executable} -m spacy download en_core_web_sm",
        "Downloading spaCy model"
    )

def check_data_files():
    """Check if required data files exist."""
    logger.info("📁 Checking data files...")
    
    data_dir = Path("data")
    if not data_dir.exists():
        logger.error("❌ Data directory not found")
        return False
    
    csv_file = data_dir / "job_dataset.csv"
    if not csv_file.exists():
        logger.error("❌ Job dataset CSV not found")
        return False
    
    logger.info("✅ Data files are available")
    return True

def train_model():
    """Train the job matching model."""
    logger.info("🤖 Training job matching model...")
    
    return run_command(
        f"{sys.executable} train_model.py",
        "Training TF-IDF model"
    )

def test_system():
    """Test the complete system."""
    logger.info("🧪 Testing system components...")
    
    return run_command(
        f"{sys.executable} test_system.py",
        "Running system tests"
    )

def create_env_file():
    """Create a .env file template if it doesn't exist."""
    env_file = Path(".env")
    if env_file.exists():
        logger.info("✅ .env file already exists")
        return True
    
    logger.info("📝 Creating .env file template...")
    
    env_content = """# RapidAPI Configuration
RAPIDAPI_KEY=your_rapidapi_key_here
RAPIDAPI_HOST=jsearch.p.rapidapi.com

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# Model Configuration
MODEL_PATH=data/trained_model.joblib
VECTORIZER_PATH=data/tfidf_vectorizer.joblib
CSV_DATA_PATH=data/job_dataset.csv
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        logger.info("✅ .env file created successfully")
        logger.info("⚠️  Please edit .env file with your actual API keys")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create .env file: {e}")
        return False

def main():
    """Main setup function."""
    logger.info("🚀 Career Guidance Platform Setup")
    logger.info("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check data files
    if not check_data_files():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Download spaCy model
    if not download_spacy_model():
        return False
    
    # Create .env file
    if not create_env_file():
        return False
    
    # Train model
    if not train_model():
        return False
    
    # Test system
    if not test_system():
        logger.warning("⚠️  System tests failed, but setup completed")
        logger.warning("   You can still try to run the application")
    
    logger.info("\n🎉 Setup completed successfully!")
    logger.info("\n📋 Next steps:")
    logger.info("   1. Edit .env file with your RapidAPI key (optional)")
    logger.info("   2. Start the application: python app.py")
    logger.info("   3. Open http://localhost:5000 in your browser")
    logger.info("\n📚 For more information, see README.md")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⏹️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error during setup: {e}")
        sys.exit(1) 