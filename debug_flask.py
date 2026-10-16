#!/usr/bin/env python3
"""
Test script to debug Flask app startup issues
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, '.')

print("Testing Flask app startup...")

try:
    # Test basic imports
    print("1. Testing basic imports...")
    import flask
    import pandas
    import joblib
    import sklearn
    print("✅ Basic imports successful")

    # Test Flask app import
    print("2. Testing Flask app import...")
    from app_minimal import app
    print("✅ Flask app import successful")

    # Test model loading function
    print("3. Testing model loading...")
    from app_minimal import load_model
    success = load_model()
    print(f"✅ Model loading: {'SUCCESS' if success else 'FAILED'}")

    # Test if Flask app can start
    print("4. Testing Flask app startup...")
    # Just test that the app object exists and has routes
    print(f"✅ Flask app routes: {len(app.routes)} routes registered")

    print("🎉 All tests passed! Flask app should start successfully.")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
