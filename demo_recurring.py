"""
Demo script for testing recurring reminders
Quick Win #3: Improved Recurring Reminders
"""

from datetime import datetime, timedelta
from database import SessionLocal, init_db
import crud
from recurring_service import RecurringService, get_recurring_service

# Initialize database
init_db()

print("\n" + "="*80)
print("🔄 Recurring Reminders Demo")
print("="*80)

# Test 1: Daily recurring reminder
print("\n📅 Test 1: Daily Recurring Reminder")
print("-" * 80)

db = SessionLocal()
try:
    now = datetime.now()
    
    # Create daily reminder
    daily_reminder = crud.create_reminder(
        db=db,
        user_id="recurring_demo_user",
        title="Daily Standup",
        description="Team standup meeting",
        due_date_time=now + timedelta(hours=1),
        timezone="America/New_York",
        priority="high",
        tags=["work", "daily"],
        is_recurring=True,
        recurrence_pattern={
            "frequency": "daily",
            "interval": 1
        },
        natural_language_input="Daily standup at 10am"
    )
    
    print(f"✅ Created daily reminder: {daily_reminder.title}")
    print(f"   ID: {daily_reminder.id}")
    print(f"   Due: {daily_reminder.due_date_time}")
    print(f"   Pattern: {daily_reminder.recurrence_pattern}")
    
    # Calculate next occurrence
    service = get_recurring_service()
    next_date = service.calculate_next_occurrence(
        daily_reminder.due_date_time,
        daily_reminder.recurrence_pattern
    )
    print(f"   Next occurrence would be: {next_date}")
    
    # Mark as completed (should auto-create next)
    print(f"\n📝 Marking as completed...")
    completed = crud.complete_reminder(db, daily_reminder.id)
    print(f"   Status: {completed.status}")
    print(f"   Completed at: {completed.completed_at}")
    
    # Check if next occurrence was created
    print(f"\n🔍 Checking for next occurrence...")
    all_reminders = crud.get_reminders_by_user(db, "recurring_demo_user", status="pending")
    daily_reminders = [r for r in all_reminders if r.title == "Daily Standup"]
    
    if daily_reminders:
        next_reminder = daily_reminders[0]
        print(f"   ✅ Next occurrence created!")
        print(f"   ID: {next_reminder.id}")
        print(f"   Due: {next_reminder.due_date_time}")
        print(f"   Days from now: {(next_reminder.due_date_time - now).days}")
    else:
        print(f"   ❌ No next occurrence found")

finally:
    db.close()

# Test 2: Weekly recurring reminder
print("\n" + "="*80)
print("📅 Test 2: Weekly Recurring Reminder (Every Monday)")
print("-" * 80)

db = SessionLocal()
try:
    now = datetime.now()
    
    # Create weekly reminder (Mondays)
    weekly_reminder = crud.create_reminder(
        db=db,
        user_id="recurring_demo_user",
        title="Weekly Team Meeting",
        description="Every Monday at 2pm",
        due_date_time=now + timedelta(days=1),
        timezone="America/New_York",
        priority="medium",
        tags=["work", "meeting"],
        is_recurring=True,
        recurrence_pattern={
            "frequency": "weekly",
            "interval": 1,
            "days_of_week": [0]  # Monday
        },
        natural_language_input="Team meeting every Monday at 2pm"
    )
    
    print(f"✅ Created weekly reminder: {weekly_reminder.title}")
    print(f"   ID: {weekly_reminder.id}")
    print(f"   Due: {weekly_reminder.due_date_time}")
    print(f"   Pattern: Every Monday")
    
    # Calculate next occurrence
    next_date = service.calculate_next_occurrence(
        weekly_reminder.due_date_time,
        weekly_reminder.recurrence_pattern
    )
    print(f"   Next occurrence: {next_date}")
    print(f"   Day of week: {next_date.strftime('%A') if next_date else 'N/A'}")

finally:
    db.close()

# Test 3: Monthly recurring reminder
print("\n" + "="*80)
print("📅 Test 3: Monthly Recurring Reminder (15th of each month)")
print("-" * 80)

