#!/usr/bin/env python3
"""
Install OpenAI package for enhanced interview functionality
"""

import subprocess
import sys

def install_openai():
    """Install OpenAI package"""
    try:
        print("Installing OpenAI package...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openai>=1.0.0"])
        print("✅ OpenAI package installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install OpenAI package: {e}")
        return False

if __name__ == "__main__":
    install_openai()
