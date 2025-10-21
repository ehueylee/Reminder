"""
POC Demo for Database Foundation (Sub-Phase 1.1)
Demonstrates database CRUD operations.
"""

from database import SessionLocal, init_db
from models import Reminder
from crud import (
    create_reminder,
    get_reminder,
    get_reminders_by_user,
    update_reminder,
    complete_reminder,
    delete_reminder
)
from datetime import datetime, timedelta


def demo():
    """Demonstrate database CRUD operations."""
    
    print("=" * 60)
    print("DATABASE FOUNDATION - POC DEMO")
    print("=" * 60)
    print()
    
    # Initialize database
    print("1. Initializing database...")
    init_db()
    print()
    
    # Create session
    db = SessionLocal()
    
    try:
        # CREATE - Add some test reminders
        print("2. Creating test reminders...")
        print("-" * 60)
        
        reminder1 = create_reminder(
            db=db,
            user_id="demo_user",
            title="Call mom",
            description="Weekly catch-up call",
            due_date_time=datetime.utcnow() + timedelta(days=1),
            timezone="America/New_York",
            priority="high",
            tags=["personal", "family"]
        )
        print(f"✅ Created reminder: {reminder1.id[:8]}... - {reminder1.title}")
        
        reminder2 = create_reminder(
            db=db,
            user_id="demo_user",
            title="Team standup meeting",
            description="Daily team sync",
            due_date_time=datetime.utcnow() + timedelta(hours=2),
            timezone="UTC",
            priority="medium",
            tags=["work", "meeting"],
            is_recurring=True,
            recurrence_pattern={"frequency": "daily", "interval": 1}
        )
        print(f"✅ Created reminder: {reminder2.id[:8]}... - {reminder2.title}")
        
        reminder3 = create_reminder(
            db=db,
            user_id="demo_user",
            title="Submit quarterly report",
            description="Q4 2025 financial report",
            due_date_time=datetime.utcnow() + timedelta(days=7),
            timezone="UTC",
            priority="urgent",
            tags=["work", "deadline"]
        )
        print(f"✅ Created reminder: {reminder3.id[:8]}... - {reminder3.title}")
        print()
        
        # READ - Get all reminders
        print("3. Reading reminders for user 'demo_user'...")
        print("-" * 60)
        reminders = get_reminders_by_user(db, "demo_user")
        print(f"✅ Found {len(reminders)} reminder(s):")
        for r in reminders:
            print(f"   - {r.title}")
            print(f"     Due: {r.due_date_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"     Priority: {r.priority}")
            print(f"     Status: {r.status}")
            if r.tags:
                print(f"     Tags: {', '.join(r.tags)}")
            print()
        
        # READ - Get specific reminder
        print("4. Getting specific reminder...")
        print("-" * 60)
        fetched = get_reminder(db, reminder1.id)
        if fetched:
            print(f"✅ Retrieved reminder: {fetched.title}")
            print(f"   ID: {fetched.id}")
            print(f"   Description: {fetched.description}")
            print(f"   Timezone: {fetched.timezone}")
            print()
        
        # UPDATE - Modify a reminder
        print("5. Updating reminder...")
        print("-" * 60)
        updated = update_reminder(
            db,
            reminder2.id,
            priority="high",
            description="Updated: Important daily team sync"
        )
        if updated:
            print(f"✅ Updated reminder: {updated.title}")
            print(f"   New priority: {updated.priority}")
            print(f"   New description: {updated.description}")
            print()
        
        # READ - Filter by status
        print("6. Filtering by status (active)...")
        print("-" * 60)
        active_reminders = get_reminders_by_user(db, "demo_user", status="active")
        print(f"✅ Found {len(active_reminders)} active reminder(s)")
        print()
        
        # COMPLETE - Mark reminder as done
        print("7. Completing a reminder...")
        print("-" * 60)
        completed = complete_reminder(db, reminder1.id)
        if completed:
            print(f"✅ Completed reminder: {completed.title}")
            print(f"   Status: {completed.status}")
            print(f"   Completed at: {completed.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
        
        # READ - Check completed reminders
        print("8. Filtering by status (completed)...")
        print("-" * 60)
        completed_reminders = get_reminders_by_user(db, "demo_user", status="completed")
        print(f"✅ Found {len(completed_reminders)} completed reminder(s):")
        for r in completed_reminders:
            print(f"   - {r.title} (completed on {r.completed_at.strftime('%Y-%m-%d')})")
        print()
        
        # DELETE - Remove a reminder
        print("9. Deleting a reminder...")
        print("-" * 60)
        deleted = delete_reminder(db, reminder3.id)
        if deleted:
            print(f"✅ Deleted reminder successfully")
            print()
        
        # VERIFY - Check remaining reminders
        print("10. Verifying remaining reminders...")
        print("-" * 60)
        final_reminders = get_reminders_by_user(db, "demo_user")
        print(f"✅ Total reminders remaining: {len(final_reminders)}")
        for r in final_reminders:
            print(f"   - {r.title} ({r.status})")
        print()
        
        print("=" * 60)
        print("🎉 DATABASE POC DEMO COMPLETE!")
        print("=" * 60)
        print()
        print("Summary:")
        print(f"  • Created: 3 reminders")
        print(f"  • Read: Multiple queries")
        print(f"  • Updated: 1 reminder")
        print(f"  • Completed: 1 reminder")
        print(f"  • Deleted: 1 reminder")
        print(f"  • Final count: {len(final_reminders)} reminders")
        print()
        
    finally:
        db.close()


if __name__ == "__main__":
    demo()
