#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

print("Testing auth imports...")

try:
    print("1. Testing database import...")
    from config.database import get_db_config
    print("✅ Database import successful")
    
    print("2. Testing database connection...")
    db_config = get_db_config()
    print(f"✅ Database config created. Use fallback: {db_config.use_local_fallback}")
    
    print("3. Testing auth models import...")
    from auth.models import User, Session
    print("✅ Auth models import successful")
    
    print("4. Testing auth utils import...")
    from auth.utils import AuthUtils
    print("✅ Auth utils import successful")
    
    print("5. Testing auth middleware import...")
    from auth.middleware import require_auth
    print("✅ Auth middleware import successful")
    
    print("6. Testing auth routes import...")
    from auth.routes import auth_bp
    print("✅ Auth routes import successful")
    print(f"✅ Blueprint name: {auth_bp.name}")
    print(f"✅ Blueprint URL prefix: {auth_bp.url_prefix}")
    
    # Test if routes are registered
    print("7. Testing blueprint routes...")
    rules = []
    for rule in auth_bp.deferred_functions:
        rules.append(str(rule))
    print(f"✅ Found {len(rules)} deferred functions")
    
except Exception as e:
    import traceback
    print(f"❌ Error: {e}")
    traceback.print_exc()