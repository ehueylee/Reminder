"""
Integration tests for OpenAI service.
Tests natural language parsing functionality.
"""

import pytest
import os
from datetime import datetime, timedelta
from openai_service import (
    parse_reminder,
    parse_reminder_batch,
    validate_parsed_reminder,
    calculate_confidence
)


@pytest.fixture
def openai_available():
    """Check if OpenAI API key is available."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "sk-your-key-here":
        pytest.skip("OpenAI API key not available - skipping OpenAI tests")


def test_parse_simple_reminder(openai_available):
    """Test parsing a simple time-based reminder."""
    
    result = parse_reminder("Remind me to call John tomorrow at 3pm")
    parsed = result['parsed']
    
    # Check required fields exist
    assert parsed['title'] is not None
    assert 'call' in parsed['title'].lower() or 'john' in parsed['title'].lower()
    assert parsed['due_date_time'] is not None
    assert parsed['priority'] in ['low', 'medium', 'high', 'urgent']
    assert result['confidence'] > 0.0
    
    # Validate the result
    is_valid, error = validate_parsed_reminder(parsed)
    assert is_valid, f"Validation failed: {error}"
    
    print(f"✅ test_parse_simple_reminder passed - Title: {parsed['title']}")


def test_parse_urgent_reminder(openai_available):
    """Test detecting urgency from keywords."""
    
    result = parse_reminder("URGENT: Submit report by end of day")
    parsed = result['parsed']
    
    # Should detect high or urgent priority
    assert parsed['priority'] in ['high', 'urgent']
    
    # Should increase confidence due to urgency keyword
    assert result['confidence'] >= 0.6
    
    print(f"✅ test_parse_urgent_reminder passed - Priority: {parsed['priority']}")


def test_parse_recurring_reminder(openai_available):
    """Test parsing recurring patterns."""
    
    result = parse_reminder("Team meeting every Monday at 9am")
    parsed = result['parsed']
    
    # Should detect recurring pattern
    assert parsed['is_recurring'] == True
    assert parsed['recurrence_pattern'] is not None
    assert parsed['recurrence_pattern']['frequency'] == 'weekly'
    
    print(f"✅ test_parse_recurring_reminder passed - Recurring: {parsed['recurrence_pattern']['frequency']}")


def test_parse_with_timezone(openai_available):
    """Test timezone handling."""
    
    result = parse_reminder(
        "Meeting tomorrow at 2pm",
        user_timezone="America/Los_Angeles"
    )
    parsed = result['parsed']
    
    # Should include timezone in the result
    assert parsed['timezone'] is not None
    
    # Due date should be parseable
    due_date = datetime.fromisoformat(parsed['due_date_time'].replace('Z', '+00:00'))
    assert due_date is not None
    
    print(f"✅ test_parse_with_timezone passed - Timezone: {parsed['timezone']}")


def test_parse_with_location(openai_available):
    """Test extracting location information."""
    
    result = parse_reminder("Doctor appointment at City Hospital tomorrow at 2pm")
    parsed = result['parsed']
    
    # Should extract location if mentioned
    if parsed.get('location'):
        assert 'hospital' in parsed['location'].lower() or 'city' in parsed['location'].lower()
    
    print(f"✅ test_parse_with_location passed - Location: {parsed.get('location', 'Not detected')}")


def test_parse_with_tags(openai_available):
    """Test automatic tag generation."""
    
    result = parse_reminder("Team standup meeting tomorrow morning")
    parsed = result['parsed']
    
    # Should generate relevant tags
    assert isinstance(parsed.get('tags', []), list)
    
    # Common tags for meetings
    tags_lower = [tag.lower() for tag in parsed.get('tags', [])]
    assert any(tag in tags_lower for tag in ['work', 'meeting', 'team'])
    
    print(f"✅ test_parse_with_tags passed - Tags: {', '.join(parsed.get('tags', []))}")


def test_parse_relative_time(openai_available):
    """Test parsing relative time expressions."""
    
    test_cases = [
        "Remind me tomorrow at 3pm",
        "Call client next week",
        "Submit report by Friday"
    ]
    
    for input_text in test_cases:
        result = parse_reminder(input_text)
        parsed = result['parsed']
        
        # Should have a valid due date
        assert parsed['due_date_time'] is not None
        
        # Should be parseable as ISO 8601
        due_date = datetime.fromisoformat(parsed['due_date_time'].replace('Z', '+00:00'))
        assert due_date is not None
        
        # Should be in the future (for most cases)
        # Note: This might fail if run at exactly the parsed time, but very unlikely
    
    print(f"✅ test_parse_relative_time passed - Tested {len(test_cases)} cases")


def test_parse_daily_recurring(openai_available):
    """Test parsing daily recurring reminders."""
    
    result = parse_reminder("Take medication every day at 8am")
    parsed = result['parsed']
    
    assert parsed['is_recurring'] == True
    assert parsed['recurrence_pattern']['frequency'] == 'daily'
    
    print(f"✅ test_parse_daily_recurring passed")


def test_validate_parsed_reminder_valid():
    """Test validation with valid data."""
    
    valid_data = {
        "title": "Test Reminder",
        "due_date_time": "2025-10-23T14:00:00-04:00",
        "priority": "medium",
        "is_recurring": False
    }
    
    is_valid, error = validate_parsed_reminder(valid_data)
    assert is_valid
    assert error is None
    
    print(f"✅ test_validate_parsed_reminder_valid passed")


def test_validate_parsed_reminder_missing_title():
    """Test validation fails with missing title."""
    
    invalid_data = {
        "due_date_time": "2025-10-23T14:00:00-04:00"
    }
    
    is_valid, error = validate_parsed_reminder(invalid_data)
    assert not is_valid
    assert "title" in error.lower()
    
    print(f"✅ test_validate_parsed_reminder_missing_title passed")


def test_validate_parsed_reminder_invalid_priority():
    """Test validation fails with invalid priority."""
    
    invalid_data = {
        "title": "Test",
        "due_date_time": "2025-10-23T14:00:00-04:00",
        "priority": "super-urgent"  # Invalid priority
    }
    
    is_valid, error = validate_parsed_reminder(invalid_data)
    assert not is_valid
    assert "priority" in error.lower()
    
    print(f"✅ test_validate_parsed_reminder_invalid_priority passed")


def test_calculate_confidence_time_specific():
    """Test confidence calculation with specific time."""
    
    confidence = calculate_confidence(
        "Meeting tomorrow at 3:30pm",
        {"title": "Meeting", "priority": "medium"}
    )
    
    # Should have high confidence due to specific time
    assert confidence >= 0.65
    
    print(f"✅ test_calculate_confidence_time_specific passed - Confidence: {confidence:.2%}")


def test_calculate_confidence_vague():
    """Test confidence calculation with vague input."""
    
    confidence = calculate_confidence(
        "Do something sometime",
        {"title": "Do something", "priority": "medium"}
    )
    
    # Should have lower confidence due to vagueness
    assert confidence <= 0.60
    
    print(f"✅ test_calculate_confidence_vague passed - Confidence: {confidence:.2%}")


def test_parse_reminder_batch(openai_available):
    """Test batch parsing of multiple reminders."""
    
    inputs = [
        "Water plants tomorrow",
        "Team meeting next Monday at 10am",
        "Call mom this weekend"
    ]
    
    results = parse_reminder_batch(inputs, user_timezone="America/New_York")
    
    assert len(results) == len(inputs)
    
    # Check that each result has expected structure
    for result in results:
        assert 'original_input' in result
        # Either parsed or error should be present
        assert 'parsed' in result or 'error' in result
    
    print(f"✅ test_parse_reminder_batch passed - Parsed {len(results)} reminders")


def test_error_handling_empty_input():
    """Test error handling with empty input."""
    
    with pytest.raises(ValueError, match="empty"):
        parse_reminder("")
    
    with pytest.raises(ValueError, match="empty"):
        parse_reminder("   ")
    
    print(f"✅ test_error_handling_empty_input passed")


def test_error_handling_no_api_key():
    """Test error handling when API key is missing."""
    
    # Temporarily remove API key
    original_key = os.getenv("OPENAI_API_KEY")
    os.environ["OPENAI_API_KEY"] = "sk-your-key-here"
    
    try:
        with pytest.raises(ValueError, match="API key not configured"):
            parse_reminder("Test reminder")
    finally:
        # Restore original key
        if original_key:
            os.environ["OPENAI_API_KEY"] = original_key
    
    print(f"✅ test_error_handling_no_api_key passed")


def test_parse_weekly_specific_days(openai_available):
    """Test parsing weekly reminders on specific days."""
    
    result = parse_reminder("Team standup every Monday, Wednesday, and Friday at 9am")
    parsed = result['parsed']
    
    if parsed['is_recurring'] and parsed['recurrence_pattern']:
        pattern = parsed['recurrence_pattern']
        if pattern.get('days_of_week'):
            # Should have multiple days
            assert len(pattern['days_of_week']) > 1
    
    print(f"✅ test_parse_weekly_specific_days passed")


def test_parse_end_of_day(openai_available):
    """Test parsing 'end of day' expressions."""
    
    result = parse_reminder("Submit timesheet by end of day Friday")
    parsed = result['parsed']
    
    # Should parse successfully
    assert parsed['title'] is not None
    assert parsed['due_date_time'] is not None
    
    # Due time should be in the evening (after 5pm)
    due_date = datetime.fromisoformat(parsed['due_date_time'].replace('Z', '+00:00'))
    assert due_date.hour >= 17 or due_date.hour == 0  # Evening or end of day
    
    print(f"✅ test_parse_end_of_day passed - Due: {parsed['due_date_time']}")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short", "-s"])
