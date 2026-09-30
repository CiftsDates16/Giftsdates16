#!/usr/bin/env python3
"""
Backend API Testing for GiftsDates Dating App
Tests core authentication and profile flows after restoration from GitHub
"""

import requests
import json
from datetime import datetime
import sys

# Backend URL from frontend/.env
BASE_URL = "https://gift-saver-2.preview.emergentagent.com/api"

# Test results tracking
test_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def log_test(test_name, passed, message="", details=None):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"\n{status}: {test_name}")
    if message:
        print(f"  {message}")
    if details:
        print(f"  Details: {json.dumps(details, indent=2)}")
    
    if passed:
        test_results["passed"].append(test_name)
    else:
        test_results["failed"].append({"test": test_name, "message": message, "details": details})

def log_warning(message):
    """Log warning"""
    print(f"\n⚠️  WARNING: {message}")
    test_results["warnings"].append(message)

def print_summary():
    """Print test summary"""
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"✅ Passed: {len(test_results['passed'])}")
    print(f"❌ Failed: {len(test_results['failed'])}")
    print(f"⚠️  Warnings: {len(test_results['warnings'])}")
    
    if test_results['failed']:
        print("\nFailed Tests:")
        for fail in test_results['failed']:
            print(f"  - {fail['test']}: {fail['message']}")
    
    if test_results['warnings']:
        print("\nWarnings:")
        for warn in test_results['warnings']:
            print(f"  - {warn}")
    
    print("="*80)
    return len(test_results['failed']) == 0

# Test data
test_user_email = f"emma.rodriguez.{int(datetime.now().timestamp())}@gmail.com"
test_user_password = "SecurePassword123!"
test_user_data = {
    "email": test_user_email,
    "password": test_user_password,
    "name": "Emma Rodriguez",
    "age": 28,
    "gender": "female",
    "interested_in": "male",
    "orientation": "straight",
    "city": "New York",
    "country": "USA",
    "bio": "Love traveling and meeting new people",
    "birth_year": 1996,
    "birth_month": 5,
    "birth_day": 15,
    "lat": 40.7128,
    "lng": -74.0060
}

# Store auth token
auth_token = None

