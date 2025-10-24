# Quick Win #1: Email Notifications - Setup Guide

## Overview

Email notifications allow you to receive reminder alerts via email when reminders are due. This feature integrates seamlessly with the existing scheduler.

## Features

✅ **Beautiful HTML Emails** - Responsive design with color-coded priorities  
✅ **Plain Text Fallback** - Works with all email clients  
✅ **Priority Indicators** - Visual cues for urgent/high/medium/low priorities  
✅ **Complete Reminder Details** - Title, description, due date, location, tags  
✅ **SMTP Support** - Works with Gmail, Outlook, or any SMTP server  
✅ **Easy Configuration** - Simple environment variable setup  

## Setup Instructions

### Option 1: Gmail with App Password (Recommended)

1. **Enable 2-Factor Authentication** on your Google account
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Create an App Password**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Name it "Reminder App"
   - Copy the 16-character password

3. **Configure Environment Variables**

Add to your `.env` file:

```bash
# Email Configuration (Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your.email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
FROM_EMAIL=your.email@gmail.com
FROM_NAME=Reminder App

# Default notification recipient
DEFAULT_NOTIFICATION_EMAIL=your.email@gmail.com
```

### Option 2: Other SMTP Providers

#### Outlook/Hotmail
```bash
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your.email@outlook.com
SMTP_PASSWORD=your-password
```

#### Yahoo Mail
```bash
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME=your.email@yahoo.com
SMTP_PASSWORD=your-app-password
```

#### Custom SMTP Server
```bash
SMTP_HOST=smtp.yourdomain.com
SMTP_PORT=587  # or 465 for SSL
SMTP_USERNAME=your-username
SMTP_PASSWORD=your-password
```

## Usage

### Automatic Integration

Email notifications are automatically integrated with the scheduler. Once configured, they work alongside other notification methods.

### Enable Email Notifications

Update your scheduler to include the email handler:

```python
from email_service import email_notification_handler
from scheduler import get_scheduler

# Add email handler
scheduler = get_scheduler()
scheduler.add_notification_handler(email_notification_handler)
```

Or modify `main.py` to include email notifications by default.

### Manual Test

Test email sending:

```python
from email_service import get_email_service
from database import SessionLocal
import crud

# Get email service
email_service = get_email_service()

# Get a reminder
db = SessionLocal()
reminder = crud.get_reminder(db, "your-reminder-id")

# Send test email
email_service.send_reminder_notification(
    reminder=reminder,
    to_email="your.email@gmail.com"
)
```

## Email Template Preview

### Subject Line
```
🚨 URGENT: Reminder: Team Meeting  # For urgent priority
Reminder: Buy groceries              # For other priorities
```

### Email Content

The email includes:
- **Header** - Gradient purple background with priority emoji
- **Title** - Large, bold reminder title
- **Due Date** - Highlighted yellow box with date/time
- **Description** - Clear, readable text
- **Metadata** - Priority badge, location, tags
- **Footer** - Reminder ID and creation date

### Priority Colors

- 🚨 **Urgent**: Red badge
- ❗ **High**: Orange badge
- ⚠️ **Medium**: Yellow badge
- ℹ️ **Low**: Blue badge

## Configuration Options

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SMTP_HOST` | Yes | `smtp.gmail.com` | SMTP server hostname |
| `SMTP_PORT` | No | `587` | SMTP server port (587=TLS, 465=SSL) |
| `SMTP_USERNAME` | Yes | - | SMTP username (usually your email) |
| `SMTP_PASSWORD` | Yes | - | SMTP password or app password |
| `FROM_EMAIL` | No | `SMTP_USERNAME` | Sender email address |
| `FROM_NAME` | No | `Reminder App` | Sender display name |
| `DEFAULT_NOTIFICATION_EMAIL` | No | - | Default recipient for notifications |

### Security Notes

⚠️ **Never commit `.env` file to git**  
⚠️ **Use app passwords, not your main password**  
⚠️ **Keep SMTP credentials secure**  

## Testing

### Test Email Configuration

```bash
# Create a test script
python -c "
from email_service import get_email_service
service = get_email_service()
print(f'Email configured: {service.is_configured}')
print(f'SMTP Host: {service.smtp_host}')
print(f'From: {service.from_email}')
"
```

### Send Test Reminder Email

Use the scheduler demo:

```bash
# Run demo with email notifications
python demo_scheduler.py
# Choose option 3 (1-minute test)
```

Watch your inbox for reminder notifications!

## Troubleshooting

### "Email service not configured"

**Cause**: SMTP environment variables not set

**Solution**: 
1. Create/update `.env` file with SMTP settings
2. Restart the server
3. Verify with: `python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('SMTP_HOST'))"`

### "Authentication failed"

**Cause**: Invalid credentials or app password required

**Solution**:
1. For Gmail: Use app password, not regular password
2. Verify credentials are correct
3. Check if 2FA is enabled (required for Gmail app passwords)

### "Connection timeout"

**Cause**: Wrong SMTP host or port

**Solution**:
1. Verify SMTP_HOST is correct
2. Try port 587 (TLS) or 465 (SSL)
3. Check firewall settings

### "No recipient email configured"

**Cause**: DEFAULT_NOTIFICATION_EMAIL not set

**Solution**:
Add to `.env`:
```bash
DEFAULT_NOTIFICATION_EMAIL=your.email@example.com
```

### Emails go to spam

**Cause**: SPF/DKIM not configured

**Solution**:
1. Check spam folder first
2. Mark as "Not Spam"
3. For production: Configure SPF/DKIM records
4. Consider using SendGrid or Mailgun for better deliverability

## Advanced Usage

### Per-User Email Addresses

To send emails to different users (future enhancement):

```python
# Extend the handler
def email_notification_handler_per_user(reminder, message):
    # Get user's email from database
    user_email = get_user_email(reminder.user_id)
    email_notification_handler(reminder, message, to_email=user_email)
```

### Custom Email Templates

Modify `email_service.py` to customize the HTML template:

```python
# Edit the format_reminder_email method
def format_reminder_email(self, reminder: Reminder) -> tuple[str, str]:
    # Your custom HTML here
    html_content = f"""
    <!DOCTYPE html>
    <html>
    ...
    </html>
    """
    return html_content, text_content
```

### Multiple Recipients

```python
# Send to multiple recipients
recipients = ["user1@example.com", "user2@example.com"]
for recipient in recipients:
    email_service.send_reminder_notification(reminder, recipient)
```

## Performance Considerations

- **Rate Limiting**: Most SMTP servers limit sending rate (e.g., Gmail: 500/day)
- **Async Sending**: Current implementation is synchronous; consider async for high volume
- **Queue System**: For production, use Celery or similar for background sending
- **Retry Logic**: Add retry mechanism for failed sends

## Next Steps

1. ✅ Email notifications working
2. 🔄 Add SMS notifications (Quick Win #2)
3. 🔄 Add per-user email preferences
4. 🔄 Add email digest (daily/weekly summary)
5. 🔄 Add "mark as done" button in email

## Cost

**SMTP Email**: FREE (using your existing email account)

Limits:
- Gmail: 500 emails/day (free)
- Outlook: 300 emails/day (free)

For higher volume, consider:
- SendGrid: 100 emails/day (free tier)
- Mailgun: 100 emails/day (free tier)
- AWS SES: $0.10 per 1,000 emails

## Support

If you encounter issues:
1. Check the logs for error messages
2. Verify all environment variables are set
3. Test with a simple Python script first
4. Check your email provider's SMTP documentation

---

**Congratulations! You now have email notifications for your reminders!** 📧🎉
