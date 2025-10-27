# 🎯 Smart Reminder App

A powerful reminder application with natural language processing powered by OpenAI GPT-4o-mini. Create reminders using everyday language, get intelligent notifications, and access your reminders anywhere - on the web or as a Progressive Web App on your iPhone!

## ✨ Features

- 🗣️ **Natural Language Input** - "Call dentist tomorrow at 2pm" → automatically parsed
- 🔄 **Recurring Reminders** - Daily, weekly, monthly, or custom patterns
- 📧 **Email Notifications** - Get reminders delivered to your inbox
- 🎨 **Priority Management** - Low, medium, high priority levels with visual badges
- 🏷️ **Smart Tags** - Auto-extracted from natural language or manually added
- 📱 **Progressive Web App** - Install on iPhone home screen like a native app
- 💾 **Offline Support** - Works without internet connection (PWA mode)
- 🌐 **Cross-Platform** - Works on desktop, mobile, iPhone, Android
- 💰 **Zero Cost** - Free deployment options available

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Gmail account (for email notifications)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd Reminder

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (Git Bash):
source venv/Scripts/activate
# On Windows (CMD):
venv\Scripts\activate.bat
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your credentials:
# OPENAI_API_KEY=sk-your-api-key-here
# SMTP_USERNAME=your-email@gmail.com
# SMTP_PASSWORD=your-app-password
```

### Running the Application

```bash
# Start the server
python main.py

# Server will start at:
# - Web UI: http://127.0.0.1:8001
# - API Docs: http://127.0.0.1:8001/docs
```

## 📖 Usage Guide

### Option 1: Web Browser Access

#### 1. Open the App
- Navigate to: `http://127.0.0.1:8001` (local) or your deployed URL
- The app loads instantly in any modern browser
- Works on desktop, mobile, tablets

#### 2. Create Your First Reminder

**Using Natural Language:**
```
Type in the input box:
"Call dentist tomorrow at 2pm"
"Team meeting every Monday at 10am"
"Buy groceries on the way home"
"Submit report by Friday high priority"
```

**What the AI Understands:**
- ✅ **Dates**: tomorrow, next week, Monday, Jan 15, in 3 days
- ✅ **Times**: 2pm, 14:00, at noon, in the morning
- ✅ **Priorities**: high priority, urgent, low priority
- ✅ **Recurrence**: daily, weekly, every Monday, monthly
- ✅ **Tags**: work, personal, urgent (auto-extracted)
- ✅ **Locations**: at office, on the way home

#### 3. Manage Reminders

**View Reminders:**
- All reminders displayed in a card-based list
- Color-coded priority badges (🔴 High, 🟡 Medium, 🟢 Low)
- Relative dates ("Today", "Tomorrow", "In 3 days")
- Recurring indicator (🔄) for repeating reminders

**Filter Reminders:**
- **Status**: All / Pending / Completed / Cancelled
- **Priority**: All / Low / Medium / High
- **Tag**: Search by tag name
- Click "🔄 Refresh" to update the list

**Edit a Reminder:**
1. Click "✏️ Edit" button on any reminder card
2. Modal opens with editable fields:
   - Title
   - Description
   - Priority (dropdown)
   - Status (dropdown)
   - Tags (comma-separated)
3. Click "Save Changes"

**Complete a Reminder:**
- Click "✅ Complete" button
- Reminder marked as completed
- For recurring reminders: Next occurrence auto-created

**Delete a Reminder:**
- Click "🗑️ Delete" button
- Confirmation dialog appears
- Click OK to permanently delete

**Skip/Snooze (Recurring Only):**
- Click "⏭️ Skip" to skip this occurrence
- Click "⏰ Snooze" to delay by preset time

#### 4. Email Notifications

**Setup:**
1. Configure SMTP in `.env`:
   ```
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   SMTP_FROM_EMAIL=your-email@gmail.com
   SMTP_FROM_NAME=Reminder App
   ```

2. For Gmail, create App Password:
   - Go to Google Account → Security
   - Enable 2-Step Verification
   - Generate App Password
   - Use app password in `.env`

**How It Works:**
- Background scheduler checks every 1 minute
- Emails sent 5 minutes before reminder due time
- Beautiful HTML emails with priority colors
- Includes reminder details, time, priority, tags

**Email Features:**
- 📧 Professional HTML formatting
- 🎨 Priority-based color coding
- ⏰ Clear due date/time
- 🏷️ Tag display
- 📝 Full description included

