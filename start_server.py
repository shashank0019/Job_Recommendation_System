#!/usr/bin/env python3
"""
Start the correct server for job recommendations with file upload support
"""

import os
import sys
import subprocess
import time
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_port_available(port):
    """Check if a port is available"""
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def kill_process_on_port(port):
    """Kill any process running on the specified port"""
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            # For Windows, we'll just inform the user
            logger.warning(f"Port {port} is in use. Please manually stop any servers running on port {port}")
        else:  # Unix/Linux/Mac
            subprocess.run(['lsof', '-ti', f':{port}', '|', 'xargs', 'kill', '-9'], shell=True)
    except Exception as e:
        logger.warning(f"Could not kill process on port {port}: {e}")

def test_server_endpoints():
    """Test that all required endpoints are working"""
    base_url = "http://localhost:5000"
    
    tests = [
        {
            'name': 'Health Check',
            'method': 'GET',
            'url': f'{base_url}/health',
            'expected_keys': ['status']
        },
        {
            'name': 'JSON Upload',
            'method': 'POST',
            'url': f'{base_url}/upload',
            'data': {'resume_text': 'Software Engineer with React, Node.js, Python experience'},
            'expected_keys': ['success', 'parsed', 'jobs', 'live_jobs']
        },
        {
            'name': 'File Upload',
            'method': 'POST',
            'url': f'{base_url}/upload',
            'files': {'resume_file': ('test.txt', 'Software Engineer with React, Python, 5 years experience', 'text/plain')},
            'expected_keys': ['success', 'parsed', 'jobs', 'live_jobs']
        }
    ]
    
    logger.info("🧪 Testing server endpoints...")
    
    for test in tests:
        try:
            if test['method'] == 'GET':
                response = requests.get(test['url'], timeout=5)
            elif test['method'] == 'POST':
                if 'files' in test:
                    response = requests.post(test['url'], files=test['files'], timeout=10)
                else:
                    response = requests.post(test['url'], json=test['data'], timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if all(key in data for key in test['expected_keys']):
                    logger.info(f"✅ {test['name']}: PASSED")
                else:
                    logger.warning(f"⚠️ {test['name']}: Response missing expected keys")
            else:
                logger.error(f"❌ {test['name']}: HTTP {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ {test['name']}: {e}")
    
    logger.info("🎯 Server testing complete!")

def main():
    """Main function to start the server"""
    logger.info("🚀 Starting Career Guidance Platform Server")
    logger.info("=" * 60)
    
    # Check if port 5000 is available
    if not check_port_available(5000):
        logger.warning("Port 5000 is in use!")
        logger.info("Attempting to free port 5000...")
        kill_process_on_port(5000)
        time.sleep(2)
    
    # Start the main app
    logger.info("Starting app.py server...")
    logger.info("📝 Available endpoints:")
    logger.info("   - GET  /health          - Health check")
    logger.info("   - POST /recommend       - Job recommendations (JSON)")
    logger.info("   - POST /upload          - File/JSON upload with job matching")
    logger.info("   - POST /train           - Retrain the model")
    logger.info("")
    logger.info("🌐 Frontend should connect to: http://localhost:5000")
    logger.info("📁 File uploads: PDF, TXT, DOC, DOCX supported")
    logger.info("💻 JSON uploads: Send resume_text in request body")
    logger.info("")
    
    try:
        # Import and run the app
        from app import app
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        logger.info("\n👋 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        logger.info("💡 Try running: python app.py directly")

if __name__ == "__main__":
    main()
