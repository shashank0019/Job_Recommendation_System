#!/usr/bin/env python3
"""
Keep the recommendation server running persistently
"""
import subprocess
import time
import requests
import os
import signal
import sys

def check_server_health():
    """Check if the server is responding"""
    try:
        response = requests.get('http://localhost:5000/', timeout=5)
        return response.status_code == 200
    except:
        return False

def start_server():
    """Start the server process"""
    print("🚀 Starting recommendation server...")
    
    # Change to the correct directory
    os.chdir(r'c:\Users\SHASHANK\Downloads\Documents\vs code\Final_pro')
    
    # Start the server process
    process = subprocess.Popen(
        ['python', 'simple_recommendation_server.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    return process

def main():
    """Main server management loop"""
    process = None
    
    def signal_handler(sig, frame):
        print("\n🛑 Shutting down server...")
        if process:
            process.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    while True:
        try:
            # Check if server is running
            if not check_server_health():
                print("💊 Server not responding, starting/restarting...")
                
                # Kill existing process if any
                if process and process.poll() is None:
                    process.terminate()
                    process.wait()
                
                # Start new process
                process = start_server()
                
                # Wait for server to start
                print("⏳ Waiting for server to start...")
                for i in range(10):
                    time.sleep(2)
                    if check_server_health():
                        print("✅ Server is now running!")
                        break
                    print(f"   Attempt {i+1}/10...")
                else:
                    print("❌ Server failed to start after 10 attempts")
                    # Print server output for debugging
                    if process:
                        try:
                            output, _ = process.communicate(timeout=1)
                            print("Server output:", output)
                        except:
                            pass
            else:
                print("✅ Server is running normally")
            
            # Wait before next check
            time.sleep(10)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error in server management: {e}")
            time.sleep(5)

if __name__ == "__main__":
    print("🎯 Experience Server Manager")
    print("📍 Keeping recommendation server alive for experiences API")
    print("🔧 Press Ctrl+C to stop")
    main()