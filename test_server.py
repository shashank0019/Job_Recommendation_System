#!/usr/bin/env python3
"""Simple test server to verify Unicode encoding fix."""

from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    """Test route with UTF-8 encoding fix."""
    try:
        content = open('templates/index.html', 'r', encoding='utf-8').read()
        print(f"✅ SUCCESS: Template loaded successfully ({len(content)} chars)")
        return render_template_string(content)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return f"Error: {e}", 500

if __name__ == '__main__':
    print("🚀 Starting test server to verify Unicode fix...")
    app.run(host='localhost', port=5001, debug=False)