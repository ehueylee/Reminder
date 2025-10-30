# 💾 Data Ownership Architecture Guide

**Local-First, Cloud-Optional: You Own Your Data**

## 🎯 Philosophy

**Your data should live on YOUR device, not locked in someone else's cloud.**

This app implements a **local-first architecture**:
1. **Data stored locally first** (browser/device)
2. **Optional cloud sync** for backup/multi-device
3. **Full export/import** - no vendor lock-in
4. **Works offline** - no internet required after setup

---

## 🌐 Web Browser: IndexedDB

### What is IndexedDB?

A powerful browser database that stores data **locally on your computer**.

**Benefits:**
- ✅ Large storage capacity (50MB+ typical, unlimited with permission)
- ✅ Structured data with indexes
- ✅ Async API (doesn't block UI)
- ✅ Transactional (safe, consistent)
- ✅ Works offline
- ✅ Data persists across sessions

### How We Use It

```javascript
// All reminders stored in YOUR browser
LocalDB.createReminder({
    title: "Call dentist",
    due_date_time: "2025-11-01T14:00:00",
    user_id: "you"
});

// Query locally - no network needed
const reminders = await LocalDB.getReminders("you");

// Export YOUR data anytime
const backup = await LocalDB.exportData("you");
```

### Storage Location

**Windows:**
```
C:\Users\YourName\AppData\Local\Google\Chrome\User Data\Default\IndexedDB\
```

**Mac:**
```
~/Library/Application Support/Google/Chrome/Default/IndexedDB/
```

**Linux:**
```
~/.config/google-chrome/Default/IndexedDB/
```

---

## 📱 Native Mobile Apps: SQLite

When wrapping the app as a native mobile app (iOS/Android), **SQLite** replaces IndexedDB.

### iOS (Swift/Objective-C)

**Storage Options:**

1. **Core Data** (Apple's ORM)
   ```swift
   // High-level API over SQLite
   let reminder = Reminder(context: context)
   reminder.title = "Call dentist"
   reminder.dueDateTime = Date()
   try context.save()
   ```

2. **SQLite.swift** (Direct SQLite)
   ```swift
   let db = try Connection("reminders.db")
   try db.run(reminders.insert(
       title <- "Call dentist",
       dueDateTime <- Date()
   ))
   ```

3. **Realm** (Modern alternative)
   ```swift
   let reminder = Reminder()
   reminder.title = "Call dentist"
   realm.write {
       realm.add(reminder)
   }
   ```

**Storage Location:**
```
/var/mobile/Containers/Data/Application/[UUID]/Documents/reminders.db
```

**Backup:** Automatically included in iCloud/iTunes backup

---

### Android (Kotlin/Java)

**Storage Options:**

1. **Room Database** (Google's ORM)
   ```kotlin
   @Dao
   interface ReminderDao {
       @Insert
       fun insert(reminder: Reminder)
       
       @Query("SELECT * FROM reminders")
       fun getAll(): List<Reminder>
   }
   ```

2. **SQLite directly**
   ```kotlin
   val db = ReminderDBHelper(context).writableDatabase
   val values = ContentValues().apply {
       put("title", "Call dentist")
       put("due_date_time", "2025-11-01 14:00:00")
   }
   db.insert("reminders", null, values)
   ```

**Storage Location:**
```
/data/data/com.yourapp.reminder/databases/reminders.db
```

**Backup:** User-controlled via Android Backup API

---

## 🖥️ Desktop Apps: Electron + SQLite

For desktop apps (Windows/Mac/Linux), use **Electron** with **SQLite**.

**Storage Options:**

1. **better-sqlite3** (Fast, synchronous)
   ```javascript
   const Database = require('better-sqlite3');
   const db = new Database('reminders.db');
   
   const insert = db.prepare(`
       INSERT INTO reminders (title, due_date_time) 
       VALUES (?, ?)
   `);
   insert.run('Call dentist', '2025-11-01 14:00:00');
   ```

2. **LowDB** (JSON file database)
   ```javascript
   const low = require('lowdb');
   const FileSync = require('lowdb/adapters/FileSync');
   
   const adapter = new FileSync('db.json');
   const db = low(adapter);
   
   db.get('reminders')
     .push({ title: 'Call dentist' })
     .write();
   ```

**Storage Location:**
```
Windows: C:\Users\YourName\AppData\Roaming\ReminderApp\
Mac:     ~/Library/Application Support/ReminderApp/
Linux:   ~/.config/ReminderApp/
```

---

## 🔄 Cross-Platform: React Native / Flutter

### React Native

**Storage Options:**

1. **AsyncStorage** (Key-value)
   ```javascript
   import AsyncStorage from '@react-native-async-storage/async-storage';
   
   await AsyncStorage.setItem('reminders', JSON.stringify(reminders));
   const data = await AsyncStorage.getItem('reminders');
   ```

2. **Realm** (Object database)
   ```javascript
   const realm = await Realm.open({schema: [ReminderSchema]});
   
   realm.write(() => {
       realm.create('Reminder', {
           title: 'Call dentist',
           dueDateTime: new Date()
       });
   });
   ```

3. **WatermelonDB** (SQLite wrapper)
   ```javascript
   await database.write(async () => {
       await remindersCollection.create(reminder => {
           reminder.title = 'Call dentist';
           reminder.dueDateTime = new Date();
       });
   });
   ```

### Flutter

**Storage Options:**

1. **Hive** (Fast NoSQL)
   ```dart
   var box = await Hive.openBox('reminders');
   box.put('reminder1', Reminder(
       title: 'Call dentist',
       dueDateTime: DateTime.now()
   ));
   ```

2. **sqflite** (SQLite plugin)
   ```dart
   final Database database = await openDatabase('reminders.db');
   await database.insert('reminders', {
       'title': 'Call dentist',
       'due_date_time': DateTime.now().toIso8601String()
   });
   ```

---

## ☁️ Hybrid Architecture: Local + Optional Cloud

### How It Works

```
┌─────────────────────────────────────────┐
│         Your Device (PRIMARY)           │
│  ┌───────────────────────────────────┐  │
│  │   IndexedDB/SQLite (Your Data)    │  │
│  │   - All reminders stored here     │  │
│  │   - Works offline                 │  │
│  │   - Full CRUD operations          │  │
│  └───────────────────────────────────┘  │
│                  ▲                       │
│                  │                       │
│         Background Sync (Optional)      │
│                  │                       │
│                  ▼                       │
│  ┌───────────────────────────────────┐  │
│  │   Cloud Backup (OPTIONAL)         │  │
│  │   - Railway PostgreSQL            │  │
│  │   - Only if sync enabled          │  │
│  │   - Multi-device access           │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### Sync Modes

**1. Local-Only Mode** (Maximum Privacy)
```javascript
localDB.setSyncEnabled(false);
// All data stays on device
// Zero cloud dependency
// 100% offline
```

**2. Hybrid Mode** (Default)
```javascript
localDB.setSyncEnabled(true);
// Data stored locally first
// Synced to cloud in background
// Works offline, syncs when online
```

**3. Cloud-Sync Mode** (Multi-Device)
```javascript
// Same data across all devices
// Auto-sync every 5 minutes
// Conflict resolution built-in
```

---

## 📊 Comparison Table

| Feature | IndexedDB (Web) | SQLite (Native) | Cloud (Railway) |
|---------|----------------|-----------------|-----------------|
| **Storage Location** | Browser folder | App sandbox | Remote server |
| **Ownership** | ✅ You own it | ✅ You own it | ⚠️ Provider owns |
| **Offline Access** | ✅ Full | ✅ Full | ❌ No |
| **Backup Control** | ✅ You control | ✅ You control | ⚠️ Auto-backup |
| **Multi-Device** | ❌ No | ❌ No | ✅ Yes |
| **Privacy** | ✅ 100% local | ✅ 100% local | ⚠️ Data leaves device |
| **Storage Limit** | ~50MB-unlimited | Device storage | Database limits |
| **Export/Import** | ✅ Easy | ✅ Easy | ⚠️ API dependent |
| **Speed** | ⚡ Instant | ⚡ Instant | 🐌 Network delay |

---

## 🛠️ Implementation Guide

### Step 1: Choose Your Platform

**Web App (Current):**
- Use `static/db.js` (IndexedDB)
- Include in `index.html`:
  ```html
  <script src="db.js"></script>
  ```

**Mobile App (React Native):**
1. Install Realm:
   ```bash
   npm install realm
   ```
2. Replace IndexedDB calls with Realm

**Desktop App (Electron):**
1. Install better-sqlite3:
   ```bash
   npm install better-sqlite3
   ```
2. Use SQLite instead of IndexedDB

### Step 2: Enable Local-First

```javascript
// Initialize local database
await localDB.init();

// Create reminder locally
const reminder = await localDB.createReminder({
    title: "Call dentist",
    user_id: "you",
    due_date_time: new Date(),
    timezone: "America/New_York"
});

// Optional: Sync to cloud
if (navigator.onLine) {
    await localDB.syncToCloud(reminder);
}
```

### Step 3: Export Your Data Anytime

```javascript
// Download all your data
const backup = await localDB.exportData("your-user-id");

// Save to file
const blob = new Blob(
    [JSON.stringify(backup, null, 2)], 
    {type: 'application/json'}
);
const url = URL.createObjectURL(blob);
// Download...
```

---

## 🔐 Privacy & Security

### Data Never Leaves Your Device (Local-Only Mode)

**What stays local:**
- ✅ All reminder content
- ✅ Dates, times, priorities
- ✅ Tags and descriptions
- ✅ Complete history

**What goes to cloud (only if sync enabled):**
- Reminder text → OpenAI API (for NLP parsing)
- Parsed data → Your Railway database (if you deployed)

**You control:**
- Toggle sync on/off anytime
- Export all data with one click
- Delete cloud copy, keep local
- Switch providers without data loss

---

## 🚀 Migration Paths

### From ChatGPT to This App

```javascript
// 1. Export your reminders to JSON
const backup = await localDB.exportData("you");

// 2. Store locally - no cloud needed
// Your data lives in YOUR browser

// 3. Optional: Enable cloud sync later
localDB.setSyncEnabled(true);
```

### Between Devices

```javascript
// Device 1: Export
const backup = await localDB.exportData("you");
// Download JSON file

// Device 2: Import
await localDB.importData(backup, "you");
// All data restored
```

### Self-Hosted to Cloud (or vice versa)

```javascript
// Same export/import mechanism
// Data format identical
// Zero vendor lock-in
```

---

## 📚 Further Reading

- [IndexedDB API](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API)
- [SQLite](https://www.sqlite.org/)
- [Realm Database](https://realm.io/)
- [Local-First Software](https://www.inkandswitch.com/local-first/)

---

## 💡 Best Practices

1. **Default to Local**: Store everything locally first
2. **Sync is Optional**: User chooses cloud backup
3. **Export Regularly**: Weekly backups to USB/cloud storage
4. **Clear Ownership**: User owns the data, not the app
5. **Easy Migration**: Standard JSON export format
6. **Privacy First**: Minimal data sent to cloud
7. **Offline-Capable**: Full functionality without internet

**Remember:** IndexedDB (web) and SQLite (native) are essentially the same concept - **local structured storage that YOU control**.
