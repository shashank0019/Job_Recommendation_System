"""
Minimal Flask app for authentication testing
"""
from flask import Flask
from flask_cors import CORS
import logging
from config.database import get_db_config
from auth.routes import auth_bp

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-this-in-production'

# Enable CORS
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5174", "http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Initialize database connection
logger.info("Initializing database connection...")
db_config = get_db_config()
db_config.connect()

if db_config.db is not None:
    logger.info(f"✅ Database connected: {db_config.db.name}")
else:
    logger.error("❌ Database connection failed")

# Register authentication blueprint
app.register_blueprint(auth_bp, url_prefix='/auth')

# Register problems API blueprint
try:
    from problems_api import problems_bp
    app.register_blueprint(problems_bp, url_prefix='/api')
    logger.info("✅ Problems API registered at /api")
except Exception as e:
    logger.warning(f"⚠️ Problems API not available: {e}")

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return {'status': 'ok', 'message': 'Server is running'}, 200

# Root endpoint
@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return {'message': 'Authentication API Server', 'version': '1.0'}, 200

# Simple interview questions endpoint
@app.route('/interview/questions', methods=['POST', 'GET'])
def interview_questions():
    """Return sample interview questions"""
    return {
        'questions': [
            {
                'id': 1,
                'text': 'Tell me about yourself',
                'category': 'behavioral',
                'difficulty': 'easy'
            },
            {
                'id': 2,
                'text': 'What are your strengths?',
                'category': 'behavioral',
                'difficulty': 'easy'
            },
            {
                'id': 3,
                'text': 'Describe a challenging project you worked on',
                'category': 'technical',
                'difficulty': 'medium'
            }
        ]
    }, 200

if __name__ == '__main__':
    logger.info("Starting Flask server on http://localhost:5000")
    logger.info("Registered routes:")
    for rule in app.url_map.iter_rules():
        logger.info(f"  {rule.endpoint}: {rule.rule} [{', '.join(rule.methods)}]")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