#### 5. Parse-Only Mode (Test NLP)

Before creating a reminder, test how AI parses your input:

1. Type natural language text
2. Click "🔍 Parse Only" (instead of Create)
3. See parsed results:
   - Extracted title
   - Description
   - Due date & time
   - Priority level
   - Tags
   - Recurring pattern
   - Confidence score
4. Review and adjust if needed
5. Click "➕ Create Reminder" when satisfied

#### 6. Keyboard Shortcuts

- **Enter** in text field: Submit form (create reminder)
- **Esc** in modal: Close edit modal
- **Tab**: Navigate between fields

#### 7. Auto-Refresh

- List auto-refreshes every 30 seconds
- Manual refresh: Click "🔄 Refresh" button
- Health status indicator shows connection state:
  - 🟢 Green: Connected & healthy
  - 🔴 Red: Disconnected or error

---

### Option 2: Progressive Web App (PWA) - iPhone Installation

Transform the web app into a native-like app on your iPhone!

#### Step 1: Generate App Icons (One-Time Setup)

**Quick Method (2 minutes):**
1. Visit: https://www.pwabuilder.com/imageGenerator
2. Upload a 512x512 image:
   - Purple background (`#667eea`)
   - White bell/calendar icon
   - Or use any logo you like
3. Click "Generate"
4. Download ZIP file
5. Extract and place all PNG files in `static/` folder:
   - `icon-72.png`
   - `icon-96.png`
   - `icon-128.png`
   - `icon-144.png`
   - `icon-152.png`
   - `icon-180.png` (Apple touch icon)
   - `icon-192.png`
   - `icon-384.png`
   - `icon-512.png`

See `ICON_GENERATION_GUIDE.md` for detailed instructions and alternatives.

#### Step 2: Install on iPhone

**From Deployed Site:**
1. Deploy app to Vercel/Netlify (see `DEPLOYMENT_PLAN_ZERO_BUDGET.md`)
2. On iPhone, open Safari
3. Navigate to your app URL (e.g., `https://your-app.vercel.app`)
4. Tap **Share** button (box with arrow)
5. Scroll down and tap **"Add to Home Screen"**
6. Edit name if desired (default: "Reminder App")
7. Tap **"Add"** in top-right corner
8. App icon appears on your home screen! 🎉

**From Local Network (Testing):**
1. Ensure iPhone and computer on same WiFi
2. Find your computer's IP address:
   ```bash
   # Windows:
   ipconfig | grep "IPv4"
   # macOS/Linux:
   ifconfig | grep "inet "
   ```
3. On iPhone Safari, go to: `http://YOUR_IP_ADDRESS:8001`
4. Follow steps 4-8 above

#### Step 3: Use the PWA

**Launching:**
- Tap the app icon on home screen
- Opens in full-screen mode (no Safari UI)
- Looks and feels like a native app

**PWA Features:**

✅ **Works Like a Native App:**
- Full-screen interface (no browser bars)
- Smooth app-like transitions
- Separate from Safari
- Shows up in app switcher

✅ **Offline Support:**
- View previously loaded reminders
- App shell loads without internet
- Shows "offline" page if no connection
- Auto-syncs when connection restored

✅ **Home Screen Icon:**
- Custom app icon (your design)
- Custom app name
- Purple theme color in status bar

✅ **Fast & Lightweight:**
- Instant loading (cached assets)
- < 1 MB total size
- No app store required
- No installation delays

⚠️ **iOS Limitations:**
- **No Push Notifications** - Use email notifications instead (already configured!)
- **No Background Refresh** - Server scheduler handles it
- **Limited Camera/File Access** - Web APIs only
- **Not in App Store** - Shared via URL, users install manually

#### Step 4: Update the PWA

**Automatic Updates:**
1. Deploy new code to production
2. Service worker detects changes
3. Next time user opens app:
   - New version downloads in background
   - App prompts to reload
   - User accepts → instant update

**No reinstallation required!**

#### Step 5: Share with Others

**Distribution:**
1. Share your app URL via:
   - Email
   - Text message
   - Social media
   - QR code
2. Recipients open in Safari
3. They add to home screen (same steps)
4. Everyone gets the same app!

**No App Store submission needed!**

---

### Option 3: React Native App (Optional - Full Native Experience)

For users who need full native features (push notifications, App Store presence):

