"""
POC Demo for OpenAI Integration (Sub-Phase 1.2)
Demonstrates natural language parsing capabilities.
"""

from openai_service import parse_reminder, parse_reminder_batch, validate_parsed_reminder
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


def demo():
    """Demonstrate OpenAI natural language parsing capabilities."""
    
    print("=" * 80)
    print("OPENAI INTEGRATION - POC DEMO")
    print("Natural Language Reminder Parsing")
    print("=" * 80)
    print()
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "sk-your-key-here":
        print("❌ ERROR: OpenAI API key not configured!")
        print()
        print("Please set your OpenAI API key in the .env file:")
        print("OPENAI_API_KEY=sk-your-actual-key-here")
        print()
        print("Get your API key from: https://platform.openai.com/api-keys")
        return
    
    print(f"✅ OpenAI API key configured: {api_key[:8]}...{api_key[-4:]}")
    print()
    
    # Test cases
    test_cases = [
        {
            "category": "Simple Time-Based Reminders",
            "inputs": [
                "Remind me to call mom tomorrow at 3pm",
                "Buy milk today at 6pm",
                "Meeting with John next Monday at 10am"
            ]
        },
        {
            "category": "Recurring Reminders",
            "inputs": [
                "Team standup every Monday at 9am",
                "Weekly team lunch every Thursday at noon",
                "Daily exercise at 7am"
            ]
        },
        {
            "category": "Priority Detection",
            "inputs": [
                "URGENT: Submit quarterly report by Friday 5pm",
                "Important: Call dentist this week",
                "Review proposal when you get a chance"
            ]
        },
        {
            "category": "Complex Context",
            "inputs": [
                "Doctor appointment next Tuesday afternoon at General Hospital",
                "Pick up prescription from CVS on Main Street tomorrow",
                "Team meeting every other Monday at 2pm for the next month"
            ]
        },
        {
            "category": "Relative Time Expressions",
            "inputs": [
                "Remind me in 2 hours to check the oven",
                "Call back the client next week",
                "Submit timesheet by end of day Friday"
            ]
        }
    ]
    
    # Run tests for each category
    total_tests = 0
    successful_tests = 0
    
    for test_group in test_cases:
        print("-" * 80)
        print(f"📋 {test_group['category']}")
        print("-" * 80)
        print()
        
        for input_text in test_group['inputs']:
            total_tests += 1
            print(f"Input: \"{input_text}\"")
            
            try:
                # Parse the reminder
                result = parse_reminder(input_text, user_timezone="America/New_York")
                parsed = result['parsed']
                
                # Validate the result
                is_valid, error = validate_parsed_reminder(parsed)
                
                if is_valid:
                    successful_tests += 1
                    print(f"  ✅ Status: Successfully parsed")
                    print(f"  📝 Title: {parsed['title']}")
                    print(f"  📅 Due: {parsed['due_date_time']}")
                    print(f"  🌍 Timezone: {parsed['timezone']}")
                    print(f"  🎯 Priority: {parsed['priority']}")
                    
                    if parsed.get('description'):
                        print(f"  📄 Description: {parsed['description']}")
                    
                    if parsed.get('is_recurring'):
                        pattern = parsed['recurrence_pattern']
                        print(f"  🔁 Recurring: {pattern['frequency']} (interval: {pattern['interval']})")
                        if pattern.get('days_of_week'):
                            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                            selected_days = [days[d] for d in pattern['days_of_week']]
                            print(f"     Days: {', '.join(selected_days)}")
                    else:
                        print(f"  🔁 Recurring: No")
                    
                    if parsed.get('tags'):
                        print(f"  🏷️  Tags: {', '.join(parsed['tags'])}")
                    
                    if parsed.get('location'):
                        print(f"  📍 Location: {parsed['location']}")
                    
                    print(f"  💯 Confidence: {result['confidence']:.1%}")
                    print(f"  🤖 Model: {result['model_used']}")
                else:
                    print(f"  ⚠️  Validation failed: {error}")
                
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
            
            print()
        
        print()
    
    # Summary
    print("=" * 80)
    print("DEMO SUMMARY")
    print("=" * 80)
    print()
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Success Rate: {(successful_tests/total_tests*100):.1f}%")
    print()
    
    if successful_tests == total_tests:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"⚠️  {total_tests - successful_tests} test(s) failed")
    
    print()
    
    # Batch parsing demo
    print("-" * 80)
    print("📦 BATCH PARSING DEMO")
    print("-" * 80)
    print()
    
    batch_inputs = [
        "Water plants tomorrow morning",
        "Pay bills by Friday",
        "Call Sarah next week"
    ]
    
    print("Parsing multiple reminders at once...")
    print()
    
    batch_results = parse_reminder_batch(batch_inputs, user_timezone="America/New_York")
    
    for i, result in enumerate(batch_results, 1):
        if result.get('parsed'):
            parsed = result['parsed']
            print(f"{i}. \"{result['original_input']}\"")
            print(f"   → {parsed['title']} (due: {parsed['due_date_time']})")
        else:
            print(f"{i}. \"{result['original_input']}\"")
            print(f"   → Error: {result.get('error', 'Unknown error')}")
    
    print()
    print("=" * 80)
    print("🎉 OPENAI INTEGRATION POC DEMO COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    demo()
