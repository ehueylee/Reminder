# Recurring Reminders Guide

## Overview

Quick Win #3 adds powerful recurring reminder functionality to the Reminder App. Reminders can now automatically repeat on daily, weekly, monthly, or yearly schedules, with intelligent next-occurrence creation.

## Features

✅ **Automatic Next Occurrence Creation** - When you complete a recurring reminder, the next one is created automatically  
✅ **Multiple Frequencies** - Daily, weekly, monthly, and yearly patterns  
✅ **Skip Functionality** - Skip an occurrence and create the next one immediately  
✅ **Snooze Support** - Delay a reminder by N minutes without affecting the recurrence pattern  
✅ **Flexible Patterns** - Configure intervals, specific days, day of month, etc.

---

## Recurrence Pattern Format

Recurring reminders use a JSON pattern stored in the `recurrence_pattern` field:

### Daily Pattern

```json
{
  "frequency": "daily",
  "interval": 1
}
```

- **interval**: Number of days between occurrences (1 = every day, 2 = every other day, etc.)

**Examples:**
- Every day: `{"frequency": "daily", "interval": 1}`
- Every 3 days: `{"frequency": "daily", "interval": 3}`

---

### Weekly Pattern

```json
{
  "frequency": "weekly",
  "interval": 1,
  "days_of_week": [0, 2, 4]
}
```

- **interval**: Number of weeks between occurrences
- **days_of_week**: List of days (0=Monday, 1=Tuesday, ..., 6=Sunday)

**Examples:**
- Every Monday: `{"frequency": "weekly", "interval": 1, "days_of_week": [0]}`
- Every Mon/Wed/Fri: `{"frequency": "weekly", "interval": 1, "days_of_week": [0, 2, 4]}`
- Every other Friday: `{"frequency": "weekly", "interval": 2, "days_of_week": [4]}`

---

### Monthly Pattern

```json
{
  "frequency": "monthly",
  "interval": 1,
  "day_of_month": 15
}
```

- **interval**: Number of months between occurrences
- **day_of_month**: Day of the month (1-31)

**Examples:**
- 15th of every month: `{"frequency": "monthly", "interval": 1, "day_of_month": 15}`
- 1st of every quarter: `{"frequency": "monthly", "interval": 3, "day_of_month": 1}`
- Last day handling: If day > days in month, uses last day (e.g., Feb 30 → Feb 28/29)

---

### Yearly Pattern

```json
{
  "frequency": "yearly",
  "interval": 1,
  "month": 6,
  "day_of_month": 15
}
```

- **interval**: Number of years between occurrences
- **month**: Month number (1-12)
- **day_of_month**: Day of the month (1-31)

**Examples:**
- Every June 15th: `{"frequency": "yearly", "interval": 1, "month": 6, "day_of_month": 15}`
- Birthday/anniversary reminders

---

## Using the API

### Creating a Recurring Reminder

```bash
curl -X POST "http://127.0.0.1:8001/reminders/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "title": "Daily Standup",
    "description": "Team standup meeting",
    "due_date_time": "2025-10-25T10:00:00",
    "timezone": "America/New_York",
    "priority": "high",
    "is_recurring": true,
    "recurrence_pattern": {
      "frequency": "daily",
      "interval": 1
    }
  }'
```

### Completing a Recurring Reminder

When you mark a recurring reminder as complete, the next occurrence is **automatically created**:

```bash
curl -X POST "http://127.0.0.1:8001/reminders/{reminder_id}/complete"
```

**What happens:**
1. Current reminder marked as `completed`
2. Next occurrence calculated based on pattern
3. New reminder created with same title, description, priority, tags
4. New reminder has new due date/time
5. Original reminder's `completed_at` timestamp recorded

---

### Skipping an Occurrence

Skip the current occurrence and immediately create the next one:

```bash
curl -X POST "http://127.0.0.1:8001/reminders/{reminder_id}/skip"
```

**What happens:**
1. Current reminder marked as `cancelled`
2. Next occurrence calculated and created
3. Returns the newly created reminder

**Use cases:**
- Meeting cancelled this week
- Holiday - skip this occurrence
- One-time schedule change

---

### Snoozing a Reminder

