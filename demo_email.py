"""
Demo script for testing email notifications
Quick Win #1: Email Notifications
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from database import SessionLocal, init_db
import crud
from email_service import get_email_service, email_notification_handler

# Initialize database
init_db()

print("\n" + "="*80)
print("📧 Email Notification Demo")
print("="*80)

# Check email configuration
email_service = get_email_service()

print(f"\n📋 Email Configuration:")
print(f"  SMTP Host: {email_service.smtp_host}")
print(f"  SMTP Port: {email_service.smtp_port}")
print(f"  From Email: {email_service.from_email}")
print(f"  From Name: {email_service.from_name}")
print(f"  Configured: {'✅ Yes' if email_service.is_configured else '❌ No'}")

if not email_service.is_configured:
    print("\n❌ Email is not configured!")
    print("\nTo configure email notifications:")
    print("1. Copy .env.example to .env")
    print("2. Fill in your SMTP settings")
    print("3. For Gmail:")
    print("   - Enable 2FA: https://myaccount.google.com/security")
    print("   - Create app password: https://myaccount.google.com/apppasswords")
    print("4. Restart this script")
    print("\nSee README_EMAIL_NOTIFICATIONS.md for detailed instructions.")
    exit(1)

# Get recipient email
recipient_email = os.getenv("DEFAULT_NOTIFICATION_EMAIL", "")
if not recipient_email:
    recipient_email = input("\nEnter recipient email address: ").strip()

print(f"\n📨 Will send test email to: {recipient_email}")

# Create a test reminder
print("\n📝 Creating test reminder...")
db = SessionLocal()
try:
    now = datetime.now()
    reminder = crud.create_reminder(
        db=db,
        user_id="email_demo_user",
        title="Test Email Notification",
        description="This is a test reminder to verify email notifications are working correctly. If you receive this, your email setup is successful!",
        due_date_time=now + timedelta(minutes=1),
        timezone="America/New_York",
        priority="high",
        tags=["test", "email", "demo"],
        location="Your Inbox",
        is_recurring=False,
        natural_language_input="Test email notification"
    )
    print(f"✅ Created reminder: {reminder.title} (ID: {reminder.id})")
    print(f"   Due: {reminder.due_date_time}")
    print(f"   Priority: {reminder.priority}")

finally:
    db.close()

# Send test email
print("\n📧 Sending test email...")
print("   This may take a few seconds...")

try:
    success = email_service.send_reminder_notification(
        reminder=reminder,
        to_email=recipient_email
    )
    
    if success:
        print("\n✅ Email sent successfully!")
        print(f"\n📬 Check your inbox: {recipient_email}")
        print("\nWhat to look for:")
        print("  - Subject: '❗ Reminder: Test Email Notification'")
        print("  - Beautiful HTML email with gradient header")
        print("  - Color-coded priority badge (orange for high)")
        print("  - All reminder details included")
        print("\nIf you don't see it:")
        print("  1. Check your spam/junk folder")
        print("  2. Wait a minute (email delivery can be delayed)")
        print("  3. Check the SMTP settings in .env file")
    else:
        print("\n❌ Failed to send email")
        print("\nTroubleshooting:")
        print("  1. Check SMTP credentials in .env")
        print("  2. For Gmail: Verify app password (not regular password)")
        print("  3. Check firewall/antivirus settings")
        print("  4. Try a different SMTP port (587 or 465)")
        print("\nSee README_EMAIL_NOTIFICATIONS.md for detailed troubleshooting.")
        
except Exception as e:
    print(f"\n❌ Error sending email: {e}")
    print("\nCommon issues:")
    print("  - Gmail: Need to use app password, not regular password")
    print("  - Authentication failed: Check username/password")
    print("  - Connection timeout: Check host/port")
    print("\nSee README_EMAIL_NOTIFICATIONS.md for solutions.")

print("\n" + "="*80)
print("\n💡 Next Steps:")
print("  1. Check your email inbox")
print("  2. Configure DEFAULT_NOTIFICATION_EMAIL in .env")
print("  3. Restart the server to enable automatic email notifications")
print("  4. Run demo_scheduler.py to see emails in action!")
print("\n" + "="*80 + "\n")
