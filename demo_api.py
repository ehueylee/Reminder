"""
REST API POC Demo
Tests all API endpoints with various scenarios
"""

import sys
import os

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import requests
import json
from datetime import datetime
from time import sleep

# Configuration
BASE_URL = "http://localhost:8001"
USER_ID = "demo_user_123"

# ANSI colors for output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(title):
    """Print section header."""
    print(f"\n{BOLD}{'='*80}")
    print(f"{title}")
    print(f"{'='*80}{RESET}\n")


def print_test(name, status, details=""):
    """Print test result."""
    symbol = f"{GREEN}✅{RESET}" if status else f"{RED}❌{RESET}"
    print(f"{symbol} {name}")
    if details:
        print(f"   {details}")


def print_json(data, indent=2):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=indent, default=str))


def check_api_running():
    """Check if API server is running."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def test_health_check():
    """Test health check endpoint."""
    print_header("📋 Test 1: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        
        if response.status_code == 200:
            data = response.json()
            print_test("GET /health", True, f"Status: {data['status']}")
            print(f"   Database: {data['database']}")
            print(f"   OpenAI: {data['openai']}")
            print(f"   Version: {data['version']}")
            return True
        else:
            print_test("GET /health", False, f"Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print_test("GET /health", False, str(e))
        return False


def test_parse_only():
    """Test parse-only endpoint (no database save)."""
    print_header("📋 Test 2: Parse Natural Language (No Save)")
    
    test_cases = [
        "Call mom tomorrow at 3pm",
        "Team meeting every Monday at 9am",
        "URGENT: Submit report by Friday 5pm"
    ]
    
    results = []
    
    for nl_input in test_cases:
        print(f"\n{BLUE}Input:{RESET} '{nl_input}'")
        
        try:
            response = requests.post(
                f"{BASE_URL}/reminders/parse",
                json={
                    "natural_input": nl_input,
                    "user_timezone": "America/New_York"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                parsed = data['parsed']
                confidence = data['confidence']
                
                print_test("POST /reminders/parse", True)
                print(f"   Title: {parsed['title']}")
                print(f"   Due: {parsed['due_date_time']}")
                print(f"   Priority: {parsed['priority']}")
                print(f"   Recurring: {parsed['is_recurring']}")
                print(f"   Confidence: {confidence*100:.1f}%")
                print(f"   Valid: {data['validation']['is_valid']}")
                results.append(True)
            else:
                print_test("POST /reminders/parse", False, f"Status: {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print_test("POST /reminders/parse", False, str(e))
            results.append(False)
    
    return all(results)


def test_create_reminders():
    """Test creating reminders."""
    print_header("📋 Test 3: Create Reminders")
    
    test_cases = [
        {
            "name": "Simple reminder",
            "input": "Buy groceries tomorrow at 5pm"
        },
        {
            "name": "Recurring reminder",
            "input": "Gym workout every Tuesday and Thursday at 6am"
        },
        {
            "name": "Urgent reminder",
            "input": "URGENT: Submit proposal by end of day Friday"
        },
        {
            "name": "Location reminder",
            "input": "Doctor appointment next Wednesday at 2pm at City Hospital"
        }
    ]
    
    created_ids = []
    
    for test in test_cases:
        print(f"\n{BLUE}{test['name']}:{RESET} '{test['input']}'")
        
        try:
            response = requests.post(
                f"{BASE_URL}/reminders",
                json={
                    "natural_input": test['input'],
                    "user_id": USER_ID,
                    "user_timezone": "America/New_York"
                }
            )
            
            if response.status_code == 201:
                data = response.json()
                reminder = data['reminder']
                parsing = data['parsing_details']
                
                print_test("POST /reminders", True)
                print(f"   ID: {reminder['id']}")
                print(f"   Title: {reminder['title']}")
                print(f"   Due: {reminder['due_date_time']}")
                print(f"   Priority: {reminder['priority']}")
                print(f"   Status: {reminder['status']}")
                print(f"   Confidence: {parsing['confidence']*100:.1f}%")
                
                created_ids.append(reminder['id'])
            else:
                print_test("POST /reminders", False, f"Status: {response.status_code}")
                print(f"   {response.text}")
                
        except Exception as e:
            print_test("POST /reminders", False, str(e))
    
    return created_ids


def test_get_reminders(user_id):
    """Test getting list of reminders."""
    print_header("📋 Test 4: Get All Reminders")
    
    try:
        response = requests.get(
            f"{BASE_URL}/reminders",
            params={"user_id": user_id}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_test("GET /reminders", True)
            print(f"   Total reminders: {data['total']}")
            print(f"   Page: {data['page']}")
            print(f"   Page size: {data['page_size']}")
            
            if data['reminders']:
                print(f"\n   {BOLD}Reminders:{RESET}")
                for r in data['reminders'][:5]:  # Show first 5
                    print(f"   - {r['title']} (Due: {r['due_date_time']}, Priority: {r['priority']})")
            
            return True
        else:
            print_test("GET /reminders", False, f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_test("GET /reminders", False, str(e))
        return False


def test_get_single_reminder(reminder_id):
    """Test getting a single reminder."""
    print_header("📋 Test 5: Get Single Reminder")
    
    try:
        response = requests.get(f"{BASE_URL}/reminders/{reminder_id}")
        
        if response.status_code == 200:
            data = response.json()
            print_test("GET /reminders/{id}", True)
            print(f"   ID: {data['id']}")
            print(f"   Title: {data['title']}")
            print(f"   User ID: {data['user_id']}")
            print(f"   Due: {data['due_date_time']}")
            print(f"   Priority: {data['priority']}")
            print(f"   Status: {data['status']}")
            print(f"   Tags: {', '.join(data['tags']) if data['tags'] else 'None'}")
            print(f"   Parsed by AI: {data['parsed_by_ai']}")
            if data['ai_confidence']:
                print(f"   AI Confidence: {data['ai_confidence']*100:.1f}%")
            return True
        else:
            print_test("GET /reminders/{id}", False, f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_test("GET /reminders/{id}", False, str(e))
        return False


def test_update_reminder(reminder_id):
    """Test updating a reminder."""
    print_header("📋 Test 6: Update Reminder")
    
    try:
        # Update priority and add tags
        response = requests.put(
            f"{BASE_URL}/reminders/{reminder_id}",
            json={
                "priority": "high",
                "tags": ["important", "personal", "health"]
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print_test("PUT /reminders/{id}", True)
            print(f"   Updated priority: {data['priority']}")
            print(f"   Updated tags: {', '.join(data['tags'])}")
            return True
        else:
            print_test("PUT /reminders/{id}", False, f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_test("PUT /reminders/{id}", False, str(e))
        return False


def test_complete_reminder(reminder_id):
    """Test completing a reminder."""
    print_header("📋 Test 7: Complete Reminder")
    
    try:
        response = requests.post(f"{BASE_URL}/reminders/{reminder_id}/complete")
        
        if response.status_code == 200:
            data = response.json()
            print_test("POST /reminders/{id}/complete", True)
            print(f"   Status: {data['status']}")
            print(f"   Completed at: {data['completed_at']}")
            return True
        else:
            print_test("POST /reminders/{id}/complete", False, f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_test("POST /reminders/{id}/complete", False, str(e))
        return False


def test_filter_reminders(user_id):
    """Test filtering reminders."""
    print_header("📋 Test 8: Filter Reminders")
    
    tests = [
        ("By status=pending", {"user_id": user_id, "status": "pending"}),
        ("By priority=high", {"user_id": user_id, "priority": "high"}),
        ("By tag=personal", {"user_id": user_id, "tag": "personal"}),
    ]
    
    results = []
    
    for name, params in tests:
        try:
            response = requests.get(f"{BASE_URL}/reminders", params=params)
            
            if response.status_code == 200:
                data = response.json()
                print_test(f"GET /reminders ({name})", True, f"Found {data['total']} reminders")
                results.append(True)
            else:
                print_test(f"GET /reminders ({name})", False, f"Status: {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print_test(f"GET /reminders ({name})", False, str(e))
            results.append(False)
    
    return all(results)


def test_delete_reminder(reminder_id):
    """Test deleting a reminder."""
    print_header("📋 Test 9: Delete Reminder")
    
    try:
        response = requests.delete(f"{BASE_URL}/reminders/{reminder_id}")
        
        if response.status_code == 200:
            data = response.json()
            print_test("DELETE /reminders/{id}", True, data['message'])
            
            # Verify deletion
            verify = requests.get(f"{BASE_URL}/reminders/{reminder_id}")
            if verify.status_code == 404:
                print_test("Verify deletion", True, "Reminder no longer exists")
                return True
            else:
                print_test("Verify deletion", False, "Reminder still exists!")
                return False
        else:
            print_test("DELETE /reminders/{id}", False, f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_test("DELETE /reminders/{id}", False, str(e))
        return False


def test_error_handling():
    """Test error handling."""
    print_header("📋 Test 10: Error Handling")
    
    tests = [
        {
            "name": "Get non-existent reminder",
            "method": "GET",
            "url": f"{BASE_URL}/reminders/00000000-0000-0000-0000-000000000000",
            "expected_status": 404
        },
        {
            "name": "Update non-existent reminder",
            "method": "PUT",
            "url": f"{BASE_URL}/reminders/00000000-0000-0000-0000-000000000000",
            "json": {"title": "Test"},
            "expected_status": 404
        },
        {
            "name": "Delete non-existent reminder",
            "method": "DELETE",
            "url": f"{BASE_URL}/reminders/00000000-0000-0000-0000-000000000000",
            "expected_status": 404
        }
    ]
    
    results = []
    
    for test in tests:
        try:
            if test['method'] == 'GET':
                response = requests.get(test['url'])
            elif test['method'] == 'PUT':
                response = requests.put(test['url'], json=test.get('json', {}))
            elif test['method'] == 'DELETE':
                response = requests.delete(test['url'])
            
            success = response.status_code == test['expected_status']
            print_test(test['name'], success, f"Status: {response.status_code} (expected {test['expected_status']})")
            results.append(success)
            
        except Exception as e:
            print_test(test['name'], False, str(e))
            results.append(False)
    
    return all(results)


def main():
    """Run all API tests."""
    print_header(f"{BOLD}REMINDER API - POC DEMO{RESET}")
    
    # Check if API is running
    print("Checking if API server is running...")
    if not check_api_running():
        print(f"\n{RED}❌ ERROR: API server is not running!{RESET}")
        print(f"\nPlease start the server first:")
        print(f"  {YELLOW}python main.py{RESET}")
        print(f"  or")
        print(f"  {YELLOW}uvicorn main:app --reload{RESET}")
        return
    
    print(f"{GREEN}✅ API server is running{RESET}\n")
    sleep(0.5)
    
    # Run tests
    results = []
    
    # Test 1: Health check
    results.append(test_health_check())
    sleep(0.5)
    
    # Test 2: Parse only
    results.append(test_parse_only())
    sleep(0.5)
    
    # Test 3: Create reminders
    created_ids = test_create_reminders()
    results.append(len(created_ids) > 0)
    sleep(0.5)
    
    if created_ids:
        # Test 4: Get all reminders
        results.append(test_get_reminders(USER_ID))
        sleep(0.5)
        
        # Test 5: Get single reminder
        results.append(test_get_single_reminder(created_ids[0]))
        sleep(0.5)
        
        # Test 6: Update reminder
        results.append(test_update_reminder(created_ids[0]))
        sleep(0.5)
        
        # Test 7: Complete reminder
        if len(created_ids) > 1:
            results.append(test_complete_reminder(created_ids[1]))
            sleep(0.5)
        
        # Test 8: Filter reminders
        results.append(test_filter_reminders(USER_ID))
        sleep(0.5)
        
        # Test 9: Delete reminder
        if len(created_ids) > 2:
            results.append(test_delete_reminder(created_ids[2]))
            sleep(0.5)
    
    # Test 10: Error handling
    results.append(test_error_handling())
    
    # Summary
    print_header(f"{BOLD}📊 DEMO SUMMARY{RESET}")
    
    total = len([r for r in results if r is not None])
    passed = len([r for r in results if r])
    failed = total - passed
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"Total Tests: {total}")
    print(f"{GREEN}Passed: {passed}{RESET}")
    if failed > 0:
        print(f"{RED}Failed: {failed}{RESET}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print(f"\n{GREEN}{BOLD}🎉 ALL TESTS PASSED!{RESET}")
    elif success_rate >= 80:
        print(f"\n{YELLOW}{BOLD}⚠️  MOST TESTS PASSED{RESET}")
    else:
        print(f"\n{RED}{BOLD}❌ MANY TESTS FAILED{RESET}")
    
    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}🎉 API POC DEMO COMPLETE!{RESET}")
    print(f"{BOLD}{'='*80}{RESET}\n")
    
    print(f"💡 Try the interactive API docs:")
    print(f"   📚 Swagger UI: {BLUE}http://localhost:8000/docs{RESET}")
    print(f"   📖 ReDoc: {BLUE}http://localhost:8000/redoc{RESET}")
    print()


if __name__ == "__main__":
    main()
