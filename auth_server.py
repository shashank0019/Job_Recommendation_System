#!/usr/bin/env python3
"""
Minimal Flask server for authentication only
"""

from flask import Flask, jsonify
from flask_cors import CORS
import logging

# Setup logging  
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

# Initialize database and auth
try:
    from config.database import db_config
    from auth.routes import auth_bp
    
    # Connect to database
    logger.info("Connecting to database...")
    db_config.connect()
    logger.info(f"Database connected. Using fallback: {db_config.use_local_fallback}")
    
    # Register auth blueprint
    app.register_blueprint(auth_bp, url_prefix='/auth')
    logger.info("Authentication routes registered")
    
except Exception as e:
    logger.error(f"Failed to initialize: {e}")
    import traceback
    traceback.print_exc()

@app.route('/')
def home():
    return jsonify({
        'status': 'running',
        'message': 'Authentication server',
        'endpoints': ['/auth/signup', '/auth/signin', '/auth/health']
    })

@app.route('/health')  
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'auth-server'
    })

if __name__ == '__main__':
    logger.info("🚀 Starting Authentication Server...")
    try:
        # Use waitress for a more stable server
        try:
            from waitress import serve
            logger.info("Using Waitress server...")
            serve(app, host='127.0.0.1', port=5000)
        except ImportError:
            logger.info("Waitress not available, using Flask dev server...")
            app.run(
                host='127.0.0.1',
                port=5000,
                debug=False,
                use_reloader=False,
                threaded=False
            )
    except Exception as e:
        logger.error(f"Server error: {e}")
        import traceback
        traceback.print_exc()