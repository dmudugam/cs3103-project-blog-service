#!/usr/bin/env python3
"""
API Test Cases with curl Commands

All tests should run successfully, including those that 
require verification.

Usage:
- Run this file directly to execute all tests in sequence: python test_api.py
- Run specific test functions by modifying the main section
- Copy individual curl commands to run them manually

Author: Iresh Issarsing
Date: March 2025
"""

import os
import subprocess
import json
import time
import sys

# Base URL for the API
BASE_URL = "https://cs3103.cs.unb.ca:8006"

# Cookie file for maintaining session
COOKIE_JAR = "cookies.txt"

# Verified account credentials
TEST_USERNAME = "Test_User"
TEST_EMAIL = "cs3103blogservice@gmail.com"
TEST_PASSWORD = "P@ssword123"

# Test data for new content
TEST_BLOG_TITLE = "API Test Blog Title"
TEST_BLOG_CONTENT = "This is a test blog post created via the API testing suite. It should be automatically deleted at the end of the test."
TEST_UPDATED_BLOG_TITLE = "Updated API Test Blog"
TEST_UPDATED_BLOG_CONTENT = "This content has been updated through the API test suite. The update functionality is working correctly."

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_header(text):
    """Print a formatted header"""
    print(f"\n{BLUE}{'=' * 80}{RESET}")
    print(f"{BLUE}== {text}{RESET}")
    print(f"{BLUE}{'=' * 80}{RESET}")

def print_test(test_name):
    """Print test name"""
    print(f"\n{YELLOW}--- {test_name} ---{RESET}")

def run_curl(command, expected_status=None, capture_json=True, exit_on_error=False):
    """Run a curl command and return the result"""
    print(f"$ {command}")
    
    try:
        # Add verbose flag to show HTTP status code
        if "-v" not in command:
            command = command.replace("curl", "curl -v")
            
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        
        # Extract status code
        status_code = None
        for line in stderr.split('\n'):
            if "< HTTP/" in line:
                try:
                    status_code = int(line.split()[2])
                    break
                except (IndexError, ValueError):
                    pass
        
        # Check status code
        if expected_status and status_code != expected_status:
            print(f"{RED}Expected status {expected_status}, got {status_code}{RESET}")
            if exit_on_error:
                sys.exit(1)
        elif status_code:
            print(f"{GREEN}Status: {status_code}{RESET}")
        
        # Process response
        if stdout:
            if capture_json and (stdout.strip().startswith('{') or stdout.strip().startswith('[')):
                try:
                    json_data = json.loads(stdout)
                    print(f"Response: {json.dumps(json_data, indent=2)}")
                    return json_data
                except json.JSONDecodeError:
                    print(f"Response: {stdout}")
                    return stdout
            else:
                print(f"Response: {stdout}")
                return stdout
        else:
            print("No response body")
            return None
    except Exception as e:
        print(f"{RED}Error: {str(e)}{RESET}")
        if exit_on_error:
            sys.exit(1)
        return None

##########################################
# Authentication Test Cases
##########################################

def test_login_with_verified_account():
    print_test("Login with verified account")
    # Clean any existing cookie jar
    if os.path.exists(COOKIE_JAR):
        os.remove(COOKIE_JAR)
        
    command = f"""
    curl -X POST {BASE_URL}/auth/login \\
      -H "Content-Type: application/json" \\
      -c {COOKIE_JAR} \\
      -d '{{"username": "{TEST_USERNAME}", "password": "{TEST_PASSWORD}", "type": "local"}}' \\
      -k
    """
    return run_curl(command, expected_status=200, exit_on_error=True)

def test_check_auth():
    print_test("Check authentication status")
    command = f"""
    curl -X GET {BASE_URL}/auth/login \\
      -H "Accept: application/json" \\
      -b {COOKIE_JAR} \\
      -k
    """
    return run_curl(command, expected_status=200)

def test_login_failure():
    print_test("Login with invalid credentials")
    command = f"""
    curl -X POST {BASE_URL}/auth/login \\
      -H "Content-Type: application/json" \\
      -d '{{"username": "{TEST_USERNAME}", "password": "WrongPassword", "type": "local"}}' \\
      -k
    """
    response = run_curl(command, expected_status=401)
    # Verify the error message contains what we expect
    if isinstance(response, dict) and response.get('message') == "Invalid credentials":
        print(f"{GREEN}Authentication failure test passed{RESET}")
    return response