Delay a reminder without affecting the recurrence pattern:

```bash
curl -X POST "http://127.0.0.1:8001/reminders/{reminder_id}/snooze?minutes=30"
```

**What happens:**
1. Current reminder's `due_date_time` updated (adds N minutes)
2. Recurrence pattern unchanged
3. Next occurrence still calculated from original date

**Use cases:**
- Busy right now - remind me in 30 minutes
- Need a bit more time
- Quick postponement without disrupting schedule

---

## Python Code Examples

### Creating Recurring Reminders

```python
from datetime import datetime, timedelta
from database import SessionLocal
import crud

db = SessionLocal()

# Daily reminder
daily = crud.create_reminder(
    db=db,
    user_id="user123",
    title="Daily Exercise",
    description="30 minutes of exercise",
    due_date_time=datetime.now() + timedelta(hours=8),
    is_recurring=True,
    recurrence_pattern={
        "frequency": "daily",
        "interval": 1
    }
)

# Weekly reminder (every Monday and Wednesday)
weekly = crud.create_reminder(
    db=db,
    user_id="user123",
    title="Team Meeting",
    description="Weekly sync",
    due_date_time=datetime.now() + timedelta(days=1),
    is_recurring=True,
    recurrence_pattern={
        "frequency": "weekly",
        "interval": 1,
        "days_of_week": [0, 2]  # Monday, Wednesday
    }
)

# Monthly reminder (15th of each month)
monthly = crud.create_reminder(
    db=db,
    user_id="user123",
    title="Monthly Report",
    description="Submit report by 5pm",
    due_date_time=datetime.now().replace(day=15, hour=17, minute=0),
    is_recurring=True,
    recurrence_pattern={
        "frequency": "monthly",
        "interval": 1,
        "day_of_month": 15
    }
)

db.close()
```

### Using RecurringService

```python
from recurring_service import get_recurring_service
from database import SessionLocal
import crud

db = SessionLocal()
service = get_recurring_service()

# Get a reminder
reminder = crud.get_reminder(db, reminder_id)

# Skip occurrence
next_reminder = service.skip_occurrence(reminder)
print(f"Next occurrence: {next_reminder.due_date_time}")

# Snooze for 1 hour
snoozed = service.snooze_reminder(reminder, snooze_minutes=60)
print(f"New due time: {snoozed.due_date_time}")

# Calculate next occurrence (without creating)
next_date = service.calculate_next_occurrence(
    reminder.due_date_time,
    reminder.recurrence_pattern
)
print(f"Next would be: {next_date}")

db.close()
```

---

## How It Works

### Automatic Next Occurrence

The `recurring_service.py` module provides:

1. **Pattern Parsing** - Validates and normalizes recurrence patterns
2. **Date Calculation** - Uses `python-dateutil` for smart date math
3. **Auto-Creation** - Hooks into CRUD completion events
4. **Skip/Snooze** - Manual control over recurring reminders

### Integration Points

**CRUD Layer (`crud.py`):**
```python
def complete_reminder(db, reminder_id):
    # Mark as complete
    reminder.status = "completed"
    
    # If recurring, create next occurrence
    if reminder.is_recurring:
        on_reminder_completed(reminder)
    
    return reminder
```

**Recurring Service (`recurring_service.py`):**
```python
def on_reminder_completed(reminder: Reminder):
    """Called when a recurring reminder is completed"""
    if should_create_next_occurrence(reminder):
        next_reminder = create_next_occurrence(reminder)
        return next_reminder
```

### Date Calculation Logic

The service uses `python-dateutil` for accurate date arithmetic:

- **Daily**: Simple `timedelta(days=interval)`
- **Weekly**: Find next matching day of week
- **Monthly**: Use `relativedelta(months=interval)` to handle month boundaries
- **Yearly**: Use `relativedelta(years=interval)` for anniversaries

**Edge case handling:**
- Feb 30 → Feb 28 (or 29 in leap years)
- Month-end dates handled correctly
- Timezone-aware calculations

---

## Testing Recurring Reminders

Run the demo script to test all functionality:

```bash
python demo_recurring.py
```