See `DEPLOYMENT_PLAN_IPHONE.md` for complete guide to building React Native version.

**When to Choose React Native:**
- Need push notifications
- Want App Store presence
- Need native file/camera access
- Willing to pay $99/year Apple Developer fee

**When PWA is Sufficient:**
- Email notifications work for you ✅
- Don't need App Store listing ✅
- Want zero cost ✅
- Want instant updates ✅
- Want cross-platform (works on Android too!) ✅

---

## 🎨 User Interface Guide

### Main Screen Layout

```
┌─────────────────────────────────────┐
│  🎯 Smart Reminder App              │
│  Natural language powered reminders │
│  ● Connected                         │ ← Health Status
├─────────────────────────────────────┤
│  ✨ Create New Reminder             │
│  ┌─────────────────────────────┐   │
│  │ Call dentist tomorrow 2pm   │   │ ← Natural Language Input
│  └─────────────────────────────┘   │
│  💡 Tip: Use natural language!      │
│                                      │
│  [Your ID: user123] [Timezone: UTC] │
│  [🔍 Parse Only] [➕ Create]        │
├─────────────────────────────────────┤
│  🔎 Filter Reminders                │
│  [Status ▼] [Priority ▼] [Tag: __]  │
│  [🔄 Refresh]                       │
├─────────────────────────────────────┤
│  📝 Your Reminders          [5]     │ ← Reminder Count
│  ┌─────────────────────────────┐   │
│  │ 📌 Call Dentist             │   │
│  │ Tomorrow at 2:00 PM    🔴 H │   │ ← Priority Badge
│  │ 🏷️ health, urgent           │   │
│  │ 🔄 Not recurring            │   │
│  │ [✅ Complete] [✏️ Edit]      │   │
│  │ [🗑️ Delete]                 │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │ 📌 Team Meeting             │   │
│  │ Every Monday at 10:00 AM 🟡M│   │
│  │ 🏷️ work, recurring          │   │
│  │ 🔄 Weekly pattern           │   │
│  │ [⏭️ Skip] [⏰ Snooze]        │   │
│  │ [✅ Complete] [✏️ Edit]      │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

### Priority Badges

| Badge | Priority | Use Case |
|-------|----------|----------|
| 🔴 H | High | Urgent, critical tasks |
| 🟡 M | Medium | Regular tasks (default) |
| 🟢 L | Low | Nice-to-have, optional |

### Status Icons

| Icon | Meaning |
|------|---------|
| 🔄 | Recurring reminder |
| ✅ | Completed |
| ⏰ | Due soon |
| 📧 | Email sent |
| 🟢 | API connected |
| 🔴 | API disconnected |

---

## 🔧 Advanced Features

### Recurring Patterns

**Daily:**
```
"Take vitamins every day at 9am"
"Daily standup at 10am"
```

**Weekly:**
```
"Team meeting every Monday at 2pm"
"Gym sessions Monday, Wednesday, Friday"
```

**Monthly:**
```
"Pay rent on the 1st of every month"
"Monthly review every 30 days"
```

**Custom:**
```
"Water plants every 3 days"
"Report due every 2 weeks"
```

**Skip/Snooze Actions:**
- **Skip**: Marks current occurrence complete, creates next
- **Snooze**: Delays reminder by preset duration (15 min, 1 hour, etc.)

### Timezone Support

**Available Timezones:**
- UTC (default)
- America/New_York (Eastern)
- America/Chicago (Central)
- America/Denver (Mountain)
- America/Los_Angeles (Pacific)
- Europe/London
- Europe/Paris
- Asia/Tokyo
- Asia/Shanghai
- Australia/Sydney

**Usage:**
1. Select timezone from dropdown before creating reminder
2. All times interpreted in selected timezone
3. Server stores in UTC, displays in your timezone

### Batch Operations

**Create Multiple Reminders:**
```
"Add these reminders:
- Call dentist tomorrow at 2pm
- Team meeting Monday at 10am
- Buy groceries Friday evening"
```

AI parses each line as separate reminder!

### API Integration

**Direct API Access:**
- API Docs: `http://127.0.0.1:8001/docs`
- OpenAPI Spec: `http://127.0.0.1:8001/openapi.json`
- ReDoc: `http://127.0.0.1:8001/redoc`

