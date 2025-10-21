"""
CRUD operations for Reminder model.
Provides functions to Create, Read, Update, and Delete reminders.
"""

from sqlalchemy.orm import Session
from models import Reminder
from datetime import datetime
from typing import List, Optional


def create_reminder(
    db: Session,
    user_id: str,
    title: str,
    due_date_time: datetime,
    timezone: str = "UTC",
    description: Optional[str] = None,
    priority: str = "medium",
    tags: Optional[List[str]] = None,
    is_recurring: bool = False,
    recurrence_pattern: Optional[dict] = None,
    natural_language_input: Optional[str] = None,
    parsed_by_ai: bool = False
) -> Reminder:
    """Create a new reminder."""
    
    reminder = Reminder(
        user_id=user_id,
        title=title,
        description=description,
        due_date_time=due_date_time,
        timezone=timezone,
        priority=priority,
        tags=tags or [],
        is_recurring=is_recurring,
        recurrence_pattern=recurrence_pattern,
        natural_language_input=natural_language_input,
        parsed_by_ai=parsed_by_ai
    )
    
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    
    return reminder


def get_reminder(db: Session, reminder_id: str) -> Optional[Reminder]:
    """Get a reminder by ID."""
    return db.query(Reminder).filter(Reminder.id == reminder_id).first()


def get_reminders_by_user(
    db: Session,
    user_id: str,
    status: Optional[str] = None,
    limit: int = 100
) -> List[Reminder]:
    """Get all reminders for a user, optionally filtered by status."""
    
    query = db.query(Reminder).filter(Reminder.user_id == user_id)
    
    if status:
        query = query.filter(Reminder.status == status)
    
    return query.order_by(Reminder.due_date_time).limit(limit).all()


def get_reminders_by_tag(
    db: Session,
    user_id: str,
    tag: str
) -> List[Reminder]:
    """Get reminders by tag."""
    
    # For SQLite with JSON, we need to use different approach
    # This is a simple implementation; for production, consider JSON functions
    reminders = db.query(Reminder).filter(Reminder.user_id == user_id).all()
    return [r for r in reminders if tag in (r.tags or [])]


def update_reminder(
    db: Session,
    reminder_id: str,
    **kwargs
) -> Optional[Reminder]:
    """Update a reminder with the provided fields."""
    
    reminder = get_reminder(db, reminder_id)
    
    if not reminder:
        return None
    
    # Update fields
    for key, value in kwargs.items():
        if hasattr(reminder, key):
            setattr(reminder, key, value)
    
    reminder.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(reminder)
    
    return reminder


def complete_reminder(db: Session, reminder_id: str) -> Optional[Reminder]:
    """Mark a reminder as completed."""
    
    reminder = get_reminder(db, reminder_id)
    
    if not reminder:
        return None
    
    reminder.status = "completed"
    reminder.completed_at = datetime.utcnow()
    reminder.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(reminder)
    
    return reminder


def delete_reminder(db: Session, reminder_id: str) -> bool:
    """Delete a reminder."""
    
    reminder = get_reminder(db, reminder_id)
    
    if not reminder:
        return False
    
    db.delete(reminder)
    db.commit()
    
    return True


def get_due_reminders(
    db: Session,
    start_time: datetime,
    end_time: datetime,
    status: str = "active"
) -> List[Reminder]:
    """Get reminders due within a time range."""
    
    return db.query(Reminder).filter(
        Reminder.status == status,
        Reminder.due_date_time >= start_time,
        Reminder.due_date_time <= end_time
    ).all()
