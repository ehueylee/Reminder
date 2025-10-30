# 📋 Setup Wizard FAQ

Frequently asked questions about pre-requisites, setup process, self-hosting, and data storage.

---

## **📋 Pre-requisites for Setup Wizard**

**Hardware/Software:**
1. **Computer**: Windows, Mac, or Linux
2. **Python 3.11+**: Free programming language (like Microsoft Word for running code)
3. **Admin Access**: To install Python
4. **30 minutes**: For first-time setup
5. **Internet**: For downloading Python, the app, and initial setup

**Services Needed:**
1. **OpenAI API Key** (~$0.15/month):
   - Create account at https://platform.openai.com/signup
   - Add $5 credit to your account
   - Generate API key
   - This powers the natural language understanding ("Call dentist tomorrow" → structured reminder)

2. **Gmail Account** (Optional, for email notifications):
   - Your existing Gmail
   - Gmail App Password (16-character code from Google)

---

## **🔧 What Exactly Gets Setup?**

The wizard installs:

1. **Python** → The programming language that runs the app
2. **Reminder App Code** → Downloaded from GitHub to your Documents folder
3. **Dependencies** → Libraries the app needs (installed via `pip install -r requirements.txt`)
4. **Configuration File** (`.env`) → Your settings (API key, email, etc.)
5. **SQLite Database** → Created automatically as `reminders.db` in app folder

**After setup, you have:**
```
Documents/
└── Reminder/
    ├── main.py              (The app)
    ├── reminders.db         (YOUR DATA - this is where reminders are stored)
    ├── .env                 (Your secret settings)
    ├── static/              (Web interface files)
    └── venv/                (Python virtual environment)
```

---

## **🏠 What is "Self-Hosted"?**

**Self-hosted means:**
- The app runs **on your computer** (not in "the cloud")
- You start it with `python main.py`
- You access it at `http://localhost:8001` in your browser
- It's like running Microsoft Word or Excel on your computer

**Comparison:**

| Cloud (Railway) | Self-Hosted (Your Computer) |
|----------------|----------------------------|
| App runs on Railway's servers | App runs on YOUR computer |
| Access at https://web-production-129e7.up.railway.app | Access at http://localhost:8001 |
| Data stored on Railway's database | Data stored in YOUR Documents folder |
| Accessible from anywhere | Only accessible from your computer* |
| Always running | Only runs when you start it |
| Free tier ($5/month Railway credit) | $0 cost (just OpenAI ~$0.15/month) |

*Can be made accessible remotely with Tailscale/ngrok

---

## **💾 Where Are "Own Data" Stored?**

**Your data lives in TWO places:**

### 1. **Reminders Database** (Main Data)
- **File**: `Documents/Reminder/reminders.db`
- **What's Inside**: All your reminders, times, descriptions, user ID
- **Format**: SQLite database (single file)
- **Access**: Only you can access this file on your computer
- **Backup**: Copy this file to USB/cloud backup

**Example location:**
- Windows: `C:\Users\YourName\Documents\Reminder\reminders.db`
- Mac: `/Users/YourName/Documents/Reminder/reminders.db`

### 2. **Configuration File** (Settings)
- **File**: `Documents/Reminder/.env`
- **What's Inside**: Your OpenAI API key, email settings
- **Security**: Keep this file secret! Contains your API key

---

## **🔒 Privacy Guarantee**

**What STAYS on your computer:**
- ✅ Full reminder text/descriptions
- ✅ All timestamps and user IDs
- ✅ Complete history
- ✅ Database file (`reminders.db`)

**What LEAVES your computer:**
- 📤 Only the reminder text goes to OpenAI API (to parse "tomorrow at 2pm" → structured data)
- 📤 Email notifications (if you enable email reminders)

**What NEVER leaves your computer:**
- ❌ Your database file
- ❌ Your configuration/secrets
- ❌ Usage analytics (we don't track anything)

---

## **🎯 Quick Summary**

**Pre-requisites:**
- Computer + Python + OpenAI API key + 30 minutes

**Setup Process:**
1. Install Python (one-time)
2. Download app to Documents folder
3. Create `.env` config file with your API key
4. Run `pip install -r requirements.txt`
5. Start with `python main.py`

**Self-Hosted Means:**
- App runs on YOUR computer (not a website)
- Access at http://localhost:8001
- Like using Microsoft Word (local app, not cloud)

**Your Data Lives:**
- `Documents/Reminder/reminders.db` (SQLite database file)
- On YOUR hard drive, nobody else can access it
- Backup by copying this file to USB/cloud

**Cost:**
- Self-hosted: ~$0.15/month (OpenAI only)
- vs Railway cloud: $0/month (using free tier)
- vs ChatGPT Plus: $20/month (240x more expensive!)

---

## **🔗 Related Resources**

- [SELF_HOSTING_FOR_BEGINNERS.md](SELF_HOSTING_FOR_BEGINNERS.md) - Detailed step-by-step guide
- [Setup Wizard](static/setup-wizard.html) - Visual setup wizard at http://localhost:8001/ui/setup-wizard.html
- [README.md](README.md) - Main project documentation
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - For deploying to Railway/cloud