def test_forgot_password():
    print_test("Test password reset request")
    command = f"""
    curl -X POST {BASE_URL}/auth/forgot-password \\
      -H "Content-Type: application/json" \\
      -d '{{"email": "{TEST_EMAIL}"}}' \\
      -k
    """
    return run_curl(command, expected_status=200)

def test_logout():
    print_test("Logout user")
    command = f"""
    curl -X POST {BASE_URL}/auth/logout \\
      -H "Content-Type: application/json" \\
      -b {COOKIE_JAR} \\
      -k
    """
    response = run_curl(command, expected_status=200)
    
    # Test that we're actually logged out
    print_test("Verify logout - Check authentication status")
    logout_check_command = f"""
    curl -X GET {BASE_URL}/auth/login \\
      -H "Accept: application/json" \\
      -b {COOKIE_JAR} \\
      -k
    """
    logout_check = run_curl(logout_check_command, expected_status=401)
    if isinstance(logout_check, dict) and logout_check.get('status') == 'error':
        print(f"{GREEN}Logout successful - session terminated{RESET}")
    
    return response

##########################################
# Blog Test Cases
##########################################

def test_get_blogs():
    print_test("Get all blogs")
    # Try both main endpoints to find the correct one
    endpoints = [
        f"{BASE_URL}/blogs?limit=5&offset=0",
        f"{BASE_URL}/blogs-api?limit=5&offset=0"
    ]
    
    for endpoint in endpoints:
        print(f"Trying endpoint: {endpoint}")
        command = f"""
        curl -X GET "{endpoint}" \\
          -H "Accept: application/json" \\
          -b {COOKIE_JAR} \\
          -k
        """
        response = run_curl(command)
        
        # If we get a successful response that is a list or dict without error, use it
        if response is not None:
            if isinstance(response, list) or (isinstance(response, dict) and 'status' not in response):
                return response
            elif isinstance(response, dict) and response.get('status') != 'error':
                return response
                
    print(f"{YELLOW}Warning: Could not get blogs from any endpoint{RESET}")
    return None

def test_create_blog():
    print_test("Create a new blog")
    command = f"""
    curl -X POST {BASE_URL}/blogs/create \\
      -H "Content-Type: application/json" \\
      -b {COOKIE_JAR} \\
      -d '{{"title": "{TEST_BLOG_TITLE}", "content": "{TEST_BLOG_CONTENT}"}}' \\
      -k
    """
    response = run_curl(command, expected_status=201)
    
    # If we can't create a blog, the rest of the tests will fail
    if not response or not isinstance(response, dict) or 'blogId' not in response:
        print(f"{RED}Failed to create blog - skipping related tests{RESET}")
        return None
        
    print(f"{GREEN}Successfully created test blog with ID: {response['blogId']}{RESET}")
    return response

def test_create_blog_invalid():
    print_test("Create blog with invalid data (missing fields)")
    command = f"""
    curl -X POST {BASE_URL}/blogs/create \\
      -H "Content-Type: application/json" \\
      -b {COOKIE_JAR} \\
      -d '{{"title": "Missing Content Blog"}}' \\
      -k
    """
    response = run_curl(command, expected_status=400)
    # Verify we get the right error
    if isinstance(response, dict) and 'message' in response and 'content' in response['message'].lower():
        print(f"{GREEN}Invalid blog creation test passed{RESET}")
    return response

def test_get_blog_details(blog_id):
    print_test(f"Get blog details (ID: {blog_id})")
    # Try both possible endpoints
    endpoints = [
        f"{BASE_URL}/blogs/{blog_id}",
        f"{BASE_URL}/blogs-api/{blog_id}"
    ]
    
    for endpoint in endpoints:
        print(f"Trying endpoint: {endpoint}")
        command = f"""
        curl -X GET {endpoint} \\
          -H "Accept: application/json" \\
          -b {COOKIE_JAR} \\
          -k
        """
        response = run_curl(command)
        
        # If we get a successful response with the blog data, use it
        if response and isinstance(response, dict) and ('blogId' in response or 'title' in response):
            # Verify it has the title we expect
            if response.get('title') == TEST_BLOG_TITLE:
                print(f"{GREEN}Blog details match expected title{RESET}")
            return response
                
    print(f"{RED}Could not get blog details from any endpoint{RESET}")
    return None

