#!/usr/bin/env python3
"""
Minimal Flask app to test basic functionality
"""

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"]}})

@app.route('/api/problems')
def test_problems():
    return {"success": True, "message": "Flask app is working!", "items": []}

@app.route('/')
def index():
    return "Flask app is running!"

if __name__ == '__main__':
    print("🚀 Starting minimal Flask app...")
    app.run(host='127.0.0.1', port=5000, debug=False)
