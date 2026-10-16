#!/usr/bin/env python3
"""
Career Guidance Platform - Complete Startup Script
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

# Ensure UTF-8 output encoding on Windows
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def get_python_executable():
    """Find the best Python executable with required dependencies installed"""
    try:
        import flask, sklearn, pandas, joblib  # noqa: F401
        return sys.executable
    except ImportError:
        pass
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base_dir, ".venv", "Scripts", "python.exe"),
        os.path.join(os.getcwd(), ".venv", "Scripts", "python.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Python\Python313\python.exe"),
        r"C:\Users\shash\AppData\Local\Programs\Python\Python313\python.exe",
        r"C:\Python313\python.exe",
    ]
    for cand in candidates:
        if os.path.exists(cand):
            try:
                res = subprocess.run([cand, "-c", "import flask, sklearn, pandas; print('ok')"], capture_output=True, text=True)
                if "ok" in res.stdout:
                    return cand
            except Exception:
                pass
    
    try:
        p = subprocess.run(["py", "-3.13", "-c", "import sys; print(sys.executable)"], capture_output=True, text=True)
        path = p.stdout.strip()
        if os.path.exists(path):
            return path
    except Exception:
        pass
    
    return sys.executable

def print_banner():
    """Print startup banner"""
    banner = """
🚀 Career Guidance Platform - Enhanced Edition
===============================================
✨ AI-Powered Job Recommendations
🎯 Intelligent Interview System  
💻 LeetCode-Style Coding Problems
🎨 Beautiful Modern Interface
🔒 Comprehensive Security Features
===============================================
    """
    print(banner)

def check_dependencies(python_exe=None):
    """Check if required dependencies are installed"""
    print("📦 Checking dependencies...")
    if not python_exe:
        python_exe = get_python_executable()
    
    required_packages = [
        'flask', 'pandas', 'scikit-learn', 'requests', 
        'flask-cors', 'joblib', 'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        mod_name = package.replace('-', '_')
        cmd = [python_exe, "-c", f"import {mod_name}"]
        res = subprocess.run(cmd, capture_output=True)
        if res.returncode == 0:
            print(f"   ✅ {package}")
        else:
            missing_packages.append(package)
            print(f"   ❌ {package} - Missing")
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        try:
            subprocess.check_call([python_exe, "-m", "pip", "install"] + missing_packages)
            print("✅ All packages installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages. Please run: pip install -r requirements.txt")
            return False
    
    # Check OpenAI (optional)
    res_openai = subprocess.run([python_exe, "-c", "import openai"], capture_output=True)
    if res_openai.returncode == 0:
        print("   ✅ openai (Enhanced features available)")
    else:
        print("   ⚠️ openai - Optional (Enhanced features disabled)")
    
    return True

def check_data_files():
    """Check if required data files exist"""
    print("\n📁 Checking data files...")
    
    required_files = [
        "data/unified_job_dataset.csv",
        "data/tfidf_vectorizer.joblib", 
        "data/trained_model.joblib",
        "data/Problems/problems.json"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            print(f"   ✅ {file_path} ({size:.1f} MB)")
        else:
            missing_files.append(file_path)
            print(f"   ❌ {file_path} - Missing")
    
    if missing_files:
        print(f"\n⚠️ Missing data files: {len(missing_files)} files")
        print("Some features may not work properly.")
        return False
    
    return True

def start_backend(python_exe=None):
    """Start the Flask backend"""
    print("\n🔧 Starting backend server...")
    if not python_exe:
        python_exe = get_python_executable()
    
    try:
        backend_log = open("backend.log", "w", encoding="utf-8")
        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        process = subprocess.Popen(
            [python_exe, "-X", "utf8", "app_minimal.py"],
            stdout=backend_log,
            stderr=subprocess.STDOUT,
            text=True,
            env=env
        )
        
        # Poll health endpoint up to 15 seconds
        print("   ⏳ Loading machine learning models and dataset...", end="", flush=True)
        started = False
        import urllib.request
        for _ in range(15):
            time.sleep(1)
            print(".", end="", flush=True)
            if process.poll() is not None:
                break
            try:
                req = urllib.request.urlopen("http://127.0.0.1:5000/health", timeout=1)
                if req.status == 200:
                    started = True
                    break
            except Exception:
                pass
        print()
        
        if started or (process.poll() is None):
            print("   ✅ Backend server started successfully!")
            print("   🌐 API available at: http://127.0.0.1:5000")
            print("   📄 Logs: backend.log")
            return process
        else:
            backend_log.close()
            with open("backend.log", "r", encoding="utf-8", errors="replace") as f:
                err_content = f.read()
            print(f"   ❌ Backend failed to start:")
            print(f"   Error: {err_content}")
            return None
            
    except Exception as e:
        print(f"   ❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the React frontend"""
    print("\n🎨 Starting frontend development server...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("   ❌ Frontend directory not found")
        return None
    
    try:
        # Check if node_modules exists
        node_modules = frontend_dir / "node_modules"
        if not node_modules.exists():
            print("   📦 Installing frontend dependencies...")
            subprocess.check_call(["npm", "install"], cwd=frontend_dir)
        
        # Start development server with log file to avoid pipe buffer deadlock
        frontend_log = open("frontend.log", "w", encoding="utf-8")
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_dir,
            stdout=frontend_log,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True
        )
        
        # Wait for server to start
        time.sleep(5)
        
        if process.poll() is None:
            print("   ✅ Frontend server started successfully!")
            print("   🌐 Application available at: http://localhost:5173")
            print("   📄 Logs: frontend.log")
            return process
        else:
            frontend_log.close()
            with open("frontend.log", "r", encoding="utf-8") as f:
                err_content = f.read()
            print(f"   ❌ Frontend failed to start:")
            print(f"   Error: {err_content}")
            return None
            
    except FileNotFoundError:
        print("   ❌ Node.js/npm not found. Please install Node.js first.")
        return None
    except Exception as e:
        print(f"   ❌ Failed to start frontend: {e}")
        return None

