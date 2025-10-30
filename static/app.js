// API Configuration
const API_BASE_URL = 'https://web-production-129e7.up.railway.app';
// const API_BASE_URL = 'http://127.0.0.1:8001';

// Global State
let reminders = [];
let currentFilters = {
    status: '',
    priority: '',
    tag: ''
};

// Initialize App
document.addEventListener('DOMContentLoaded', function() {
    // Load saved user preferences
    loadUserPreferences();
    
    // Check API health
    checkHealth();
    
    // Load reminders
    loadReminders();
    
    // Setup event listeners
    setupEventListeners();
    
    // Auto-refresh every 30 seconds
    setInterval(loadReminders, 30000);
});

// Load user preferences from localStorage
function loadUserPreferences() {
    const savedUserId = localStorage.getItem('userId');
    const savedTimezone = localStorage.getItem('timezone');
    
    if (savedUserId) {
        document.getElementById('user-id').value = savedUserId;
    }
    if (savedTimezone) {
        document.getElementById('timezone').value = savedTimezone;
    }
}

// Save user preferences to localStorage
function saveUserPreferences(userId, timezone) {
    localStorage.setItem('userId', userId);
    localStorage.setItem('timezone', timezone);
}

// Event Listeners
function setupEventListeners() {
    // Create form
    document.getElementById('create-form').addEventListener('submit', handleCreateReminder);
    document.getElementById('parse-btn').addEventListener('click', handleParseOnly);
    
    // Filters
    document.getElementById('filter-status').addEventListener('change', handleFilterChange);
    document.getElementById('filter-priority').addEventListener('change', handleFilterChange);
    document.getElementById('filter-tag').addEventListener('input', handleFilterChange);
    document.getElementById('refresh-btn').addEventListener('click', loadReminders);
    
    // Edit form
    document.getElementById('edit-form').addEventListener('submit', handleUpdateReminder);
    
    // Modal close
    document.querySelector('.modal-close').addEventListener('click', closeEditModal);
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('edit-modal');
        if (event.target === modal) {
            closeEditModal();
        }
    });
    
    // Event delegation for reminder action buttons
    document.getElementById('reminders-list').addEventListener('click', function(event) {
        const button = event.target.closest('button[data-action]');
        if (!button) return;
        
        const action = button.dataset.action;
        const id = button.dataset.id;
        
        if (action === 'complete') {
            completeReminder(id);
        } else if (action === 'edit') {
            editReminder(id);
        } else if (action === 'delete') {
            deleteReminder(id);
        }
    });
}

// Health Check
async function checkHealth() {
    const indicator = document.getElementById('health-indicator');
    const text = document.getElementById('health-text');
    
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            indicator.classList.add('healthy');
            text.textContent = 'API Connected';
        } else {
            indicator.classList.add('unhealthy');
            text.textContent = 'API Issues Detected';
        }
    } catch (error) {
        indicator.classList.add('unhealthy');
        text.textContent = 'API Offline';
        showToast('Cannot connect to API server. Make sure it is running on port 8001.', 'error');
    }
}

// Parse Only
async function handleParseOnly() {
    const naturalInput = document.getElementById('natural-input').value.trim();
    const timezone = document.getElementById('timezone').value;
    
    if (!naturalInput) {
        showToast('Please enter a reminder description', 'error');
        return;
    }
    
    const parseBtn = document.getElementById('parse-btn');
    parseBtn.disabled = true;
    parseBtn.textContent = '⏳ Parsing...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/reminders/parse`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                natural_input: naturalInput,
                user_timezone: timezone
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayParseResult(data);
            showToast('Successfully parsed!', 'success');
        } else {
            showToast(`Parse error: ${data.detail}`, 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        parseBtn.disabled = false;
        parseBtn.textContent = '🔍 Parse Only';
    }
}

