#!/usr/bin/env python3

try:
    print("Testing app imports...")
    import app
    print("✅ App imported successfully")
    
    # Check if blueprints are registered
    print(f"📋 Registered routes:")
    for rule in app.app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint}")
        
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
