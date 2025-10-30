/**
 * IndexedDB Local Storage Layer
 * Local-first architecture: Data stored in browser, optionally synced to cloud
 * 
 * This gives users:
 * - Complete data ownership (stored locally in their browser)
 * - Offline-first functionality
 * - Optional cloud sync for backup/multi-device
 * - No vendor lock-in - export anytime
 */

class LocalReminderDB {
    constructor() {
        this.dbName = 'ReminderAppDB';
        this.version = 1;
        this.db = null;
        this.syncEnabled = true; // Toggle cloud sync on/off
    }

    /**
     * Initialize IndexedDB
     */
    async init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.version);

            request.onerror = () => {
                console.error('IndexedDB error:', request.error);
                reject(request.error);
            };

            request.onsuccess = () => {
                this.db = request.result;
                console.log('✅ IndexedDB initialized');
                resolve(this.db);
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;

                // Create reminders object store
                if (!db.objectStoreNames.contains('reminders')) {
                    const reminderStore = db.createObjectStore('reminders', { 
                        keyPath: 'id', 
                        autoIncrement: true 
                    });

                    // Create indexes for efficient querying
                    reminderStore.createIndex('user_id', 'user_id', { unique: false });
                    reminderStore.createIndex('status', 'status', { unique: false });
                    reminderStore.createIndex('priority', 'priority', { unique: false });
                    reminderStore.createIndex('due_date_time', 'due_date_time', { unique: false });
                    reminderStore.createIndex('created_at', 'created_at', { unique: false });
                    reminderStore.createIndex('sync_status', 'sync_status', { unique: false });
                }

                // Create sync metadata store
                if (!db.objectStoreNames.contains('sync_meta')) {
                    const syncStore = db.createObjectStore('sync_meta', { keyPath: 'key' });
                }

                // Create settings store
                if (!db.objectStoreNames.contains('settings')) {
                    const settingsStore = db.createObjectStore('settings', { keyPath: 'key' });
                }

                console.log('✅ IndexedDB schema created');
            };
        });
    }

    /**
     * Create a new reminder locally
     */
    async createReminder(reminderData) {
        const transaction = this.db.transaction(['reminders'], 'readwrite');
        const store = transaction.objectStore('reminders');

        const reminder = {
            ...reminderData,
            created_at: reminderData.created_at || new Date().toISOString(),
            updated_at: new Date().toISOString(),
            sync_status: 'pending', // pending, synced, conflict
            local_only: false
        };

        return new Promise((resolve, reject) => {
            const request = store.add(reminder);

            request.onsuccess = () => {
                reminder.id = request.result;
                console.log('✅ Reminder created locally:', reminder.id);
                
                // Optionally sync to cloud in background
                if (this.syncEnabled) {
                    this.syncToCloud(reminder).catch(console.error);
                }
                
                resolve(reminder);
            };

            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Get all reminders for a user
     */
    async getReminders(userId, filters = {}) {
        const transaction = this.db.transaction(['reminders'], 'readonly');
        const store = transaction.objectStore('reminders');
        const index = store.index('user_id');

        return new Promise((resolve, reject) => {
            const request = index.getAll(userId);

            request.onsuccess = () => {
                let reminders = request.result;

                // Apply filters
                if (filters.status) {
                    reminders = reminders.filter(r => r.status === filters.status);
                }
                if (filters.priority) {
                    reminders = reminders.filter(r => r.priority === filters.priority);
                }
                if (filters.tag) {
                    reminders = reminders.filter(r => 
                        r.tags && r.tags.includes(filters.tag)
                    );
                }

                // Sort by due date
                reminders.sort((a, b) => 
                    new Date(a.due_date_time) - new Date(b.due_date_time)
                );

                resolve(reminders);
            };

            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Get a single reminder by ID
     */
    async getReminder(id) {
        const transaction = this.db.transaction(['reminders'], 'readonly');
        const store = transaction.objectStore('reminders');

        return new Promise((resolve, reject) => {
            const request = store.get(id);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Update a reminder
     */
    async updateReminder(id, updates) {
        const reminder = await this.getReminder(id);
        if (!reminder) {
            throw new Error('Reminder not found');
        }

        const updatedReminder = {
            ...reminder,
            ...updates,
            updated_at: new Date().toISOString(),
            sync_status: 'pending'
        };

        const transaction = this.db.transaction(['reminders'], 'readwrite');
        const store = transaction.objectStore('reminders');

        return new Promise((resolve, reject) => {
            const request = store.put(updatedReminder);

            request.onsuccess = () => {
                console.log('✅ Reminder updated locally:', id);
                
                // Optionally sync to cloud
                if (this.syncEnabled) {
                    this.syncToCloud(updatedReminder).catch(console.error);
                }
                
                resolve(updatedReminder);
            };

            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Delete a reminder
     */
    async deleteReminder(id) {
        const transaction = this.db.transaction(['reminders'], 'readwrite');
        const store = transaction.objectStore('reminders');

        return new Promise((resolve, reject) => {
            const request = store.delete(id);

            request.onsuccess = () => {
                console.log('✅ Reminder deleted locally:', id);
                
                // Optionally sync deletion to cloud
                if (this.syncEnabled) {
                    this.syncDeletionToCloud(id).catch(console.error);
                }
                
                resolve(true);
            };

            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Export all data (for backup/portability)
     */
    async exportData(userId) {
        const reminders = await this.getReminders(userId);
        
        const exportData = {
            export_metadata: {
                user_id: userId,
                export_date: new Date().toISOString(),
                total_reminders: reminders.length,
                app_version: '1.0.0',
                storage_type: 'IndexedDB'
            },
            reminders: reminders.map(r => ({
                ...r,
                sync_status: undefined, // Remove internal sync metadata
                local_only: undefined
            }))
        };

        return exportData;
    }

    /**
     * Import data from backup
     */
    async importData(importData, userId) {
        if (!importData.reminders) {
            throw new Error('Invalid import format');
        }

        const results = {
            imported: 0,
            skipped: 0,
            errors: []
        };

        for (const reminderData of importData.reminders) {
            try {
                // Check if already exists
                const existing = await this.getReminder(reminderData.id);
                if (existing) {
                    results.skipped++;
                    continue;
                }

                // Create new reminder
                await this.createReminder({
                    ...reminderData,
                    user_id: userId,
                    sync_status: 'synced', // Mark as already synced
                    local_only: false
                });

                results.imported++;
            } catch (error) {
                results.errors.push({
                    reminder_id: reminderData.id,
                    title: reminderData.title,
                    error: error.message
                });
            }
        }

        return results;
    }

    /**
     * Sync to cloud (optional background sync)
     */
    async syncToCloud(reminder) {
        if (!this.syncEnabled) return;

        try {
            // Check if online
            if (!navigator.onLine) {
                console.log('⏸️ Offline - sync queued for later');
                return;
            }

            // Send to server API
            const response = await fetch('/reminders', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    natural_input: reminder.natural_language_input || reminder.title,
                    user_id: reminder.user_id,
                    timezone: reminder.timezone
                })
            });

            if (response.ok) {
                // Mark as synced
                await this.updateReminder(reminder.id, {
                    sync_status: 'synced',
                    synced_at: new Date().toISOString()
                });
                console.log('☁️ Synced to cloud:', reminder.id);
            }
        } catch (error) {
            console.error('Sync failed:', error);
            // Keep as pending for retry
        }
    }

    /**
     * Sync deletion to cloud
     */
    async syncDeletionToCloud(id) {
        if (!this.syncEnabled || !navigator.onLine) return;

        try {
            await fetch(`/reminders/${id}`, { method: 'DELETE' });
            console.log('☁️ Deletion synced to cloud:', id);
        } catch (error) {
            console.error('Deletion sync failed:', error);
        }
    }

    /**
     * Sync all pending changes
     */
    async syncAll() {
        const transaction = this.db.transaction(['reminders'], 'readonly');
        const store = transaction.objectStore('reminders');
        const index = store.index('sync_status');

        return new Promise((resolve, reject) => {
            const request = index.getAll('pending');

            request.onsuccess = async () => {
                const pendingReminders = request.result;
                console.log(`🔄 Syncing ${pendingReminders.length} pending reminders...`);

                for (const reminder of pendingReminders) {
                    await this.syncToCloud(reminder);
                }

                resolve(pendingReminders.length);
            };

            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Toggle sync on/off
     */
    setSyncEnabled(enabled) {
        this.syncEnabled = enabled;
        console.log(`☁️ Cloud sync: ${enabled ? 'enabled' : 'disabled'}`);
    }

    /**
     * Get sync status
     */
    async getSyncStatus(userId) {
        const reminders = await this.getReminders(userId);
        
        const pending = reminders.filter(r => r.sync_status === 'pending').length;
        const synced = reminders.filter(r => r.sync_status === 'synced').length;
        const localOnly = reminders.filter(r => r.local_only).length;

        return {
            total: reminders.length,
            pending,
            synced,
            localOnly,
            online: navigator.onLine
        };
    }

    /**
     * Clear all data (use with caution!)
     */
    async clearAll() {
        const transaction = this.db.transaction(['reminders'], 'readwrite');
        const store = transaction.objectStore('reminders');

        return new Promise((resolve, reject) => {
            const request = store.clear();
            request.onsuccess = () => {
                console.log('⚠️ All local data cleared');
                resolve(true);
            };
            request.onerror = () => reject(request.error);
        });
    }
}

// Create singleton instance
const localDB = new LocalReminderDB();

// Auto-initialize when script loads
if (typeof window !== 'undefined') {
    localDB.init().catch(console.error);

    // Sync pending changes when coming online
    window.addEventListener('online', () => {
        console.log('📡 Network restored - syncing pending changes...');
        localDB.syncAll().catch(console.error);
    });

    // Periodic sync every 5 minutes
    setInterval(() => {
        if (navigator.onLine && localDB.syncEnabled) {
            localDB.syncAll().catch(console.error);
        }
    }, 5 * 60 * 1000);
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { LocalReminderDB, localDB };
}