def test_get_nonexistent_blog():
    print_test("Get non-existent blog details")
    nonexistent_id = 999999
    command = f"""
    curl -X GET {BASE_URL}/blogs/{nonexistent_id} \\
      -H "Accept: application/json" \\
      -b {COOKIE_JAR} \\
      -k
    """
    response = run_curl(command, expected_status=404)
    # Verify we get a not found error
    if isinstance(response, dict) and response.get('message') == 'Blog not found':
        print(f"{GREEN}Non-existent blog test passed{RESET}")
    return response

def test_update_blog(blog_id):
    print_test(f"Update blog (ID: {blog_id})")
    command = f"""
    curl -X PUT {BASE_URL}/blogs/{blog_id}/update \\
      -H "Content-Type: application/json" \\
      -b {COOKIE_JAR} \\
      -d '{{"title": "{TEST_UPDATED_BLOG_TITLE}", "content": "{TEST_UPDATED_BLOG_CONTENT}"}}' \\
      -k
    """
    response = run_curl(command, expected_status=200)
    
    # Verify the update worked by checking the title
    if response and isinstance(response, dict) and response.get('title') == TEST_UPDATED_BLOG_TITLE:
        print(f"{GREEN}Blog update successful - title matched{RESET}")
    return response

def test_update_blog_invalid(blog_id):
    print_test(f"Update blog with invalid data (ID: {blog_id})")
    command = f"""
    curl -X PUT {BASE_URL}/blogs/{blog_id}/update \\
      -H "Content-Type: application/json" \\
      -b {COOKIE_JAR} \\
      -d '{{"title": ""}}' \\
      -k
    """
    response = run_curl(command, expected_status=400)
    # Verify we get the right error
    if isinstance(response, dict) and 'message' in response:
        print(f"{GREEN}Invalid blog update test passed{RESET}")
    return response

def test_delete_blog(blog_id):
    print_test(f"Delete blog (ID: {blog_id})")
    command = f"""
    curl -X DELETE {BASE_URL}/blogs/{blog_id}/delete \\
      -H "Accept: application/json" \\
      -b {COOKIE_JAR} \\
      -k
    """
    response = run_curl(command, expected_status=204, capture_json=False)
    
    # Verify it's really deleted by trying to fetch it
    verification = test_get_blog_details(blog_id)
    if verification and isinstance(verification, dict) and verification.get('status') == 'error':
        print(f"{GREEN}Blog deletion confirmed - blog no longer accessible{RESET}")
        
    return response

def test_delete_nonexistent_blog():
    print_test("Delete non-existent blog")
    nonexistent_id = 999999
    command = f"""
    curl -X DELETE {BASE_URL}/blogs/{nonexistent_id}/delete \\
      -H "Accept: application/json" \\
      -b {COOKIE_JAR} \\
      -k
    """
    response = run_curl(command, expected_status=404)
    # Verify we get a not found error
    if isinstance(response, dict) and 'message' in response and 'not found' in response['message'].lower():
        print(f"{GREEN}Non-existent blog deletion test passed{RESET}")
    return response

##########################################
# Comment Test Cases
##########################################

def test_create_comment(blog_id):
    print_test(f"Create comment on blog (ID: {blog_id})")
    command = f"""
    curl -X POST {BASE_URL}/blogs/{blog_id}/comments/create \\
      -H "Content-Type: application/json" \\
      -b {COOKIE_JAR} \\
      -d '{{"content": "This is a test comment created by the API test suite."}}' \\
      -k
    """
    response = run_curl(command, expected_status=201)
    
    # Check if comment creation worked
    if response and isinstance(response, dict) and 'commentId' in response:
        print(f"{GREEN}Comment created successfully with ID: {response['commentId']}{RESET}")
    return response

