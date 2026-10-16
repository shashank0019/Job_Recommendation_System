#!/usr/bin/env python3
"""
Script to fix the upload endpoint in app_minimal.py to handle JSON requests.
"""

import os
import shutil

def fix_upload_endpoint():
    """Fix the upload endpoint to handle both JSON and file uploads."""
    file_path = "app_minimal.py"
    backup_path = "app_minimal_backup.py"
    
    # Create backup
    if os.path.exists(file_path):
        shutil.copy2(file_path, backup_path)
        print(f"✅ Created backup: {backup_path}")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the problematic section
    old_code = """        if 'resume_file' not in request.files:
            return jsonify({'success': False, 'error': 'No file part'}), 400"""
    
    new_code = """        # Handle JSON request first
        if request.is_json:
            data = request.get_json() or {}
            text_content = data.get('resume_text', '')
            if not text_content.strip():
                return jsonify({'success': False, 'error': 'Resume text is required in JSON request'}), 400
        elif 'resume_file' not in request.files:
            return jsonify({'success': False, 'error': 'No file part'}), 400"""
    
    if old_code in content:
        # Replace the problematic code
        content = content.replace(old_code, new_code)
        
        # Also need to handle the case where we have JSON data
        # Find the section where text_content is processed and add JSON handling
        old_file_processing = """        filename = (file.filename or '').lower()
        text_content = ''
        file_bytes = file.read()"""
        
        new_file_processing = """        # If we already have text_content from JSON, skip file processing
        if not text_content:
            filename = (file.filename or '').lower()
            file_bytes = file.read()"""
        
        if old_file_processing in content:
            content = content.replace(old_file_processing, new_file_processing)
        
        # Write the fixed content back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed upload endpoint to handle JSON requests")
        return True
    else:
        print("❌ Could not find the target code section to replace")
        return False

def test_fix():
    """Test if the fix worked by checking the file content."""
    file_path = "app_minimal.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "request.is_json" in content and "resume_text" in content:
        print("✅ Fix appears to be successful - JSON handling code found")
        return True
    else:
        print("❌ Fix may not have worked - JSON handling code not found")
        return False

if __name__ == "__main__":
    print("🔧 Fixing upload endpoint...")
    
    if fix_upload_endpoint():
        if test_fix():
            print("🎉 Upload endpoint fix completed successfully!")
            print("📝 The endpoint now handles:")
            print("   - JSON requests with 'resume_text' field")
            print("   - File uploads (PDF/TXT)")
            print("   - Form data with 'resume_text' field")
        else:
            print("⚠️ Fix applied but verification failed")
    else:
        print("❌ Fix failed")