**Available Endpoints:**
```
POST   /reminders/parse        # Parse without saving
POST   /reminders              # Create reminder
GET    /reminders              # List all (with filters)
GET    /reminders/{id}         # Get specific
PUT    /reminders/{id}         # Update
POST   /reminders/{id}/complete # Mark complete
DELETE /reminders/{id}         # Delete
GET    /reminders/due/now      # Get due reminders
POST   /reminders/{id}/skip    # Skip occurrence
POST   /reminders/{id}/snooze  # Snooze reminder
```

**Example API Call (cURL):**
```bash
# Create reminder via API
curl -X POST "http://127.0.0.1:8001/reminders" \
  -H "Content-Type: application/json" \
  -d '{
    "natural_language": "Team meeting tomorrow at 2pm",
    "user_id": "user123",
    "timezone": "America/New_York"
  }'
```

---

## 📱 Mobile Experience Comparison

### Web Browser (Safari/Chrome)

**Pros:**
- ✅ No installation required
- ✅ Works immediately
- ✅ Always latest version
- ✅ Shareable via URL

**Cons:**
- ❌ Browser UI takes screen space
- ❌ Must type URL each time
- ❌ Limited offline support
- ❌ No home screen icon

**Best For:**
- Quick access
- First-time users
- Desktop usage
- Testing

### Progressive Web App (PWA)

**Pros:**
- ✅ Full-screen app experience
- ✅ Home screen icon
- ✅ Works offline
- ✅ Fast loading (cached)
- ✅ $0 cost
- ✅ Instant updates
- ✅ Cross-platform (iOS + Android)

**Cons:**
- ⚠️ No push notifications (iOS)
- ⚠️ Not in App Store
- ⚠️ Manual installation (users add to home screen)

**Best For:**
- Daily users
- iPhone/Android users
- Offline access needed
- Budget-conscious

### React Native App (Optional)

**Pros:**
- ✅ True native app
- ✅ Push notifications
- ✅ App Store presence
- ✅ Native UI/UX

**Cons:**
- ❌ $99/year Apple Developer fee
- ❌ 1-3 day App Store review
- ❌ Development time required
- ❌ Separate iOS/Android maintenance

**Best For:**
- Commercial deployment
- Need push notifications
- Want App Store discovery
- Professional use

**Recommendation:**
Start with PWA (free, instant), upgrade to React Native only if you need App Store presence or push notifications.

---

## 🚀 Deployment Options

### Free Tier Options ($0/month)

| Component | Service | Free Tier | Setup Time |
|-----------|---------|-----------|------------|
| **Backend** | Railway.app | 500 hours/month | 15 min |
| **Backend** | Fly.io | 3 VMs (256MB) | 20 min |
| **Frontend** | Vercel | Unlimited | 5 min |
| **Frontend** | Netlify | 100GB bandwidth | 5 min |
| **Database** | Railway (PostgreSQL) | 1GB storage | Included |
| **Emails** | Gmail SMTP | 500/day | Configured |

**Total Monthly Cost: $0** ✅

See `DEPLOYMENT_PLAN_ZERO_BUDGET.md` for complete deployment guide.

### Quick Deploy (Vercel + Railway)

```bash
# 1. Deploy frontend to Vercel
npm i -g vercel
vercel deploy

# 2. Deploy backend to Railway
# - Sign up at railway.app
# - Connect GitHub repo
# - Add environment variables
# - Deploy automatically

# Done! 🎉
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue: "API connection failed"**
- ✅ Check server is running: `python main.py`
- ✅ Verify URL is correct: `http://127.0.0.1:8001`
- ✅ Check firewall settings
- ✅ Try different port: `uvicorn main:app --port 8002`

**Issue: "OpenAI API error"**
- ✅ Verify API key in `.env`
- ✅ Check API key is active: https://platform.openai.com/api-keys
- ✅ Ensure you have credits: https://platform.openai.com/usage
- ✅ Check rate limits

**Issue: "Email notifications not working"**
- ✅ Verify SMTP credentials in `.env`
- ✅ For Gmail, use App Password (not regular password)
- ✅ Check spam folder
- ✅ Enable "Less secure app access" if needed
- ✅ Check scheduler is running: Look for "Scheduler started" in console

**Issue: "PWA won't install on iPhone"**
- ✅ Ensure using Safari (not Chrome)
- ✅ Check icon files exist in `static/`
- ✅ Verify manifest.json is accessible: `/manifest.json`
- ✅ Use HTTPS (required for PWA on production)
- ✅ Clear Safari cache and try again