def test_create_comment_invalid(blog_id):
    print_test(f"Create invalid comment on blog (ID: {blog_id})")
    command = f"""
    curl -X POST {BASE_URL}/blogs/{blog_id}/comments/create \\
      -H "Content-Type: application/json" \\
      -b {COOKIE_JAR} \\
      -d '{{"content": ""}}' \\
      -k
    """
    response = run_curl(command, expected_status=400)
    # Verify we get the right error about content being required
    if isinstance(response, dict) and 'message' in response and 'content' in response['message'].lower():
        print(f"{GREEN}Invalid comment creation test passed{RESET}")
    return response

def test_get_comments(blog_id):
    print_test(f"Get comments for blog (ID: {blog_id})")
    # Try both possible endpoints
    endpoints = [
        f"{BASE_URL}/blogs/{blog_id}/comments",
        f"{BASE_URL}/blogs-api/{blog_id}/comments"
    ]
    
    for endpoint in endpoints:
        print(f"Trying endpoint: {endpoint}")
        command = f"""
        curl -X GET {endpoint} \\
          -H "Accept: application/json" \\
          -b {COOKIE_JAR} \\
          -k
        """
        response = run_curl(command)
        
        # If we get an array or a dict without error status, use it
        if response is not None:
            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and response.get('status') != 'error':
                return response
                
    print(f"{YELLOW}Warning: Could not get comments from any endpoint{RESET}")
    return None

def test_get_comment_details(comment_id):
    print_test(f"Get comment details (ID: {comment_id})")
    command = f"""
    curl -X GET {BASE_URL}/comments/{comment_id} \\
      -H "Accept: application/json" \\
      -b {COOKIE_JAR} \\
      -k
    """
    response = run_curl(command, expected_status=200)
    
    # Verify the comment ID matches
    if response and isinstance(response, dict) and response.get('commentId') == comment_id:
        print(f"{GREEN}Comment details retrieved successfully{RESET}")
    return response

def test_reply_to_comment(comment_id):
    print_test(f"Reply to comment (ID: {comment_id})")
    command = f"""
    curl -X POST {BASE_URL}/comments/{comment_id}/replies/create \\
      -H "Content-Type: application/json" \\
      -b {COOKIE_JAR} \\
      -d '{{"content": "This is a test reply to a comment via the API test suite."}}' \\
      -k
    """
    response = run_curl(command, expected_status=201)
    
    # Verify reply creation worked
    if response and isinstance(response, dict) and 'commentId' in response:
        print(f"{GREEN}Reply created successfully with ID: {response['commentId']}{RESET}")
        # Also verify it has the correct parent
        if response.get('parentCommentId') == comment_id:
            print(f"{GREEN}Reply has correct parent comment ID{RESET}")
    return response

def test_get_comment_replies(comment_id):
    print_test(f"Get replies to comment (ID: {comment_id})")
    command = f"""
    curl -X GET {BASE_URL}/comments/{comment_id}/replies \\
      -H "Accept: application/json" \\
      -b {COOKIE_JAR} \\
      -k
    """
    response = run_curl(command, expected_status=200)
    
    # Verify replies are returned
    if response is not None:
        if isinstance(response, list) and len(response) > 0:
            print(f"{GREEN}Retrieved {len(response)} replies{RESET}")
        elif isinstance(response, dict) and not response.get('status') == 'error':
            print(f"{GREEN}Retrieved replies successfully{RESET}")
    return response

def test_delete_comment(comment_id):
    print_test(f"Delete comment (ID: {comment_id})")
    command = f"""
    curl -X DELETE {BASE_URL}/comments/{comment_id}/delete \\
      -H "Accept: application/json" \\
      -b {COOKIE_JAR} \\
      -k
    """
    response = run_curl(command, expected_status=204, capture_json=False)
    
    # Verify comment is deleted by trying to fetch it
    verification_command = f"""
    curl -X GET {BASE_URL}/comments/{comment_id} \\
      -H "Accept: application/json" \\
      -b {COOKIE_JAR} \\
      -k
    """
    verification = run_curl(verification_command)
    if verification and isinstance(verification, dict) and verification.get('status') == 'error':
        print(f"{GREEN}Comment deletion confirmed{RESET}")
        
    return response

##########################################
# User Test Cases
##########################################