**Tests included:**
1. ✅ Daily recurring reminder with auto-creation
2. ✅ Weekly reminder (specific days)
3. ✅ Monthly reminder (day of month)
4. ✅ Skip occurrence functionality
5. ✅ Snooze reminder functionality

---

## Database Schema

Recurring reminders use these fields in the `reminders` table:

```sql
is_recurring BOOLEAN DEFAULT 0
recurrence_pattern TEXT  -- JSON string
```

**Example stored pattern:**
```json
{"frequency": "weekly", "interval": 1, "days_of_week": [0, 2, 4]}
```

---

## Common Use Cases

### 1. Daily Habits

```python
# Morning meditation
{
    "title": "Morning Meditation",
    "due_date_time": "2025-10-25T07:00:00",
    "is_recurring": True,
    "recurrence_pattern": {
        "frequency": "daily",
        "interval": 1
    }
}
```

### 2. Weekly Meetings

```python
# Team standup every Monday
{
    "title": "Team Standup",
    "due_date_time": "2025-10-27T10:00:00",
    "is_recurring": True,
    "recurrence_pattern": {
        "frequency": "weekly",
        "interval": 1,
        "days_of_week": [0]  # Monday
    }
}
```

### 3. Monthly Bills

```python
# Rent payment on 1st
{
    "title": "Pay Rent",
    "due_date_time": "2025-11-01T09:00:00",
    "is_recurring": True,
    "recurrence_pattern": {
        "frequency": "monthly",
        "interval": 1,
        "day_of_month": 1
    }
}
```

### 4. Annual Events

```python
# Birthday reminder
{
    "title": "Mom's Birthday",
    "due_date_time": "2026-06-15T12:00:00",
    "is_recurring": True,
    "recurrence_pattern": {
        "frequency": "yearly",
        "interval": 1,
        "month": 6,
        "day_of_month": 15
    }
}
```

---

## Troubleshooting

### Next occurrence not created

**Check:**
1. Is `is_recurring` set to `True`?
2. Is `recurrence_pattern` valid JSON?
3. Check logs for errors during completion

### Wrong next date calculated

**Common causes:**
- Timezone mismatch
- Invalid day of month (e.g., Feb 30)
- Incorrect pattern format

**Debug:**
```python
# Test calculation without creating
service = get_recurring_service()
next_date = service.calculate_next_occurrence(
    reminder.due_date_time,
    reminder.recurrence_pattern
)
print(f"Next: {next_date}")
```

### Skip/Snooze not working

**Verify:**
- Reminder exists and is `pending`
- Reminder has valid recurrence pattern
- Database transaction commits

---

## Dependencies

```
python-dateutil==2.9.0.post0  # Date calculations
six==1.17.0                   # Python 2/3 compatibility
```

Install with:
```bash
pip install python-dateutil
```

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   User Interface                    │
│  (Complete, Skip, Snooze recurring reminders)       │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│                    REST API                         │
│  POST /reminders/{id}/complete                      │
│  POST /reminders/{id}/skip                          │
│  POST /reminders/{id}/snooze?minutes=30             │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│                   CRUD Layer                        │
│  complete_reminder() → calls on_reminder_completed()│
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│              Recurring Service                      │
│  - parse_recurrence_pattern()                       │
│  - calculate_next_occurrence()                      │
│  - create_next_occurrence()                         │
│  - skip_occurrence()                                │
│  - snooze_reminder()                                │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│                   Database                          │
│  reminders table (is_recurring, recurrence_pattern) │
└─────────────────────────────────────────────────────┘
```

---

## Next Steps

After implementing recurring reminders, consider:

1. **End dates** - Stop recurring after N occurrences or specific date
2. **Series view** - View all occurrences in a series
3. **Modify series** - Update all future occurrences
4. **Exception dates** - Skip specific dates (holidays)
5. **Custom patterns** - "2nd Tuesday of each month", etc.

---

## Summary

✅ **Created** - Complete recurring reminder service  
✅ **Automatic** - Next occurrence created on completion  
✅ **Flexible** - Daily, weekly, monthly, yearly patterns  
✅ **Control** - Skip and snooze functionality  
✅ **Tested** - Comprehensive demo script  

Recurring reminders are now fully functional! 🎉
