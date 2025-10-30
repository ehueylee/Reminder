# Local Storage Options: Browser vs Native Apps

## Quick Answer

**Browser (Web):** IndexedDB  
**Native iOS:** Core Data / SQLite  
**Native Android:** Room Database / SQLite  
**Desktop (Electron):** SQLite / LowDB  
**React Native:** Realm / AsyncStorage  
**Flutter:** Hive / sqflite  

## Common Thread: All Use SQLite Under the Hood

IndexedDB (browser) and SQLite (native) are **functionally equivalent**:

| Feature | IndexedDB | SQLite |
|---------|-----------|--------|
| Type | Browser API | Database file |
| Storage | Structured data | Structured data |
| Query | JavaScript API | SQL queries |
| Async | Yes | Yes (with wrappers) |
| Offline | ✅ Yes | ✅ Yes |
| Size | 50MB-unlimited | Limited by device |
| Ownership | ✅ User's browser | ✅ User's device |

## Our Implementation

### Web (Current)
- **File:** `static/db.js`
- **Technology:** IndexedDB
- **Location:** Browser's local storage
- **Usage:**
  ```javascript
  await localDB.init();
  await localDB.createReminder({...});
  const reminders = await localDB.getReminders("user-id");
  ```

### Native Mobile (Future)
Replace IndexedDB calls with:
- **iOS:** Core Data / SQLite.swift
- **Android:** Room Database
- **React Native:** Realm Database

### Desktop (Future)
- **Electron:** better-sqlite3
- **Storage:** User's AppData folder
- **Same API:** Just different backend

## Key Principle

**Local-first, cloud-optional:**
1. Data stored on user's device first
2. Optional background sync to cloud
3. Full export/import capability
4. No vendor lock-in

## Files Created

1. **`static/db.js`** - IndexedDB implementation for web
2. **`DATA_OWNERSHIP_GUIDE.md`** - Complete guide with all platforms
3. **This file** - Quick reference

## Next Steps

To enable local-first in the web app:

1. Include db.js in index.html:
   ```html
   <script src="db.js"></script>
   ```

2. Toggle between local/cloud:
   ```javascript
   // Local-only mode
   localDB.setSyncEnabled(false);
   
   // Hybrid mode (default)
   localDB.setSyncEnabled(true);
   ```

3. Export data anytime:
   ```javascript
   const backup = await localDB.exportData("user-id");
   // Downloads JSON with all reminders
   ```

## Benefits

✅ User owns their data  
✅ Works offline  
✅ No vendor lock-in  
✅ Export/import anytime  
✅ Choose local vs cloud  
✅ Privacy-first architecture  

See `DATA_OWNERSHIP_GUIDE.md` for detailed implementation guides for each platform.
