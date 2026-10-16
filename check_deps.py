#!/usr/bin/env python3

import sys
import importlib

def check_dependency(module_name, import_path=None):
    """Check if a dependency is installed and importable."""
    try:
        if import_path:
            importlib.import_module(import_path)
        else:
            importlib.import_module(module_name)
        print(f"✅ {module_name}: OK")
        return True
    except ImportError as e:
        print(f"❌ {module_name}: MISSING - {e}")
        return False
    except Exception as e:
        print(f"⚠️  {module_name}: ERROR - {e}")
        return False

def check_spacy_model():
    """Check if spaCy English model is available."""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✅ spaCy en_core_web_sm model: OK")
        return True
    except OSError:
        print("❌ spaCy en_core_web_sm model: MISSING")
        print("   Install with: python -m spacy download en_core_web_sm")
        return False
    except Exception as e:
        print(f"⚠️  spaCy en_core_web_sm model: ERROR - {e}")
        return False

def main():
    print("🔍 Checking dependencies for Career Guidance Platform...")
    print("=" * 60)
    
    dependencies = [
        ("Flask", "flask"),
        ("Flask-CORS", "flask_cors"),
        ("spaCy", "spacy"),
        ("NLTK", "nltk"),
        ("PyPDF2", "PyPDF2"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("scikit-learn", "sklearn"),
        ("joblib", "joblib"),
        ("requests", "requests"),
        ("python-dotenv", "dotenv"),
        ("pymongo", "pymongo"),
        ("bcrypt", "bcrypt"),
    ]
    
    missing_deps = []
    
    for name, module in dependencies:
        if not check_dependency(name, module):
            missing_deps.append(name)
    
    print("\n🔍 Checking spaCy model...")
    if not check_spacy_model():
        missing_deps.append("spaCy en_core_web_sm model")
    
    print("\n" + "=" * 60)
    if missing_deps:
        print(f"❌ {len(missing_deps)} dependencies are missing:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nTo fix, run:")
        print("   pip install -r requirements.txt")
        print("   python -m spacy download en_core_web_sm")
    else:
        print("✅ All dependencies are installed correctly!")
    
    # Test resume parser specifically
    print("\n🧪 Testing ResumeParser...")
    try:
        from resume_parser import ResumeParser
        parser = ResumeParser()
        test_result = parser.parse_resume("Python developer with React experience")
        if test_result.get('success'):
            print("✅ ResumeParser: Working correctly")
        else:
            print(f"❌ ResumeParser: Error - {test_result.get('error')}")
    except Exception as e:
        print(f"❌ ResumeParser: Failed to import/test - {e}")

if __name__ == "__main__":
    main()
