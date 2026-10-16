"""
Comprehensive API Testing Script
Tests all endpoints to verify they're working correctly
"""
import requests
import json
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:5001"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def test_endpoint(name: str, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> Dict[str, Any]:
    """Test a single API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            return {"status": "SKIP", "message": "Unsupported method"}
        
        status = "PASS" if response.status_code in [200, 201] else "FAIL"
        
        return {
            "status": status,
            "code": response.status_code,
            "response": response.json() if response.headers.get('content-type') == 'application/json' else response.text[:200]
        }
    
    except requests.exceptions.ConnectionError:
        return {"status": "ERROR", "message": "Server not running"}
    except requests.exceptions.Timeout:
        return {"status": "ERROR", "message": "Request timeout"}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

def print_result(name: str, result: Dict[str, Any]):
    """Print test result with colors"""
    if result["status"] == "PASS":
        print(f"{Colors.GREEN}✓ PASS{Colors.RESET} - {name} (Status: {result.get('code', 'N/A')})")
    elif result["status"] == "FAIL":
        print(f"{Colors.RED}✗ FAIL{Colors.RESET} - {name} (Status: {result.get('code', 'N/A')})")
        if 'response' in result:
            print(f"  Response: {result['response']}")
    elif result["status"] == "ERROR":
        print(f"{Colors.RED}✗ ERROR{Colors.RESET} - {name}: {result.get('message', 'Unknown error')}")
    else:
        print(f"{Colors.YELLOW}⊘ SKIP{Colors.RESET} - {name}")

def main():
    print(f"\n{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BLUE}API TESTING REPORT - Career Guidance Platform{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}\n")
    
    tests_passed = 0
    tests_failed = 0
    tests_error = 0
    
    # Test cases
    tests = [
        # Basic endpoints
        ("Health Check", "GET", "/health", None),
        ("Test Route", "GET", "/test", None),
        ("Home Page", "GET", "/", None),
        
        # Authentication endpoints
        ("Auth Health Check", "GET", "/auth/health", None),
        ("Auth Verify (no token)", "GET", "/auth/verify", None),
        
        # Job posting endpoints
        ("Get All Jobs", "GET", "/api/jobs", None),
        ("Get My Jobs (no auth)", "GET", "/api/my-jobs", None),
        
        # Interview experience endpoints
        ("Get All Experiences", "GET", "/api/experiences", None),
        ("Get My Experiences (no auth)", "GET", "/api/my-experiences", None),
        
        # Resume upload endpoint - test with sample data
        ("Upload Resume (JSON)", "POST", "/upload", {
            "resume_text": "Software Engineer with 5 years of experience in Python, JavaScript, React, Node.js, MongoDB, AWS."
        }),
        
        # Recommendation endpoint - test with sample data
        ("Get Recommendations", "POST", "/recommend", {
            "resume_text": "Python Developer with experience in Flask, Django, Machine Learning, Data Science, SQL, MongoDB.",
            "max_results": 5
        }),
        
        # Problems endpoint
        ("Get Problems", "GET", "/api/problems", None),
        
        # Auth Signup test (will fail if user exists, but tests endpoint)
        ("Signup Test", "POST", "/auth/signup", {
            "email": "test@example.com",
            "password": "Test123!",
            "name": "Test User"
        }),
        
        # Auth Signin test (will fail if user doesn't exist, but tests endpoint)
        ("Signin Test", "POST", "/auth/signin", {
            "email": "test@example.com",
            "password": "Test123!"
        }),
    ]
    
    print(f"{Colors.YELLOW}Running {len(tests)} API tests...{Colors.RESET}\n")
    
    for test_name, method, endpoint, data in tests:
        result = test_endpoint(test_name, method, endpoint, data)
        print_result(test_name, result)
        
        if result["status"] == "PASS":
            tests_passed += 1
        elif result["status"] == "FAIL":
            tests_failed += 1
        elif result["status"] == "ERROR":
            tests_error += 1
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BLUE}TEST SUMMARY{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.GREEN}Passed:{Colors.RESET} {tests_passed}")
    print(f"{Colors.RED}Failed:{Colors.RESET} {tests_failed}")
    print(f"{Colors.RED}Errors:{Colors.RESET} {tests_error}")
    print(f"Total: {len(tests)}")
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}\n")
    
    # Additional endpoint info
    print(f"{Colors.YELLOW}Available Endpoints:{Colors.RESET}")
    print(f"  • GET  {BASE_URL}/health - Health check")
    print(f"  • GET  {BASE_URL}/test - Test route")
    print(f"  • POST {BASE_URL}/upload - Upload resume")
    print(f"  • POST {BASE_URL}/recommend - Get job recommendations")
    print(f"  • GET  {BASE_URL}/api/problems - Get coding problems")
    print(f"  • POST {BASE_URL}/auth/signup - User signup")
    print(f"  • POST {BASE_URL}/auth/signin - User signin")
    print(f"  • GET  {BASE_URL}/auth/profile - Get user profile")
    print(f"  • GET  {BASE_URL}/api/jobs - Get all jobs")
    print(f"  • POST {BASE_URL}/api/jobs - Create job posting")
    print(f"  • GET  {BASE_URL}/api/experiences - Get interview experiences")
    print(f"  • POST {BASE_URL}/api/experiences - Create interview experience")
    print(f"\n{Colors.YELLOW}Note:{Colors.RESET} Make sure the backend server is running on {BASE_URL}\n")

if __name__ == "__main__":
    main()