// Display Parse Result
function displayParseResult(data) {
    const resultDiv = document.getElementById('parse-result');
    const contentDiv = document.getElementById('parse-content');
    
    const parsed = data.parsed;
    const confidence = data.confidence_score || 0;
    
    let html = `
        <div class="parse-detail">
            <div class="parse-label">Title:</div>
            <div class="parse-value"><strong>${parsed.title || 'N/A'}</strong></div>
        </div>
        <div class="parse-detail">
            <div class="parse-label">Description:</div>
            <div class="parse-value">${parsed.description || 'N/A'}</div>
        </div>
        <div class="parse-detail">
            <div class="parse-label">Due Date/Time:</div>
            <div class="parse-value">${parsed.due_date_time ? formatDateTime(parsed.due_date_time) : 'Not specified'}</div>
        </div>
        <div class="parse-detail">
            <div class="parse-label">Priority:</div>
            <div class="parse-value"><span class="priority-badge priority-${parsed.priority || 'medium'}">${parsed.priority || 'medium'}</span></div>
        </div>
        <div class="parse-detail">
            <div class="parse-label">Recurring:</div>
            <div class="parse-value">${parsed.is_recurring ? '✅ Yes' : '❌ No'}</div>
        </div>
        ${parsed.recurrence_rule ? `
        <div class="parse-detail">
            <div class="parse-label">Recurrence:</div>
            <div class="parse-value">${parsed.recurrence_rule}</div>
        </div>
        ` : ''}
        ${parsed.tags && parsed.tags.length > 0 ? `
        <div class="parse-detail">
            <div class="parse-label">Tags:</div>
            <div class="parse-value">${parsed.tags.map(tag => `<span class="tag">${tag}</span>`).join(' ')}</div>
        </div>
        ` : ''}
        ${parsed.location ? `
        <div class="parse-detail">
            <div class="parse-label">Location:</div>
            <div class="parse-value">📍 ${parsed.location}</div>
        </div>
        ` : ''}
        <div class="parse-detail">
            <div class="parse-label">AI Confidence:</div>
            <div class="parse-value">
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: ${confidence}%"></div>
                </div>
                <div class="confidence-text">${confidence}% confident</div>
            </div>
        </div>
        <div class="parse-detail">
            <div class="parse-label">Model Used:</div>
            <div class="parse-value">${data.model_used || 'Unknown'}</div>
        </div>
    `;
    
    contentDiv.innerHTML = html;
    resultDiv.style.display = 'block';
}

// Create Reminder
async function handleCreateReminder(event) {
    event.preventDefault();
    
    const naturalInput = document.getElementById('natural-input').value.trim();
    const userId = document.getElementById('user-id').value.trim();
    const timezone = document.getElementById('timezone').value;
    
    if (!naturalInput || !userId) {
        showToast('Please fill in all required fields', 'error');
        return;
    }
    
    // Save user preferences
    saveUserPreferences(userId, timezone);
    
    const submitBtn = event.target.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.textContent = '⏳ Creating...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/reminders`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                natural_input: naturalInput,
                user_id: userId,
                user_timezone: timezone
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('✅ Reminder created successfully!', 'success');
            document.getElementById('create-form').reset();
            // Restore user preferences after reset
            loadUserPreferences();
            document.getElementById('parse-result').style.display = 'none';
            loadReminders();
        } else {
            showToast(`Error: ${data.detail}`, 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = '➕ Create Reminder';
    }
}

// Load Reminders
async function loadReminders() {
    const userId = document.getElementById('user-id').value.trim() || 'user123';
    const listDiv = document.getElementById('reminders-list');
    
    // Build query params
    let params = new URLSearchParams({
        user_id: userId,
        limit: 100
    });
    
    if (currentFilters.status) params.append('status', currentFilters.status);
    if (currentFilters.priority) params.append('priority', currentFilters.priority);
    if (currentFilters.tag) params.append('tag', currentFilters.tag);
    
    try {
        const response = await fetch(`${API_BASE_URL}/reminders?${params}`);
        const data = await response.json();
        
        if (response.ok) {
            reminders = data.reminders || [];
            displayReminders(reminders);
            document.getElementById('reminder-count').textContent = data.total || 0;
        } else {
            listDiv.innerHTML = `<div class="loading" style="color: var(--danger-color);">Error loading reminders</div>`;
        }
    } catch (error) {
        listDiv.innerHTML = `<div class="loading" style="color: var(--danger-color);">Cannot connect to API</div>`;
    }
}

