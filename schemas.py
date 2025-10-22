"""
Pydantic schemas for API request/response validation.
These define the structure of data sent to and received from the API.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Literal
from datetime import datetime


# Request Schemas

class ReminderCreateRequest(BaseModel):
    """Request schema for creating a reminder with natural language."""
    natural_input: str = Field(..., description="Natural language reminder input")
    user_id: str = Field(..., description="User identifier")
    user_timezone: str = Field(default="America/New_York", description="User's timezone")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "natural_input": "Call mom tomorrow at 3pm",
                "user_id": "user123",
                "user_timezone": "America/New_York"
            }
        }
    )


class ReminderUpdateRequest(BaseModel):
    """Request schema for updating a reminder."""
    title: Optional[str] = None
    description: Optional[str] = None
    due_date_time: Optional[datetime] = None
    timezone: Optional[str] = None
    status: Optional[Literal["pending", "completed", "cancelled"]] = None
    priority: Optional[Literal["urgent", "high", "medium", "low"]] = None
    tags: Optional[List[str]] = None
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[dict] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Call mom",
                "priority": "high",
                "tags": ["personal", "family"]
            }
        }
    )


class ParseOnlyRequest(BaseModel):
    """Request schema for parsing without creating a reminder."""
    natural_input: str = Field(..., description="Natural language reminder input")
    user_timezone: str = Field(default="America/New_York", description="User's timezone")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "natural_input": "Team meeting every Monday at 9am",
                "user_timezone": "America/New_York"
            }
        }
    )


# Response Schemas

class ReminderResponse(BaseModel):
    """Response schema for a single reminder."""
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    due_date_time: datetime
    timezone: str
    is_recurring: bool
    recurrence_pattern: Optional[dict] = None
    status: str
    completed_at: Optional[datetime] = None
    priority: str
    tags: List[str]
    location: Optional[str] = None
    natural_language_input: Optional[str] = None
    parsed_by_ai: bool
    ai_confidence: Optional[float] = None  # 0.0-1.0
    last_notified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        """Override to convert ai_confidence from integer (0-100) to float (0.0-1.0)."""
        instance = super().model_validate(obj, *args, **kwargs)
        # Convert integer percentage (0-100) to float (0.0-1.0)
        if instance.ai_confidence is not None and instance.ai_confidence > 1:
            instance.ai_confidence = instance.ai_confidence / 100.0
        return instance


class ReminderCreateResponse(BaseModel):
    """Response schema for creating a reminder."""
    reminder: ReminderResponse
    parsing_details: Optional[dict] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "reminder": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "user_id": "user123",
                    "title": "Call mom",
                    "due_date_time": "2025-10-23T15:00:00-04:00",
                    "timezone": "America/New_York",
                    "priority": "medium",
                    "status": "pending"
                },
                "parsing_details": {
                    "confidence": 0.85,
                    "model": "gpt-4o-mini"
                }
            }
        }
    )


class ReminderListResponse(BaseModel):
    """Response schema for listing reminders."""
    reminders: List[ReminderResponse]
    total: int
    page: int
    page_size: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "reminders": [],
                "total": 10,
                "page": 1,
                "page_size": 50
            }
        }
    )


class ParseOnlyResponse(BaseModel):
    """Response schema for parse-only endpoint."""
    parsed: dict
    confidence: float
    model: str
    original_input: str
    validation: dict
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "parsed": {
                    "title": "Team meeting",
                    "due_date_time": "2025-10-28T09:00:00-04:00",
                    "priority": "medium",
                    "is_recurring": True
                },
                "confidence": 0.85,
                "model": "gpt-4o-mini",
                "original_input": "Team meeting every Monday at 9am",
                "validation": {
                    "is_valid": True,
                    "error": None
                }
            }
        }
    )


class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""
    status: str
    timestamp: datetime
    database: str
    openai: str
    version: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "timestamp": "2025-10-22T10:00:00",
                "database": "connected",
                "openai": "configured",
                "version": "1.0.0"
            }
        }
    )


class ErrorResponse(BaseModel):
    """Response schema for errors."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "Reminder not found",
                "detail": "No reminder exists with id: 550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2025-10-22T10:00:00"
            }
        }
    )


class SuccessResponse(BaseModel):
    """Generic success response."""
    message: str
    timestamp: datetime
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Reminder deleted successfully",
                "timestamp": "2025-10-22T10:00:00"
            }
        }
    )