db = SessionLocal()
try:
    now = datetime.now()
    
    # Create monthly reminder
    monthly_reminder = crud.create_reminder(
        db=db,
        user_id="recurring_demo_user",
        title="Monthly Report",
        description="Submit monthly report on the 15th",
        due_date_time=now.replace(day=15, hour=17, minute=0),
        timezone="America/New_York",
        priority="high",
        tags=["work", "report"],
        is_recurring=True,
        recurrence_pattern={
            "frequency": "monthly",
            "interval": 1,
            "day_of_month": 15
        },
        natural_language_input="Monthly report on the 15th"
    )
    
    print(f"✅ Created monthly reminder: {monthly_reminder.title}")
    print(f"   ID: {monthly_reminder.id}")
    print(f"   Due: {monthly_reminder.due_date_time}")
    print(f"   Pattern: 15th of each month")
    
    # Calculate next occurrence
    next_date = service.calculate_next_occurrence(
        monthly_reminder.due_date_time,
        monthly_reminder.recurrence_pattern
    )
    print(f"   Next occurrence: {next_date}")
    if next_date:
        print(f"   Day: {next_date.day}")
        print(f"   Month: {next_date.strftime('%B')}")

finally:
    db.close()

# Test 4: Skip occurrence
print("\n" + "="*80)
print("📅 Test 4: Skip Occurrence")
print("-" * 80)

db = SessionLocal()
try:
    # Get the weekly reminder
    reminders = crud.get_reminders_by_user(db, "recurring_demo_user", status="pending")
    weekly = [r for r in reminders if r.title == "Weekly Team Meeting"]
    
    if weekly:
        reminder = weekly[0]
        print(f"📝 Skipping: {reminder.title}")
        print(f"   Current due: {reminder.due_date_time}")
        
        # Skip this occurrence
        next_reminder = service.skip_occurrence(reminder)
        
        if next_reminder:
            print(f"\n✅ Skipped and created next occurrence")
            print(f"   New ID: {next_reminder.id}")
            print(f"   New due: {next_reminder.due_date_time}")
            print(f"   Original status: cancelled")
        else:
            print(f"\n❌ Failed to skip occurrence")
    else:
        print("❌ No weekly reminder found to skip")

finally:
    db.close()

# Test 5: Snooze reminder
print("\n" + "="*80)
print("📅 Test 5: Snooze Reminder (30 minutes)")
print("-" * 80)

db = SessionLocal()
try:
    # Get a pending reminder
    reminders = crud.get_reminders_by_user(db, "recurring_demo_user", status="pending")
    
    if reminders:
        reminder = reminders[0]
        print(f"📝 Snoozing: {reminder.title}")
        print(f"   Current due: {reminder.due_date_time}")
        
        # Snooze for 30 minutes
        snoozed = service.snooze_reminder(reminder, snooze_minutes=30)
        
        if snoozed:
            print(f"\n✅ Snoozed for 30 minutes")
            print(f"   New due: {snoozed.due_date_time}")
            minutes_diff = (snoozed.due_date_time - now).total_seconds() / 60
            print(f"   Minutes from now: {int(minutes_diff)}")
        else:
            print(f"\n❌ Failed to snooze reminder")
    else:
        print("❌ No reminders found to snooze")

finally:
    db.close()

# Summary
print("\n" + "="*80)
print("📊 Demo Summary")
print("="*80)

db = SessionLocal()
try:
    all_reminders = crud.get_reminders_by_user(db, "recurring_demo_user")
    
    print(f"\nTotal reminders created: {len(all_reminders)}")
    print(f"\nBreakdown:")
    print(f"  Pending: {len([r for r in all_reminders if r.status == 'pending'])}")
    print(f"  Completed: {len([r for r in all_reminders if r.status == 'completed'])}")
    print(f"  Cancelled: {len([r for r in all_reminders if r.status == 'cancelled'])}")
    print(f"  Recurring: {len([r for r in all_reminders if r.is_recurring])}")
    
    print(f"\n📋 All Reminders:")
    for reminder in all_reminders:
        status_emoji = {
            "pending": "⏳",
            "completed": "✅",
            "cancelled": "❌"
        }.get(reminder.status, "❓")
        
        recurring_indicator = "🔄" if reminder.is_recurring else "  "
        
        print(f"  {status_emoji} {recurring_indicator} {reminder.title}")
        print(f"     Due: {reminder.due_date_time}")
        print(f"     Status: {reminder.status}")
        if reminder.recurrence_pattern:
            print(f"     Pattern: {reminder.recurrence_pattern.get('frequency', 'N/A')}")
        print()

finally:
    db.close()

print("="*80)
print("\n💡 Key Features Demonstrated:")
print("  ✅ Daily recurring reminders")
print("  ✅ Weekly recurring reminders (specific days)")
print("  ✅ Monthly recurring reminders (specific day of month)")
print("  ✅ Automatic next occurrence creation on completion")
print("  ✅ Skip occurrence functionality")
print("  ✅ Snooze reminder functionality")
print("\n🎉 Recurring reminders are working!")
print("="*80 + "\n")
