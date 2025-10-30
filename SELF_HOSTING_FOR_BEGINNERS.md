# 🏠 Self-Hosting Guide for Non-Technical Users

**Own your data. No coding required.**

This guide helps you run the Smart Reminder App on your own computer, so your reminders stay private and under your control.

## 🎯 What is Self-Hosting?

**Instead of using a website someone else controls:**
- ✅ You run the app on YOUR computer
- ✅ Your reminders are stored on YOUR hard drive
- ✅ Nobody else can see your data
- ✅ No monthly fees
- ✅ Works even without internet (after setup)

**Think of it like:** Using Microsoft Word on your computer instead of Google Docs online.

---

## 📋 Prerequisites

You need:
- ✅ Windows, Mac, or Linux computer
- ✅ 30 minutes of time
- ✅ Administrator access to your computer
- ✅ OpenAI API key (costs ~$0.15/month for typical use)

**No coding experience required!** Just copy-paste the commands.

---

## 🚀 Quick Start (5 Steps)

### Step 1: Install Python (5 minutes)

Python is like Microsoft Word for running code. Free and safe.

**Windows:**
1. Visit: https://www.python.org/downloads/
2. Click big yellow "Download Python 3.11" button
3. Run the installer
4. ⚠️ **IMPORTANT:** Check "Add Python to PATH" box
5. Click "Install Now"
6. Wait for installation to complete

**Mac:**
1. Open Terminal (search "Terminal" in Spotlight)
2. Install Homebrew (copy-paste this):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
3. Install Python:
   ```bash
   brew install python@3.11
   ```

**Verify Installation:**
Open Command Prompt (Windows) or Terminal (Mac) and type:
```bash
python --version
```
You should see: `Python 3.11.x`

---

### Step 2: Download the App (2 minutes)

**Option A: Easy Download (No Git)**
1. Visit: https://github.com/ehueylee/Reminder
2. Click green "Code" button
3. Click "Download ZIP"
4. Extract ZIP to your Documents folder
5. Rename folder to "Reminder"

**Option B: Using Git (Recommended)**
1. Install Git: https://git-scm.com/downloads
2. Open Command Prompt/Terminal
3. Navigate to Documents:
   ```bash
   cd Documents
   ```
4. Clone repository:
   ```bash
   git clone https://github.com/ehueylee/Reminder.git
   cd Reminder
   ```

---

### Step 3: Get OpenAI API Key (3 minutes)

OpenAI powers the natural language understanding.

1. Visit: https://platform.openai.com/signup
2. Create free account (email + password)
3. Add payment method:
   - Click "Settings" → "Billing"
   - Add credit card
   - Add $5 credit (will last months)
