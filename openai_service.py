"""
OpenAI Service for Natural Language Reminder Parsing.
Uses OpenAI's function calling to parse natural language into structured reminder data.
"""

import os
import json
from datetime import datetime
from typing import Optional, List, Literal
from openai import OpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class RecurrencePattern(BaseModel):
    """Schema for recurring reminder patterns."""
    frequency: Literal['daily', 'weekly', 'monthly', 'yearly'] = Field(
        description="How often the reminder repeats"
    )
    interval: int = Field(
        default=1,
        description="Interval between recurrences (e.g., every 2 days, every 3 weeks)"
    )
    days_of_week: Optional[List[int]] = Field(
        default=None,
        description="For weekly: list of days (0=Monday, 6=Sunday)"
    )
    day_of_month: Optional[int] = Field(
        default=None,
        description="For monthly: day of month (1-31)"
    )
    end_date: Optional[str] = Field(
        default=None,
        description="When to stop recurring (ISO 8601 format)"
    )


class ParsedReminder(BaseModel):
    """Schema for parsed reminder data."""
    title: str = Field(
        description="Brief title or summary of the reminder"
    )
    description: Optional[str] = Field(
        default=None,
        description="Additional details about the reminder"
    )
    due_date_time: str = Field(
        description="When the reminder is due in ISO 8601 format (e.g., 2025-10-23T14:00:00-04:00)"
    )
    timezone: str = Field(
        default="UTC",
        description="Timezone for the due date (e.g., America/New_York, UTC)"
    )
    is_recurring: bool = Field(
        default=False,
        description="Whether this reminder repeats"
    )
    recurrence_pattern: Optional[RecurrencePattern] = Field(
        default=None,
        description="Pattern for recurring reminders"
    )
    priority: Literal['low', 'medium', 'high', 'urgent'] = Field(
        default='medium',
        description="Priority level based on urgency words in input"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Relevant tags or categories (e.g., work, personal, health)"
    )
    location: Optional[str] = Field(
        default=None,
        description="Location mentioned in the reminder"
    )


def parse_reminder(
    natural_input: str,
    user_timezone: str = "UTC",
    current_time: Optional[datetime] = None
) -> dict:
    """
    Parse natural language input into structured reminder data using OpenAI.
    
    Args:
        natural_input: Natural language description of the reminder
        user_timezone: User's timezone (e.g., "America/New_York")
        current_time: Current time for relative date calculations (defaults to now)
    
    Returns:
        dict containing:
            - parsed: ParsedReminder object as dict
            - original_input: The original input text
            - confidence: Confidence score (0-1)
            - model_used: Which OpenAI model was used
    
    Raises:
        ValueError: If input is empty or API key is missing
        Exception: If OpenAI API call fails
    """
    
    # Validation
    if not natural_input or not natural_input.strip():
        raise ValueError("Natural language input cannot be empty")
    
    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "sk-your-key-here":
        raise ValueError("OpenAI API key not configured. Please set OPENAI_API_KEY in .env file")
    
    # Use provided time or current time
    if current_time is None:
        current_time = datetime.now()
    
    # Format current time for context
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    current_day = current_time.strftime("%A")
    
    # Create system message with context
    system_message = f"""You are an expert reminder parsing assistant. Parse the user's natural language input into a structured reminder.

Current Information:
- Current date/time: {current_time_str}
- Current day: {current_day}
- User timezone: {user_timezone}

Guidelines:
1. Convert relative times to absolute ISO 8601 format with timezone
2. Detect recurring patterns from phrases like "every day", "weekly", "every Monday"
3. Infer priority from urgency words (URGENT, ASAP, important -> high/urgent)
4. Extract location if mentioned
5. Generate relevant tags based on context (e.g., work, personal, health, meeting)
6. For "tomorrow", "next week", etc., calculate the exact date/time
7. If no specific time is mentioned, use sensible defaults:
   - Morning: 09:00
   - Afternoon: 14:00
   - Evening: 18:00
   - Night: 20:00
8. For recurring reminders, set is_recurring to true and provide the pattern
9. Keep the title concise (under 100 characters)

Examples of relative time conversion:
- "tomorrow at 3pm" -> tomorrow's date at 15:00:00
- "next Monday" -> date of next Monday at 09:00:00
- "in 2 hours" -> current time + 2 hours
- "next week" -> 7 days from now at 09:00:00
"""
    
    # Create messages for the API call
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": natural_input}
    ]
    
    # Define tools using Pydantic model
    tools = [
        {
            "type": "function",
            "function": {
                "name": "create_reminder",
                "description": "Create a structured reminder from natural language input",
                "parameters": ParsedReminder.model_json_schema()
            }
        }
    ]
    
    # Call OpenAI API
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Cost-effective model
            messages=messages,
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "create_reminder"}},
            temperature=0.1  # Lower temperature for more consistent parsing
        )
        
        # Extract the function call
        message = response.choices[0].message
        
        if not message.tool_calls:
            raise Exception("No tool call returned from OpenAI")
        
        tool_call = message.tool_calls[0]
        parsed_data = json.loads(tool_call.function.arguments)
        
        # Calculate confidence based on how specific the input was
        confidence = calculate_confidence(natural_input, parsed_data)
        
        return {
            "parsed": parsed_data,
            "original_input": natural_input,
            "confidence": confidence,
            "model_used": response.model
        }
    
    except Exception as e:
        raise Exception(f"Failed to parse reminder with OpenAI: {str(e)}")


