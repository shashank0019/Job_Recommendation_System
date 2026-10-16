#!/usr/bin/env python3
"""
Simple Flask app to test upload endpoint functionality.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/test-upload', methods=['POST'])
def test_upload():
    """Test upload endpoint that handles both JSON and files."""
    try:
        print(f"Request method: {request.method}")
        print(f"Content type: {request.content_type}")
        print(f"Is JSON: {request.is_json}")
        print(f"Has files: {bool(request.files)}")
        print(f"Has form: {bool(request.form)}")
        
        text_content = ''
        
        # Handle JSON request
        if request.is_json:
            data = request.get_json() or {}
            text_content = data.get('resume_text', '')
            print(f"JSON data received: {len(text_content)} characters")
            
            if not text_content.strip():
                return jsonify({'success': False, 'error': 'Resume text is required in JSON request'}), 400
                
            return jsonify({
                'success': True,
                'message': 'JSON upload successful',
                'text_length': len(text_content),
                'method': 'JSON'
            })
        
        # Handle form data
        elif request.form and 'resume_text' in request.form:
            text_content = request.form.get('resume_text', '')
            print(f"Form data received: {len(text_content)} characters")
            
            if not text_content.strip():
                return jsonify({'success': False, 'error': 'Resume text is required in form data'}), 400
                
            return jsonify({
                'success': True,
                'message': 'Form upload successful',
                'text_length': len(text_content),
                'method': 'FORM'
            })
        
        # Handle file upload
        elif 'resume_file' in request.files:
            file = request.files['resume_file']
            if not file or file.filename == '':
                return jsonify({'success': False, 'error': 'No selected file'}), 400
                
            filename = file.filename
            content = file.read().decode('utf-8', errors='ignore')
            print(f"File upload received: {filename}, {len(content)} characters")
            
            return jsonify({
                'success': True,
                'message': 'File upload successful',
                'filename': filename,
                'text_length': len(content),
                'method': 'FILE'
            })
        
        else:
            return jsonify({
                'success': False, 
                'error': 'No data provided',
                'debug': {
                    'is_json': request.is_json,
                    'has_files': bool(request.files),
                    'has_form': bool(request.form),
                    'content_type': request.content_type
                }
            }), 400
            
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'test-upload'})

if __name__ == '__main__':
    print("🧪 Starting test upload server on port 5001...")
    app.run(debug=True, port=5001, host='0.0.0.0')
