"""
Demo script for testing the Background Scheduler
Phase 1.5: Background Scheduler demonstration
"""

import time
from datetime import datetime, timedelta
from database import SessionLocal, init_db
import crud
from scheduler import ReminderScheduler, console_notification_handler, file_notification_handler

# Initialize database
init_db()


def create_test_reminders():
    """Create test reminders with various due times."""
    db = SessionLocal()
    try:
        print("\n📝 Creating test reminders...")
        
        # Current time
        now = datetime.now()
        
        # Reminder 1: Due in 1 minute (should trigger soon)
        reminder1 = crud.create_reminder(
            db=db,
            user_id="demo_user",
            title="Test Reminder - Due in 1 minute",
            description="This reminder should trigger very soon",
            due_date_time=now + timedelta(minutes=1),
            timezone="America/New_York",
            priority="high",
            tags=["test", "urgent"],
            is_recurring=False,
            natural_language_input="Test reminder in 1 minute"
        )
        print(f"  ✅ Created: {reminder1.title} (ID: {reminder1.id})")
        
        # Reminder 2: Due in 2 minutes
        reminder2 = crud.create_reminder(
            db=db,
            user_id="demo_user",
            title="Test Reminder - Due in 2 minutes",
            description="This reminder should trigger in about 2 minutes",
            due_date_time=now + timedelta(minutes=2),
            timezone="America/New_York",
            priority="medium",
            tags=["test"],
            is_recurring=False,
            natural_language_input="Test reminder in 2 minutes"
        )
        print(f"  ✅ Created: {reminder2.title} (ID: {reminder2.id})")
        
        # Reminder 3: Due in 4 minutes
        reminder3 = crud.create_reminder(
            db=db,
            user_id="demo_user",
            title="Test Reminder - Due in 4 minutes",
            description="This reminder should trigger in about 4 minutes",
            due_date_time=now + timedelta(minutes=4),
            timezone="America/New_York",
            priority="low",
            tags=["test", "demo"],
            location="Home Office",
            is_recurring=False,
            natural_language_input="Test reminder in 4 minutes"
        )
        print(f"  ✅ Created: {reminder3.title} (ID: {reminder3.id})")
        
        # Reminder 4: Due in 10 minutes (outside 5-minute window)
        reminder4 = crud.create_reminder(
            db=db,
            user_id="demo_user",
            title="Test Reminder - Due in 10 minutes",
            description="This reminder is outside the initial check window",
            due_date_time=now + timedelta(minutes=10),
            timezone="America/New_York",
            priority="low",
            tags=["test"],
            is_recurring=False,
            natural_language_input="Test reminder in 10 minutes"
        )
        print(f"  ✅ Created: {reminder4.title} (ID: {reminder4.id})")
        
        print(f"\n✅ Created 4 test reminders")
        return [reminder1, reminder2, reminder3, reminder4]
        
    finally:
        db.close()


def run_scheduler_demo(duration_minutes: int = 5):
    """
    Run the scheduler for a specified duration.
    
    Args:
        duration_minutes: How long to run the demo (default: 5 minutes)
    """
    print("\n" + "="*80)
    print("🎬 Background Scheduler Demo")
    print("="*80)
    
    # Create test reminders
    reminders = create_test_reminders()
    
    # Set up scheduler
    print("\n⏰ Setting up scheduler...")
    scheduler = ReminderScheduler()
    
    # Add notification handlers
    scheduler.add_notification_handler(console_notification_handler)
    scheduler.add_notification_handler(
        lambda r, m: file_notification_handler(r, m, filepath="demo_notifications.log")
    )
    
    # Start scheduler (check every minute)
    scheduler.start(check_interval_minutes=1)
    
    print(f"\n🏃 Running demo for {duration_minutes} minutes...")
    print("   Watch for notifications as reminders become due!")
    print("   (Press Ctrl+C to stop early)\n")
    
    try:
        # Run for the specified duration
        end_time = time.time() + (duration_minutes * 60)
        
        while time.time() < end_time:
            remaining = int(end_time - time.time())
            minutes_left = remaining // 60
            seconds_left = remaining % 60
            
            print(f"⏳ Time remaining: {minutes_left}m {seconds_left}s", end="\r")
            time.sleep(1)
        
        print("\n\n✅ Demo completed!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrupted by user")
    
    finally:
        # Stop scheduler
        scheduler.stop()
        print("\n🛑 Scheduler stopped")
        
        # Show summary
        print("\n" + "="*80)
        print("📊 Demo Summary")
        print("="*80)
        
        db = SessionLocal()
        try:
            # Count completed reminders (use fresh queries, not detached objects)
            completed_count = 0
            reminder_ids = [r.id for r in reminders]
            
            for reminder_id in reminder_ids:
                current = crud.get_reminder(db, reminder_id)
                if current and current.status == "completed":
                    completed_count += 1
            
            print(f"  Total reminders created: {len(reminder_ids)}")
            print(f"  Reminders completed: {completed_count}")
            print(f"  Reminders still pending: {len(reminder_ids) - completed_count}")
            print(f"\n  📄 Notifications logged to: demo_notifications.log")
            
        finally:
            db.close()
        
        print("\n" + "="*80)


def manual_check_demo():
    """Manually trigger a reminder check (for immediate testing)."""
    print("\n" + "="*80)
    print("🔍 Manual Scheduler Check Demo")
    print("="*80)
    
    # Create test reminders
    reminders = create_test_reminders()
    
    # Set up scheduler
    print("\n⏰ Setting up scheduler...")
    scheduler = ReminderScheduler()
    scheduler.add_notification_handler(console_notification_handler)
    
    # Manually trigger check (don't start background scheduler)
    print("\n🔎 Manually checking for due reminders...")
    scheduler.check_due_reminders()
    
    print("\n✅ Manual check complete!")
    print("   (Note: Reminders may not be due yet if you just created them)")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    print("\n🎯 Background Scheduler Demo Options:")
    print("  1. Run scheduler demo (5 minutes)")
    print("  2. Manual check (immediate)")
    print("  3. Quick test (1 minute)")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        run_scheduler_demo(duration_minutes=5)
    elif choice == "2":
        manual_check_demo()
    elif choice == "3":
        run_scheduler_demo(duration_minutes=1)
    else:
        print("❌ Invalid choice. Running default 5-minute demo...")
        run_scheduler_demo(duration_minutes=5)