def calculate_confidence(input_text: str, parsed_data: dict) -> float:
    """
    Calculate confidence score based on input specificity.
    
    Args:
        input_text: Original natural language input
        parsed_data: Parsed reminder data
    
    Returns:
        Confidence score between 0 and 1
    """
    confidence = 0.5  # Base confidence
    
    input_lower = input_text.lower()
    
    # Increase confidence for specific time mentions
    time_keywords = ['at', 'pm', 'am', 'o\'clock', ':']
    if any(keyword in input_lower for keyword in time_keywords):
        confidence += 0.15
    
    # Increase confidence for specific date mentions
    date_keywords = ['tomorrow', 'today', 'monday', 'tuesday', 'wednesday', 
                     'thursday', 'friday', 'saturday', 'sunday', 'next week']
    if any(keyword in input_lower for keyword in date_keywords):
        confidence += 0.15
    
    # Increase confidence for priority keywords
    priority_keywords = ['urgent', 'important', 'asap', 'critical']
    if any(keyword in input_lower for keyword in priority_keywords):
        confidence += 0.1
    
    # Increase confidence for recurring patterns
    recurring_keywords = ['every', 'daily', 'weekly', 'monthly']
    if any(keyword in input_lower for keyword in recurring_keywords):
        confidence += 0.1
    
    # Cap at 0.95 (never 100% certain)
    return min(confidence, 0.95)


def parse_reminder_batch(
    inputs: List[str],
    user_timezone: str = "UTC"
) -> List[dict]:
    """
    Parse multiple reminders in batch.
    
    Args:
        inputs: List of natural language inputs
        user_timezone: User's timezone
    
    Returns:
        List of parsed reminder results
    """
    results = []
    for input_text in inputs:
        try:
            result = parse_reminder(input_text, user_timezone)
            results.append(result)
        except Exception as e:
            results.append({
                "parsed": None,
                "original_input": input_text,
                "error": str(e),
                "confidence": 0.0
            })
    
    return results


def validate_parsed_reminder(parsed_data: dict) -> tuple[bool, Optional[str]]:
    """
    Validate parsed reminder data.
    
    Args:
        parsed_data: Parsed reminder dictionary
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check required fields
        if not parsed_data.get("title"):
            return False, "Title is required"
        
        if not parsed_data.get("due_date_time"):
            return False, "Due date/time is required"
        
        # Validate due_date_time is ISO 8601 format
        try:
            datetime.fromisoformat(parsed_data["due_date_time"].replace('Z', '+00:00'))
        except ValueError:
            return False, "Invalid due_date_time format (must be ISO 8601)"
        
        # Validate priority
        valid_priorities = ['low', 'medium', 'high', 'urgent']
        if parsed_data.get("priority") and parsed_data["priority"] not in valid_priorities:
            return False, f"Priority must be one of: {', '.join(valid_priorities)}"
        
        # Validate recurrence pattern if recurring
        if parsed_data.get("is_recurring") and not parsed_data.get("recurrence_pattern"):
            return False, "Recurrence pattern required for recurring reminders"
        
        return True, None
    
    except Exception as e:
        return False, f"Validation error: {str(e)}"


# Example usage and testing
if __name__ == "__main__":
    # Test with sample inputs
    test_inputs = [
        "Remind me to call mom tomorrow at 3pm",
        "Team standup every Monday at 9am",
        "URGENT: Submit report by Friday 5pm",
        "Buy groceries this weekend",
        "Doctor appointment next Tuesday afternoon at General Hospital"
    ]
    
    print("=" * 70)
    print("OPENAI SERVICE - SAMPLE PARSING")
    print("=" * 70)
    print()
    
    for i, text in enumerate(test_inputs, 1):
        print(f"{i}. Input: \"{text}\"")
        try:
            result = parse_reminder(text, user_timezone="America/New_York")
            parsed = result["parsed"]
            
            print(f"   ✅ Title: {parsed['title']}")
            print(f"   📅 Due: {parsed['due_date_time']}")
            print(f"   🎯 Priority: {parsed['priority']}")
            print(f"   🔁 Recurring: {parsed['is_recurring']}")
            if parsed.get('tags'):
                print(f"   🏷️  Tags: {', '.join(parsed['tags'])}")
            if parsed.get('location'):
                print(f"   📍 Location: {parsed['location']}")
            print(f"   💯 Confidence: {result['confidence']:.0%}")
            print()
        except Exception as e:
            print(f"   ❌ Error: {e}")
            print()