def test_get_user_blogs():
    print_test("Get user's blogs")
    # Get user ID from session
    auth_data = test_check_auth()
    if not auth_data or 'userId' not in auth_data:
        print(f"{RED}Failed to get user ID{RESET}")
        return None
    
    user_id = auth_data['userId']
    
    # Try both possible endpoints
    endpoints = [
        f"{BASE_URL}/users/{user_id}/blogs",
        f"{BASE_URL}/users-api/{user_id}/blogs"
    ]
    
    for endpoint in endpoints:
        print(f"Trying endpoint: {endpoint}")
        command = f"""
        curl -X GET {endpoint} \\
          -H "Accept: application/json" \\
          -b {COOKIE_JAR} \\
          -k
        """
        response = run_curl(command)
        
        # If we get an array or a dict without error status, use it
        if response is not None:
            if isinstance(response, list):
                print(f"{GREEN}Retrieved {len(response)} user blogs{RESET}")
                return response
            elif isinstance(response, dict) and response.get('status') != 'error':
                return response
                
    print(f"{YELLOW}Warning: Could not get user blogs from any endpoint{RESET}")
    return None

def test_update_email():
    print_test("Update user email")
    # We don't want to actually change the verified email, so we'll 
    # just update it to the same value
    command = f"""
    curl -X PUT {BASE_URL}/users/email \\
      -H "Content-Type: application/json" \\
      -b {COOKIE_JAR} \\
      -d '{{"email": "{TEST_EMAIL}"}}' \\
      -k
    """
    response = run_curl(command, expected_status=200)
    
    # If the response contains our email, the test passed
    if response and isinstance(response, dict) and response.get('email') == TEST_EMAIL:
        print(f"{GREEN}Email update (to same value) successful{RESET}")
    return response

def test_update_email_invalid():
    print_test("Update with invalid email")
    command = f"""
    curl -X PUT {BASE_URL}/users/email \\
      -H "Content-Type: application/json" \\
      -b {COOKIE_JAR} \\
      -d '{{"email": "not-an-email"}}' \\
      -k
    """
    response = run_curl(command, expected_status=400)
    # Verify we get the right error
    if isinstance(response, dict) and 'message' in response and 'invalid email' in response['message'].lower():
        print(f"{GREEN}Invalid email update test passed{RESET}")
    return response

def test_update_phone():
    print_test("Update user phone number")
    # Use some test phone number
    test_phone = "+16473959303"
    command = f"""
    curl -X PUT {BASE_URL}/users/phone \\
      -H "Content-Type: application/json" \\
      -b {COOKIE_JAR} \\
      -d '{{"phone": "{test_phone}"}}' \\
      -k
    """
    response = run_curl(command)
    
    # Check if the phone was updated
    if response and isinstance(response, dict) and response.get('phone_number') == test_phone:
        print(f"{GREEN}Phone number update successful{RESET}")
    return response

def test_update_phone_invalid():
    print_test("Update with invalid phone number")
    command = f"""
    curl -X PUT {BASE_URL}/users/phone \\
      -H "Content-Type: application/json" \\
      -b {COOKIE_JAR} \\
      -d '{{"phone": "not-a-phone"}}' \\
      -k
    """
    response = run_curl(command, expected_status=400)
    # Verify we get the right error
    if isinstance(response, dict) and 'message' in response and 'phone number' in response['message'].lower():
        print(f"{GREEN}Invalid phone update test passed{RESET}")
    return response

def test_get_notification_preferences():
    print_test("Get notification preferences")
    command = f"""
    curl -X GET {BASE_URL}/users/notification-preferences \\
      -H "Accept: application/json" \\
      -b {COOKIE_JAR} \\
      -k
    """
    response = run_curl(command, expected_status=200)
    
    # Check if we got the preferences
    if response and isinstance(response, dict) and 'userId' in response:
        print(f"{GREEN}Notification preferences retrieved successfully{RESET}")
    return response

