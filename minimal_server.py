#!/usr/bin/env python3
"""
Minimal test server to debug the upload endpoint issue.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
import sys

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def health():
    return jsonify({'status': 'OK', 'message': 'Test server is running'})

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload():
    """Minimal upload endpoint for debugging."""
    try:
        print(f"Request method: {request.method}")
        print(f"Request headers: {dict(request.headers)}")
        print(f"Request content type: {request.content_type}")
        print(f"Has files: {bool(request.files)}")
        print(f"Has JSON: {request.is_json}")
        print(f"Has form: {bool(request.form)}")
        
        if request.method == 'OPTIONS':
            return jsonify({'message': 'CORS preflight OK'}), 200
        
        resume_text = ""
        
        # Handle file upload
        if request.files and 'resume_file' in request.files:
            file = request.files['resume_file']
            if file and file.filename:
                print(f"File received: {file.filename}")
                content = file.read()
                if file.filename.lower().endswith('.pdf'):
                    try:
                        import PyPDF2
                        import io
                        pdf_file = io.BytesIO(content)
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        text_parts = []
                        for page in pdf_reader.pages:
                            text_parts.append(page.extract_text())
                        resume_text = '\\n'.join(text_parts)
                        print(f"PDF parsed: {len(resume_text)} characters")
                    except Exception as e:
                        print(f"PDF parsing failed: {e}")
                        resume_text = f"PDF file: {file.filename}"
                else:
                    try:
                        resume_text = content.decode('utf-8', errors='ignore')
                        print(f"Text file parsed: {len(resume_text)} characters")
                    except Exception as e:
                        print(f"Text parsing failed: {e}")
                        resume_text = f"Text file: {file.filename}"
        
        # Handle JSON data
        elif request.is_json:
            data = request.get_json()
            resume_text = data.get('resume_text', '')
            print(f"JSON received: {len(resume_text)} characters")
        
        # Handle form data
        elif request.form:
            resume_text = request.form.get('resume_text', '')
            print(f"Form received: {len(resume_text)} characters")
        
        if not resume_text:
            resume_text = "Default resume text for testing"
        
        # Return success response
        return jsonify({
            'success': True,
            'message': 'Upload successful',
            'text_length': len(resume_text),
            'parsed': {
                'skills': ['python', 'javascript', 'react'],
                'experience': '3+ years'
            },
            'jobs': [
                {'title': 'Software Engineer', 'company': 'Test Corp', 'similarity_score': 0.85}
            ],
            'live_jobs': [
                {'title': 'Python Developer', 'company': 'Live Corp', 'location': 'Remote'}
            ]
        })
        
    except Exception as e:
        error_msg = f"Upload error: {str(e)}"
        print(f"ERROR: {error_msg}")
        traceback.print_exc()
        return jsonify({'error': error_msg, 'success': False}), 500

if __name__ == '__main__':
    print("🚀 Starting minimal test server...")
    print("📡 Server will run on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)