def test_health_check():
    """Test 1: Health check endpoint"""
    print("\n" + "="*80)
    print("TEST 1: Health Check")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("service") == "GiftsDates" and data.get("ok") is True:
                log_test("Health Check", True, "Backend is running and responding correctly", data)
                return True
            else:
                log_test("Health Check", False, f"Unexpected response format", data)
                return False
        else:
            log_test("Health Check", False, f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test("Health Check", False, f"Exception: {str(e)}")
        return False

def test_registration():
    """Test 2: User registration"""
    print("\n" + "="*80)
    print("TEST 2: User Registration")
    print("="*80)
    print(f"Registering user: {test_user_email}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=test_user_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for required fields
            if "token" in data and "user" in data:
                global auth_token
                auth_token = data["token"]
                user = data["user"]
                
                # Validate user data
                # Note: age is calculated from birth_date by backend, so we check it exists and is reasonable
                checks = [
                    ("email", user.get("email") == test_user_email.lower()),
                    ("name", user.get("name") == test_user_data["name"]),
                    ("age", user.get("age") is not None and 18 <= user.get("age") <= 100),
                    ("gender", user.get("gender") == test_user_data["gender"]),
                    ("city", user.get("city") == test_user_data["city"]),
                    ("country", user.get("country") == test_user_data["country"]),
                    ("user_id", "id" in user and len(user["id"]) > 0),
                    ("referral_code", "referral_code" in user)
                ]
                
                failed_checks = [name for name, result in checks if not result]
                
                if not failed_checks:
                    log_test("User Registration", True, 
                            f"User registered successfully with ID: {user.get('id')}", 
                            {"user_id": user.get("id"), "email": user.get("email")})
                    return True
                else:
                    log_test("User Registration", False, 
                            f"Missing or incorrect fields: {', '.join(failed_checks)}", 
                            user)
                    return False
            else:
                log_test("User Registration", False, "Missing token or user in response", data)
                return False
        elif response.status_code == 400 and "already registered" in response.text.lower():
            log_warning("Email already registered - this is expected if tests were run before")
            # Try to login instead
            return test_login_fallback()
        else:
            log_test("User Registration", False, 
                    f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test("User Registration", False, f"Exception: {str(e)}")
        return False

def test_login_fallback():
    """Fallback login if registration fails due to existing user"""
    print("\nAttempting login with existing credentials...")
    return test_login()

def test_login():
    """Test 3: User login"""
    print("\n" + "="*80)
    print("TEST 3: User Login")
    print("="*80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": test_user_email,
                "password": test_user_password
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if "token" in data and "user" in data:
                global auth_token
                auth_token = data["token"]
                user = data["user"]
                
                log_test("User Login", True, 
                        f"Login successful for user: {user.get('email')}", 
                        {"user_id": user.get("id"), "email": user.get("email")})
                return True
            else:
                log_test("User Login", False, "Missing token or user in response", data)
                return False
        elif response.status_code == 401:
            log_test("User Login", False, "Invalid credentials (401)", response.text)
            return False
        else:
            log_test("User Login", False, f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test("User Login", False, f"Exception: {str(e)}")
        return False

def test_authenticated_profile():
    """Test 4: Get current user profile (authenticated endpoint)"""
    print("\n" + "="*80)
    print("TEST 4: Authenticated Profile Endpoint")
    print("="*80)
    
    if not auth_token:
        log_test("Authenticated Profile", False, "No auth token available - previous tests failed")
        return False
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            user = response.json()
            
            # Validate user data
            required_fields = ["id", "email", "name", "age", "gender", "city", "country"]
            missing_fields = [field for field in required_fields if field not in user]
            
            if not missing_fields:
                log_test("Authenticated Profile", True, 
                        f"Profile retrieved successfully for: {user.get('email')}", 
                        {"user_id": user.get("id"), "name": user.get("name")})
                return True
            else:
                log_test("Authenticated Profile", False, 
                        f"Missing required fields: {', '.join(missing_fields)}", 
                        user)
                return False
        elif response.status_code == 401:
            log_test("Authenticated Profile", False, "Unauthorized (401) - token invalid or expired")
            return False
        else:
            log_test("Authenticated Profile", False, 
                    f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test("Authenticated Profile", False, f"Exception: {str(e)}")
        return False

def test_browse_profiles():
    """Test 5: Browse/list profiles endpoint"""
    print("\n" + "="*80)
    print("TEST 5: Browse Profiles Endpoint")
    print("="*80)
    
    if not auth_token:
        log_test("Browse Profiles", False, "No auth token available - previous tests failed")
        return False
    
    try:
        response = requests.get(
            f"{BASE_URL}/profiles",
            headers={"Authorization": f"Bearer {auth_token}"},
            params={"limit": 10},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # The endpoint returns a list of profiles directly, not wrapped in an object
            if isinstance(data, list):
                log_test("Browse Profiles", True, 
                        f"Profiles endpoint working - returned {len(data)} profiles", 
                        {"count": len(data)})
                return True
            else:
                log_test("Browse Profiles", False, 
                        "Response is not a list of profiles", 
                        {"type": type(data).__name__})
                return False
        elif response.status_code == 401:
            log_test("Browse Profiles", False, "Unauthorized (401) - token invalid")
            return False
        else:
            log_test("Browse Profiles", False, 
                    f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test("Browse Profiles", False, f"Exception: {str(e)}")
        return False

def test_meta_endpoint():
    """Test 6: Meta endpoint (app configuration)"""
    print("\n" + "="*80)
    print("TEST 6: Meta Endpoint (App Configuration)")
    print("="*80)
    
    if not auth_token:
        log_test("Meta Endpoint", False, "No auth token available - previous tests failed")
        return False
    
    try:
        response = requests.get(
            f"{BASE_URL}/meta",
            headers={"Authorization": f"Bearer {auth_token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for expected configuration fields
            expected_fields = ["gifts", "coin_packages", "premium", "video_rate"]
            missing_fields = [field for field in expected_fields if field not in data]
            
            if not missing_fields:
                log_test("Meta Endpoint", True, 
                        "Meta endpoint working - app configuration retrieved", 
                        {"coin_packages_count": len(data.get("coin_packages", []))})
                return True
            else:
                log_test("Meta Endpoint", False, 
                        f"Missing expected fields: {', '.join(missing_fields)}", 
                        data)
                return False
        else:
            log_test("Meta Endpoint", False, 
                    f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test("Meta Endpoint", False, f"Exception: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("GIFTSDATES BACKEND API TESTING")
    print("Testing restored app from GitHub")
    print("="*80)
    print(f"Backend URL: {BASE_URL}")
    print(f"Test started at: {datetime.now().isoformat()}")
    
    # Run tests in sequence
    tests = [
        ("Health Check", test_health_check),
        ("User Registration", test_registration),
        ("User Login", test_login),
        ("Authenticated Profile", test_authenticated_profile),
        ("Browse Profiles", test_browse_profiles),
        ("Meta Endpoint", test_meta_endpoint)
    ]
    
    # Execute tests
    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            log_test(test_name, False, f"Unexpected exception: {str(e)}")
    
    # Print summary
    success = print_summary()
    
    print(f"\nTest completed at: {datetime.now().isoformat()}")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
