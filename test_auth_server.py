#!/usr/bin/env python3
"""
Simplified Flask app with just authentication for testing
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import authentication modules
try:
    from auth.routes import auth_bp
    from config.database import db_config
    
    # Initialize Flask app
    app = Flask(__name__)
    CORS(app)
    
    # Register authentication blueprint
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Initialize database connection
    db_config.connect()
    
    @app.route('/')
    def index():
        """Simple health check"""
        return jsonify({
            'status': 'healthy',
            'service': 'Authentication Test Server',
            'version': '1.0.0'
        })
    
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'Authentication Test Server',
            'database_fallback': db_config.use_local_fallback
        })
    
    if __name__ == '__main__':
        print("🚀 Starting Authentication Test Server...")
        print("🔐 Authentication endpoints available at /auth/")
        print("📊 Database fallback active:", db_config.use_local_fallback)
        app.run(host='0.0.0.0', port=5000, debug=True)
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please make sure all authentication modules are properly installed.")
except Exception as e:
    print(f"❌ Server startup error: {e}")
    import traceback
    traceback.print_exc()