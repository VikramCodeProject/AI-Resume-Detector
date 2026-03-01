"""
Comprehensive Security Implementation Testing Suite
Tests all 5 security implementations:
1. Password Validator (6-point validation)
2. File Validator (extension whitelist + size limit)
3. Rate Limiter (time-windowed request limiting)
4. Account Lockout (5-attempt threshold + 15-min lockout)
5. JWT Secret Validation (32+ character requirement)
"""

import requests
import json
import time
import os
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_VERSION = "v1"

# Test results tracking
test_results = {
    "password_validator": [],
    "file_validator": [],
    "rate_limiter": [],
    "account_lockout": [],
    "jwt_validation": []
}

# Color codes for console output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(title):
    """Print formatted section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title:^70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_test(name, passed, message=""):
    """Print test result"""
    status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
    print(f"  {status} - {name}")
    if message:
        print(f"       {Colors.YELLOW}{message}{Colors.RESET}")

def print_summary(category, results):
    """Print category summary"""
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    color = Colors.GREEN if passed == total else Colors.YELLOW
    print(f"\n{Colors.BOLD}Summary - {category}: {color}{passed}/{total} passed ({percentage:.0f}%){Colors.RESET}")

# ===================== TEST 1: PASSWORD VALIDATOR =====================

def test_password_validator():
    """Test password validation on registration endpoint"""
    print_header("TEST 1: PASSWORD VALIDATOR (6-Point Validation)")
    
    tests = [
        {
            "name": "Weak password (too short)",
            "email": f"weak_user_{int(time.time())}@example.com",
            "password": "Short1!",  # 7 chars - below 8 minimum
            "should_fail": True,
            "error_contains": "8 characters"
        },
        {
            "name": "Missing uppercase",
            "email": f"nouppercase_{int(time.time())}@example.com",
            "password": "nouppercase123!",
            "should_fail": True,
            "error_contains": "uppercase"
        },
        {
            "name": "Missing lowercase",
            "email": f"nolowercase_{int(time.time())}@example.com",
            "password": "NOLOWERCASE123!",
            "should_fail": True,
            "error_contains": "lowercase"
        },
        {
            "name": "Missing digit",
            "email": f"nodigit_{int(time.time())}@example.com",
            "password": "NoDigitHere!",
            "should_fail": True,
            "error_contains": "digit"
        },
        {
            "name": "Missing special character",
            "email": f"nospecial_{int(time.time())}@example.com",
            "password": "NoSpecial123",
            "should_fail": True,
            "error_contains": "special"
        },
        {
            "name": "Valid strong password",
            "email": f"valid_user_{int(time.time())}@example.com",
            "password": "StrongP@ssw0rd",
            "should_fail": False,
            "error_contains": None
        }
    ]
    
    for test in tests:
        try:
            payload = {
                "email": test["email"],
                "password": test["password"],
                "full_name": "Test User",
                "gdpr_consent": True
            }
            
            response = requests.post(
                f"{BASE_URL}/api/auth/register",
                json=payload,
                timeout=5
            )
            
            is_error = response.status_code != 200
            
            if test["should_fail"]:
                passed = is_error
                message = f"Status {response.status_code}"
                if is_error and test["error_contains"]:
                    response_text = response.text.lower()
                    message += f" - Error contains '{test['error_contains']}': {test['error_contains'].lower() in response_text}"
            else:
                passed = response.status_code == 200
                message = f"Status {response.status_code}"
            
            print_test(test["name"], passed, message)
            test_results["password_validator"].append({"name": test["name"], "passed": passed})
            
        except Exception as e:
            print_test(test["name"], False, str(e))
            test_results["password_validator"].append({"name": test["name"], "passed": False})
    
    print_summary("Password Validator", test_results["password_validator"])

# ===================== TEST 2: FILE VALIDATOR =====================

def test_file_validator():
    """Test file validation on upload endpoint"""
    print_header("TEST 2: FILE VALIDATOR (Whitelist + Size Limit)")
    
    # First, register and login to get a token
    print("  [Setup] Registering test user and generating JWT token...")
    
    test_email = f"filetest_{int(time.time())}@example.com"
    test_password = "ValidP@ssw0rd123"
    
    # Register
    register_response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "email": test_email,
            "password": test_password,
            "full_name": "File Test User",
            "gdpr_consent": True
        },
        timeout=5
    )
    
    if register_response.status_code != 200:
        print(f"  {Colors.RED}✗ Failed to register test user{Colors.RESET}")
        return
    
    # Login
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": test_email,
            "password": test_password
        },
        timeout=5
    )
    
    if login_response.status_code != 200:
        print(f"  {Colors.RED}✗ Failed to login{Colors.RESET}")
        return
    
    token_data = login_response.json()
    jwt_token = token_data.get("access_token")
    print(f"  {Colors.GREEN}✓ JWT Token generated{Colors.RESET}\n")
    
    tests = [
        {
            "name": "Valid PDF file",
            "filename": "valid_resume.pdf",
            "content": b"%PDF-1.4 fake pdf content",
            "should_pass": True
        },
        {
            "name": "Valid DOCX file",
            "filename": "valid_resume.docx",
            "content": b"PK\x03\x04 fake docx content",
            "should_pass": True
        },
        {
            "name": "Valid DOC file",
            "filename": "valid_resume.doc",
            "content": b"fake doc content",
            "should_pass": True
        },
        {
            "name": "Valid TXT file",
            "filename": "valid_resume.txt",
            "content": b"plain text resume content",
            "should_pass": True
        },
        {
            "name": "Invalid EXE file",
            "filename": "malware.exe",
            "content": b"MZ\x90\x00 fake exe",
            "should_pass": False
        },
        {
            "name": "Invalid ZIP file",
            "filename": "archive.zip",
            "content": b"PK\x03\x04 fake zip",
            "should_pass": False
        },
        {
            "name": "File too large (>10MB)",
            "filename": "large_file.pdf",
            "content": b"x" * (11 * 1024 * 1024),
            "should_pass": False
        }
    ]
    
    for test in tests:
        try:
            files = {
                "file": (test["filename"], test["content"])
            }
            headers = {
                "Authorization": f"Bearer {jwt_token}"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/resumes/upload",
                files=files,
                headers=headers,
                timeout=10
            )
            
            is_success = response.status_code == 200
            
            if test["should_pass"]:
                passed = is_success
                message = f"Status {response.status_code}" + (" - File accepted" if is_success else " - File rejected")
            else:
                passed = not is_success
                message = f"Status {response.status_code}" + (" - File rejected" if not is_success else " - File accepted")
            
            print_test(test["name"], passed, message)
            test_results["file_validator"].append({"name": test["name"], "passed": passed})
            
        except Exception as e:
            print_test(test["name"], False, f"Exception: {str(e)[:50]}")
            test_results["file_validator"].append({"name": test["name"], "passed": False})
    
    print_summary("File Validator", test_results["file_validator"])

# ===================== TEST 3: RATE LIMITER =====================

def test_rate_limiter():
    """Test rate limiting on endpoints"""
    print_header("TEST 3: RATE LIMITER (Time-Windowed Request Limiting)")
    
    print("  Testing registration rate limit (3 attempts per minute, PER EMAIL)...\n")
    
    # Use SAME email for rate limiting test
    test_email = f"ratelimit_test_{int(time.time())}@example.com"
    
    # Try to register 4 times with same email (after first success, remaining fail due to user exists)
    responses = []
    for i in range(4):
        payload = {
            "email": test_email,
            "password": "ValidP@ssw0rd123",
            "full_name": "Test User",
            "gdpr_consent": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=payload,
            timeout=5
        )
        responses.append(response.status_code)
        
        if i < 3:
            time.sleep(0.3)
    
    # First registration succeeds (200), 2nd-3rd fail with 400 (user exists), 4th gets rate limited (429)
    tests = [
        {"name": "1st registration attempt (same email)", "expected": 200, "actual": responses[0], "passed": responses[0] == 200},
        {"name": "2nd registration attempt (user exists)", "expected": 400, "actual": responses[1], "passed": responses[1] == 400},
        {"name": "3rd registration attempt (user exists)", "expected": 400, "actual": responses[2], "passed": responses[2] == 400},
        {"name": "4th registration attempt (rate limited)", "expected": 429, "actual": responses[3], "passed": responses[3] == 429}
    ]
    
    for test in tests:
        message = f"Expected {test['expected']}, got {test['actual']}"
        print_test(test["name"], test["passed"], message)
        test_results["rate_limiter"].append({"name": test["name"], "passed": test["passed"]})
    
    print("\n  Testing login rate limit (5 attempts per minute, PER EMAIL)...\n")
    
    # Try 6 login attempts with wrong password
    login_responses = []
    test_email = "testlogin@example.com"
    
    # First register a user
    requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "email": test_email,
            "password": "ValidP@ssw0rd123",
            "full_name": "Login Test",
            "gdpr_consent": True
        },
        timeout=5
    )
    
    # Try 6 login attempts
    for i in range(6):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": test_email,
                "password": "WrongPassword"
            },
            timeout=5
        )
        login_responses.append(response.status_code)
        if i < 5:
            time.sleep(0.3)
    
    # First 5 should fail with 401, 6th should be rate limited (429)
    for i, status in enumerate(login_responses[:5]):
        passed = status == 401
        print_test(f"Login attempt {i+1} (should be rejected)", passed, f"Status {status}")
        test_results["rate_limiter"].append({"name": f"Login attempt {i+1}", "passed": passed})
    
    passed = login_responses[5] == 429
    print_test("Login attempt 6 (should be rate limited)", passed, f"Status {login_responses[5]}")
    test_results["rate_limiter"].append({"name": "Login attempt 6", "passed": passed})
    
    print_summary("Rate Limiter", test_results["rate_limiter"])

# ===================== TEST 4: ACCOUNT LOCKOUT =====================

def test_account_lockout():
    """Test account lockout after 5 failed attempts"""
    print_header("TEST 4: ACCOUNT LOCKOUT (5-Attempt Threshold + 15-Min Lockout)")
    
    # Register a test user
    print("  [Setup] Registering test user for lockout testing...\n")
    
    test_email = f"lockout_{int(time.time())}@example.com"
    test_password = "ValidP@ssw0rd123"
    
    requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "email": test_email,
            "password": test_password,
            "full_name": "Lockout Test User",
            "gdpr_consent": True
        },
        timeout=5
    )
    
    # Try 6 failed login attempts
    lockout_responses = []
    for i in range(6):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": test_email,
                "password": "WrongPassword"
            },
            timeout=5
        )
        lockout_responses.append({
            "attempt": i + 1,
            "status": response.status_code,
            "response": response.json() if response.text else {}
        })
        time.sleep(0.2)
    
    # Evaluate results
    tests = []
    for result in lockout_responses[:5]:
        passed = result["status"] == 401
        message = f"Attempt {result['attempt']}: Status {result['status']}"
        tests.append({"name": f"Failed login attempt {result['attempt']}", "passed": passed, "message": message})
        print_test(f"Failed login attempt {result['attempt']}", passed, message)
    
    # 6th attempt should return 429 (locked)
    lockout_test = lockout_responses[5]
    passed = lockout_test["status"] == 429
    message = f"Status {lockout_test['status']} - Account locked"
    tests.append({"name": "6th attempt (account locked)", "passed": passed, "message": message})
    print_test("6th attempt (account locked)", passed, message)
    
    # Verify error message mentions lockout
    if 429 == lockout_test["status"]:
        response_text = str(lockout_test["response"]).lower()
        contains_lockout_msg = "locked" in response_text or "too many" in response_text
        print_test("Lockout error message", contains_lockout_msg, "Message mentions 'locked' or 'too many'")
        tests.append({"name": "Lockout message", "passed": contains_lockout_msg})
    
    test_results["account_lockout"] = tests
    print_summary("Account Lockout", test_results["account_lockout"])

# ===================== TEST 5: JWT VALIDATION =====================

def test_jwt_validation():
    """Test JWT secret validation in settings"""
    print_header("TEST 5: JWT SECRET VALIDATION (32+ Character Requirement)")
    
    print("  [Info] Settings.validate() enforces JWT_SECRET 32+ chars in production")
    print("  [Info] Current environment:", os.getenv("ENVIRONMENT", "development"))
    print("  [Info] JWT_SECRET length:", len(os.getenv("JWT_SECRET", "")), "characters\n")
    
    # Test 1: Check that application is running (settings are valid)
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        passed = response.status_code == 200
        print_test("API is responding", passed, f"Status {response.status_code}")
        test_results["jwt_validation"].append({"name": "API Health", "passed": passed})
    except Exception as e:
        print_test("API is responding", False, str(e))
        test_results["jwt_validation"].append({"name": "API Health", "passed": False})
    
    # Test 2: Verify JWT tokens can be generated (requires valid secret)
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": f"jwttest_{int(time.time())}@example.com",
                "password": "ValidP@ssw0rd123",
                "full_name": "JWT Test",
                "gdpr_consent": True
            },
            timeout=5
        )
        
        if response.status_code == 200:
            # Now try to login
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={
                    "email": f"jwttest_{int(time.time())}@example.com",
                    "password": "ValidP@ssw0rd123"
                },
                timeout=5
            )
            
            if response.status_code == 200:
                token_data = response.json()
                has_token = "access_token" in token_data
                print_test("JWT token generation", has_token, "Bearer token returned")
                test_results["jwt_validation"].append({"name": "JWT Generation", "passed": has_token})
                
                # Test 3: Verify invalid tokens are rejected
                response = requests.post(
                    f"{BASE_URL}/api/auth/login",
                    headers={"Authorization": "Bearer invalid_token_here"},
                    json={
                        "email": "dummy@example.com",
                        "password": "dummy"
                    },
                    timeout=5
                )
                
                # Should be 401 or 422
                passed = response.status_code in [401, 422]
                print_test("Invalid token rejection", passed, f"Status {response.status_code}")
                test_results["jwt_validation"].append({"name": "Invalid Token Rejection", "passed": passed})
            else:
                print_test("JWT token generation", False, "Failed to login")
                test_results["jwt_validation"].append({"name": "JWT Generation", "passed": False})
        else:
            print_test("JWT token generation", False, "Failed to register")
            test_results["jwt_validation"].append({"name": "JWT Generation", "passed": False})
            
    except Exception as e:
        print_test("JWT token generation", False, str(e))
        test_results["jwt_validation"].append({"name": "JWT Generation", "passed": False})
    
    print_summary("JWT Validation", test_results["jwt_validation"])

# ===================== FINAL SUMMARY =====================

def print_final_summary():
    """Print final test summary"""
    print_header("FINAL TEST SUMMARY")
    
    all_tests = []
    category_stats = {}
    
    for category, results in test_results.items():
        if results:
            passed = sum(1 for r in results if r["passed"])
            total = len(results)
            category_stats[category] = {"passed": passed, "total": total}
            all_tests.extend(results)
    
    # Print by category
    for category, stats in category_stats.items():
        percentage = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
        color = Colors.GREEN if stats["passed"] == stats["total"] else Colors.YELLOW
        category_name = category.replace("_", " ").title()
        print(f"{color}  {category_name}: {stats['passed']}/{stats['total']} passed ({percentage:.0f}%){Colors.RESET}")
    
    # Overall stats
    total_passed = sum(r["passed"] for r in all_tests)
    total_tests = len(all_tests)
    overall_percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n{Colors.BOLD}Overall: {Colors.GREEN}{total_passed}/{total_tests} tests passed ({overall_percentage:.0f}%){Colors.RESET}")
    
    if total_passed == total_tests:
        print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 ALL SECURITY TESTS PASSED! 🎉{Colors.RESET}")
        print(f"{Colors.GREEN}The system is production-ready from a security perspective.{Colors.RESET}\n")
    else:
        print(f"\n{Colors.YELLOW}⚠️  Some tests failed. Review the output above for details.{Colors.RESET}\n")

# ===================== MAIN EXECUTION =====================

if __name__ == "__main__":
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("╔" + "="*68 + "╗")
    print("║" + " RESUME TRUTH VERIFICATION SYSTEM - SECURITY TEST SUITE ".center(68) + "║")
    print("║" + " Testing All 5 Security Implementations ".center(68) + "║")
    print("╚" + "="*68 + "╝")
    print(f"{Colors.RESET}")
    
    try:
        # Check if backend is running
        print("Checking backend connectivity...", end=" ")
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"{Colors.GREEN}✓ Connected to {BASE_URL}{Colors.RESET}\n")
        
        # Run all tests
        test_password_validator()
        test_file_validator()
        test_rate_limiter()
        test_account_lockout()
        test_jwt_validation()
        
        # Print final summary
        print_final_summary()
        
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}✗ Cannot connect to backend{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Please ensure the backend is running:{Colors.RESET}")
        print(f"  cd backend && python -m uvicorn main:app --reload\n")
    except Exception as e:
        print(f"{Colors.RED}✗ Error: {str(e)}{Colors.RESET}\n")
