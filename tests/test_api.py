"""
Integration tests for REST API
Tests all endpoints with various scenarios
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Import app and dependencies
from main import app, get_db
from models import Base
from database import SessionLocal

# Create test database
TEST_DATABASE_URL = "sqlite:///./test_reminders.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Create test client
client = TestClient(app)

# Test user ID
TEST_USER_ID = "test_user_123"


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()


# Override database dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Setup test database before each test."""
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    yield
    # Drop tables after test
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def sample_reminder_data():
    """Sample reminder data for testing."""
    return {
        "natural_input": "Call mom tomorrow at 3pm",
        "user_id": TEST_USER_ID,
        "user_timezone": "America/New_York"
    }


# Test Root and Health Endpoints

def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "endpoints" in data


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "openai" in data
    assert data["database"] == "connected"


# Test Parse Only Endpoint

def test_parse_only_simple():
    """Test parsing simple reminder without saving."""
    response = client.post(
        "/reminders/parse",
        json={
            "natural_input": "Buy milk tomorrow at 5pm",
            "user_timezone": "America/New_York"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "parsed" in data
    assert "confidence" in data
    assert "validation" in data
    assert data["parsed"]["title"] is not None
    assert data["validation"]["is_valid"] is True


def test_parse_only_recurring():
    """Test parsing recurring reminder."""
    response = client.post(
        "/reminders/parse",
        json={
            "natural_input": "Team meeting every Monday at 9am",
            "user_timezone": "America/New_York"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["parsed"]["is_recurring"] is True
    assert "recurrence_pattern" in data["parsed"]


def test_parse_only_urgent():
    """Test parsing urgent reminder."""
    response = client.post(
        "/reminders/parse",
        json={
            "natural_input": "URGENT: Submit report by Friday",
            "user_timezone": "America/New_York"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["parsed"]["priority"] in ["urgent", "high"]


# Test Create Reminder

@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not available")
def test_create_reminder_simple(sample_reminder_data):
    """Test creating a simple reminder."""
    response = client.post("/reminders", json=sample_reminder_data)
    assert response.status_code == 201
    data = response.json()
    assert "reminder" in data
    assert "parsing_details" in data
    
    reminder = data["reminder"]
    assert reminder["user_id"] == TEST_USER_ID
    assert reminder["title"] is not None
    assert reminder["status"] == "pending"
    assert reminder["parsed_by_ai"] is True
    
    parsing = data["parsing_details"]
    assert "confidence" in parsing
    assert "model" in parsing


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not available")
def test_create_reminder_recurring():
    """Test creating recurring reminder."""
    response = client.post(
        "/reminders",
        json={
            "natural_input": "Gym workout every Tuesday at 6am",
            "user_id": TEST_USER_ID,
            "user_timezone": "America/New_York"
        }
    )
    assert response.status_code == 201
    data = response.json()
    reminder = data["reminder"]
    assert reminder["is_recurring"] is True
    assert reminder["recurrence_pattern"] is not None


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not available")
def test_create_reminder_with_location():
    """Test creating reminder with location."""
    response = client.post(
        "/reminders",
        json={
            "natural_input": "Doctor appointment at City Hospital tomorrow at 2pm",
            "user_id": TEST_USER_ID,
            "user_timezone": "America/New_York"
        }
    )
    assert response.status_code == 201
    data = response.json()
    reminder = data["reminder"]
    assert reminder["location"] is not None


# Test Get Reminders

@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not available")
def test_get_reminders_empty():
    """Test getting reminders when none exist."""
    response = client.get("/reminders", params={"user_id": TEST_USER_ID})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["reminders"] == []


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not available")
def test_get_reminders_after_create(sample_reminder_data):
    """Test getting reminders after creating one."""
    # Create a reminder
    create_response = client.post("/reminders", json=sample_reminder_data)
    assert create_response.status_code == 201
    
    # Get reminders
    get_response = client.get("/reminders", params={"user_id": TEST_USER_ID})
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["total"] == 1
    assert len(data["reminders"]) == 1


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not available")
def test_get_reminders_with_pagination(sample_reminder_data):
    """Test pagination."""
    # Create multiple reminders
    for i in range(5):
        client.post("/reminders", json=sample_reminder_data)
    
    # Get with pagination
    response = client.get("/reminders", params={"user_id": TEST_USER_ID, "page": 1, "page_size": 2})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["reminders"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2


# Test Get Single Reminder

@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not available")
def test_get_single_reminder(sample_reminder_data):
    """Test getting a specific reminder."""
    # Create a reminder
    create_response = client.post("/reminders", json=sample_reminder_data)
    reminder_id = create_response.json()["reminder"]["id"]
    
    # Get the reminder
    get_response = client.get(f"/reminders/{reminder_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == reminder_id
    assert data["user_id"] == TEST_USER_ID


def test_get_single_reminder_not_found():
    """Test getting non-existent reminder."""
    response = client.get("/reminders/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


# Test Update Reminder

@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not available")
def test_update_reminder_priority(sample_reminder_data):
    """Test updating reminder priority."""
    # Create a reminder
    create_response = client.post("/reminders", json=sample_reminder_data)
    reminder_id = create_response.json()["reminder"]["id"]
    
    # Update priority
    update_response = client.put(
        f"/reminders/{reminder_id}",
        json={"priority": "high"}
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["priority"] == "high"


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not available")
def test_update_reminder_tags(sample_reminder_data):
    """Test updating reminder tags."""
    # Create a reminder
    create_response = client.post("/reminders", json=sample_reminder_data)
    reminder_id = create_response.json()["reminder"]["id"]
    
    # Update tags
    update_response = client.put(
        f"/reminders/{reminder_id}",
        json={"tags": ["important", "family", "personal"]}
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert "important" in data["tags"]
    assert "family" in data["tags"]


def test_update_reminder_not_found():
    """Test updating non-existent reminder."""
    response = client.put(
        "/reminders/00000000-0000-0000-0000-000000000000",
        json={"title": "Test"}
    )
    assert response.status_code == 404


# Test Complete Reminder

@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not available")
def test_complete_reminder(sample_reminder_data):
    """Test completing a reminder."""
    # Create a reminder
    create_response = client.post("/reminders", json=sample_reminder_data)
    reminder_id = create_response.json()["reminder"]["id"]
    
    # Complete the reminder
    complete_response = client.post(f"/reminders/{reminder_id}/complete")
    assert complete_response.status_code == 200
    data = complete_response.json()
    assert data["status"] == "completed"
    assert data["completed_at"] is not None


def test_complete_reminder_not_found():
    """Test completing non-existent reminder."""
    response = client.post("/reminders/00000000-0000-0000-0000-000000000000/complete")
    assert response.status_code == 404


# Test Delete Reminder

@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not available")
def test_delete_reminder(sample_reminder_data):
    """Test deleting a reminder."""
    # Create a reminder
    create_response = client.post("/reminders", json=sample_reminder_data)
    reminder_id = create_response.json()["reminder"]["id"]
    
    # Delete the reminder
    delete_response = client.delete(f"/reminders/{reminder_id}")
    assert delete_response.status_code == 200
    data = delete_response.json()
    assert "deleted successfully" in data["message"]
    
    # Verify it's gone
    get_response = client.get(f"/reminders/{reminder_id}")
    assert get_response.status_code == 404


def test_delete_reminder_not_found():
    """Test deleting non-existent reminder."""
    response = client.delete("/reminders/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


# Test Filtering

@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not available")
def test_filter_by_status(sample_reminder_data):
    """Test filtering reminders by status."""
    # Create reminders
    create_response = client.post("/reminders", json=sample_reminder_data)
    reminder_id = create_response.json()["reminder"]["id"]
    client.post("/reminders", json=sample_reminder_data)
    
    # Complete one
    client.post(f"/reminders/{reminder_id}/complete")
    
    # Filter by pending
    response = client.get("/reminders", params={"user_id": TEST_USER_ID, "status": "pending"})
    assert response.status_code == 200
    data = response.json()
    assert all(r["status"] == "pending" for r in data["reminders"])
    
    # Filter by completed
    response = client.get("/reminders", params={"user_id": TEST_USER_ID, "status": "completed"})
    assert response.status_code == 200
    data = response.json()
    assert all(r["status"] == "completed" for r in data["reminders"])


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not available")
def test_filter_by_priority():
    """Test filtering reminders by priority."""
    # Create high priority reminder
    client.post(
        "/reminders",
        json={
            "natural_input": "URGENT: Submit report",
            "user_id": TEST_USER_ID,
            "user_timezone": "America/New_York"
        }
    )
    
    # Create medium priority reminder
    client.post(
        "/reminders",
        json={
            "natural_input": "Review document",
            "user_id": TEST_USER_ID,
            "user_timezone": "America/New_York"
        }
    )
    
    # Filter by high/urgent priority
    response = client.get("/reminders", params={"user_id": TEST_USER_ID, "priority": "high"})
    assert response.status_code == 200


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not available")
def test_filter_by_tag(sample_reminder_data):
    """Test filtering reminders by tag."""
    # Create a reminder
    create_response = client.post("/reminders", json=sample_reminder_data)
    reminder_id = create_response.json()["reminder"]["id"]
    
    # Add specific tag
    client.put(
        f"/reminders/{reminder_id}",
        json={"tags": ["test_tag"]}
    )
    
    # Filter by tag
    response = client.get("/reminders", params={"user_id": TEST_USER_ID, "tag": "test_tag"})
    assert response.status_code == 200
    data = response.json()
    assert all("test_tag" in r["tags"] for r in data["reminders"])


# Test Due Reminders

@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not available")
def test_get_due_reminders():
    """Test getting due reminders."""
    # Create a past-due reminder
    client.post(
        "/reminders",
        json={
            "natural_input": "This was due yesterday",
            "user_id": TEST_USER_ID,
            "user_timezone": "America/New_York"
        }
    )
    
    # Get due reminders
    response = client.get("/reminders/due/now", params={"user_id": TEST_USER_ID})
    assert response.status_code == 200
    data = response.json()
    assert "reminders" in data
    assert "total" in data


# Test Error Handling

def test_create_reminder_invalid_data():
    """Test creating reminder with invalid data."""
    response = client.post(
        "/reminders",
        json={"invalid": "data"}
    )
    assert response.status_code == 422  # Validation error


def test_parse_only_empty_input():
    """Test parsing with empty input."""
    response = client.post(
        "/reminders/parse",
        json={
            "natural_input": "",
            "user_timezone": "America/New_York"
        }
    )
    # Should either fail validation or return error
    assert response.status_code in [400, 422, 500]


# Cleanup

@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    """Cleanup test database after all tests."""
    yield
    import os
    if os.path.exists("./test_reminders.db"):
        os.remove("./test_reminders.db")
