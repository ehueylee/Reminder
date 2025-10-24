"""
Email Notification Service for Reminder Application
Quick Win #1: Email Notifications

Supports both SMTP and Gmail with app passwords.
"""

import os
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime
import logging

from models import Reminder

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailService:
    """
    Email notification service using SMTP.
    
    Supports:
    - Gmail with app passwords
    - Generic SMTP servers
    - HTML and plain text emails
    - Async sending (optional)
    """
    
    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_username: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ):
        """
        Initialize email service with SMTP configuration.
        
        Args:
            smtp_host: SMTP server hostname (e.g., smtp.gmail.com)
            smtp_port: SMTP server port (587 for TLS, 465 for SSL)
            smtp_username: SMTP username (usually your email)
            smtp_password: SMTP password or app password
            from_email: Sender email address
            from_name: Sender display name
        """
        # Load from environment variables if not provided
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = smtp_username or os.getenv("SMTP_USERNAME", "")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD", "")
        self.from_email = from_email or os.getenv("FROM_EMAIL", self.smtp_username)
        self.from_name = from_name or os.getenv("FROM_NAME", "Reminder App")
        
        # Validate configuration
        self.is_configured = bool(
            self.smtp_host and 
            self.smtp_username and 
            self.smtp_password
        )
        
        if not self.is_configured:
            logger.warning("Email service not configured. Set SMTP_* environment variables.")
    
    def format_reminder_email(self, reminder: Reminder) -> tuple[str, str]:
        """
        Format reminder into HTML and plain text email content.
        
        Args:
            reminder: Reminder object
            
        Returns:
            Tuple of (html_content, text_content)
        """
        # Format due date
        due_str = reminder.due_date_time.strftime("%A, %B %d, %Y at %I:%M %p") if reminder.due_date_time else "No due date"
        
        # Priority indicator
        priority_emoji = {
            "urgent": "🚨",
            "high": "❗",
            "medium": "⚠️",
            "low": "ℹ️"
        }.get(reminder.priority, "📌")
        
        # Plain text version
        text_content = f"""
{priority_emoji} REMINDER: {reminder.title}

Due: {due_str}

{reminder.description or 'No description'}

{'Location: ' + reminder.location if reminder.location else ''}
{'Tags: ' + ', '.join(reminder.tags) if reminder.tags else ''}

Priority: {reminder.priority.upper()}
Status: {reminder.status.upper()}

---
Reminder ID: {reminder.id}
Created: {reminder.created_at.strftime("%Y-%m-%d %H:%M")}
"""
        
        # HTML version
        priority_color = {
            "urgent": "#dc2626",
            "high": "#ea580c",
            "medium": "#ca8a04",
            "low": "#0891b2"
        }.get(reminder.priority, "#6b7280")
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px 10px 0 0;
            text-align: center;
        }}
        .content {{
            background: #f9fafb;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }}
        .reminder-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .title {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #1f2937;
        }}
        .due-date {{
            font-size: 18px;
            color: #4b5563;
            margin-bottom: 15px;
            padding: 10px;
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            border-radius: 4px;
        }}
        .description {{
            font-size: 16px;
            color: #6b7280;
            margin-bottom: 15px;
            line-height: 1.8;
        }}
        .meta {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #e5e7eb;
        }}
        .meta-item {{
            font-size: 14px;
            color: #6b7280;
        }}
        .priority {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
            background: {priority_color};
            color: white;
        }}
        .tag {{
            display: inline-block;
            padding: 4px 10px;
            background: #e0e7ff;
            color: #4338ca;
            border-radius: 12px;
            font-size: 12px;
            margin-right: 5px;
        }}
        .footer {{
            text-align: center;
            margin-top: 20px;
            font-size: 12px;
            color: #9ca3af;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{priority_emoji} Reminder Notification</h1>
    </div>
    <div class="content">
        <div class="reminder-card">
            <div class="title">{reminder.title}</div>
            
            <div class="due-date">
                📅 Due: {due_str}
            </div>
            
            {f'<div class="description">{reminder.description}</div>' if reminder.description else ''}
            
            <div class="meta">
                <div class="meta-item">
                    <strong>Priority:</strong> <span class="priority">{reminder.priority}</span>
                </div>
                
                {f'<div class="meta-item"><strong>📍 Location:</strong> {reminder.location}</div>' if reminder.location else ''}
                
                {f'''<div class="meta-item">
                    <strong>🏷️ Tags:</strong> 
                    {''.join(f'<span class="tag">{tag}</span>' for tag in reminder.tags)}
                </div>''' if reminder.tags else ''}
                
                <div class="meta-item">
                    <strong>Status:</strong> {reminder.status.title()}
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Reminder ID: {reminder.id}</p>
            <p>Created: {reminder.created_at.strftime("%Y-%m-%d %H:%M")}</p>
            <p>This is an automated reminder from your Reminder App</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html_content, text_content
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str
    ) -> bool:
        """
        Send email using SMTP.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text email body
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.is_configured:
            logger.error("Email service not configured")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Attach parts
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()  # Enable TLS
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.from_email, to_email, msg.as_string())
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def send_reminder_notification(self, reminder: Reminder, to_email: str) -> bool:
        """
        Send reminder notification email.
        
        Args:
            reminder: Reminder object
            to_email: Recipient email address
            
        Returns:
            True if sent successfully, False otherwise
        """
        # Format email content
        html_content, text_content = self.format_reminder_email(reminder)
        
        # Create subject
        priority_prefix = "🚨 URGENT: " if reminder.priority == "urgent" else ""
        subject = f"{priority_prefix}Reminder: {reminder.title}"
        
        # Send email
        return self.send_email(to_email, subject, html_content, text_content)


# Global email service instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """
    Get or create the global email service instance.
    
    Returns:
        EmailService instance
    """
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service


# Notification handler for scheduler integration
def email_notification_handler(reminder: Reminder, message: str, to_email: Optional[str] = None):
    """
    Email notification handler for scheduler.
    
    Args:
        reminder: Reminder object
        message: Formatted notification message (not used, we create our own)
        to_email: Recipient email address (defaults to env variable)
    """
    email_service = get_email_service()
    
    if not email_service.is_configured:
        logger.warning("Email notifications disabled - SMTP not configured")
        return
    
    # Get recipient email
    recipient = to_email or os.getenv("DEFAULT_NOTIFICATION_EMAIL", "")
    
    if not recipient:
        logger.warning("No recipient email configured for notification")
        return
    
    # Send notification
    success = email_service.send_reminder_notification(reminder, recipient)
    
    if success:
        logger.info(f"✅ Email notification sent for reminder: {reminder.title}")
    else:
        logger.error(f"❌ Failed to send email notification for reminder: {reminder.title}")
