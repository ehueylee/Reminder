"""
Quick automated test for the scheduler
"""

from datetime import datetime, timedelta
from database import SessionLocal, init_db
import crud
from scheduler import ReminderScheduler, console_notification_handler

# Initialize database
init_db()

print("\n" + "="*80)
print("🧪 Quick Scheduler Test")
print("="*80)

# Create a test reminder due in 1 minute
db = SessionLocal()
try:
    now = datetime.now()
    reminder = crud.create_reminder(
        db=db,
        user_id="test_user",
        title="Quick Test Reminder",
        description="This is a test reminder for the scheduler",
        due_date_time=now + timedelta(minutes=1),
        timezone="America/New_York",
        priority="high",
        tags=["test"],
        is_recurring=False,
        natural_language_input="Test reminder"
    )
    print(f"\n✅ Created test reminder (ID: {reminder.id})")
    print(f"   Due at: {reminder.due_date_time}")
finally:
    db.close()

# Set up and test scheduler
print("\n⏰ Setting up scheduler...")
scheduler = ReminderScheduler()
scheduler.add_notification_handler(console_notification_handler)

print("\n🔎 Checking for due reminders...")
scheduler.check_due_reminders()

print("\n✅ Test complete!")
print("   If the reminder was due within the next 5 minutes, it should have been detected.")
print("="*80 + "\n")
