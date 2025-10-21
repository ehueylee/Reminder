"""
Integration tests for database operations.
Tests CRUD functionality for the Reminder model.
"""

import pytest
from datetime import datetime, timedelta
from database import SessionLocal, init_db
from models import Reminder
from crud import (
    create_reminder,
    get_reminder,
    get_reminders_by_user,
    get_reminders_by_tag,
    update_reminder,
    complete_reminder,
    delete_reminder,
    get_due_reminders
)


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session."""
    init_db()
    db = SessionLocal()
    
    # Clean up any existing test data
    db.query(Reminder).filter(Reminder.user_id == "test_user").delete()
    db.commit()
    
    yield db
    
    # Clean up after test
    db.query(Reminder).filter(Reminder.user_id == "test_user").delete()
    db.commit()
    db.close()


def test_create_reminder(db_session):
    """Test creating a reminder."""
    
    reminder = create_reminder(
        db=db_session,
        user_id="test_user",
        title="Test Reminder",
        due_date_time=datetime.utcnow() + timedelta(days=1),
        timezone="UTC",
        priority="high",
        tags=["test", "demo"]
    )
    
    assert reminder.id is not None
    assert reminder.user_id == "test_user"
    assert reminder.title == "Test Reminder"
    assert reminder.status == "active"
    assert reminder.priority == "high"
    assert reminder.created_at is not None
    assert reminder.tags == ["test", "demo"]
    
    print(f"✅ test_create_reminder passed - Created reminder: {reminder.id[:8]}")


def test_read_reminders(db_session):
    """Test reading reminders."""
    
    # Create test reminders
    for i in range(3):
        create_reminder(
            db=db_session,
            user_id="test_user",
            title=f"Reminder {i}",
            due_date_time=datetime.utcnow() + timedelta(days=i+1),
            timezone="UTC"
        )
    
    # Query reminders
    reminders = get_reminders_by_user(db_session, "test_user")
    
    assert len(reminders) == 3
    assert all(r.user_id == "test_user" for r in reminders)
    
    print(f"✅ test_read_reminders passed - Found {len(reminders)} reminders")


def test_read_reminders_by_status(db_session):
    """Test filtering reminders by status."""
    
    # Create active reminder
    create_reminder(
        db=db_session,
        user_id="test_user",
        title="Active Reminder",
        due_date_time=datetime.utcnow() + timedelta(days=1),
        timezone="UTC"
    )
    
    # Create and complete another reminder
    reminder2 = create_reminder(
        db=db_session,
        user_id="test_user",
        title="Completed Reminder",
        due_date_time=datetime.utcnow() + timedelta(days=2),
        timezone="UTC"
    )
    complete_reminder(db_session, reminder2.id)
    
    # Test filtering
    active = get_reminders_by_user(db_session, "test_user", status="active")
    completed = get_reminders_by_user(db_session, "test_user", status="completed")
    
    assert len(active) == 1
    assert len(completed) == 1
    assert active[0].status == "active"
    assert completed[0].status == "completed"
    
    print(f"✅ test_read_reminders_by_status passed - Active: {len(active)}, Completed: {len(completed)}")


def test_update_reminder(db_session):
    """Test updating a reminder."""
    
    reminder = create_reminder(
        db=db_session,
        user_id="test_user",
        title="Original Title",
        due_date_time=datetime.utcnow() + timedelta(days=1),
        timezone="UTC",
        priority="medium"
    )
    
    original_id = reminder.id
    
    # Update the reminder
    updated = update_reminder(
        db_session,
        reminder.id,
        title="Updated Title",
        priority="high",
        description="Added description"
    )
    
    assert updated is not None
    assert updated.id == original_id
    assert updated.title == "Updated Title"
    assert updated.priority == "high"
    assert updated.description == "Added description"
    
    print(f"✅ test_update_reminder passed - Updated reminder: {updated.title}")


def test_complete_reminder(db_session):
    """Test completing a reminder."""
    
    reminder = create_reminder(
        db=db_session,
        user_id="test_user",
        title="Task to Complete",
        due_date_time=datetime.utcnow() + timedelta(days=1),
        timezone="UTC"
    )
    
    # Complete the reminder
    completed = complete_reminder(db_session, reminder.id)
    
    assert completed is not None
    assert completed.status == "completed"
    assert completed.completed_at is not None
    assert completed.completed_at <= datetime.utcnow()
    
    print(f"✅ test_complete_reminder passed - Completed: {completed.title}")


def test_delete_reminder(db_session):
    """Test deleting a reminder."""
    
    reminder = create_reminder(
        db=db_session,
        user_id="test_user",
        title="To Be Deleted",
        due_date_time=datetime.utcnow() + timedelta(days=1),
        timezone="UTC"
    )
    
    reminder_id = reminder.id
    
    # Delete the reminder
    deleted = delete_reminder(db_session, reminder_id)
    
    assert deleted is True
    
    # Verify it's gone
    fetched = get_reminder(db_session, reminder_id)
    assert fetched is None
    
    print(f"✅ test_delete_reminder passed - Deleted reminder: {reminder_id[:8]}")


def test_get_specific_reminder(db_session):
    """Test getting a specific reminder by ID."""
    
    reminder = create_reminder(
        db=db_session,
        user_id="test_user",
        title="Specific Reminder",
        due_date_time=datetime.utcnow() + timedelta(days=1),
        timezone="UTC"
    )
    
    fetched = get_reminder(db_session, reminder.id)
    
    assert fetched is not None
    assert fetched.id == reminder.id
    assert fetched.title == reminder.title
    
    print(f"✅ test_get_specific_reminder passed - Retrieved: {fetched.title}")


def test_get_reminders_by_tag(db_session):
    """Test filtering reminders by tag."""
    
    create_reminder(
        db=db_session,
        user_id="test_user",
        title="Work Task",
        due_date_time=datetime.utcnow() + timedelta(days=1),
        timezone="UTC",
        tags=["work", "important"]
    )
    
    create_reminder(
        db=db_session,
        user_id="test_user",
        title="Personal Task",
        due_date_time=datetime.utcnow() + timedelta(days=2),
        timezone="UTC",
        tags=["personal"]
    )
    
    work_reminders = get_reminders_by_tag(db_session, "test_user", "work")
    personal_reminders = get_reminders_by_tag(db_session, "test_user", "personal")
    
    assert len(work_reminders) == 1
    assert len(personal_reminders) == 1
    assert "work" in work_reminders[0].tags
    
    print(f"✅ test_get_reminders_by_tag passed - Work: {len(work_reminders)}, Personal: {len(personal_reminders)}")


def test_get_due_reminders(db_session):
    """Test getting reminders due in a time range."""
    
    now = datetime.utcnow()
    
    # Create reminders at different times
    create_reminder(
        db=db_session,
        user_id="test_user",
        title="Due Soon",
        due_date_time=now + timedelta(minutes=30),
        timezone="UTC"
    )
    
    create_reminder(
        db=db_session,
        user_id="test_user",
        title="Due Later",
        due_date_time=now + timedelta(days=2),
        timezone="UTC"
    )
    
    # Get reminders due in the next hour
    soon = now + timedelta(hours=1)
    due_soon = get_due_reminders(db_session, now, soon)
    
    assert len(due_soon) == 1
    assert due_soon[0].title == "Due Soon"
    
    print(f"✅ test_get_due_reminders passed - Found {len(due_soon)} reminders due soon")


def test_reminder_with_recurrence(db_session):
    """Test creating a recurring reminder."""
    
    reminder = create_reminder(
        db=db_session,
        user_id="test_user",
        title="Weekly Meeting",
        due_date_time=datetime.utcnow() + timedelta(days=1),
        timezone="UTC",
        is_recurring=True,
        recurrence_pattern={
            "frequency": "weekly",
            "interval": 1,
            "days_of_week": [1, 3, 5]  # Mon, Wed, Fri
        }
    )
    
    assert reminder.is_recurring is True
    assert reminder.recurrence_pattern is not None
    assert reminder.recurrence_pattern["frequency"] == "weekly"
    assert reminder.recurrence_pattern["days_of_week"] == [1, 3, 5]
    
    print(f"✅ test_reminder_with_recurrence passed - Created recurring reminder")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
