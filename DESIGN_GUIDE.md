# Reminder App Design Guide
## Building an Advanced Reminder System with OpenAI API

**Version:** 1.0  
**Last Updated:** October 20, 2025

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Core Components](#core-components)
4. [OpenAI API Integration](#openai-api-integration)
5. [Database Design](#database-design)
6. [Features & Capabilities](#features--capabilities)
7. [Implementation Roadmap](#implementation-roadmap)
8. [Security & Best Practices](#security--best-practices)
9. [Scalability Considerations](#scalability-considerations)
10. [Code Examples](#code-examples)

---

## Executive Summary

This design guide outlines the architecture for building a production-ready reminder application that leverages OpenAI's API to provide intelligent task management capabilities without the limitations found in ChatGPT's reminder feature (such as the 20-task limit).

### Key Advantages Over ChatGPT Reminders

- **Unlimited Tasks**: No artificial cap on reminder count
- **Persistent Storage**: Reminders stored in your own database
- **Custom Scheduling**: Advanced recurrence patterns and time zones
- **Multi-user Support**: Scale to thousands of users
- **Custom Integrations**: Connect with calendars, email, SMS, etc.
- **Advanced NLP**: Leverage GPT-4 for intelligent parsing
- **Full Control**: Own your data and functionality

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Layer                            │
│  (Web App / Mobile App / Browser Extension / CLI)           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTPS/REST API
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   API Gateway Layer                          │
│  (Authentication, Rate Limiting, Request Routing)            │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌────────────────┐      ┌────────────────────┐
│  Application   │      │   OpenAI API       │
│  Service       │◄────►│   Integration      │
│  Layer         │      │   Service          │
└────────┬───────┘      └────────────────────┘
         │                       ▲
         │                       │
         ▼                       │
┌────────────────────────────────┴────────────────────────────┐
│               Business Logic Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Reminder    │  │  NLP Parser  │  │  Scheduler   │     │
│  │  Manager     │  │  (OpenAI)    │  │  Service     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌────────────────┐      ┌────────────────────┐
│   Database     │      │  Notification      │
│   (PostgreSQL/ │      │  Service           │
│   MongoDB)     │      │  (Email/SMS/Push)  │
└────────────────┘      └────────────────────┘
```

### Technology Stack Recommendations

#### Backend Options
- **Python**: Flask/FastAPI + OpenAI SDK + SQLAlchemy
- **Node.js**: Express/NestJS + OpenAI SDK + Prisma/TypeORM
- **C#/.NET**: ASP.NET Core + Azure OpenAI SDK + Entity Framework
- **Go**: Gin/Echo + OpenAI API + GORM

#### Database Options
- **PostgreSQL**: Best for structured data, ACID compliance
- **MongoDB**: Flexible schema, good for rapid development
- **SQLite**: Simple single-user applications
- **Azure Cosmos DB**: Cloud-native, global distribution

#### Frontend Options
- **Web App**: React/Vue/Angular + TypeScript
- **Mobile**: React Native / Flutter
- **Browser Extension**: Chrome Extension API + React
- **Desktop**: Electron / Tauri

---

## Core Components

### 1. Reminder Entity Model

```typescript
interface Reminder {
  id: string;
  userId: string;
  title: string;
  description?: string;
  dueDateTime: DateTime;
  timezone: string;
  
  // Recurrence
  isRecurring: boolean;
  recurrencePattern?: {
    frequency: 'daily' | 'weekly' | 'monthly' | 'yearly' | 'custom';
    interval: number;
    daysOfWeek?: number[];
    dayOfMonth?: number;
    endDate?: DateTime;
  };
  
  // Status
  status: 'active' | 'completed' | 'snoozed' | 'cancelled';
  completedAt?: DateTime;
  
  // Notifications
  notificationChannels: ('push' | 'email' | 'sms')[];
  notificationLeadTime: number; // minutes before
  
  // Metadata
  priority: 'low' | 'medium' | 'high' | 'urgent';
  tags: string[];
  location?: {
    address: string;
    coordinates: { lat: number; lng: number };
  };
  
  // AI Processing
  naturalLanguageInput?: string;
  parsedByAI: boolean;
  confidence?: number;
  
  // Timestamps
  createdAt: DateTime;
  updatedAt: DateTime;
  lastNotifiedAt?: DateTime;
}
```

---

## OpenAI API Integration

### 1. Authentication Setup

#### Using OpenAI API (Python)

```python
import os
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)
```

#### Using Azure OpenAI (Python)

```python
import os
from openai import OpenAI

# Initialize Azure OpenAI client
client = OpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    base_url="https://YOUR-RESOURCE-NAME.openai.azure.com/openai/v1/"
)
```

### 2. Natural Language Parsing with Function Calling

The core feature is using OpenAI's function calling capability to parse natural language reminders into structured data.

```python
from typing import Optional, List, Literal
from pydantic import BaseModel
from datetime import datetime
import openai

class RecurrencePattern(BaseModel):
    frequency: Literal['daily', 'weekly', 'monthly', 'yearly', 'custom']
    interval: int
    days_of_week: Optional[List[int]] = None
    day_of_month: Optional[int] = None
    end_date: Optional[str] = None

class ReminderSchema(BaseModel):
    title: str
    description: Optional[str] = None
    due_date_time: str  # ISO 8601 format
    timezone: str = "UTC"
    is_recurring: bool = False
    recurrence_pattern: Optional[RecurrencePattern] = None
    priority: Literal['low', 'medium', 'high', 'urgent'] = 'medium'
    tags: List[str] = []
    location: Optional[str] = None

def parse_reminder_with_openai(natural_language_input: str, user_timezone: str = "UTC") -> dict:
    """
    Parse natural language reminder into structured data using OpenAI.
    """
    
    # Define the function schema for OpenAI
    tools = [openai.pydantic_function_tool(ReminderSchema)]
    
    # Current date/time for context
    current_datetime = datetime.now().isoformat()
    
    messages = [
        {
            "role": "system",
            "content": f"""You are an expert reminder parsing assistant. 
            Parse the user's natural language reminder into structured data.
            Current date/time: {current_datetime}
            User timezone: {user_timezone}
            
            Guidelines:
            - Extract the task title, due date/time, and any other details
            - Convert relative times (e.g., "tomorrow", "next week") to absolute ISO 8601 format
            - Detect recurring patterns (daily, weekly, monthly)
            - Infer priority from urgency words (urgent, important, ASAP)
            - Extract location information if mentioned
            - Tag based on context (work, personal, health, etc.)
            """
        },
        {
            "role": "user",
            "content": natural_language_input
        }
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o",  # or "gpt-4o-mini" for cost savings
        messages=messages,
        tools=tools,
        tool_choice="required"
    )
    
    # Extract the parsed reminder
    tool_call = response.choices[0].message.tool_calls[0]
    reminder_data = eval(tool_call.function.arguments)
    
    return {
        "reminder": reminder_data,
        "confidence": 0.95,  # You can implement confidence scoring
        "original_input": natural_language_input
    }
```

### 3. Example Parsing Scenarios

```python
# Example 1: Simple reminder
result = parse_reminder_with_openai(
    "Remind me to call mom tomorrow at 3pm",
    user_timezone="America/New_York"
)
# Output:
# {
#   "title": "Call mom",
#   "due_date_time": "2025-10-21T15:00:00-04:00",
#   "priority": "medium",
#   "tags": ["personal"]
# }

# Example 2: Recurring reminder
result = parse_reminder_with_openai(
    "Every Monday at 9am remind me about the team standup meeting"
)
# Output:
# {
#   "title": "Team standup meeting",
#   "due_date_time": "2025-10-27T09:00:00Z",  # Next Monday
#   "is_recurring": True,
#   "recurrence_pattern": {
#     "frequency": "weekly",
#     "interval": 1,
#     "days_of_week": [1]  # Monday
#   },
#   "tags": ["work", "meeting"]
# }

# Example 3: Complex reminder with location
result = parse_reminder_with_openai(
    "URGENT: Pick up prescription from CVS on Main Street by Friday 5pm"
)
# Output:
# {
#   "title": "Pick up prescription",
#   "due_date_time": "2025-10-24T17:00:00Z",
#   "priority": "urgent",
#   "location": "CVS on Main Street",
#   "tags": ["health", "errands"]
# }
```

### 4. Enhanced Context with Conversation History

For more intelligent parsing, maintain conversation context:

```python
def parse_reminder_with_context(
    natural_language_input: str,
    conversation_history: List[dict],
    user_timezone: str = "UTC"
) -> dict:
    """
    Parse reminder with conversation context for follow-up commands.
    """
    
    tools = [openai.pydantic_function_tool(ReminderSchema)]
    
    messages = [
        {
            "role": "system",
            "content": f"""You are a reminder assistant with context awareness.
            Current time: {datetime.now().isoformat()}
            User timezone: {user_timezone}
            
            Handle follow-up commands like:
            - "Make that 6pm instead"
            - "Also add a note to bring the contract"
            - "Change it to weekly"
            """
        },
        *conversation_history,
        {
            "role": "user",
            "content": natural_language_input
        }
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools
    )
    
    return response
```

### 5. Smart Reminder Suggestions

Use OpenAI to suggest optimal reminder times:

```python
def suggest_reminder_time(task: str, user_context: dict) -> List[dict]:
    """
    Suggest optimal reminder times based on task and user context.
    """
    
    messages = [
        {
            "role": "system",
            "content": """You are a productivity expert. Suggest optimal times 
            for reminders based on the task type and user's schedule."""
        },
        {
            "role": "user",
            "content": f"""Task: {task}
            User Context:
            - Work hours: {user_context.get('work_hours', '9am-5pm')}
            - Timezone: {user_context.get('timezone', 'UTC')}
            - Preferred morning time: {user_context.get('morning_time', '8am')}
            
            Suggest 3 optimal reminder times and explain why.
            """
        }
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    
    return response.choices[0].message.content
```

---

## Database Design

### PostgreSQL Schema

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    timezone VARCHAR(50) DEFAULT 'UTC',
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Reminders table
CREATE TABLE reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Core fields
    title VARCHAR(500) NOT NULL,
    description TEXT,
    due_date_time TIMESTAMP WITH TIME ZONE NOT NULL,
    timezone VARCHAR(50) NOT NULL,
    
    -- Recurrence
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_pattern JSONB,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'snoozed', 'cancelled')),
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Notifications
    notification_channels TEXT[] DEFAULT ARRAY['push'],
    notification_lead_time INTEGER DEFAULT 15, -- minutes
    last_notified_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    location JSONB,
    
    -- AI Processing
    natural_language_input TEXT,
    parsed_by_ai BOOLEAN DEFAULT FALSE,
    ai_confidence DECIMAL(3,2),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Indexes for performance
CREATE INDEX idx_reminders_user_id ON reminders(user_id);
CREATE INDEX idx_reminders_due_date ON reminders(due_date_time);
CREATE INDEX idx_reminders_status ON reminders(status);
CREATE INDEX idx_reminders_user_status_due ON reminders(user_id, status, due_date_time);
CREATE INDEX idx_reminders_tags ON reminders USING GIN(tags);

-- Notification history table
CREATE TABLE notification_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reminder_id UUID NOT NULL REFERENCES reminders(id) ON DELETE CASCADE,
    channel VARCHAR(20) NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'sent',
    error_message TEXT,
    metadata JSONB
);

-- User preferences table
CREATE TABLE user_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    work_hours_start TIME DEFAULT '09:00:00',
    work_hours_end TIME DEFAULT '17:00:00',
    quiet_hours_start TIME DEFAULT '22:00:00',
    quiet_hours_end TIME DEFAULT '08:00:00',
    default_notification_channel VARCHAR(20) DEFAULT 'push',
    default_lead_time INTEGER DEFAULT 15,
    language VARCHAR(10) DEFAULT 'en',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Conversation context table (for multi-turn interactions)
CREATE TABLE conversation_context (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID NOT NULL,
    messages JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP + INTERVAL '1 hour'
);

CREATE INDEX idx_conversation_user_session ON conversation_context(user_id, session_id);
```

### MongoDB Schema (Alternative)

```javascript
// users collection
{
  _id: ObjectId,
  email: String,
  username: String,
  timezone: String,
  preferences: {
    workHoursStart: String,
    workHoursEnd: String,
    quietHoursStart: String,
    quietHoursEnd: String,
    defaultNotificationChannel: String,
    defaultLeadTime: Number,
    language: String
  },
  createdAt: Date,
  updatedAt: Date
}

// reminders collection
{
  _id: ObjectId,
  userId: ObjectId,
  title: String,
  description: String,
  dueDateTime: Date,
  timezone: String,
  
  isRecurring: Boolean,
  recurrencePattern: {
    frequency: String,
    interval: Number,
    daysOfWeek: [Number],
    dayOfMonth: Number,
    endDate: Date
  },
  
  status: String,
  completedAt: Date,
  
  notificationChannels: [String],
  notificationLeadTime: Number,
  lastNotifiedAt: Date,
  
  priority: String,
  tags: [String],
  location: {
    address: String,
    coordinates: {
      lat: Number,
      lng: Number
    }
  },
  
  naturalLanguageInput: String,
  parsedByAI: Boolean,
  aiConfidence: Number,
  
  createdAt: Date,
  updatedAt: Date
}

// Indexes
db.reminders.createIndex({ userId: 1, status: 1, dueDateTime: 1 })
db.reminders.createIndex({ dueDateTime: 1 })
db.reminders.createIndex({ tags: 1 })
```

---

## Features & Capabilities

### 1. Core Features

#### Natural Language Input
- **Simple**: "Remind me to call John at 3pm"
- **Relative**: "Remind me tomorrow morning"
- **Recurring**: "Every Monday at 9am"
- **Complex**: "Remind me to review the proposal every day next week except Wednesday"

#### Smart Scheduling
- Automatic timezone conversion
- Conflict detection (overlapping reminders)
- Workday vs weekend awareness
- Quiet hours respect

#### Multiple Notification Channels
- Push notifications
- Email
- SMS
- Webhook/API callbacks
- Browser notifications
- Mobile app notifications

#### Recurring Patterns
- Daily, weekly, monthly, yearly
- Custom intervals (every 3 days, every 2 weeks)
- Specific days (Mon, Wed, Fri)
- End date or occurrence count
- Skip patterns (except holidays)

### 2. Advanced Features

#### AI-Powered Enhancements

```python
class AIEnhancedReminderService:
    """Advanced AI features for reminder management."""
    
    def suggest_related_tasks(self, reminder: dict) -> List[dict]:
        """Suggest related tasks based on current reminder."""
        
        messages = [
            {
                "role": "system",
                "content": "You are a productivity assistant. Suggest related tasks."
            },
            {
                "role": "user",
                "content": f"""I have a reminder: "{reminder['title']}"
                Suggest 3-5 related tasks I might need to complete."""
            }
        ]
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        
        return response.choices[0].message.content
    
    def prioritize_reminders(self, reminders: List[dict]) -> List[dict]:
        """Use AI to prioritize reminders based on urgency and importance."""
        
        reminder_list = "\n".join([
            f"- {r['title']} (due: {r['due_date_time']})"
            for r in reminders
        ])
        
        messages = [
            {
                "role": "system",
                "content": """You are a time management expert using the 
                Eisenhower Matrix (urgent/important). Analyze and prioritize tasks."""
            },
            {
                "role": "user",
                "content": f"Here are my pending reminders:\n{reminder_list}\n\n" +
                          "Prioritize them in order of what I should tackle first."
            }
        ]
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        
        return response.choices[0].message.content
    
    def generate_reminder_summary(self, user_id: str, period: str = "today") -> str:
        """Generate a natural language summary of reminders."""
        
        # Fetch reminders from database
        reminders = self.get_user_reminders(user_id, period)
        
        messages = [
            {
                "role": "system",
                "content": "Create a concise, friendly summary of the user's reminders."
            },
            {
                "role": "user",
                "content": f"Summarize these {period}'s reminders:\n" +
                          "\n".join([f"- {r['title']} at {r['due_date_time']}" 
                                    for r in reminders])
            }
        ]
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        
        return response.choices[0].message.content
    
    def detect_reminder_conflicts(self, new_reminder: dict, existing_reminders: List[dict]) -> dict:
        """Detect scheduling conflicts using AI."""
        
        messages = [
            {
                "role": "system",
                "content": """You are a scheduling assistant. Detect conflicts and 
                suggest optimal times."""
            },
            {
                "role": "user",
                "content": f"""New reminder: {new_reminder['title']} at {new_reminder['due_date_time']}
                
                Existing reminders:
                """ + "\n".join([f"- {r['title']} at {r['due_date_time']}" 
                                for r in existing_reminders]) +
                "\n\nAre there any conflicts? Suggest alternatives if needed."
            }
        ]
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        
        return response.choices[0].message.content
```

#### Location-Based Reminders

```python
def create_location_reminder(title: str, location: str, trigger: str = "arrive") -> dict:
    """
    Create location-based reminders.
    Trigger can be 'arrive' or 'leave'.
    """
    
    # Use OpenAI to parse the location
    messages = [
        {
            "role": "system",
            "content": "Extract location details and suggest coordinates."
        },
        {
            "role": "user",
            "content": f"Location: {location}\nProvide address and approximate coordinates."
        }
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )
    
    # Parse response and create reminder with location data
    return {
        "title": title,
        "location": location,
        "trigger": trigger,
        "parsed_location": response.choices[0].message.content
    }
```

#### Smart Snooze Suggestions

```python
def suggest_snooze_times(reminder: dict, current_time: datetime) -> List[dict]:
    """Suggest intelligent snooze times based on context."""
    
    messages = [
        {
            "role": "system",
            "content": "Suggest optimal snooze times based on task urgency and time of day."
        },
        {
            "role": "user",
            "content": f"""Task: {reminder['title']}
            Original time: {reminder['due_date_time']}
            Current time: {current_time}
            Priority: {reminder.get('priority', 'medium')}
            
            Suggest 3 snooze options with reasoning."""
        }
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    
    return response.choices[0].message.content
```

---

## Implementation Roadmap

### Phase 1: MVP - Local Development Setup (4-6 weeks)

> **💡 Cost-Effective Approach**: This phase uses only local infrastructure and free-tier services. The only paid service required is OpenAI API (~$5-20/month for development).

#### Local Infrastructure Setup

**Required Tools (All Free)**
- **Python 3.10+** or **Node.js 18+**: Runtime environment
- **SQLite**: Local database (no server needed, file-based)
- **OpenAI API Key**: Only paid component (~$0.002 per request with GPT-4o-mini)
- **VS Code** or any text editor
- **Postman** or **Thunder Client**: API testing (optional)

**Optional for Enhanced Experience**
- **PostgreSQL**: Can run locally via Docker or installer
- **Redis**: Local instance for caching (optional in Phase 1)

---

## Sub-Phase 1.1: Database Foundation (3-4 days)

**Goal**: Set up database schema and basic CRUD operations

### Setup

```bash
# 1. Create project directory
mkdir reminder-app
cd reminder-app

# 2. Set up Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install minimal dependencies
pip install sqlalchemy python-dotenv pytest

# 4. Create .env file
cat > .env << EOF
DATABASE_URL=sqlite:///./reminders.db
ENVIRONMENT=development
EOF
```

### Implementation Tasks

- [ ] Create database models (`models.py`)
- [ ] Set up SQLAlchemy connection (`database.py`)
- [ ] Implement CRUD functions for reminders (`crud.py`)
- [ ] Create database initialization script

### Code Structure

```python
# models.py
from sqlalchemy import Column, String, DateTime, Boolean, JSON, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Reminder(Base):
    __tablename__ = "reminders"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(String, nullable=True)
    due_date_time = Column(DateTime, nullable=False, index=True)
    timezone = Column(String(50), nullable=False, default="UTC")
    
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(JSON, nullable=True)
    
    status = Column(String(20), default="active", index=True)
    completed_at = Column(DateTime, nullable=True)
    
    priority = Column(String(20), default="medium")
    tags = Column(JSON, default=list)
    
    natural_language_input = Column(String, nullable=True)
    parsed_by_ai = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### POC Demo

```python
# demo_database.py
from database import SessionLocal, engine, init_db
from models import Base, Reminder
from datetime import datetime, timedelta

def demo():
    """Demonstrate database CRUD operations."""
    
    # Initialize database
    init_db()
    print("✅ Database initialized")
    
    # Create session
    db = SessionLocal()
    
    # Create a reminder
    reminder = Reminder(
        user_id="demo_user",
        title="Test Reminder",
        description="This is a test",
        due_date_time=datetime.utcnow() + timedelta(days=1),
        timezone="America/New_York",
        priority="high",
        tags=["test", "demo"]
    )
    db.add(reminder)
    db.commit()
    print(f"✅ Created reminder: {reminder.id}")
    
    # Read reminders
    reminders = db.query(Reminder).filter_by(user_id="demo_user").all()
    print(f"✅ Found {len(reminders)} reminder(s)")
    for r in reminders:
        print(f"   - {r.title} (due: {r.due_date_time})")
    
    # Update reminder
    reminder.status = "completed"
    reminder.completed_at = datetime.utcnow()
    db.commit()
    print(f"✅ Updated reminder status to: {reminder.status}")
    
    # Delete reminder
    db.delete(reminder)
    db.commit()
    print(f"✅ Deleted reminder")
    
    db.close()
    print("\n🎉 Database POC Demo Complete!")

if __name__ == "__main__":
    demo()
```

### Integration Tests

```python
# tests/test_database.py
import pytest
from datetime import datetime, timedelta
from database import SessionLocal, init_db
from models import Reminder

@pytest.fixture
def db_session():
    """Create a test database session."""
    init_db()
    db = SessionLocal()
    yield db
    db.close()

def test_create_reminder(db_session):
    """Test creating a reminder."""
    reminder = Reminder(
        user_id="test_user",
        title="Test Reminder",
        due_date_time=datetime.utcnow() + timedelta(days=1),
        timezone="UTC"
    )
    db_session.add(reminder)
    db_session.commit()
    
    assert reminder.id is not None
    assert reminder.status == "active"
    assert reminder.created_at is not None

def test_read_reminders(db_session):
    """Test reading reminders."""
    # Create test reminders
    for i in range(3):
        reminder = Reminder(
            user_id="test_user",
            title=f"Reminder {i}",
            due_date_time=datetime.utcnow() + timedelta(days=i+1),
            timezone="UTC"
        )
        db_session.add(reminder)
    db_session.commit()
    
    # Query reminders
    reminders = db_session.query(Reminder).filter_by(user_id="test_user").all()
    assert len(reminders) == 3

def test_update_reminder(db_session):
    """Test updating a reminder."""
    reminder = Reminder(
        user_id="test_user",
        title="Test",
        due_date_time=datetime.utcnow() + timedelta(days=1),
        timezone="UTC"
    )
    db_session.add(reminder)
    db_session.commit()
    
    reminder.status = "completed"
    reminder.completed_at = datetime.utcnow()
    db_session.commit()
    
    updated = db_session.query(Reminder).filter_by(id=reminder.id).first()
    assert updated.status == "completed"
    assert updated.completed_at is not None

def test_delete_reminder(db_session):
    """Test deleting a reminder."""
    reminder = Reminder(
        user_id="test_user",
        title="Test",
        due_date_time=datetime.utcnow() + timedelta(days=1),
        timezone="UTC"
    )
    db_session.add(reminder)
    db_session.commit()
    reminder_id = reminder.id
    
    db_session.delete(reminder)
    db_session.commit()
    
    deleted = db_session.query(Reminder).filter_by(id=reminder_id).first()
    assert deleted is None
```

### Run Tests

```bash
# Install pytest
pip install pytest

# Run tests
pytest tests/test_database.py -v

# Expected output:
# tests/test_database.py::test_create_reminder PASSED
# tests/test_database.py::test_read_reminders PASSED
# tests/test_database.py::test_update_reminder PASSED
# tests/test_database.py::test_delete_reminder PASSED
```

### Verification Checklist

- [ ] Database file created (`reminders.db`)
- [ ] Can create reminders with all fields
- [ ] Can query reminders by user_id and status
- [ ] Can update reminder status and fields
- [ ] Can delete reminders
- [ ] All tests pass

**Deliverable**: Working database layer with passing tests

---

## Sub-Phase 1.2: OpenAI Integration (3-4 days)

**Goal**: Parse natural language into structured reminder data

### Setup

```bash
# Install additional dependencies
pip install openai pydantic

# Update .env file
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
```

### Implementation Tasks

- [ ] Create OpenAI service module (`openai_service.py`)
- [ ] Define Pydantic schemas for structured output
- [ ] Implement natural language parsing with function calling
- [ ] Add caching for common patterns
- [ ] Handle parsing errors gracefully

### Code Structure

```python
# openai_service.py
import os
import openai
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import datetime
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class RecurrencePattern(BaseModel):
    frequency: Literal['daily', 'weekly', 'monthly', 'yearly']
    interval: int = 1
    days_of_week: Optional[List[int]] = None

class ParsedReminder(BaseModel):
    title: str
    description: Optional[str] = None
    due_date_time: str  # ISO 8601 format
    timezone: str = "UTC"
    is_recurring: bool = False
    recurrence_pattern: Optional[RecurrencePattern] = None
    priority: Literal['low', 'medium', 'high', 'urgent'] = 'medium'
    tags: List[str] = []

def parse_reminder(natural_input: str, user_timezone: str = "UTC") -> dict:
    """Parse natural language into structured reminder data."""
    
    current_time = datetime.now().isoformat()
    
    messages = [
        {
            "role": "system",
            "content": f"""You are a reminder parsing assistant.
Current time: {current_time}
User timezone: {user_timezone}

Parse the user's input into a structured reminder.
Convert relative times to absolute ISO 8601 format.
Detect recurring patterns and priority from context."""
        },
        {
            "role": "user",
            "content": natural_input
        }
    ]
    
    tools = [openai.pydantic_function_tool(ParsedReminder)]
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="required"
    )
    
    tool_call = response.choices[0].message.tool_calls[0]
    parsed_data = json.loads(tool_call.function.arguments)
    
    return {
        "parsed": parsed_data,
        "original_input": natural_input,
        "confidence": 0.95
    }
```

### POC Demo

```python
# demo_openai.py
from openai_service import parse_reminder
from dotenv import load_dotenv

load_dotenv()

def demo():
    """Demonstrate OpenAI parsing capabilities."""
    
    test_inputs = [
        "Remind me to call mom tomorrow at 3pm",
        "Every Monday at 9am team standup meeting",
        "URGENT: Submit report by Friday 5pm",
        "Buy groceries next Saturday morning",
        "Weekly team lunch every Thursday at noon"
    ]
    
    print("🤖 OpenAI Natural Language Parsing Demo\n")
    
    for input_text in test_inputs:
        print(f"Input: '{input_text}'")
        
        try:
            result = parse_reminder(input_text, user_timezone="America/New_York")
            parsed = result['parsed']
            
            print(f"✅ Title: {parsed['title']}")
            print(f"   Due: {parsed['due_date_time']}")
            print(f"   Priority: {parsed['priority']}")
            print(f"   Recurring: {parsed['is_recurring']}")
            if parsed.get('tags'):
                print(f"   Tags: {', '.join(parsed['tags'])}")
            print()
            
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    print("🎉 OpenAI POC Demo Complete!")

if __name__ == "__main__":
    demo()
```

### Integration Tests

```python
# tests/test_openai_service.py
import pytest
from openai_service import parse_reminder
from datetime import datetime
import os

@pytest.fixture
def openai_available():
    """Check if OpenAI API key is available."""
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OpenAI API key not available")

def test_parse_simple_reminder(openai_available):
    """Test parsing a simple reminder."""
    result = parse_reminder("Remind me to call John tomorrow at 3pm")
    parsed = result['parsed']
    
    assert 'call' in parsed['title'].lower() or 'john' in parsed['title'].lower()
    assert parsed['due_date_time'] is not None
    assert parsed['priority'] in ['low', 'medium', 'high', 'urgent']

def test_parse_urgent_reminder(openai_available):
    """Test detecting urgency."""
    result = parse_reminder("URGENT: Submit report today")
    parsed = result['parsed']
    
    assert parsed['priority'] in ['high', 'urgent']

def test_parse_recurring_reminder(openai_available):
    """Test parsing recurring patterns."""
    result = parse_reminder("Every Monday at 9am team meeting")
    parsed = result['parsed']
    
    assert parsed['is_recurring'] == True
    assert parsed['recurrence_pattern'] is not None
    assert parsed['recurrence_pattern']['frequency'] == 'weekly'

def test_parse_with_timezone(openai_available):
    """Test timezone handling."""
    result = parse_reminder(
        "Meeting tomorrow at 2pm",
        user_timezone="America/Los_Angeles"
    )
    parsed = result['parsed']
    
    assert parsed['timezone'] is not None

def test_error_handling():
    """Test handling of empty or invalid input."""
    with pytest.raises(Exception):
        parse_reminder("")
```

### Run Tests

```bash
pytest tests/test_openai_service.py -v

# Expected output:
# tests/test_openai_service.py::test_parse_simple_reminder PASSED
# tests/test_openai_service.py::test_parse_urgent_reminder PASSED
# tests/test_openai_service.py::test_parse_recurring_reminder PASSED
# tests/test_openai_service.py::test_parse_with_timezone PASSED
```

### Verification Checklist

- [ ] Can parse simple time expressions ("tomorrow at 3pm")
- [ ] Detects urgency from keywords (URGENT, ASAP)
- [ ] Identifies recurring patterns (daily, weekly, monthly)
- [ ] Handles timezone conversions
- [ ] Returns structured JSON output
- [ ] All tests pass

**Deliverable**: Working OpenAI parser with passing tests

---

## Sub-Phase 1.3: REST API (4-5 days)

**Goal**: Create FastAPI endpoints to manage reminders

### Setup

```bash
# Install FastAPI dependencies
pip install fastapi uvicorn python-jose[cryptography] passlib[bcrypt]
```

### Implementation Tasks

- [ ] Create FastAPI application (`main.py`)
- [ ] Implement authentication (simple JWT)
- [ ] Create API endpoints (CRUD + parse)
- [ ] Add request/response schemas
- [ ] Add error handling
- [ ] Enable CORS for frontend

### Code Structure

```python
# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os

from database import SessionLocal, init_db
from models import Reminder
from openai_service import parse_reminder

app = FastAPI(title="Reminder API", version="1.0.0")

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup():
    init_db()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Request/Response schemas
class CreateReminderRequest(BaseModel):
    natural_language_input: str
    timezone: Optional[str] = "UTC"

class ReminderResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    due_date_time: datetime
    status: str
    priority: str
    
    class Config:
        from_attributes = True

# Endpoints
@app.post("/api/reminders", response_model=ReminderResponse)
def create_reminder(request: CreateReminderRequest, db = Depends(get_db)):
    """Create a reminder from natural language."""
    
    # Parse with OpenAI
    parsed = parse_reminder(request.natural_language_input, request.timezone)
    parsed_data = parsed['parsed']
    
    # Create reminder
    reminder = Reminder(
        user_id="default_user",  # TODO: Get from auth
        title=parsed_data['title'],
        description=parsed_data.get('description'),
        due_date_time=datetime.fromisoformat(parsed_data['due_date_time']),
        timezone=parsed_data['timezone'],
        priority=parsed_data['priority'],
        tags=parsed_data.get('tags', []),
        natural_language_input=request.natural_language_input,
        parsed_by_ai=True
    )
    
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    
    return reminder

@app.get("/api/reminders", response_model=List[ReminderResponse])
def list_reminders(
    status: Optional[str] = "active",
    limit: int = 50,
    db = Depends(get_db)
):
    """List reminders."""
    
    query = db.query(Reminder).filter_by(user_id="default_user")
    
    if status:
        query = query.filter_by(status=status)
    
    reminders = query.order_by(Reminder.due_date_time).limit(limit).all()
    return reminders

@app.get("/api/reminders/{reminder_id}", response_model=ReminderResponse)
def get_reminder(reminder_id: str, db = Depends(get_db)):
    """Get a specific reminder."""
    
    reminder = db.query(Reminder).filter_by(id=reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    return reminder

@app.put("/api/reminders/{reminder_id}/complete")
def complete_reminder(reminder_id: str, db = Depends(get_db)):
    """Mark reminder as complete."""
    
    reminder = db.query(Reminder).filter_by(id=reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    reminder.status = "completed"
    reminder.completed_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Reminder completed"}

@app.delete("/api/reminders/{reminder_id}")
def delete_reminder(reminder_id: str, db = Depends(get_db)):
    """Delete a reminder."""
    
    reminder = db.query(Reminder).filter_by(id=reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    db.delete(reminder)
    db.commit()
    
    return {"message": "Reminder deleted"}

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
```

### POC Demo

```bash
# Start the server
uvicorn main:app --reload --port 8000

# In another terminal, test the API:

# 1. Health check
curl http://localhost:8000/health

# 2. Create a reminder
curl -X POST http://localhost:8000/api/reminders \
  -H "Content-Type: application/json" \
  -d '{"natural_language_input": "Remind me to test the API tomorrow at 2pm"}'

# 3. List reminders
curl http://localhost:8000/api/reminders

# 4. Complete a reminder (use ID from previous response)
curl -X PUT http://localhost:8000/api/reminders/<reminder-id>/complete

# 5. Delete a reminder
curl -X DELETE http://localhost:8000/api/reminders/<reminder-id>

# 6. Open interactive docs
# Visit http://localhost:8000/docs in your browser
```

### Integration Tests

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from main import app
from database import init_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    """Initialize database before each test."""
    init_db()

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_reminder():
    """Test creating a reminder."""
    response = client.post(
        "/api/reminders",
        json={
            "natural_language_input": "Remind me to test tomorrow at 2pm",
            "timezone": "UTC"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["status"] == "active"

def test_list_reminders():
    """Test listing reminders."""
    # Create a reminder first
    client.post(
        "/api/reminders",
        json={"natural_language_input": "Test reminder tomorrow"}
    )
    
    response = client.get("/api/reminders")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_reminder():
    """Test getting a specific reminder."""
    # Create a reminder
    create_response = client.post(
        "/api/reminders",
        json={"natural_language_input": "Test reminder"}
    )
    reminder_id = create_response.json()["id"]
    
    # Get the reminder
    response = client.get(f"/api/reminders/{reminder_id}")
    assert response.status_code == 200
    assert response.json()["id"] == reminder_id

def test_complete_reminder():
    """Test completing a reminder."""
    # Create a reminder
    create_response = client.post(
        "/api/reminders",
        json={"natural_language_input": "Test reminder"}
    )
    reminder_id = create_response.json()["id"]
    
    # Complete it
    response = client.put(f"/api/reminders/{reminder_id}/complete")
    assert response.status_code == 200
    
    # Verify status changed
    get_response = client.get(f"/api/reminders/{reminder_id}")
    assert get_response.json()["status"] == "completed"

def test_delete_reminder():
    """Test deleting a reminder."""
    # Create a reminder
    create_response = client.post(
        "/api/reminders",
        json={"natural_language_input": "Test reminder"}
    )
    reminder_id = create_response.json()["id"]
    
    # Delete it
    response = client.delete(f"/api/reminders/{reminder_id}")
    assert response.status_code == 200
    
    # Verify it's gone
    get_response = client.get(f"/api/reminders/{reminder_id}")
    assert get_response.status_code == 404
```

### Run Tests

```bash
pytest tests/test_api.py -v

# Expected output:
# tests/test_api.py::test_health_check PASSED
# tests/test_api.py::test_create_reminder PASSED
# tests/test_api.py::test_list_reminders PASSED
# tests/test_api.py::test_get_reminder PASSED
# tests/test_api.py::test_complete_reminder PASSED
# tests/test_api.py::test_delete_reminder PASSED
```

### Verification Checklist

- [ ] Server starts without errors
- [ ] Interactive docs available at `/docs`
- [ ] Can create reminders via API
- [ ] Can list reminders with filters
- [ ] Can complete reminders
- [ ] Can delete reminders
- [ ] All tests pass
- [ ] CORS enabled for frontend

**Deliverable**: Working REST API with passing tests

---

## Sub-Phase 1.4: Simple UI (3-4 days)

**Goal**: Create a basic interface to interact with reminders

### Option A: Command Line Interface

```python
# cli.py
import click
import requests
from datetime import datetime
from tabulate import tabulate

API_BASE_URL = "http://localhost:8000"

@click.group()
def cli():
    """Reminder CLI - Manage your reminders from the command line."""
    pass

@cli.command()
@click.argument('text')
def add(text):
    """Add a new reminder using natural language."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/reminders",
            json={"natural_language_input": text}
        )
        response.raise_for_status()
        data = response.json()
        
        click.echo(f"✅ Reminder created:")
        click.echo(f"   ID: {data['id']}")
        click.echo(f"   Title: {data['title']}")
        click.echo(f"   Due: {data['due_date_time']}")
        click.echo(f"   Priority: {data['priority']}")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)

@cli.command()
@click.option('--status', default='active', help='Filter by status')
def list(status):
    """List all reminders."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/reminders",
            params={"status": status}
        )
        response.raise_for_status()
        reminders = response.json()
        
        if not reminders:
            click.echo("No reminders found.")
            return
        
        # Format as table
        table_data = []
        for r in reminders:
            due = datetime.fromisoformat(r['due_date_time'].replace('Z', '+00:00'))
            table_data.append([
                r['id'][:8],
                r['title'][:40],
                due.strftime('%Y-%m-%d %H:%M'),
                r['priority'],
                r['status']
            ])
        
        headers = ['ID', 'Title', 'Due Date', 'Priority', 'Status']
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)

@cli.command()
@click.argument('reminder_id')
def complete(reminder_id):
    """Mark a reminder as complete."""
    try:
        response = requests.put(f"{API_BASE_URL}/api/reminders/{reminder_id}/complete")
        response.raise_for_status()
        click.echo(f"✅ Reminder {reminder_id[:8]} marked as complete")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)

@cli.command()
@click.argument('reminder_id')
def delete(reminder_id):
    """Delete a reminder."""
    if click.confirm(f'Are you sure you want to delete reminder {reminder_id[:8]}?'):
        try:
            response = requests.delete(f"{API_BASE_URL}/api/reminders/{reminder_id}")
            response.raise_for_status()
            click.echo(f"✅ Reminder {reminder_id[:8]} deleted")
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)

if __name__ == '__main__':
    cli()
```

### Option B: Simple HTML Interface

```html
<!-- frontend/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reminder App</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #333;
            margin-bottom: 30px;
            text-align: center;
        }
        .input-section {
            margin-bottom: 30px;
        }
        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
        }
        input[type="text"] {
            flex: 1;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
        }
        button {
            padding: 15px 30px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
        }
        button:hover { background: #5568d3; }
        button:disabled { background: #ccc; cursor: not-allowed; }
        .examples {
            font-size: 14px;
            color: #666;
            margin-top: 10px;
        }
        .examples ul { padding-left: 20px; }
        .reminders-list {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .reminder-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        .reminder-card.urgent { border-left-color: #e74c3c; }
        .reminder-card.high { border-left-color: #f39c12; }
        .reminder-card.medium { border-left-color: #3498db; }
        .reminder-card.low { border-left-color: #95a5a6; }
        .reminder-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 8px;
            color: #333;
        }
        .reminder-meta {
            font-size: 14px;
            color: #666;
            margin-bottom: 15px;
        }
        .reminder-actions {
            display: flex;
            gap: 10px;
        }
        .btn-complete {
            padding: 8px 16px;
            background: #27ae60;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
        }
        .btn-delete {
            padding: 8px 16px;
            background: #e74c3c;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
        }
        .loading { text-align: center; padding: 20px; color: #666; }
        .error {
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📝 My Reminders</h1>
        
        <div class="input-section">
            <div class="input-group">
                <input 
                    type="text" 
                    id="reminderInput" 
                    placeholder="e.g., Remind me to call mom tomorrow at 3pm"
                />
                <button id="addButton">Add Reminder</button>
            </div>
            <div class="examples">
                <strong>Try:</strong>
                <ul>
                    <li>"Remind me to review the proposal by Friday"</li>
                    <li>"Every Monday at 9am team standup"</li>
                    <li>"URGENT: Submit report today at 5pm"</li>
                </ul>
            </div>
        </div>
        
        <div id="error" class="error" style="display: none;"></div>
        <div id="reminders" class="reminders-list"></div>
    </div>

    <script>
        const API_URL = 'http://localhost:8000';
        
        async function loadReminders() {
            try {
                const response = await fetch(`${API_URL}/api/reminders`);
                const reminders = await response.json();
                
                const container = document.getElementById('reminders');
                
                if (reminders.length === 0) {
                    container.innerHTML = '<div class="empty-state">No reminders yet. Add one above!</div>';
                    return;
                }
                
                container.innerHTML = reminders.map(r => `
                    <div class="reminder-card ${r.priority}">
                        <div class="reminder-title">${r.title}</div>
                        <div class="reminder-meta">
                            📅 ${new Date(r.due_date_time).toLocaleString()} 
                            | 🎯 ${r.priority}
                        </div>
                        <div class="reminder-actions">
                            <button class="btn-complete" onclick="completeReminder('${r.id}')">
                                ✓ Complete
                            </button>
                            <button class="btn-delete" onclick="deleteReminder('${r.id}')">
                                🗑 Delete
                            </button>
                        </div>
                    </div>
                `).join('');
            } catch (error) {
                showError('Failed to load reminders: ' + error.message);
            }
        }
        
        async function addReminder() {
            const input = document.getElementById('reminderInput');
            const text = input.value.trim();
            
            if (!text) return;
            
            const button = document.getElementById('addButton');
            button.disabled = true;
            button.textContent = 'Adding...';
            
            try {
                const response = await fetch(`${API_URL}/api/reminders`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ natural_language_input: text })
                });
                
                if (!response.ok) throw new Error('Failed to create reminder');
                
                input.value = '';
                await loadReminders();
            } catch (error) {
                showError('Failed to add reminder: ' + error.message);
            } finally {
                button.disabled = false;
                button.textContent = 'Add Reminder';
            }
        }
        
        async function completeReminder(id) {
            try {
                await fetch(`${API_URL}/api/reminders/${id}/complete`, {
                    method: 'PUT'
                });
                await loadReminders();
            } catch (error) {
                showError('Failed to complete reminder: ' + error.message);
            }
        }
        
        async function deleteReminder(id) {
            if (!confirm('Delete this reminder?')) return;
            
            try {
                await fetch(`${API_URL}/api/reminders/${id}`, {
                    method: 'DELETE'
                });
                await loadReminders();
            } catch (error) {
                showError('Failed to delete reminder: ' + error.message);
            }
        }
        
        function showError(message) {
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            setTimeout(() => errorDiv.style.display = 'none', 5000);
        }
        
        // Event listeners
        document.getElementById('addButton').addEventListener('click', addReminder);
        document.getElementById('reminderInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') addReminder();
        });
        
        // Load reminders on page load
        loadReminders();
    </script>
</body>
</html>
```

### POC Demo

```bash
# For CLI Option:
pip install click requests tabulate

# Start backend (Terminal 1)
uvicorn main:app --reload --port 8000

# Use CLI (Terminal 2)
python cli.py add "Test reminder tomorrow at 2pm"
python cli.py list
python cli.py complete <reminder-id>

# For HTML Option:
# Start backend (Terminal 1)
uvicorn main:app --reload --port 8000

# Serve frontend (Terminal 2)
cd frontend
python -m http.server 3000

# Open browser to http://localhost:3000
```

### Integration Tests

```python
# tests/test_cli.py
from click.testing import CliRunner
from cli import cli
import requests_mock

def test_cli_add():
    """Test adding reminder via CLI."""
    runner = CliRunner()
    
    with requests_mock.Mocker() as m:
        m.post('http://localhost:8000/api/reminders', json={
            'id': '123',
            'title': 'Test',
            'due_date_time': '2025-10-21T14:00:00Z',
            'priority': 'medium'
        })
        
        result = runner.invoke(cli, ['add', 'Test reminder tomorrow'])
        assert result.exit_code == 0
        assert '✅ Reminder created' in result.output

def test_cli_list():
    """Test listing reminders via CLI."""
    runner = CliRunner()
    
    with requests_mock.Mocker() as m:
        m.get('http://localhost:8000/api/reminders', json=[{
            'id': '123',
            'title': 'Test',
            'due_date_time': '2025-10-21T14:00:00Z',
            'priority': 'medium',
            'status': 'active'
        }])
        
        result = runner.invoke(cli, ['list'])
        assert result.exit_code == 0
        assert 'Test' in result.output
```

### Verification Checklist

- [ ] Can add reminders through UI
- [ ] Reminders display with correct information
- [ ] Can complete reminders
- [ ] Can delete reminders
- [ ] UI updates automatically after actions
- [ ] Error messages display properly
- [ ] Responsive to different screen sizes (HTML option)

**Deliverable**: Working user interface (CLI or HTML)

---

## Sub-Phase 1.5: Background Scheduler (2-3 days)

**Goal**: Automatically check and notify for due reminders

### Setup

```bash
pip install schedule
```

### Implementation

```python
# scheduler.py
import schedule
import time
import threading
from datetime import datetime, timedelta
from database import SessionLocal
from models import Reminder
import smtplib
from email.mime.text import MIMEText
import os

class ReminderScheduler:
    """Simple background scheduler for reminders."""
    
    def __init__(self):
        self.running = False
        self.thread = None
    
    def check_due_reminders(self):
        """Check for reminders due in the next 5 minutes."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking for due reminders...")
        
        db = SessionLocal()
        try:
            now = datetime.utcnow()
            soon = now + timedelta(minutes=5)
            
            # Find reminders due soon that haven't been notified recently
            reminders = db.query(Reminder).filter(
                Reminder.status == 'active',
                Reminder.due_date_time >= now,
                Reminder.due_date_time <= soon
            ).all()
            
            for reminder in reminders:
                # Check if already notified in last 10 minutes
                if reminder.last_notified_at:
                    time_since_notify = now - reminder.last_notified_at
                    if time_since_notify < timedelta(minutes=10):
                        continue
                
                print(f"🔔 REMINDER DUE: {reminder.title}")
                self.send_notification(reminder, db)
        
        finally:
            db.close()
    
    def send_notification(self, reminder, db):
        """Send notification for a reminder."""
        
        # Console notification (always)
        print(f"""
        ╔════════════════════════════════════════╗
        ║          REMINDER ALERT!               ║
        ╠════════════════════════════════════════╣
        ║ {reminder.title[:40]:^40} ║
        ║ Due: {str(reminder.due_date_time)[:21]:^40} ║
        ║ Priority: {reminder.priority.upper():^31} ║
        ╚════════════════════════════════════════╝
        """)
        
        # Email notification (if configured)
        if os.getenv('GMAIL_ADDRESS'):
            try:
                self.send_email(reminder)
            except Exception as e:
                print(f"Failed to send email: {e}")
        
        # Update last_notified_at
        reminder.last_notified_at = datetime.utcnow()
        db.commit()
    
    def send_email(self, reminder):
        """Send email notification via Gmail."""
        sender = os.getenv('GMAIL_ADDRESS')
        password = os.getenv('GMAIL_APP_PASSWORD')
        recipient = os.getenv('NOTIFICATION_EMAIL', sender)
        
        if not (sender and password):
            return
        
        msg = MIMEText(f"""
Hi!

This is your reminder:

📌 {reminder.title}
🕐 Due: {reminder.due_date_time}
🎯 Priority: {reminder.priority}

---
Sent from your Reminder App
        """)
        
        msg['Subject'] = f"Reminder: {reminder.title}"
        msg['From'] = sender
        msg['To'] = recipient
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        
        print(f"✅ Email sent to {recipient}")
    
    def start(self):
        """Start the scheduler in a background thread."""
        if self.running:
            return
        
        self.running = True
        
        def run_scheduler():
            # Check every minute
            schedule.every(1).minutes.do(self.check_due_reminders)
            
            print("✅ Scheduler started (checking every minute)")
            
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        
        self.thread = threading.Thread(target=run_scheduler, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the scheduler."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("✅ Scheduler stopped")

# Add to main.py
from scheduler import ReminderScheduler

scheduler = ReminderScheduler()

@app.on_event("startup")
async def startup():
    init_db()
    scheduler.start()

@app.on_event("shutdown")
async def shutdown():
    scheduler.stop()
```

### POC Demo

```python
# demo_scheduler.py
from scheduler import ReminderScheduler
from database import SessionLocal, init_db
from models import Reminder
from datetime import datetime, timedelta
import time

def demo():
    """Demonstrate the scheduler."""
    
    # Initialize database
    init_db()
    db = SessionLocal()
    
    # Create a reminder due in 2 minutes
    reminder = Reminder(
        user_id="demo_user",
        title="Test Scheduler Notification",
        description="This should trigger in 2 minutes",
        due_date_time=datetime.utcnow() + timedelta(minutes=2),
        timezone="UTC",
        priority="high"
    )
    db.add(reminder)
    db.commit()
    
    print(f"✅ Created test reminder due at {reminder.due_date_time}")
    print("   Scheduler will check every minute...")
    
    # Start scheduler
    scheduler = ReminderScheduler()
    scheduler.start()
    
    # Wait for 5 minutes to see notification
    try:
        print("\n⏳ Waiting for notification (press Ctrl+C to stop)...")
        time.sleep(300)
    except KeyboardInterrupt:
        print("\n\nStopping demo...")
    finally:
        scheduler.stop()
        db.close()
    
    print("🎉 Scheduler Demo Complete!")

if __name__ == "__main__":
    demo()
```

### Integration Tests

```python
# tests/test_scheduler.py
import pytest
from scheduler import ReminderScheduler
from database import SessionLocal, init_db
from models import Reminder
from datetime import datetime, timedelta
import time

def test_scheduler_detects_due_reminders():
    """Test that scheduler detects due reminders."""
    init_db()
    db = SessionLocal()
    
    # Create reminder due now
    reminder = Reminder(
        user_id="test_user",
        title="Test Due Now",
        due_date_time=datetime.utcnow() + timedelta(minutes=1),
        timezone="UTC"
    )
    db.add(reminder)
    db.commit()
    reminder_id = reminder.id
    
    # Run check
    scheduler = ReminderScheduler()
    scheduler.check_due_reminders()
    
    # Verify last_notified_at was updated
    db.refresh(reminder)
    assert reminder.last_notified_at is not None
    
    db.close()

def test_scheduler_skips_already_notified():
    """Test that scheduler doesn't notify twice."""
    init_db()
    db = SessionLocal()
    
    # Create reminder already notified
    reminder = Reminder(
        user_id="test_user",
        title="Test Already Notified",
        due_date_time=datetime.utcnow() + timedelta(minutes=1),
        timezone="UTC",
        last_notified_at=datetime.utcnow()
    )
    db.add(reminder)
    db.commit()
    last_notified = reminder.last_notified_at
    
    # Run check
    scheduler = ReminderScheduler()
    scheduler.check_due_reminders()
    
    # Verify last_notified_at hasn't changed
    db.refresh(reminder)
    assert reminder.last_notified_at == last_notified
    
    db.close()
```

### Run Tests

```bash
pytest tests/test_scheduler.py -v
```

### Verification Checklist

- [ ] Scheduler starts automatically with API
- [ ] Checks for due reminders every minute
- [ ] Console notifications appear for due reminders
- [ ] Email notifications sent (if configured)
- [ ] Doesn't duplicate notifications
- [ ] All tests pass
- [ ] Can run for extended periods without crashes

**Deliverable**: Working background scheduler

---

## Phase 1 Complete: Final Integration Test

### End-to-End Test

```python
# tests/test_e2e.py
import pytest
from fastapi.testclient import TestClient
from main import app
from database import init_db
from datetime import datetime, timedelta
import time

client = TestClient(app)

def test_complete_workflow():
    """Test the complete reminder workflow."""
    
    # 1. Create a reminder
    create_response = client.post(
        "/api/reminders",
        json={
            "natural_language_input": "Team meeting tomorrow at 2pm",
            "timezone": "America/New_York"
        }
    )
    assert create_response.status_code == 200
    reminder = create_response.json()
    assert "team meeting" in reminder["title"].lower()
    
    # 2. List reminders
    list_response = client.get("/api/reminders")
    assert list_response.status_code == 200
    reminders = list_response.json()
    assert len(reminders) >= 1
    assert any(r["id"] == reminder["id"] for r in reminders)
    
    # 3. Get specific reminder
    get_response = client.get(f"/api/reminders/{reminder['id']}")
    assert get_response.status_code == 200
    fetched = get_response.json()
    assert fetched["title"] == reminder["title"]
    
    # 4. Complete reminder
    complete_response = client.put(f"/api/reminders/{reminder['id']}/complete")
    assert complete_response.status_code == 200
    
    # 5. Verify status changed
    check_response = client.get(f"/api/reminders/{reminder['id']}")
    assert check_response.json()["status"] == "completed"
    
    # 6. Delete reminder
    delete_response = client.delete(f"/api/reminders/{reminder['id']}")
    assert delete_response.status_code == 200
    
    # 7. Verify deletion
    final_response = client.get(f"/api/reminders/{reminder['id']}")
    assert final_response.status_code == 404
    
    print("✅ Complete end-to-end workflow test passed!")
```

### Run Complete Test Suite

```bash
# Run all tests
pytest tests/ -v

# Expected output:
# tests/test_database.py::test_create_reminder PASSED
# tests/test_database.py::test_read_reminders PASSED
# tests/test_database.py::test_update_reminder PASSED
# tests/test_database.py::test_delete_reminder PASSED
# tests/test_openai_service.py::test_parse_simple_reminder PASSED
# tests/test_openai_service.py::test_parse_urgent_reminder PASSED
# tests/test_openai_service.py::test_parse_recurring_reminder PASSED
# tests/test_api.py::test_health_check PASSED
# tests/test_api.py::test_create_reminder PASSED
# tests/test_api.py::test_list_reminders PASSED
# tests/test_api.py::test_get_reminder PASSED
# tests/test_api.py::test_complete_reminder PASSED
# tests/test_api.py::test_delete_reminder PASSED
# tests/test_scheduler.py::test_scheduler_detects_due_reminders PASSED
# tests/test_scheduler.py::test_scheduler_skips_already_notified PASSED
# tests/test_e2e.py::test_complete_workflow PASSED
#
# ================= 16 passed in 12.34s =================
```

### Phase 1 Final Deliverables

✅ **Database Layer**: SQLite with full CRUD operations  
✅ **OpenAI Integration**: Natural language parsing  
✅ **REST API**: FastAPI with all endpoints  
✅ **User Interface**: CLI or HTML frontend  
✅ **Background Scheduler**: Automatic notifications  
✅ **Complete Test Suite**: 16+ passing tests  
✅ **Documentation**: Setup and usage guides  

### Total Cost for Phase 1

| Item | Cost |
|------|------|
| OpenAI API | $5-20/month |
| Everything else | FREE |
| **Total** | **$5-20/month** |

**Next**: Move to Phase 2 for recurring reminders, advanced scheduling, and more features!

#### Phase 1 Complete Project Structure

```
reminder-app/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── models.py               # Database models
│   ├── schemas.py              # Pydantic schemas
│   ├── database.py             # SQLite connection
│   ├── auth.py                 # Simple JWT auth
│   ├── openai_service.py       # OpenAI integration
│   └── reminders.db            # SQLite database file
├── frontend/
│   ├── index.html              # Simple web UI (Option B)
│   ├── style.css
│   └── app.js
├── cli.py                      # CLI tool (Option A)
├── streamlit_app.py            # Streamlit UI (Option C)
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (git-ignored)
├── .gitignore
└── README.md
```

#### Local Testing Workflow

```bash
# Terminal 1: Start backend server
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Test API
curl -X POST http://localhost:8000/api/reminders \
  -H "Content-Type: application/json" \
  -d '{"natural_language_input": "Remind me to test the app tomorrow"}'

# Terminal 3: Start frontend (if using Option B)
cd frontend
python -m http.server 3000

# Or use CLI (Option A)
python cli.py add "Remind me to test the app tomorrow"
```

#### Free Email Notifications Setup

**Using Gmail SMTP (No Cost)**

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_notification(reminder: dict, recipient_email: str):
    """Send reminder via Gmail SMTP (free)."""
    
    # Use your Gmail account (enable "App Passwords" in Google Account settings)
    sender_email = "your.email@gmail.com"
    app_password = os.getenv("GMAIL_APP_PASSWORD")  # Not your regular password!
    
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = f"Reminder: {reminder['title']}"
    
    body = f"""
    Hi!
    
    This is your reminder:
    
    📌 {reminder['title']}
    🕐 Due: {reminder['due_date_time']}
    
    Priority: {reminder['priority']}
    
    ---
    Sent from your local Reminder App
    """
    
    message.attach(MIMEText(body, "plain"))
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        print(f"✅ Email sent to {recipient_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
```

**Setup Steps**:
1. Go to Google Account settings
2. Enable 2-Step Verification
3. Generate an "App Password" for mail
4. Use that password in your `.env` file

```bash
# Add to .env
GMAIL_ADDRESS=your.email@gmail.com
GMAIL_APP_PASSWORD=your-16-char-app-password
```

#### Background Task Scheduler (Local)

**Simple Approach: No Celery/Redis Needed**

```python
import schedule
import time
import threading
from datetime import datetime, timedelta

class LocalScheduler:
    """Simple local scheduler for checking reminders."""
    
    def __init__(self):
        self.running = False
    
    def check_due_reminders(self):
        """Check for reminders due in the next 5 minutes."""
        print(f"[{datetime.now()}] Checking for due reminders...")
        
        # Query database
        conn = sqlite3.connect('reminders.db')
        cursor = conn.cursor()
        
        now = datetime.utcnow()
        soon = now + timedelta(minutes=5)
        
        cursor.execute("""
            SELECT id, user_id, title, due_date_time, notification_channels
            FROM reminders
            WHERE status = 'active'
            AND due_date_time BETWEEN ? AND ?
            AND (last_notified_at IS NULL OR last_notified_at < ?)
        """, (now.isoformat(), soon.isoformat(), (now - timedelta(minutes=10)).isoformat()))
        
        reminders = cursor.fetchall()
        
        for reminder in reminders:
            self.send_notification(reminder)
        
        conn.close()
    
    def send_notification(self, reminder):
        """Send notification for reminder."""
        # Send email, log to console, etc.
        print(f"🔔 REMINDER: {reminder[2]} is due at {reminder[3]}")
        # Update last_notified_at in database
    
    def start(self):
        """Start the scheduler in a background thread."""
        self.running = True
        
        def run_scheduler():
            # Check every minute
            schedule.every(1).minutes.do(self.check_due_reminders)
            
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        
        thread = threading.Thread(target=run_scheduler, daemon=True)
        thread.start()
        print("✅ Scheduler started (checking every minute)")
    
    def stop(self):
        """Stop the scheduler."""
        self.running = False

# Usage in main.py
scheduler = LocalScheduler()

@app.on_event("startup")
async def startup_event():
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.stop()
```

**Install**:
```bash
pip install schedule
```

#### Cost Breakdown for Phase 1

| Component | Cost | Notes |
|-----------|------|-------|
| OpenAI API | $5-20/month | ~2,500-10,000 requests with GPT-4o-mini |
| SQLite | Free | Local file-based database |
| Python/Node.js | Free | Open source |
| Gmail SMTP | Free | 500 emails/day limit |
| Local Development | Free | Your own computer |
| Domain Name | Optional | $12/year if you want custom domain later |
| **Total** | **$5-20/month** | **Just OpenAI API!** |

#### Migration Path to Production (Future Phases)

When ready to scale, you can gradually migrate:

1. **Database**: SQLite → PostgreSQL (free tier: Railway, Supabase, Neon)
2. **Hosting**: Local → Cloud (free tier: Railway, Fly.io, Render)
3. **Cache**: In-memory → Redis (free tier: Redis Cloud, Upstash)
4. **Background Jobs**: Schedule library → Celery (when needed)
5. **Monitoring**: Console logs → Free tools (Sentry free tier, Logflare)

All of these have generous free tiers that work for initial production deployments!

#### Quick Start Commands

```bash
# Clone or create project
git clone <your-repo> reminder-app  # or create from scratch
cd reminder-app

# Backend setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
echo "OPENAI_API_KEY=sk-your-key" > .env
echo "DATABASE_URL=sqlite:///./reminders.db" >> .env

# Initialize database
python -c "from database import init_db; init_db()"

# Run backend
uvicorn main:app --reload --port 8000

# In another terminal, run CLI
python cli.py add "Test reminder tomorrow at 2pm"
python cli.py list

# Or open browser to http://localhost:8000/docs for API playground
```

---

### Phase 2: Enhanced Features (6-8 weeks)

**Week 7-9: Recurring Reminders**
- [ ] Recurrence pattern engine
- [ ] Calendar integration
- [ ] Bulk operations

**Week 10-12: Notifications & Scheduling**
- [ ] Push notification service
- [ ] SMS integration
- [ ] Background job scheduler (Celery/Bull)
- [ ] Notification preferences

**Week 13-14: AI Enhancements**
- [ ] Smart suggestions
- [ ] Conflict detection
- [ ] Priority recommendations
- [ ] Daily/weekly summaries

### Phase 3: Advanced Features (8-10 weeks)

**Week 15-17: Collaboration**
- [ ] Shared reminders
- [ ] Team workspaces
- [ ] Delegation features

**Week 18-20: Integrations**
- [ ] Calendar sync (Google, Outlook, Apple)
- [ ] Task manager integrations (Todoist, Asana, etc.)
- [ ] Voice assistant integration (Alexa, Google Home)

**Week 21-24: Mobile & Extensions**
- [ ] Mobile app (iOS/Android)
- [ ] Browser extension
- [ ] Offline support
- [ ] Widget support

### Phase 4: Production & Scale (4-6 weeks)

**Week 25-27: Performance & Reliability**
- [ ] Caching layer (Redis)
- [ ] Database optimization
- [ ] Load testing
- [ ] Monitoring and logging

**Week 28-30: Launch Preparation**
- [ ] Security audit
- [ ] Documentation
- [ ] User onboarding
- [ ] Beta testing
- [ ] Production deployment

---

## Security & Best Practices

### 1. API Key Management

```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# NEVER hardcode API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Use secret management services in production
# - AWS Secrets Manager
# - Azure Key Vault
# - Google Cloud Secret Manager
# - HashiCorp Vault
```

### 2. Rate Limiting & Cost Control

```python
from functools import wraps
import time
from collections import defaultdict

class RateLimiter:
    """Simple rate limiter for OpenAI API calls."""
    
    def __init__(self, max_calls: int, time_window: int):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = defaultdict(list)
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(user_id: str, *args, **kwargs):
            now = time.time()
            user_calls = self.calls[user_id]
            
            # Remove old calls outside the time window
            user_calls[:] = [call_time for call_time in user_calls 
                            if now - call_time < self.time_window]
            
            if len(user_calls) >= self.max_calls:
                raise Exception("Rate limit exceeded")
            
            user_calls.append(now)
            return func(user_id, *args, **kwargs)
        
        return wrapper

# Usage
@RateLimiter(max_calls=10, time_window=60)  # 10 calls per minute
def parse_reminder_rate_limited(user_id: str, text: str):
    return parse_reminder_with_openai(text)
```

### 3. Input Validation & Sanitization

```python
from pydantic import BaseModel, validator, Field
from datetime import datetime
from typing import Optional, List

class CreateReminderRequest(BaseModel):
    """Validated reminder creation request."""
    
    natural_language_input: str = Field(..., min_length=1, max_length=1000)
    timezone: Optional[str] = Field(default="UTC", max_length=50)
    notification_channels: Optional[List[str]] = Field(default=["push"])
    
    @validator('natural_language_input')
    def sanitize_input(cls, v):
        # Remove potentially harmful content
        dangerous_patterns = ['<script', 'javascript:', 'onerror=']
        for pattern in dangerous_patterns:
            if pattern.lower() in v.lower():
                raise ValueError("Invalid input detected")
        return v.strip()
    
    @validator('notification_channels')
    def validate_channels(cls, v):
        allowed_channels = ['push', 'email', 'sms']
        for channel in v:
            if channel not in allowed_channels:
                raise ValueError(f"Invalid notification channel: {channel}")
        return v

# Usage
try:
    request = CreateReminderRequest(
        natural_language_input=user_input,
        timezone=user_timezone
    )
    # Proceed with validated data
except ValidationError as e:
    # Handle validation errors
    return {"error": str(e)}
```

### 4. Error Handling & Retry Logic

```python
from openai import OpenAI, OpenAIError
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def parse_reminder_with_retry(text: str) -> dict:
    """Parse reminder with automatic retry on failures."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Parse reminder"},
                {"role": "user", "content": text}
            ],
            timeout=30  # 30 second timeout
        )
        return response
    
    except OpenAIError as e:
        # Log the error
        logger.error(f"OpenAI API error: {str(e)}")
        
        # Fall back to simpler model if available
        if "rate_limit" in str(e).lower():
            # Implement exponential backoff
            raise  # Retry
        
        # For other errors, you might want to fall back to rule-based parsing
        return fallback_parser(text)
```

### 5. Data Privacy & Compliance

```python
class ReminderService:
    """Service with privacy-aware OpenAI integration."""
    
    def parse_reminder(self, text: str, user_id: str, anonymize: bool = True):
        """Parse reminder with optional PII anonymization."""
        
        # Anonymize PII before sending to OpenAI
        if anonymize:
            text = self.anonymize_pii(text)
        
        # Add user consent tracking
        self.log_ai_usage(user_id, "reminder_parsing")
        
        # Parse with OpenAI
        result = parse_reminder_with_openai(text)
        
        return result
    
    def anonymize_pii(self, text: str) -> str:
        """Remove or mask PII (emails, phone numbers, etc.)"""
        import re
        
        # Mask email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                     '[EMAIL]', text)
        
        # Mask phone numbers
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
        
        return text
    
    def log_ai_usage(self, user_id: str, action: str):
        """Log AI usage for compliance/audit trail."""
        # Store in database for GDPR/compliance
        pass
```

---

## Scalability Considerations

### 1. Caching Strategy

```python
import redis
from functools import wraps
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_reminder_parse(ttl: int = 3600):
    """Cache parsed reminders to reduce OpenAI API calls."""
    
    def decorator(func):
        @wraps(func)
        def wrapper(text: str, *args, **kwargs):
            # Create cache key from input
            cache_key = f"reminder_parse:{hash(text)}"
            
            # Check cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Call OpenAI API
            result = func(text, *args, **kwargs)
            
            # Store in cache
            redis_client.setex(
                cache_key,
                ttl,
                json.dumps(result)
            )
            
            return result
        
        return wrapper
    return decorator

@cache_reminder_parse(ttl=3600)
def parse_reminder_cached(text: str):
    return parse_reminder_with_openai(text)
```

### 2. Background Job Processing

```python
from celery import Celery
from datetime import datetime, timedelta

# Initialize Celery
celery_app = Celery('reminder_app', broker='redis://localhost:6379/0')

@celery_app.task
def process_due_reminders():
    """Background task to check and send notifications for due reminders."""
    
    # Find reminders due in the next 15 minutes
    now = datetime.utcnow()
    soon = now + timedelta(minutes=15)
    
    due_reminders = Reminder.query.filter(
        Reminder.status == 'active',
        Reminder.due_date_time <= soon,
        Reminder.due_date_time > now,
        Reminder.last_notified_at.is_(None)  # Not yet notified
    ).all()
    
    for reminder in due_reminders:
        send_notification.delay(reminder.id)

@celery_app.task
def send_notification(reminder_id: str):
    """Send notification for a specific reminder."""
    
    reminder = Reminder.query.get(reminder_id)
    
    for channel in reminder.notification_channels:
        if channel == 'email':
            send_email_notification(reminder)
        elif channel == 'sms':
            send_sms_notification(reminder)
        elif channel == 'push':
            send_push_notification(reminder)
    
    # Update last notified timestamp
    reminder.last_notified_at = datetime.utcnow()
    db.session.commit()

# Schedule periodic task
celery_app.conf.beat_schedule = {
    'check-due-reminders': {
        'task': 'process_due_reminders',
        'schedule': 60.0,  # Run every minute
    },
}
```

### 3. Database Query Optimization

```python
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload

class ReminderRepository:
    """Optimized database queries for reminders."""
    
    def get_upcoming_reminders(self, user_id: str, limit: int = 50):
        """Get upcoming reminders with optimized query."""
        
        return Reminder.query.filter(
            and_(
                Reminder.user_id == user_id,
                Reminder.status == 'active',
                Reminder.due_date_time >= datetime.utcnow()
            )
        ).order_by(
            Reminder.due_date_time.asc()
        ).limit(limit).all()
    
    def get_reminders_by_tag(self, user_id: str, tags: List[str]):
        """Use GIN index for efficient tag queries."""
        
        return Reminder.query.filter(
            and_(
                Reminder.user_id == user_id,
                Reminder.tags.overlap(tags)  # PostgreSQL array overlap
            )
        ).all()
    
    def bulk_update_status(self, reminder_ids: List[str], new_status: str):
        """Efficient bulk update."""
        
        Reminder.query.filter(
            Reminder.id.in_(reminder_ids)
        ).update(
            {"status": new_status, "updated_at": datetime.utcnow()},
            synchronize_session=False
        )
        db.session.commit()
```

### 4. Horizontal Scaling Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer                         │
│                   (Nginx / AWS ALB)                      │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┬───────────┐
         │                       │           │
         ▼                       ▼           ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  API Server 1   │   │  API Server 2   │   │  API Server N   │
│  (Stateless)    │   │  (Stateless)    │   │  (Stateless)    │
└─────────────────┘   └─────────────────┘   └─────────────────┘
         │                       │                   │
         └───────────┬───────────┴───────────────────┘
                     │
         ┌───────────┴───────────┬───────────────┐
         │                       │               │
         ▼                       ▼               ▼
┌─────────────────┐   ┌─────────────────┐   ┌────────────┐
│  PostgreSQL     │   │  Redis Cache    │   │  Celery    │
│  (Primary +     │   │  (Session/      │   │  Workers   │
│   Read Replicas)│   │   Cache)        │   │  (Queue)   │
└─────────────────┘   └─────────────────┘   └────────────┘
```

---

## Code Examples

### Complete FastAPI Application Structure

```python
# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
from openai import OpenAI

# Initialize FastAPI app
app = FastAPI(title="Intelligent Reminder API", version="1.0.0")

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Security
security = HTTPBearer()

# Models
class CreateReminderRequest(BaseModel):
    natural_language_input: str
    timezone: Optional[str] = "UTC"

class ReminderResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str]
    due_date_time: datetime
    status: str
    priority: str
    tags: List[str]
    created_at: datetime

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Implement your JWT verification here
    token = credentials.credentials
    # ... verify token and return user
    return {"user_id": "user123", "email": "user@example.com"}

# Routes
@app.post("/api/reminders", response_model=ReminderResponse)
async def create_reminder(
    request: CreateReminderRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a reminder using natural language input.
    
    Example inputs:
    - "Remind me to call mom tomorrow at 3pm"
    - "Every Monday at 9am team standup"
    - "Buy groceries next Saturday morning"
    """
    
    try:
        # Parse with OpenAI
        parsed_data = parse_reminder_with_openai(
            request.natural_language_input,
            request.timezone
        )
        
        # Save to database
        reminder = save_reminder_to_db(
            user_id=current_user["user_id"],
            parsed_data=parsed_data
        )
        
        return reminder
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create reminder: {str(e)}"
        )

@app.get("/api/reminders", response_model=List[ReminderResponse])
async def list_reminders(
    status: Optional[str] = "active",
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """List user's reminders."""
    
    reminders = get_user_reminders(
        user_id=current_user["user_id"],
        status=status,
        limit=limit
    )
    
    return reminders

@app.put("/api/reminders/{reminder_id}")
async def update_reminder(
    reminder_id: str,
    request: CreateReminderRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update an existing reminder."""
    
    # Verify ownership
    reminder = get_reminder_by_id(reminder_id)
    if reminder.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Parse and update
    parsed_data = parse_reminder_with_openai(
        request.natural_language_input,
        request.timezone
    )
    
    updated_reminder = update_reminder_in_db(reminder_id, parsed_data)
    return updated_reminder

@app.delete("/api/reminders/{reminder_id}")
async def delete_reminder(
    reminder_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a reminder."""
    
    reminder = get_reminder_by_id(reminder_id)
    if reminder.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    delete_reminder_from_db(reminder_id)
    return {"message": "Reminder deleted successfully"}

@app.post("/api/reminders/{reminder_id}/complete")
async def complete_reminder(
    reminder_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark a reminder as complete."""
    
    reminder = get_reminder_by_id(reminder_id)
    if reminder.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    mark_reminder_complete(reminder_id)
    return {"message": "Reminder marked as complete"}

@app.get("/api/reminders/summary")
async def get_reminder_summary(
    period: str = "today",
    current_user: dict = Depends(get_current_user)
):
    """
    Get AI-generated summary of reminders.
    Periods: today, week, month
    """
    
    service = AIEnhancedReminderService()
    summary = service.generate_reminder_summary(
        user_id=current_user["user_id"],
        period=period
    )
    
    return {"summary": summary}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### React Frontend Example

```typescript
// src/services/reminderService.ts
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

interface CreateReminderRequest {
  naturalLanguageInput: string;
  timezone?: string;
}

interface Reminder {
  id: string;
  title: string;
  description?: string;
  dueDateTime: string;
  status: string;
  priority: string;
  tags: string[];
}

class ReminderService {
  private axios = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  setAuthToken(token: string) {
    this.axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  async createReminder(data: CreateReminderRequest): Promise<Reminder> {
    const response = await this.axios.post('/api/reminders', data);
    return response.data;
  }

  async listReminders(status: string = 'active'): Promise<Reminder[]> {
    const response = await this.axios.get('/api/reminders', {
      params: { status },
    });
    return response.data;
  }

  async completeReminder(id: string): Promise<void> {
    await this.axios.post(`/api/reminders/${id}/complete`);
  }

  async deleteReminder(id: string): Promise<void> {
    await this.axios.delete(`/api/reminders/${id}`);
  }

  async getSummary(period: string = 'today'): Promise<string> {
    const response = await this.axios.get('/api/reminders/summary', {
      params: { period },
    });
    return response.data.summary;
  }
}

export const reminderService = new ReminderService();
```

```typescript
// src/components/CreateReminder.tsx
import React, { useState } from 'react';
import { reminderService } from '../services/reminderService';

export const CreateReminder: React.FC = () => {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim()) return;

    setLoading(true);
    setError(null);

    try {
      await reminderService.createReminder({
        naturalLanguageInput: input,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      });

      setInput('');
      // Trigger refresh of reminder list
      window.dispatchEvent(new Event('remindersUpdated'));
    } catch (err) {
      setError('Failed to create reminder. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="create-reminder-form">
      <div className="input-group">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="e.g., Remind me to call mom tomorrow at 3pm"
          disabled={loading}
          className="reminder-input"
        />
        <button type="submit" disabled={loading || !input.trim()}>
          {loading ? 'Creating...' : 'Add Reminder'}
        </button>
      </div>
      
      {error && <div className="error-message">{error}</div>}
      
      <div className="examples">
        <p>Try:</p>
        <ul>
          <li>"Remind me to review the proposal by Friday"</li>
          <li>"Every Monday at 9am team standup"</li>
          <li>"Call dentist next week"</li>
        </ul>
      </div>
    </form>
  );
};
```

---

## Deployment Guide

### Environment Variables

```bash
# .env.example
# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/reminders
REDIS_URL=redis://localhost:6379/0

# Application
APP_SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
DEBUG=True

# Notification Services
SENDGRID_API_KEY=...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=...

# Frontend
REACT_APP_API_URL=http://localhost:8000
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run migrations and start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/reminders
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./:/app

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=reminders
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  celery_worker:
    build: .
    command: celery -A celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/reminders
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - redis

  celery_beat:
    build: .
    command: celery -A celery_app beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/reminders
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
  redis_data:
```

---

## Conclusion

This design guide provides a comprehensive blueprint for building an intelligent reminder application powered by OpenAI's API. The system overcomes ChatGPT's limitations while providing advanced features like:

- **Unlimited reminders** with persistent storage
- **Natural language processing** using GPT-4
- **Intelligent scheduling** and conflict detection
- **Multi-channel notifications**
- **Recurring patterns** and location-based triggers
- **AI-powered insights** and suggestions

### Next Steps

1. **Start with the MVP**: Implement basic CRUD operations and OpenAI parsing
2. **Iterate based on feedback**: Add features users actually need
3. **Optimize for scale**: Implement caching, background jobs, and monitoring
4. **Ensure security**: Proper authentication, rate limiting, and data privacy
5. **Deploy and monitor**: Use proper DevOps practices and monitoring tools

### Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Celery Documentation](https://docs.celeryq.dev/)

---

**License**: MIT  
**Author**: AI Assistant  
**Date**: October 20, 2025