def test_update_notification_preferences():
    print_test("Update notification preferences")
    # Get current prefs first 
    current_prefs = test_get_notification_preferences()
    if not current_prefs or not isinstance(current_prefs, dict):
        print(f"{RED}Failed to get current notification preferences{RESET}")
        return None
    
    # Use the opposite values of current settings
    notify_on_blog = not bool(current_prefs.get('notifyOnBlog', True))
    notify_on_comment = not bool(current_prefs.get('notifyOnComment', True))
    
    command = f"""
    curl -X PUT {BASE_URL}/users/notification-preferences \\
      -H "Content-Type: application/json" \\
      -b {COOKIE_JAR} \\
      -d '{{"notifyOnBlog": {str(notify_on_blog).lower()}, "notifyOnComment": {str(notify_on_comment).lower()}}}' \\
      -k
    """
    response = run_curl(command, expected_status=200)
    
    # Check if prefs were updated
    if response and isinstance(response, dict):
        updated_blog = bool(response.get('notifyOnBlog', False))
        updated_comment = bool(response.get('notifyOnComment', False))
        
        if updated_blog == notify_on_blog and updated_comment == notify_on_comment:
            print(f"{GREEN}Notification preferences updated successfully{RESET}")
            
    # Restore original values
    restore_command = f"""
    curl -X PUT {BASE_URL}/users/notification-preferences \\
      -H "Content-Type: application/json" \\
      -b {COOKIE_JAR} \\
      -d '{{"notifyOnBlog": {str(bool(current_prefs.get("notifyOnBlog", True))).lower()}, "notifyOnComment": {str(bool(current_prefs.get("notifyOnComment", True))).lower()}}}' \\
      -k
    """
    run_curl(restore_command)
    print(f"{GREEN}Restored original notification preferences{RESET}")
    
    return response

##########################################
# Verification Test Cases
##########################################

def test_request_email_otp():
    print_test("Request email verification OTP")
    
    # Get user ID from session first
    auth_data = test_check_auth()
    if not auth_data or 'userId' not in auth_data:
        print(f"{RED}Failed to get user ID{RESET}")
        return None
    
    user_id = auth_data['userId']
    
    # Add updatingEmail flag to force OTP generation
    command = f"""
    curl -X POST {BASE_URL}/auth/request-otp \\
      -H "Content-Type: application/json" \\
      -b {COOKIE_JAR} \\
      -d '{{"userId": {user_id}, "updatingEmail": true}}' \\
      -k
    """
    response = run_curl(command)
    
    # Handle different response formats
    if response and isinstance(response, dict):
        if 'status' in response and response['status'] == 'success':
            print(f"{GREEN}OTP request successful{RESET}")
        elif 'message' in response:
            # Handle both string and dict message formats
            if isinstance(response['message'], str):
                if 'already verified' in response['message'].lower():
                    print(f"{GREEN}Account is already verified (expected){RESET}")
                else:
                    print(f"{YELLOW}Message: {response['message']}{RESET}")
            else:
                print(f"{YELLOW}Validation errors: {response['message']}{RESET}")
    return response

def test_request_mobile_otp():
    print_test("Request mobile verification OTP")
    
    # Get user ID from session first
    auth_data = test_check_auth()
    if not auth_data or 'userId' not in auth_data:
        print(f"{RED}Failed to get user ID{RESET}")
        return None
    
    # Add updatingPhone flag to force OTP generation
    command = f"""
    curl -X POST {BASE_URL}/auth/request-mobile-otp \\
      -H "Content-Type: application/json" \\
      -b {COOKIE_JAR} \\
      -d '{{"updatingPhone": true}}' \\
      -k
    """
    response = run_curl(command)
    
    # Handle different response formats
    if response and isinstance(response, dict):
        if 'status' in response and response['status'] == 'success':
            print(f"{GREEN}Mobile OTP request successful{RESET}")
        elif 'message' in response:
            if isinstance(response['message'], str):
                print(f"{YELLOW}Message: {response['message']}{RESET}")
            else:
                print(f"{YELLOW}Validation errors: {response['message']}{RESET}")
    
    return response

##########################################
# AI Test Cases
##########################################

def test_generate_ai_content():
    print_test("Generate content with AI")
    command = f"""
    curl -X POST {BASE_URL}/ai/generate \\
      -H "Content-Type: application/json" \\
      -b {COOKIE_JAR} \\
      -d '{{"prompt": "Write a short paragraph about technology", "mode": "generate"}}' \\
      -k
    """
    response = run_curl(command)
    
    # Check if we got generated content
    if response and isinstance(response, dict) and 'generatedContent' in response:
        print(f"{GREEN}AI content generation successful{RESET}")
        content_snippet = response['generatedContent'][:50] + "..." if len(response['generatedContent']) > 50 else response['generatedContent']
        print(f"{BLUE}Generated content starts with: {content_snippet}{RESET}")
    return response

