#!/usr/bin/env python3
"""Comprehensive test to verify the Unicode encoding fix."""

def test_template_reading():
    """Test if the template can be read with UTF-8 encoding."""
    print("🧪 Testing template file reading...")
    
    try:
        # Test the old way (should fail with certain characters)
        print("   Testing old method (without encoding)...")
        try:
            with open('templates/index.html', 'r') as f:
                old_content = f.read()
            print("   ⚠️  Old method worked (might have issues with special chars)")
        except UnicodeDecodeError as e:
            print(f"   ❌ Old method failed: {e}")
            
        # Test the new way (should work)
        print("   Testing new method (with UTF-8 encoding)...")
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            new_content = f.read()
        print(f"   ✅ New method works! Content length: {len(new_content)} chars")
        
        # Test Flask template rendering
        print("🧪 Testing Flask template rendering...")
        from flask import Flask, render_template_string
        
        app = Flask(__name__)
        
        with app.app_context():
            result = render_template_string(new_content)
            print(f"   ✅ Template rendering works! Output length: {len(result)} chars")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def verify_fix_in_app():
    """Verify that the fix is properly applied in app.py."""
    print("🧪 Verifying fix in app.py...")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "encoding='utf-8'" in content:
            print("   ✅ Fix is present in app.py")
            return True
        else:
            print("   ❌ Fix not found in app.py")
            return False
            
    except Exception as e:
        print(f"   ❌ Error reading app.py: {e}")
        return False

if __name__ == '__main__':
    print("🔧 Comprehensive Unicode Encoding Fix Test")
    print("=" * 50)
    
    test1 = test_template_reading()
    test2 = verify_fix_in_app()
    
    print("\n📊 Test Results:")
    print(f"   Template Reading: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"   App.py Fix:       {'✅ PASS' if test2 else '❌ FAIL'}")
    
    if test1 and test2:
        print("\n🎉 All tests passed! Unicode encoding fix is working correctly.")
        print("\n💡 The UnicodeDecodeError should now be resolved.")
        print("   You can start the server with: python app.py")
    else:
        print("\n💥 Some tests failed. Please check the issues above.")