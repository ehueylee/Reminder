"""
Background Scheduler Service for Reminder Application
Phase 1.5: Background Scheduler implementation
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from typing import List, Optional, Callable
import logging

from database import SessionLocal
import crud
from models import Reminder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ReminderScheduler:
    """
    Background scheduler for checking due reminders and sending notifications.
    
    Features:
    - Checks for due reminders every minute
    - Sends notifications via configured channels
    - Supports multiple notification methods (console, file, webhook)
    - Handles recurring reminders
    """
    
    def __init__(self):
        """Initialize the scheduler."""
        self.scheduler = BackgroundScheduler()
        self.notification_handlers: List[Callable] = []
        self.is_running = False
        
    def add_notification_handler(self, handler: Callable):
        """
        Add a notification handler function.
        
        Args:
            handler: Function that takes (reminder, message) as arguments
        """
        self.notification_handlers.append(handler)
        logger.info(f"Added notification handler: {handler.__name__}")
        
    def check_due_reminders(self):
        """
        Check for reminders that are due and send notifications.
        
        This method:
        1. Queries the database for reminders due in the next 5 minutes
        2. Filters out already-notified reminders
        3. Sends notifications via registered handlers
        """
        db = SessionLocal()
        try:
            # Get current time and 5-minute window
            now = datetime.now()
            future_window = now + timedelta(minutes=5)
            
            # Query due reminders (pending status, due within 5 minutes)
            due_reminders = crud.get_due_reminders(
                db=db,
                start_time=now,
                end_time=future_window,
                status="pending"
            )
            
            if due_reminders:
                logger.info(f"Found {len(due_reminders)} due reminder(s)")
                
                for reminder in due_reminders:
                    self._process_reminder(reminder)
            
        except Exception as e:
            logger.error(f"Error checking due reminders: {e}")
        finally:
            db.close()
    
    def _process_reminder(self, reminder: Reminder):
        """
        Process a single due reminder and send notifications.
        
        Args:
            reminder: The Reminder object to process
        """
        try:
            # Format notification message
            message = self._format_notification_message(reminder)
            
            # Send via all registered handlers
            if self.notification_handlers:
                for handler in self.notification_handlers:
                    try:
                        handler(reminder, message)
                    except Exception as e:
                        logger.error(f"Notification handler {handler.__name__} failed: {e}")
            else:
                # Default: log to console
                logger.info(f"📢 REMINDER: {message}")
                
        except Exception as e:
            logger.error(f"Error processing reminder {reminder.id}: {e}")
    
    def _format_notification_message(self, reminder: Reminder) -> str:
        """
        Format a reminder into a notification message.
        
        Args:
            reminder: The Reminder object
            
        Returns:
            Formatted notification string
        """
        due_str = reminder.due_date_time.strftime("%Y-%m-%d %H:%M") if reminder.due_date_time else "No due date"
        
        message_parts = [
            f"🔔 REMINDER: {reminder.title}",
            f"📅 Due: {due_str}",
        ]
        
        if reminder.description:
            message_parts.append(f"📝 {reminder.description}")
            
        if reminder.priority == "high":
            message_parts.insert(0, "🚨 HIGH PRIORITY")
            
        if reminder.location:
            message_parts.append(f"📍 Location: {reminder.location}")
            
        if reminder.tags:
            message_parts.append(f"🏷️ Tags: {', '.join(reminder.tags)}")
            
        return " | ".join(message_parts)
    
    def start(self, check_interval_minutes: int = 1):
        """
        Start the scheduler.
        
        Args:
            check_interval_minutes: How often to check for due reminders (default: 1 minute)
        """
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        # Add job to check reminders every X minutes
        self.scheduler.add_job(
            func=self.check_due_reminders,
            trigger=CronTrigger(minute=f'*/{check_interval_minutes}'),
            id='check_reminders',
            name='Check Due Reminders',
            replace_existing=True
        )
        
        # Start the scheduler
        self.scheduler.start()
        self.is_running = True
        logger.info(f"✅ Scheduler started (checking every {check_interval_minutes} minute(s))")
        
    def stop(self):
        """Stop the scheduler."""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
        
        self.scheduler.shutdown()
        self.is_running = False
        logger.info("🛑 Scheduler stopped")
    
    def get_scheduled_jobs(self):
        """Get list of scheduled jobs."""
        return self.scheduler.get_jobs()


# Notification Handlers

def console_notification_handler(reminder: Reminder, message: str):
    """
    Print notification to console.
    
    Args:
        reminder: The Reminder object
        message: Formatted notification message
    """
    print("\n" + "="*80)
    print(message)
    print("="*80 + "\n")


def file_notification_handler(reminder: Reminder, message: str, filepath: str = "notifications.log"):
    """
    Append notification to a file.
    
    Args:
        reminder: The Reminder object
        message: Formatted notification message
        filepath: Path to log file (default: notifications.log)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def webhook_notification_handler(reminder: Reminder, message: str, webhook_url: str):
    """
    Send notification to a webhook endpoint.
    
    Args:
        reminder: The Reminder object
        message: Formatted notification message
        webhook_url: URL to POST notification to
    """
    import requests
    
    payload = {
        "reminder_id": reminder.id,
        "title": reminder.title,
        "description": reminder.description,
        "due_date_time": reminder.due_date_time.isoformat() if reminder.due_date_time else None,
        "priority": reminder.priority,
        "tags": reminder.tags,
        "location": reminder.location,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=5)
        response.raise_for_status()
        logger.info(f"Webhook notification sent for reminder {reminder.id}")
    except Exception as e:
        logger.error(f"Failed to send webhook notification: {e}")


# Global scheduler instance
_scheduler_instance: Optional[ReminderScheduler] = None


def get_scheduler() -> ReminderScheduler:
    """
    Get or create the global scheduler instance.
    
    Returns:
        ReminderScheduler instance
    """
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = ReminderScheduler()
    return _scheduler_instance


def setup_default_scheduler(check_interval_minutes: int = 1, enable_email: bool = True) -> ReminderScheduler:
    """
    Set up scheduler with default notification handlers.
    
    Args:
        check_interval_minutes: How often to check for due reminders
        enable_email: Enable email notifications (requires SMTP configuration)
        
    Returns:
        Configured ReminderScheduler instance
    """
    scheduler = get_scheduler()
    
    # Add console notification handler
    scheduler.add_notification_handler(console_notification_handler)
    
    # Add email notification handler if enabled
    if enable_email:
        try:
            from email_service import email_notification_handler, get_email_service
            
            # Check if email is configured
            email_service = get_email_service()
            if email_service.is_configured:
                scheduler.add_notification_handler(email_notification_handler)
                logger.info("📧 Email notifications enabled")
            else:
                logger.info("📧 Email notifications disabled (SMTP not configured)")
        except ImportError:
            logger.warning("📧 Email service not available")
    
    # Start the scheduler
    scheduler.start(check_interval_minutes)
    
    return scheduler
