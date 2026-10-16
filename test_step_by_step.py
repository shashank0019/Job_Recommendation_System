#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

print("Step-by-step auth testing...")

try:
    print("1. Creating Flask app...")
    from flask import Flask
    app = Flask(__name__)
    print("✅ Flask app created")
    
    print("2. Adding CORS...")
    from flask_cors import CORS
    CORS(app)
    print("✅ CORS added")
    
    print("3. Testing basic database config...")
    from config.database import get_db_config
    db_config = get_db_config()
    print(f"✅ Database config created. Type: {type(db_config)}")
    
    print("4. Testing database connection...")
    if db_config:
        success = db_config.connect()
        print(f"✅ Database connection result: {success}")
        print(f"✅ Use fallback: {db_config.use_local_fallback}")
    else:
        print("❌ Database config is None")
    
    print("5. Importing auth blueprint...")
    from auth.routes import auth_bp
    print("✅ Auth blueprint imported")
    
    print("6. Registering blueprint...")
    app.register_blueprint(auth_bp, url_prefix='/auth')
    print("✅ Blueprint registered")
    
    print("7. Testing User model operations...")
    from auth.models import User
    test_user = User.find_by_email("test@example.com")
    print(f"✅ User lookup worked: {test_user is not None}")
    
except Exception as e:
    import traceback
    print(f"❌ Error at step: {e}")
    traceback.print_exc()