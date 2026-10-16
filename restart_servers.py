#!/usr/bin/env python3

import subprocess
import time
import sys
import os

def kill_processes_on_port(port):
    """Kill all processes running on a specific port."""
    try:
        # Find processes using the port
        result = subprocess.run(
            f'netstat -ano | findstr ":{port}"',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            pids = set()
            
            for line in lines:
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        if pid.isdigit():
                            pids.add(pid)
            
            # Kill each PID
            for pid in pids:
                try:
                    subprocess.run(f'taskkill /F /PID {pid}', shell=True, check=True)
                    print(f"✅ Killed process {pid} on port {port}")
                except subprocess.CalledProcessError:
                    print(f"⚠️  Could not kill process {pid}")
                    
            return len(pids) > 0
        
    except Exception as e:
        print(f"❌ Error checking port {port}: {e}")
        return False
    
    return False

def wait_for_server(url, max_attempts=10):
    """Wait for a server to become available."""
    import requests
    
    for i in range(max_attempts):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False

def main():
    print("🔄 Restarting Career Guidance Platform Servers")
    print("=" * 50)
    
    # Step 1: Kill existing processes
    print("\n1️⃣ Cleaning up existing processes...")
    
    backend_killed = kill_processes_on_port(5000)
    frontend_killed = kill_processes_on_port(5174)
    
    if backend_killed or frontend_killed:
        print("⏳ Waiting for processes to terminate...")
        time.sleep(3)
    
    # Step 2: Start backend
    print("\n2️⃣ Starting backend server...")
    
    backend_process = None
    try:
        backend_process = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print("⏳ Waiting for backend to start...")
        if wait_for_server("http://localhost:5000/health"):
            print("✅ Backend server started successfully")
        else:
            print("❌ Backend server failed to start")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False
    
    # Step 3: Start frontend
    print("\n3️⃣ Starting frontend server...")
    
    frontend_process = None
    try:
        frontend_dir = os.path.join(os.getcwd(), "frontend")
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print("⏳ Waiting for frontend to start...")
        if wait_for_server("http://localhost:5174"):
            print("✅ Frontend server started successfully")
        else:
            print("❌ Frontend server failed to start")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return False
    
    # Step 4: Final test
    print("\n4️⃣ Testing all endpoints...")
    
    import requests
    
    tests = [
        ("Backend Health", "http://localhost:5000/health"),
        ("Backend Upload", "http://localhost:5000/upload"),
        ("Backend Problems", "http://localhost:5000/api/problems"),
        ("Frontend", "http://localhost:5174"),
    ]
    
    all_working = True
    for name, url in tests:
        try:
            if "upload" in url:
                response = requests.post(url, json={"resume_text": "test"}, timeout=5)
            else:
                response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {name}: Working")
            else:
                print(f"❌ {name}: Failed ({response.status_code})")
                all_working = False
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            all_working = False
    
    # Summary
    print(f"\n🎯 RESULT")
    print("-" * 30)
    
    if all_working:
        print("🎉 All servers are running correctly!")
        print("\n📋 Access URLs:")
        print("   Backend:  http://localhost:5000")
        print("   Frontend: http://localhost:5174")
        print("\n💡 The intermittent issues should now be resolved.")
        print("   If problems persist, restart your browser or clear cache.")
    else:
        print("❌ Some issues remain. Check the logs above.")
    
    return all_working

if __name__ == "__main__":
    main()