// Display Reminders
function displayReminders(remindersList) {
    const listDiv = document.getElementById('reminders-list');
    
    try {
        if (remindersList.length === 0) {
            listDiv.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <p>No reminders found. Create one above!</p>
            </div>
        `;
        return;
    }
    
    const html = remindersList.map(reminder => `
        <div class="reminder-item ${reminder.status === 'completed' ? 'completed' : ''}">
            <div class="reminder-header">
                <div class="reminder-title">${escapeHtml(reminder.title)}</div>
                <span class="priority-badge priority-${reminder.priority}">${reminder.priority}</span>
            </div>
            
            ${reminder.description ? `<div class="reminder-description">${escapeHtml(reminder.description)}</div>` : ''}
            
            <div class="reminder-meta">
                ${reminder.due_date_time ? `
                    <div class="meta-item">
                        📅 ${formatDateTime(reminder.due_date_time)}
                    </div>
                ` : ''}
                ${reminder.is_recurring ? `
                    <div class="meta-item">
                        🔄 Recurring
                    </div>
                ` : ''}
                ${reminder.location ? `
                    <div class="meta-item">
                        📍 ${escapeHtml(reminder.location)}
                    </div>
                ` : ''}
                ${reminder.ai_confidence !== null && reminder.ai_confidence !== undefined ? `
                    <div class="meta-item">
                        🤖 ${Math.round(reminder.ai_confidence * 100)}% confidence
                    </div>
                ` : ''}
                <div class="meta-item">
                    🏷️ ${reminder.status}
                </div>
            </div>
            
            ${reminder.tags && reminder.tags.length > 0 ? `
                <div class="reminder-tags">
                    ${reminder.tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
                </div>
            ` : ''}
            
            <div class="reminder-actions">
                ${reminder.status !== 'completed' ? `
                    <button class="btn btn-small btn-success" data-action="complete" data-id="${reminder.id}">
                        ✅ Complete
                    </button>
                ` : ''}
                <button class="btn btn-small btn-secondary" data-action="edit" data-id="${reminder.id}">
                    ✏️ Edit
                </button>
                <button class="btn btn-small btn-danger" data-action="delete" data-id="${reminder.id}">
                    🗑️ Delete
                </button>
            </div>
        </div>
    `).join('');
    
    listDiv.innerHTML = html;
    
    } catch (error) {
        console.error('Error in displayReminders:', error);
        listDiv.innerHTML = `<div class="loading" style="color: var(--danger-color);">Error displaying reminders: ${error.message}</div>`;
    }
}

// Complete Reminder
async function completeReminder(id) {
    if (!confirm('Mark this reminder as completed?')) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/reminders/${id}/complete`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showToast('✅ Reminder marked as completed!', 'success');
            loadReminders();
        } else {
            const data = await response.json();
            showToast(`Error: ${data.detail}`, 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

// Edit Reminder
function editReminder(id) {
    const reminder = reminders.find(r => r.id === id);
    
    if (!reminder) {
        showToast('Reminder not found', 'error');
        return;
    }
    
    document.getElementById('edit-id').value = reminder.id;
    document.getElementById('edit-title').value = reminder.title;
    document.getElementById('edit-description').value = reminder.description || '';
    document.getElementById('edit-priority').value = reminder.priority;
    document.getElementById('edit-status').value = reminder.status;
    document.getElementById('edit-tags').value = reminder.tags ? reminder.tags.join(', ') : '';
    
    document.getElementById('edit-modal').style.display = 'block';
}

// Update Reminder
async function handleUpdateReminder(event) {
    event.preventDefault();
    
    const id = document.getElementById('edit-id').value;
    const updateData = {
        title: document.getElementById('edit-title').value,
        description: document.getElementById('edit-description').value,
        priority: document.getElementById('edit-priority').value,
        status: document.getElementById('edit-status').value,
        tags: document.getElementById('edit-tags').value.split(',').map(t => t.trim()).filter(t => t)
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/reminders/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updateData)
        });
        
        if (response.ok) {
            showToast('✅ Reminder updated successfully!', 'success');
            closeEditModal();
            loadReminders();
        } else {
            const data = await response.json();
            showToast(`Error: ${data.detail}`, 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

// Delete Reminder
async function deleteReminder(id) {
    if (!confirm('Are you sure you want to delete this reminder? This action cannot be undone.')) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/reminders/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showToast('🗑️ Reminder deleted successfully!', 'success');
            loadReminders();
        } else {
            const data = await response.json();
            showToast(`Error: ${data.detail}`, 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

// Filter Change
function handleFilterChange() {
    currentFilters.status = document.getElementById('filter-status').value;
    currentFilters.priority = document.getElementById('filter-priority').value;
    currentFilters.tag = document.getElementById('filter-tag').value.trim();
    loadReminders();
}

// Close Edit Modal
function closeEditModal() {
    document.getElementById('edit-modal').style.display = 'none';
}

// Show Toast Notification
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;
    
    setTimeout(() => {
        toast.className = 'toast';
    }, 4000);
}

// Utility Functions
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDateTime(dateString) {
    if (!dateString) return 'Not set';
    
    const date = new Date(dateString);
    const now = new Date();
    
    // Compare dates only (ignore time)
    const dateOnly = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    const todayOnly = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const daysDiff = Math.round((dateOnly - todayOnly) / (1000 * 60 * 60 * 24));
    
    const options = {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    
    const formatted = date.toLocaleString('en-US', options);
    
    // Add relative time
    let relative = '';
    if (daysDiff === 0) {
        relative = ' (Today)';
    } else if (daysDiff === 1) {
        relative = ' (Tomorrow)';
    } else if (daysDiff === -1) {
        relative = ' (Yesterday)';
    } else if (daysDiff < 0) {
        relative = ` (${Math.abs(daysDiff)} days ago)`;
    } else if (daysDiff > 0 && daysDiff < 7) {
        relative = ` (in ${daysDiff} days)`;
    }
    
    return formatted + relative;
}