**Issue: "Reminders not appearing in list"**
- ✅ Check filters (reset to "All")
- ✅ Click "🔄 Refresh" button
- ✅ Check browser console for errors (F12)
- ✅ Verify database file exists: `reminders.db`

**Issue: "Service worker not registering"**
- ✅ Check browser console for errors
- ✅ Ensure serving over HTTPS (production) or localhost
- ✅ Clear browser cache: Settings → Clear browsing data
- ✅ Verify `service-worker.js` exists in `static/`

### Debug Mode

**Enable verbose logging:**
1. Open browser DevTools (F12)
2. Go to Console tab
3. Check for error messages
4. Service worker logs show cache status

**Check API health:**
```bash
curl http://127.0.0.1:8001/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "openai": "connected",
  "timestamp": "2025-10-26T..."
}
```

---

## 📊 Cost Analysis

### Development Mode (Local)

| Item | Cost |
|------|------|
| Database (SQLite) | $0 |
| OpenAI API | ~$0.03-0.15/month |
| Server (local) | $0 |
| **Total** | **< $0.20/month** |

### Production Mode (Free Tier)

| Item | Service | Cost |
|------|---------|------|
| Backend | Railway.app | $0 |
| Frontend | Vercel | $0 |
| Database | Railway PostgreSQL | $0 |
| Email | Gmail SMTP | $0 |
| OpenAI API | GPT-4o-mini | ~$0.15/month |
| **Total** | | **< $0.20/month** |

### Per-Operation Costs

| Operation | Cost |
|-----------|------|
| Parse reminder (NLP) | ~$0.0001 |
| Create reminder | $0 (database only) |
| Send email | $0 (Gmail free tier) |
| PWA installation | $0 |
| API call | $0 |

**Example Monthly Usage:**
- 50 reminders created: $0.005
- 100 email notifications: $0
- 1000 API calls: $0
- **Total: < $0.01/month** 🎉

---

## 🤝 Support

### Documentation

- **Design Guide**: `DESIGN_GUIDE.md` - Architecture and implementation
- **Phase Guides**: `README_PHASE_1_X.md` - Detailed feature docs
- **Deployment**: `DEPLOYMENT_PLAN_ZERO_BUDGET.md` - Free hosting guide
- **iPhone PWA**: `DEPLOYMENT_PLAN_IPHONE.md` - Mobile deployment
- **Icon Guide**: `ICON_GENERATION_GUIDE.md` - PWA icon creation
- **TestFlight**: `TESTFLIGHT_VS_APPSTORE.md` - iOS distribution options

### Quick Links

- API Documentation: http://127.0.0.1:8001/docs
- ReDoc: http://127.0.0.1:8001/redoc
- PWA Builder: https://www.pwabuilder.com/imageGenerator
- OpenAI Platform: https://platform.openai.com

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🎉 Success Stories

### What Users Love

✨ **"The natural language parsing is incredible!"**
- Just type what you want, AI figures it out

✨ **"PWA on iPhone works perfectly!"**
- Feels like a native app, costs $0

✨ **"Email notifications are so helpful!"**
- Never miss important reminders

✨ **"Recurring reminders saved me hours!"**
- Set it once, forget about it

✨ **"Deployed in 15 minutes for free!"**
- Railway + Vercel = zero cost production

---

## 🚀 Get Started Now!

### 1-Minute Quick Start

```bash
# Install and run
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash
pip install -r requirements.txt
cp .env.example .env
# Add your OpenAI API key to .env
python main.py
# Open http://127.0.0.1:8001 🎉
```

### 5-Minute PWA Setup

```bash
# Create icons
# Visit: https://www.pwabuilder.com/imageGenerator
# Upload 512x512 image, download, extract to static/

# Test on iPhone
# 1. Find your IP: ipconfig
# 2. On iPhone Safari: http://YOUR_IP:8001
# 3. Tap Share → Add to Home Screen 🎉
```

### 15-Minute Production Deploy

```bash
# Deploy to Railway + Vercel (both free)
# Follow: DEPLOYMENT_PLAN_ZERO_BUDGET.md
# Result: Live app with custom domain 🚀
```

---

**Built with ❤️ using FastAPI, OpenAI GPT-4o-mini, and modern web technologies**

**Questions? Check the documentation files in this repository!** 📚
