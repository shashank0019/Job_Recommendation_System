#!/usr/bin/env python3

import requests
import json
import time
import sys

def test_endpoint(url, method="GET", data=None, files=None, timeout=5):
    """Test a specific endpoint and return result."""
    try:
        if method == "GET":
            response = requests.get(url, timeout=timeout)
        elif method == "POST":
            if files:
                response = requests.post(url, files=files, timeout=timeout)
            elif data:
                response = requests.post(url, json=data, headers={"Content-Type": "application/json"}, timeout=timeout)
            else:
                response = requests.post(url, timeout=timeout)
        
        return {
            "status": "SUCCESS" if response.status_code == 200 else "FAILED",
            "status_code": response.status_code,
            "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text[:200]
        }
    except requests.exceptions.ConnectionError:
        return {"status": "CONNECTION_ERROR", "error": "Server not accessible"}
    except requests.exceptions.Timeout:
        return {"status": "TIMEOUT", "error": "Request timed out"}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}

def main():
    print("🔍 Comprehensive Platform Test")
    print("=" * 60)
    
    backend_url = "http://localhost:5000"
    frontend_url = "http://localhost:5174"
    
    # Test all backend endpoints
    print("\n🔧 BACKEND TESTS (Port 5000)")
    print("-" * 40)
    
    backend_endpoints = [
        ("Health Check", f"{backend_url}/health", "GET"),
        ("Test Route", f"{backend_url}/test", "GET"),
        ("Auth Sign-in", f"{backend_url}/auth/signin", "POST", {"email": "test@example.com", "password": "test123"}),
        ("Problems API", f"{backend_url}/api/problems", "GET"),
        ("Recommend (JSON)", f"{backend_url}/recommend", "POST", {"resume_text": "Python developer with React experience"}),
        ("Upload (JSON)", f"{backend_url}/upload", "POST", {"resume_text": "Python developer with React experience"}),
    ]
    
    backend_working = True
    for name, url, method, *args in backend_endpoints:
        data = args[0] if args else None
        result = test_endpoint(url, method, data)
        
        status_icon = "✅" if result["status"] == "SUCCESS" else "❌"
        print(f"{status_icon} {name}: {result['status']}")
        
        if result["status"] != "SUCCESS":
            backend_working = False
            if result.get("error"):
                print(f"   Error: {result['error']}")
            elif result.get("status_code"):
                print(f"   Status Code: {result['status_code']}")
    
    # Test file upload separately
    print(f"\n📁 Testing File Upload...")
    files = {'resume_file': ('test.txt', 'Python developer with React experience', 'text/plain')}
    upload_result = test_endpoint(f"{backend_url}/upload", "POST", files=files)
    status_icon = "✅" if upload_result["status"] == "SUCCESS" else "❌"
    print(f"{status_icon} Upload (File): {upload_result['status']}")
    
    # Test frontend
    print(f"\n🌐 FRONTEND TESTS (Port 5174)")
    print("-" * 40)
    
    frontend_result = test_endpoint(frontend_url)
    status_icon = "✅" if frontend_result["status"] == "SUCCESS" else "❌"
    print(f"{status_icon} Frontend Server: {frontend_result['status']}")
    
    # Summary
    print(f"\n📊 SUMMARY")
    print("-" * 40)
    
    if not backend_working:
        print("❌ Backend has issues - some endpoints are not working")
        print("🔧 Recommended actions:")
        print("   1. Check if backend server is running: python app.py")
        print("   2. Check for port conflicts on 5000")
        print("   3. Verify all dependencies are installed")
    else:
        print("✅ Backend is working correctly")
    
    if frontend_result["status"] != "SUCCESS":
        print("❌ Frontend has issues")
        print("🔧 Recommended actions:")
        print("   1. Check if frontend server is running: npm run dev")
        print("   2. Check for port conflicts on 5174")
    else:
        print("✅ Frontend is working correctly")
    
    # Check for common issues
    print(f"\n🔍 COMMON ISSUES CHECK")
    print("-" * 40)
    
    # Check if multiple servers are running
    import subprocess
    try:
        netstat_output = subprocess.check_output("netstat -ano", shell=True, text=True)
        port_5000_count = netstat_output.count(":5000")
        port_5174_count = netstat_output.count(":5174")
        
        if port_5000_count > 2:
            print(f"⚠️  Multiple processes on port 5000 detected ({port_5000_count} instances)")
            print("   This can cause intermittent issues. Kill extra processes.")
        
        if port_5174_count > 2:
            print(f"⚠️  Multiple processes on port 5174 detected ({port_5174_count} instances)")
            print("   This can cause intermittent issues. Kill extra processes.")
        
        if port_5000_count <= 2 and port_5174_count <= 2:
            print("✅ No port conflicts detected")
            
    except Exception as e:
        print(f"⚠️  Could not check for port conflicts: {e}")
    
    # Final recommendation
    print(f"\n🎯 FINAL RECOMMENDATION")
    print("-" * 40)
    
    if backend_working and frontend_result["status"] == "SUCCESS":
        print("🎉 All systems are working! The intermittent issues might be due to:")
        print("   - Network timing issues")
        print("   - Browser cache (try Ctrl+F5 to refresh)")
        print("   - Race conditions during startup")
        print("\n💡 If issues persist:")
        print("   1. Restart both servers")
        print("   2. Clear browser cache")
        print("   3. Check browser console for errors")
    else:
        print("🔧 Issues detected. Follow the recommended actions above.")

if __name__ == "__main__":
    main()