4. Create API key:
   - Click "API Keys" in left menu
   - Click "Create new secret key"
   - **IMPORTANT:** Copy the key (starts with `sk-`)
   - Save it somewhere safe (you can't see it again!)

**Cost:** ~$0.15/month for typical use (50 reminders)

---

### Step 4: Configure the App (5 minutes)

1. Open the Reminder folder you downloaded
2. Find `env.example` file
3. Make a copy and rename it to `.env` (note the dot at start)
4. Open `.env` with Notepad (Windows) or TextEdit (Mac)
5. Fill in your information:

```env
# Required: Your OpenAI API Key
OPENAI_API_KEY=sk-your-key-here-paste-the-long-key

# Optional: Email notifications (use Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password-here
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=My Reminder App
```

**To get Gmail App Password:**
1. Go to: https://myaccount.google.com/security
2. Enable "2-Step Verification" if not already on
3. Search for "App passwords"
4. Generate new app password for "Mail"
5. Copy the 16-character password
6. Paste into `.env` as `SMTP_PASSWORD`

6. Save the file

---

### Step 5: Start the App (2 minutes)

**Windows:**
1. Open Command Prompt
2. Navigate to Reminder folder:
   ```bash
   cd Documents\Reminder
   ```
3. Create virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Start the app:
   ```bash
   python main.py
   ```

**Mac/Linux:**
1. Open Terminal
2. Navigate to Reminder folder:
   ```bash
   cd Documents/Reminder
   ```
3. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Start the app:
   ```bash
   python main.py
   ```

**Success!** You should see:
```
🚀 Reminder API starting up...
📚 API Documentation: http://localhost:8001/docs
⏰ Background scheduler started
```

---

## 🎉 Using Your Self-Hosted App

### Access on Your Computer

1. Open any web browser
2. Go to: **http://localhost:8001**
3. Create reminders using natural language!

### Access on Your Phone (Same WiFi)

1. Find your computer's IP address:
   
   **Windows:**
   ```bash
   ipconfig
   ```
   Look for "IPv4 Address" (e.g., 192.168.1.100)
   
   **Mac:**
   ```bash
   ifconfig | grep inet
   ```
   Look for number like 192.168.1.100

2. On your phone's browser, go to:
   ```
   http://YOUR-IP-ADDRESS:8001
   ```
   Example: `http://192.168.1.100:8001`

3. **Install as PWA on iPhone:**
   - Open in Safari
   - Tap Share button
   - "Add to Home Screen"
   - Now it's a native-like app!

---

## 🔄 Daily Use

### Starting the App Each Day

**Create a Desktop Shortcut (Windows):**

1. Create a new text file called `start-reminder.bat`
2. Add this content:
   ```batch
   @echo off
   cd C:\Users\YourName\Documents\Reminder
   call venv\Scripts\activate
   python main.py
   pause
   ```
3. Save and double-click to start!

**Create a Shortcut (Mac):**

1. Create a file called `start-reminder.command`
2. Add this content:
   ```bash
   #!/bin/bash
   cd ~/Documents/Reminder
   source venv/bin/activate
   python main.py
   ```
3. Make executable: `chmod +x start-reminder.command`
4. Double-click to start!

### Stopping the App

- Press `Ctrl+C` in the terminal window
- Or just close the terminal

### Auto-Start on Boot (Optional)

**Windows (Task Scheduler):**
1. Search "Task Scheduler" in Start menu
2. Click "Create Basic Task"
3. Name: "Start Reminder App"
4. Trigger: "When I log on"
5. Action: "Start a program"
6. Program: `C:\Users\YourName\Documents\Reminder\venv\Scripts\python.exe`
7. Arguments: `main.py`
8. Start in: `C:\Users\YourName\Documents\Reminder`

**Mac (Login Items):**
1. Open System Preferences → Users & Groups
2. Click "Login Items"
3. Click "+" and select `start-reminder.command`

---

## 💾 Your Data Location

All your reminders are stored in:
```
Documents/Reminder/reminders.db
```

**This is YOUR file. Nobody else has access.**

**To backup:**
1. Copy `reminders.db` to USB drive or cloud storage
2. That's it! Your entire reminder history is in that one file

**To restore:**
1. Copy `reminders.db` back to the Reminder folder
2. Restart the app
3. All reminders appear!

---

## 🔒 Privacy & Security

### What Leaves Your Computer?

**Only this goes to external servers:**
- ✅ Natural language text → OpenAI (for parsing)
  - Example: "Call dentist tomorrow at 2pm"
  - OpenAI parses it, sends back structured data
  - OpenAI does NOT store your reminders
  
- ✅ Email notifications → Gmail SMTP (if configured)
  - Only when reminder is due
  - Optional - can disable

**What stays on your computer:**
- ✅ All reminder data (reminders.db)
- ✅ Scheduler state
- ✅ Application code

**Nobody can access:**
- ❌ Your reminder database
- ❌ Your .env configuration
- ❌ Your API keys (unless you share them)

### Maximum Privacy Mode

Want even more privacy? Skip email notifications:

1. In `.env`, remove or comment out SMTP settings:
   ```env
   # SMTP_USERNAME=your-email@gmail.com  # Disabled
   # SMTP_PASSWORD=your-app-password     # Disabled
   ```
2. Restart app
3. No emails sent - reminders only visible in web UI

**Trade-off:** You must check the app yourself for reminders.

---

## 🛠️ Troubleshooting

### "Python is not recognized"

**Fix:**
1. Reinstall Python
2. Check "Add Python to PATH" during installation
3. Restart computer

### "pip is not recognized"

**Fix:**
```bash
python -m pip install --upgrade pip
```

### "OpenAI API error"

**Fix:**
1. Check API key in `.env` is correct
2. Verify you have credits: https://platform.openai.com/usage
3. Make sure key starts with `sk-`

### "Cannot connect to API"

**Fix:**
1. Make sure app is running (check terminal)
2. Use `http://localhost:8001` not `https://`
3. Try `http://127.0.0.1:8001` instead

### "Email notifications not working"

**Fix:**
1. Verify Gmail App Password (16 characters, no spaces)
2. Check 2-Step Verification is enabled on Google account
3. Look in spam folder
4. Check terminal for error messages

### Port 8001 already in use

**Fix - Use different port:**
Edit `main.py`, change last line:
```python
uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
```
Then access: `http://localhost:8002`

---

## 📱 Access from Anywhere (Advanced)

Want to access from outside your home network?

### Option 1: Use Tailscale (Easiest)

Tailscale creates a private network between your devices.

1. Install Tailscale: https://tailscale.com/download
2. Install on computer running the app
3. Install on phone/other devices
4. Access via Tailscale IP (shown in Tailscale app)

**Pros:**
- ✅ Secure (encrypted)
- ✅ Free for personal use
- ✅ No port forwarding needed
- ✅ Works from anywhere

### Option 2: ngrok (Temporary Access)

For quick remote access:

1. Install ngrok: https://ngrok.com/download
2. Start your app: `python main.py`
3. In another terminal: `ngrok http 8001`
4. Use the ngrok URL shown (e.g., `https://abc123.ngrok.io`)

**Pros:**
- ✅ Quick setup
- ✅ HTTPS included
- ✅ Shareable URL

**Cons:**
- ⚠️ URL changes each time (unless paid plan)
- ⚠️ Free tier has limits

### Option 3: Deploy to Cloud (Keep Control)

Deploy to Railway but use YOUR GitHub repo:

1. Fork the repository on GitHub
2. Deploy to Railway (free tier)
3. Add YOUR_OPENAI_KEY as environment variable
4. Access from anywhere via Railway URL

**Pros:**
- ✅ Professional hosting
- ✅ Always accessible
- ✅ HTTPS automatic
- ✅ You own the code/repo

**Cons:**
- ⚠️ Database on Railway (but you control it)
- ⚠️ 500 hours/month free tier limit

---

## 💰 Cost Breakdown

### Self-Hosting Costs

| Item | Cost |
|------|------|
| Python | FREE |
| App code | FREE (open source) |
| Computer electricity | ~$0.50/month |
| OpenAI API | ~$0.15/month |
| Gmail SMTP | FREE |
| **Total** | **~$0.65/month** |

### vs ChatGPT Plus

| Feature | Self-Hosted | ChatGPT Plus |
|---------|-------------|--------------|
| Cost/month | $0.65 | $20.00 |
| Cost/year | $7.80 | $240.00 |
| **Savings** | - | **$232.20/year** |
| Task limit | Unlimited | 10 |
| Data ownership | YOU own it | OpenAI owns it |
| Privacy | Maximum | Shared with OpenAI |

---

## 🎓 Next Steps

### Become Self-Sufficient

1. **Bookmark these:**
   - This guide: `SELF_HOSTING_FOR_BEGINNERS.md`
   - Troubleshooting: `DEPLOYMENT_CHECKLIST.md`
   - Full docs: `README.md`

2. **Learn basic maintenance:**
   - Update app: `git pull` (if using Git)
   - Update dependencies: `pip install --upgrade -r requirements.txt`
   - Backup data: Copy `reminders.db` weekly

3. **Customize:**
   - Change port in `main.py`
   - Modify email templates in `email_service.py`
   - Add custom tags/priorities

### Join the Community

- GitHub Issues: Report bugs or request features
- Fork & customize: Make it yours!
- Share your setup: Help other non-technical users

---

## ✅ Success Checklist

After setup, you should have:

- [ ] App running on `http://localhost:8001`
- [ ] Can create reminders with natural language
- [ ] Reminders saved in `reminders.db`
- [ ] Email notifications working (if configured)
- [ ] Can access from phone on same WiFi
- [ ] Desktop shortcut for easy starting
- [ ] Regular backup of `reminders.db`

**Congratulations! You're now self-hosting! 🎉**

---

## 🆘 Need Help?

### Resources

1. **This repository:**
   - Open an Issue: https://github.com/ehueylee/Reminder/issues
   - Check existing issues for solutions

2. **Documentation:**
   - `README.md` - Full feature guide
   - `DEPLOYMENT_CHECKLIST.md` - Troubleshooting
   - API docs: http://localhost:8001/docs

3. **Community:**
   - Stack Overflow: Tag questions with `smart-reminder-app`
   - GitHub Discussions (if enabled)

### Common Questions

**Q: Do I need to keep the terminal open?**  
A: Yes, while using the app. Close terminal = app stops.

**Q: Can I use this on multiple computers?**  
A: Yes! Install on each computer. They'll have separate databases.

**Q: Can I sync between computers?**  
A: Not automatically. You can manually copy `reminders.db` between computers, or deploy to Railway for centralized access.

**Q: Is this safe?**  
A: Yes! It's just Python code running on your computer. Review the code if concerned: it's all open source.

**Q: What if I delete reminders.db by accident?**  
A: If you have backups, restore them. Otherwise, reminders are gone. **Backup regularly!**

**Q: Can I run this on a Raspberry Pi?**  
A: Yes! Same steps work on Raspberry Pi OS (Linux).

---

## 🎯 Why Self-Host?

### You Should Self-Host If:

✅ You value privacy  
✅ You want full control of your data  
✅ You need unlimited reminders  
✅ You want to avoid monthly fees  
✅ You're okay with computer running while using app  
✅ You have a computer available  

### Use Cloud Deployment If:

✅ You want 24/7 availability  
✅ You don't want to manage infrastructure  
✅ You need access when computer is off  
✅ You want instant mobile access  
✅ You prefer "set it and forget it"  

**Both options are valid!** Choose what fits your needs.

---

**Built with ❤️ for privacy-conscious users**

**Questions? Open an issue on GitHub!** 🚀
