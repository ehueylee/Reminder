"""
Recurring Reminder Service
Quick Win #3: Improved Recurring Reminders

Handles automatic creation of next occurrences for recurring reminders.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY

from models import Reminder
from database import SessionLocal
import crud

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecurringService:
    """
    Service for managing recurring reminders.
    
    Handles:
    - Parsing recurrence patterns
    - Calculating next occurrence dates
    - Auto-creating next reminders when current is completed
    - Skip/snooze functionality
    """
    
    @staticmethod
    def parse_recurrence_pattern(pattern: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse and validate a recurrence pattern.
        
        Expected pattern format:
        {
            "frequency": "daily" | "weekly" | "monthly" | "yearly",
            "interval": 1,  # every N days/weeks/months
            "days_of_week": [0, 1, 2, 3, 4],  # for weekly (0=Monday, 6=Sunday)
            "day_of_month": 15,  # for monthly
            "end_date": "2025-12-31",  # optional
            "count": 10  # optional, number of occurrences
        }
        
        Args:
            pattern: Recurrence pattern dictionary
            
        Returns:
            Normalized pattern or None if invalid
        """
        if not pattern or not isinstance(pattern, dict):
            return None
        
        frequency = pattern.get("frequency", "").lower()
        if frequency not in ["daily", "weekly", "monthly", "yearly"]:
            return None
        
        normalized = {
            "frequency": frequency,
            "interval": pattern.get("interval", 1),
        }
        
        # Add frequency-specific fields
        if frequency == "weekly" and "days_of_week" in pattern:
            normalized["days_of_week"] = pattern["days_of_week"]
        
        if frequency == "monthly" and "day_of_month" in pattern:
            normalized["day_of_month"] = pattern["day_of_month"]
        
        # Add optional fields
        if "end_date" in pattern:
            normalized["end_date"] = pattern["end_date"]
        
        if "count" in pattern:
            normalized["count"] = pattern["count"]
        
        return normalized
    
    @staticmethod
    def calculate_next_occurrence(
        current_date: datetime,
        pattern: Dict[str, Any]
    ) -> Optional[datetime]:
        """
        Calculate the next occurrence date based on recurrence pattern.
        
        Args:
            current_date: Current reminder date
            pattern: Recurrence pattern
            
        Returns:
            Next occurrence datetime or None if no more occurrences
        """
        if not pattern:
            return None
        
        frequency = pattern.get("frequency")
        interval = pattern.get("interval", 1)
        
        try:
            if frequency == "daily":
                return current_date + timedelta(days=interval)
            
            elif frequency == "weekly":
                # Simple weekly: add N weeks
                if "days_of_week" not in pattern:
                    return current_date + timedelta(weeks=interval)
                
                # Specific days of week
                days_of_week = pattern["days_of_week"]
                next_date = current_date + timedelta(days=1)
                
                # Find next valid day of week
                max_days = 7 * interval  # Don't search forever
                for _ in range(max_days):
                    if next_date.weekday() in days_of_week:
                        return next_date
                    next_date += timedelta(days=1)
                
                return None
            
            elif frequency == "monthly":
                # Add N months
                next_date = current_date + relativedelta(months=interval)
                
                # Specific day of month
                if "day_of_month" in pattern:
                    day = pattern["day_of_month"]
                    try:
                        next_date = next_date.replace(day=day)
                    except ValueError:
                        # Day doesn't exist in month (e.g., Feb 30)
                        # Use last day of month
                        next_date = next_date.replace(day=1) + relativedelta(months=1) - timedelta(days=1)
                
                return next_date
            
            elif frequency == "yearly":
                return current_date + relativedelta(years=interval)
            
            else:
                logger.warning(f"Unknown frequency: {frequency}")
                return None
                
        except Exception as e:
            logger.error(f"Error calculating next occurrence: {e}")
            return None
    
    @staticmethod
    def should_create_next_occurrence(reminder: Reminder) -> bool:
        """
        Check if a next occurrence should be created for this reminder.
        
        Args:
            reminder: Reminder instance
            
        Returns:
            True if next occurrence should be created
        """
        # Must be recurring
        if not reminder.is_recurring:
            return False
        
        # Must have a pattern
        if not reminder.recurrence_pattern:
            return False
        
        # Must be completed to trigger next
        if reminder.status != "completed":
            return False
        
        # Check if pattern has ended
        pattern = reminder.recurrence_pattern
        
        # Check end date
        if "end_date" in pattern:
            try:
                end_date = datetime.fromisoformat(pattern["end_date"])
                if datetime.now() >= end_date:
                    logger.info(f"Recurrence ended (end_date reached): {reminder.id}")
                    return False
            except (ValueError, TypeError):
                pass
        
        # Check count (requires tracking occurrence count - future enhancement)
        if "count" in pattern:
            # For now, always create (would need occurrence_number field)
            pass
        
        return True
    
    @staticmethod
    def create_next_occurrence(reminder: Reminder) -> Optional[Reminder]:
        """
        Create the next occurrence of a recurring reminder.
        
        Args:
            reminder: Completed recurring reminder
            
        Returns:
            New reminder instance or None if creation failed
        """
        if not RecurringService.should_create_next_occurrence(reminder):
            return None
        
        # Calculate next occurrence date
        next_date = RecurringService.calculate_next_occurrence(
            reminder.due_date_time,
            reminder.recurrence_pattern
        )
        
        if not next_date:
            logger.warning(f"Could not calculate next occurrence for: {reminder.id}")
            return None
        
        # Create new reminder
        db = SessionLocal()
        try:
            new_reminder = crud.create_reminder(
                db=db,
                user_id=reminder.user_id,
                title=reminder.title,
                description=reminder.description,
                due_date_time=next_date,
                timezone=reminder.timezone,
                priority=reminder.priority,
                tags=reminder.tags,
                is_recurring=True,
                recurrence_pattern=reminder.recurrence_pattern,
                location=reminder.location,
                natural_language_input=reminder.natural_language_input,
                parsed_by_ai=reminder.parsed_by_ai,
                ai_confidence=reminder.ai_confidence
            )
            
            logger.info(f"✅ Created next occurrence: {new_reminder.id} (from {reminder.id})")
            logger.info(f"   Next due: {next_date}")
            
            return new_reminder
            
        except Exception as e:
            logger.error(f"Failed to create next occurrence: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def skip_occurrence(reminder: Reminder) -> Optional[Reminder]:
        """
        Skip current occurrence and create next one without marking as completed.
        
        Args:
            reminder: Reminder to skip
            
        Returns:
            Next reminder instance or None
        """
        if not reminder.is_recurring:
            logger.warning(f"Cannot skip non-recurring reminder: {reminder.id}")
            return None
        
        # Calculate next occurrence
        next_date = RecurringService.calculate_next_occurrence(
            reminder.due_date_time,
            reminder.recurrence_pattern
        )
        
        if not next_date:
            return None
        
        # Mark current as cancelled
        db = SessionLocal()
        try:
            crud.update_reminder(db, reminder.id, status="cancelled")
            
            # Create next occurrence
            new_reminder = crud.create_reminder(
                db=db,
                user_id=reminder.user_id,
                title=reminder.title,
                description=reminder.description,
                due_date_time=next_date,
                timezone=reminder.timezone,
                priority=reminder.priority,
                tags=reminder.tags,
                is_recurring=True,
                recurrence_pattern=reminder.recurrence_pattern,
                location=reminder.location,
                natural_language_input=reminder.natural_language_input,
                parsed_by_ai=reminder.parsed_by_ai,
                ai_confidence=reminder.ai_confidence
            )
            
            logger.info(f"⏭️ Skipped occurrence {reminder.id}, created {new_reminder.id}")
            return new_reminder
            
        except Exception as e:
            logger.error(f"Failed to skip occurrence: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def snooze_reminder(reminder: Reminder, snooze_minutes: int = 30) -> Optional[Reminder]:
        """
        Snooze a reminder for specified minutes.
        
        Args:
            reminder: Reminder to snooze
            snooze_minutes: Minutes to snooze
            
        Returns:
            Updated reminder with new due date
        """
        new_due_date = datetime.now() + timedelta(minutes=snooze_minutes)
        
        db = SessionLocal()
        try:
            updated = crud.update_reminder(
                db,
                reminder.id,
                due_date_time=new_due_date
            )
            
            logger.info(f"⏰ Snoozed reminder {reminder.id} for {snooze_minutes} minutes")
            logger.info(f"   New due: {new_due_date}")
            
            return updated
            
        except Exception as e:
            logger.error(f"Failed to snooze reminder: {e}")
            return None
        finally:
            db.close()


# Global service instance
_recurring_service: Optional[RecurringService] = None


def get_recurring_service() -> RecurringService:
    """
    Get or create the global recurring service instance.
    
    Returns:
        RecurringService instance
    """
    global _recurring_service
    if _recurring_service is None:
        _recurring_service = RecurringService()
    return _recurring_service


def on_reminder_completed(reminder: Reminder):
    """
    Hook called when a reminder is completed.
    Creates next occurrence for recurring reminders.
    
    Args:
        reminder: Completed reminder
    """
    service = get_recurring_service()
    service.create_next_occurrence(reminder)
