#!/usr/bin/env python3
"""Stable server runner for the job posting API"""

import sys
import time
import subprocess
import requests

def is_server_running():
    """Check if server is responding"""
    try:
        response = requests.get("http://localhost:5000/", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_server():
    """Start the server process"""
    try:
        print("🚀 Starting job posting API server...")
        process = subprocess.Popen(
            [sys.executable, "simple_recommendation_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Wait for server to start
        for i in range(10):
            time.sleep(1)
            if is_server_running():
                print(f"✅ Server started successfully on http://localhost:5000")
                
                # Test API endpoints
                try:
                    print("🧪 Testing API endpoints...")
                    
                    # Test /api/jobs
                    response = requests.get("http://localhost:5000/api/jobs", timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        print(f"✅ /api/jobs: {len(data.get('jobs', []))} jobs available")
                    else:
                        print(f"❌ /api/jobs: {response.status_code}")
                    
                    # Test /api/experiences  
                    response = requests.get("http://localhost:5000/api/experiences", timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        print(f"✅ /api/experiences: {len(data.get('experiences', []))} experiences available")
                    else:
                        print(f"❌ /api/experiences: {response.status_code}")
                        
                except Exception as e:
                    print(f"⚠️ API test failed: {e}")
                
                return process
            
            print(f"⏳ Waiting for server... ({i+1}/10)")
        
        print("❌ Server failed to start within timeout")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

if __name__ == "__main__":
    server_process = start_server()
    
    if server_process:
        try:
            print("🎯 Server is running. Press Ctrl+C to stop.")
            server_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            server_process.terminate()
            print("✅ Server stopped")