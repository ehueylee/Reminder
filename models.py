"""
Database models for the Reminder application.
Defines the Reminder table structure using SQLAlchemy ORM.
"""

from sqlalchemy import Column, String, DateTime, Boolean, JSON, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class Reminder(Base):
    """Reminder model representing a user's reminder/task."""
    
    __tablename__ = "reminders"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # User information
    user_id = Column(String, nullable=False, index=True)
    
    # Core reminder fields
    title = Column(String(500), nullable=False)
    description = Column(String, nullable=True)
    due_date_time = Column(DateTime, nullable=False, index=True)
    timezone = Column(String(50), nullable=False, default="UTC")
    
    # Recurrence settings
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(JSON, nullable=True)
    
    # Status tracking
    status = Column(String(20), default="pending", index=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Metadata
    priority = Column(String(20), default="medium")
    tags = Column(JSON, default=list)
    location = Column(String(500), nullable=True)
    
    # AI processing info
    natural_language_input = Column(String, nullable=True)
    parsed_by_ai = Column(Boolean, default=False)
    ai_confidence = Column(Integer, nullable=True)  # Stored as percentage (0-100)
    
    # Notification tracking
    last_notified_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Reminder(id={self.id[:8]}, title='{self.title}', due={self.due_date_time})>"