def test_enhance_ai_content():
    print_test("Enhance content with AI")
    command = f"""
    curl -X POST {BASE_URL}/ai/generate \\
      -H "Content-Type: application/json" \\
      -b {COOKIE_JAR} \\
      -d '{{"prompt": "Make this more engaging", "mode": "enhance", "content": "Technology is important in our lives."}}' \\
      -k
    """
    response = run_curl(command)
    
    # Check if we got enhanced content
    if response and isinstance(response, dict) and 'generatedContent' in response:
        print(f"{GREEN}AI content enhancement successful{RESET}")
        content_snippet = response['generatedContent'][:50] + "..." if len(response['generatedContent']) > 50 else response['generatedContent']
        print(f"{BLUE}Enhanced content starts with: {content_snippet}{RESET}")
    return response

##########################################
# Run All Tests
##########################################

def run_all_tests():
    """Run all API tests in sequence"""
    # Create a new test results directory
    os.makedirs("test_results", exist_ok=True)
    
    print_header("BLOG SERVICE API TEST SUITE")
    print(f"Testing with verified account: {TEST_USERNAME}")
    
    try:
        # Authentication Tests
        print_header("AUTHENTICATION TESTS")
        test_login_with_verified_account()
        test_check_auth()
        test_login_failure()
        
        # User Tests
        print_header("USER TESTS")
        test_get_user_blogs()
        test_update_email()
        test_update_email_invalid()
        test_update_phone()
        test_update_phone_invalid()
        test_get_notification_preferences()
        test_update_notification_preferences()
        
        # Blog Tests
        print_header("BLOG TESTS")
        test_get_blogs()
        test_create_blog_invalid()
        blog_data = test_create_blog()
        
        # Extract blog ID
        blog_id = None
        if blog_data and isinstance(blog_data, dict) and 'blogId' in blog_data:
            blog_id = blog_data['blogId']
            print(f"Created test blog with ID: {blog_id}")
            
            test_get_blog_details(blog_id)
            test_get_nonexistent_blog()
            test_update_blog_invalid(blog_id)
            test_update_blog(blog_id)
            
            # Comment Tests
            print_header("COMMENT TESTS")
            test_create_comment_invalid(blog_id)
            comment_data = test_create_comment(blog_id)
            
            # Extract comment ID
            comment_id = None
            if comment_data and isinstance(comment_data, dict) and 'commentId' in comment_data:
                comment_id = comment_data['commentId']
                print(f"Created test comment with ID: {comment_id}")
                
                test_get_comments(blog_id)
                test_get_comment_details(comment_id)
                
                reply_data = test_reply_to_comment(comment_id)
                reply_id = None
                if reply_data and isinstance(reply_data, dict) and 'commentId' in reply_data:
                    reply_id = reply_data['commentId']
                    print(f"Created test reply with ID: {reply_id}")
                    
                    test_get_comment_replies(comment_id)
                    
                    # Delete the reply
                    test_delete_comment(reply_id)
                
                # Delete the comment
                test_delete_comment(comment_id)
            
            # Delete the blog
            test_delete_blog(blog_id)
            test_delete_nonexistent_blog()
        else:
            print(f"{RED}Failed to create test blog - skipping blog/comment tests{RESET}")
        
        # AI Tests
        print_header("AI TESTS")
        test_generate_ai_content()
        test_enhance_ai_content()
        
        # Verification Tests
        print_header("VERIFICATION TESTS")
        test_request_email_otp()
        test_request_mobile_otp()
        test_forgot_password()
        
        # Logout
        print_header("LOGOUT TEST")
        test_logout()
        
    except KeyboardInterrupt:
        print(f"{YELLOW}Test suite interrupted by user{RESET}")
    except Exception as e:
        print(f"{RED}Test suite error: {str(e)}{RESET}")
    finally:
        # Clean up cookie jar
        if os.path.exists(COOKIE_JAR):
            os.remove(COOKIE_JAR)
        
        print_header("API TESTS COMPLETED")

if __name__ == "__main__":
    run_all_tests()