#!/usr/bin/env python3
"""
Setup Enhanced Interview System with OpenAI
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    
    packages = [
        "openai>=1.0.0",
        "python-dotenv"  # For environment variable management
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True

def create_env_file():
    """Create .env file for API key"""
    env_content = """# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=true
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env template file")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def test_setup():
    """Test the setup"""
    print("\n🧪 Testing setup...")
    
    try:
        # Test import
        from interview_openai import initialize_openai_generator
        print("✅ OpenAI interview module imported successfully")
        
        # Test initialization
        api_key = os.getenv('OPENAI_API_KEY', 'your_openai_api_key_here')
        if initialize_openai_generator(api_key):
            print("✅ OpenAI generator initialized successfully")
            return True
        else:
            print("❌ Failed to initialize OpenAI generator")
            return False
            
    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Enhanced Interview System with OpenAI")
    print("=" * 60)
    
    # Step 1: Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements. Please install manually:")
        print("pip install openai>=1.0.0 python-dotenv")
        return False
    
    # Step 2: Create .env file
    if not create_env_file():
        print("❌ Failed to create .env file")
        return False
    
    # Step 3: Test setup
    if not test_setup():
        print("❌ Setup test failed")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Enhanced Interview System setup completed successfully!")
    print("\n📋 What's new:")
    print("• OpenAI-powered question generation")
    print("• Intelligent answer evaluation")
    print("• Adaptive questioning based on responses")
    print("• Enhanced feedback with specific suggestions")
    print("• Fallback to local models when needed")
    
    print("\n🚀 To start the application:")
    print("python app_minimal.py")
    
    print("\n🧪 To test the OpenAI integration:")
    print("python test_openai_interview.py")
    
    return True

if __name__ == "__main__":
    main()