def open_browser():
    """Open the application in browser"""
    print("\n🌐 Opening application in browser...")
    try:
        webbrowser.open("http://localhost:5173")
        print("   ✅ Browser opened successfully!")
    except Exception as e:
        print(f"   ⚠️ Could not open browser automatically: {e}")
        print("   Please manually open: http://localhost:5173")

def show_status():
    """Show application status and features"""
    status_info = """
🎉 Career Guidance Platform is now running!

📊 Available Features:
├── 🤖 AI Job Recommendations (123,842+ jobs)
├── 📄 Resume Analysis & Skill Gap Detection  
├── 🎯 Enhanced Interview System with OpenAI
├── 💻 Coding Problems (200+ LeetCode-style)
├── 🎨 Modern Responsive Interface
└── 🔒 Comprehensive Security Features

🌐 Access Points:
├── Main Application: http://localhost:5173
├── Backend API: http://127.0.0.1:5000
├── API Documentation: http://127.0.0.1:5000/api
└── Health Check: http://127.0.0.1:5000/health

🛠️ Management:
├── Press Ctrl+C to stop servers
├── Check logs in terminal windows
├── Restart if needed: python start_platform.py
└── Run tests: python test_enhanced_interview_system.py

💡 Tips:
├── Upload a resume to get personalized job recommendations
├── Try the interview system with different skill sets
├── Practice coding problems in the Problems section
└── Explore the beautiful responsive interface on mobile

🚀 Ready to revolutionize your career journey!
    """
    print(status_info)

def main():
    """Main startup function"""
    print_banner()
    
    # Check system requirements
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please fix issues and try again.")
        return False
    
    # Check data files (optional)
    check_data_files()
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("\n❌ Failed to start backend. Check the error messages above.")
        return False
    
    # Start frontend  
    frontend_process = start_frontend()
    if not frontend_process:
        print("\n❌ Failed to start frontend. Backend is still running.")
        print("You can access the API directly at: http://127.0.0.1:5000")
        return False
    
    # Open browser
    time.sleep(2)
    open_browser()
    
    # Show status
    show_status()
    
    try:
        # Keep script running
        print("🔄 Servers are running. Press Ctrl+C to stop...")
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("\n⚠️ Backend process stopped unexpectedly")
                break
            if frontend_process.poll() is not None:
                print("\n⚠️ Frontend process stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down servers...")
        
        # Terminate processes
        try:
            backend_process.terminate()
            frontend_process.terminate()
            
            # Wait for graceful shutdown
            backend_process.wait(timeout=5)
            frontend_process.wait(timeout=5)
            
            print("✅ Servers stopped successfully!")
            
        except subprocess.TimeoutExpired:
            print("⚠️ Force killing processes...")
            backend_process.kill()
            frontend_process.kill()
        
        except Exception as e:
            print(f"⚠️ Error during shutdown: {e}")
    
    print("\n👋 Thank you for using Career Guidance Platform!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
