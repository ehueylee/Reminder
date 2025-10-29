"""
FastAPI REST API for Reminder Application
Phase 1.3: REST API implementation
"""

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List, Literal
import os

# Import from our modules
from database import SessionLocal, init_db, engine
from models import Base
import crud
from openai_service import parse_reminder, validate_parsed_reminder, calculate_confidence
from schemas import (
    ReminderCreateRequest, ReminderUpdateRequest, ParseOnlyRequest,
    ReminderResponse, ReminderCreateResponse, ReminderListResponse,
    ParseOnlyResponse, HealthResponse, ErrorResponse, SuccessResponse
)

# Initialize database
init_db()

# Import scheduler
from scheduler import setup_default_scheduler, get_scheduler

# Lifespan events
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown."""
    # Startup
    print("🚀 Reminder API starting up...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("📖 ReDoc: http://localhost:8000/redoc")
    print("💚 Health Check: http://localhost:8000/health")
    
    # Start background scheduler
    scheduler = setup_default_scheduler(check_interval_minutes=1)
    print("⏰ Background scheduler started (checking every 1 minute)")
    
    yield
    
    # Shutdown
    print("👋 Reminder API shutting down...")
    # Stop the scheduler
    scheduler.stop()
    print("⏰ Background scheduler stopped")


# Create FastAPI app
app = FastAPI(
    title="Reminder API",
    description="Natural language reminder management API with OpenAI integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (UI)
app.mount("/ui", StaticFiles(directory="static", html=True), name="static")


# Dependency: Get database session
def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Redirect to the web UI."""
    return RedirectResponse(url="/ui/index.html")


# API info endpoint
@app.get("/api", tags=["Root"])
async def api_info():
    """API information and available endpoints."""
    return {
        "message": "Reminder API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "create": "POST /reminders",
            "list": "GET /reminders",
            "get": "GET /reminders/{id}",
            "update": "PUT /reminders/{id}",
            "delete": "DELETE /reminders/{id}",
            "parse": "POST /reminders/parse"
        }
    }


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """
    Check API health status.
    
    Returns:
        - API status
        - Database connectivity
        - OpenAI configuration status
        - Timestamp
    """
    # Check database
    db_status = "connected"
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Check OpenAI API key
    openai_status = "configured" if os.getenv("OPENAI_API_KEY") else "not configured"
    
    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        timestamp=datetime.utcnow(),
        database=db_status,
        openai=openai_status,
        version="1.0.0"
    )


# Create reminder with natural language
@app.post("/reminders", response_model=ReminderCreateResponse, tags=["Reminders"], status_code=201)
async def create_reminder(
    request: ReminderCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new reminder from natural language input.
    
    The API will:
    1. Parse the natural language input using OpenAI
    2. Extract structured data (title, due date, priority, etc.)
    3. Create and save the reminder to the database
    4. Return the created reminder with parsing details
    
    Args:
        request: Natural language input and user information
        
    Returns:
        Created reminder with parsing confidence and details
        
    Raises:
        HTTPException: If parsing fails or database error occurs
    """
    try:
        # Parse natural language input
        try:
            parse_result = parse_reminder(
                natural_input=request.natural_input,
                user_timezone=request.user_timezone,
                current_time=datetime.now()
            )
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid input: {str(e)}"
            )
        except KeyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"OpenAI response missing field: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"OpenAI parsing failed: {str(e)}"
            )
        
        parsed = parse_result.get('parsed', {})
        
        # Ensure required fields have defaults
        if 'is_recurring' not in parsed:
            parsed['is_recurring'] = False
        if 'recurrence_pattern' not in parsed:
            parsed['recurrence_pattern'] = None
        
        # Validate parsed data
        is_valid, error = validate_parsed_reminder(parsed)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Parsing validation failed: {error}"
            )
        
        # Calculate confidence
        confidence = calculate_confidence(request.natural_input, parsed)
        
        # Create reminder in database
        reminder = crud.create_reminder(
            db=db,
            user_id=request.user_id,
            title=parsed['title'],
            description=parsed.get('description'),
            due_date_time=datetime.fromisoformat(parsed['due_date_time']),
            timezone=parsed['timezone'],
            priority=parsed['priority'],
            tags=parsed.get('tags', []),
            is_recurring=parsed['is_recurring'],
            recurrence_pattern=parsed.get('recurrence_pattern'),
            location=parsed.get('location'),
            natural_language_input=request.natural_input,
            parsed_by_ai=True,
            ai_confidence=int(confidence * 100) if confidence else None
        )
        
        return ReminderCreateResponse(
            reminder=ReminderResponse.model_validate(reminder),
            parsing_details={
                "confidence": confidence,
                "model": parse_result.get('model_used', parse_result.get('model', 'unknown')),
                "original_input": request.natural_input
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating reminder: {str(e)}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating reminder: {str(e)}"
        )


# Get reminders with filtering
@app.get("/reminders", response_model=ReminderListResponse, tags=["Reminders"])
async def get_reminders(
    user_id: str = Query(..., description="User ID to fetch reminders for"),
    status: Optional[Literal["pending", "completed", "cancelled"]] = Query(None, description="Filter by status"),
    priority: Optional[Literal["urgent", "high", "medium", "low"]] = Query(None, description="Filter by priority"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Get list of reminders for a user with optional filtering.
    
    Args:
        user_id: User identifier
        status: Filter by status (pending/completed/cancelled)
        priority: Filter by priority (urgent/high/medium/low)
        tag: Filter by tag
        page: Page number (default: 1)
        page_size: Items per page (default: 50, max: 100)
        
    Returns:
        List of reminders with pagination info
    """
    try:
        # Get reminders from database
        if tag:
            reminders = crud.get_reminders_by_tag(db, user_id=user_id, tag=tag)
        else:
            reminders = crud.get_reminders_by_user(
                db, 
                user_id=user_id,
                status=status,
                priority=priority
            )
        
        # Apply pagination
        total = len(reminders)
        start = (page - 1) * page_size
        end = start + page_size
        paginated = reminders[start:end]
        
        return ReminderListResponse(
            reminders=[ReminderResponse.model_validate(r) for r in paginated],
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching reminders: {str(e)}"
        )


# Get single reminder
@app.get("/reminders/{reminder_id}", response_model=ReminderResponse, tags=["Reminders"])
async def get_reminder(
    reminder_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific reminder by ID.
    
    Args:
        reminder_id: Reminder UUID
        
    Returns:
        Reminder details
        
    Raises:
        HTTPException: If reminder not found
    """
    reminder = crud.get_reminder(db, reminder_id=reminder_id)
    if not reminder:
        raise HTTPException(
            status_code=404,
            detail=f"Reminder not found with id: {reminder_id}"
        )
    return ReminderResponse.model_validate(reminder)


# Update reminder
@app.put("/reminders/{reminder_id}", response_model=ReminderResponse, tags=["Reminders"])
async def update_reminder(
    reminder_id: str,
    request: ReminderUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update an existing reminder.
    
    Args:
        reminder_id: Reminder UUID
        request: Fields to update (only provided fields will be updated)
        
    Returns:
        Updated reminder
        
    Raises:
        HTTPException: If reminder not found or update fails
    """
    # Check if reminder exists
    existing = crud.get_reminder(db, reminder_id=reminder_id)
    if not existing:
        raise HTTPException(
            status_code=404,
            detail=f"Reminder not found with id: {reminder_id}"
        )
    
    # Build update data (only include provided fields)
    update_data = request.model_dump(exclude_unset=True)
    
    try:
        updated = crud.update_reminder(db, reminder_id=reminder_id, **update_data)
        if not updated:
            raise HTTPException(
                status_code=500,
                detail="Failed to update reminder"
            )
        return ReminderResponse.model_validate(updated)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating reminder: {str(e)}"
        )


# Delete reminder
@app.delete("/reminders/{reminder_id}", response_model=SuccessResponse, tags=["Reminders"])
async def delete_reminder(
    reminder_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a reminder.
    
    Args:
        reminder_id: Reminder UUID
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If reminder not found or deletion fails
    """
    # Check if reminder exists
    existing = crud.get_reminder(db, reminder_id=reminder_id)
    if not existing:
        raise HTTPException(
            status_code=404,
            detail=f"Reminder not found with id: {reminder_id}"
        )
    
    try:
        success = crud.delete_reminder(db, reminder_id=reminder_id)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete reminder"
            )
        return SuccessResponse(
            message=f"Reminder {reminder_id} deleted successfully",
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting reminder: {str(e)}"
        )


# Mark reminder as complete
@app.post("/reminders/{reminder_id}/complete", response_model=ReminderResponse, tags=["Reminders"])
async def complete_reminder(
    reminder_id: str,
    db: Session = Depends(get_db)
):
    """
    Mark a reminder as completed.
    
    Args:
        reminder_id: Reminder UUID
        
    Returns:
        Updated reminder with completed status
        
    Raises:
        HTTPException: If reminder not found or completion fails
    """
    # Check if reminder exists
    existing = crud.get_reminder(db, reminder_id=reminder_id)
    if not existing:
        raise HTTPException(
            status_code=404,
            detail=f"Reminder not found with id: {reminder_id}"
        )
    
    try:
        completed = crud.complete_reminder(db, reminder_id=reminder_id)
        if not completed:
            raise HTTPException(
                status_code=500,
                detail="Failed to complete reminder"
            )
        return ReminderResponse.model_validate(completed)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error completing reminder: {str(e)}"
        )


# Parse natural language without creating reminder
@app.post("/reminders/parse", response_model=ParseOnlyResponse, tags=["Parsing"])
async def parse_only(request: ParseOnlyRequest):
    """
    Parse natural language input without creating a reminder.
    
    Useful for:
    - Previewing what will be created
    - Validating input before submission
    - Testing parsing accuracy
    
    Args:
        request: Natural language input and timezone
        
    Returns:
        Parsed data with confidence score and validation results
        
    Raises:
        HTTPException: If parsing fails
    """
    try:
        # Parse natural language input
        try:
            parse_result = parse_reminder(
                natural_input=request.natural_input,
                user_timezone=request.user_timezone,
                current_time=datetime.now()
            )
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid input: {str(e)}"
            )
        except KeyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"OpenAI response missing field: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"OpenAI parsing failed: {str(e)}"
            )
        
        parsed = parse_result.get('parsed', {})
        
        # Ensure required fields have defaults
        if 'is_recurring' not in parsed:
            parsed['is_recurring'] = False
        if 'recurrence_pattern' not in parsed:
            parsed['recurrence_pattern'] = None
        
        # Validate parsed data
        is_valid, error = validate_parsed_reminder(parsed)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Parsing validation failed: {error}"
            )
        
        # Calculate confidence
        confidence = calculate_confidence(request.natural_input, parsed)
        
        return ParseOnlyResponse(
            parsed=parsed,
            confidence=confidence,
            model=parse_result.get('model_used', parse_result.get('model', 'unknown')),
            original_input=request.natural_input,
            validation={
                "is_valid": is_valid,
                "error": error
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing input: {str(e)}"
        )


# Get due reminders (for notifications)
@app.get("/reminders/due/now", response_model=ReminderListResponse, tags=["Reminders"])
async def get_due_reminders(
    user_id: str = Query(..., description="User ID to fetch due reminders for"),
    db: Session = Depends(get_db)
):
    """
    Get reminders that are due now or overdue.
    
    Useful for notification systems to check what reminders
    need to be sent to the user.
    
    Args:
        user_id: User identifier
        
    Returns:
        List of due/overdue reminders
    """
    try:
        # Get current time and one hour window
        now = datetime.now()
        one_hour_from_now = now + timedelta(hours=1)
        
        # Use the crud function with proper parameters
        due_reminders = crud.get_due_reminders(
            db=db,
            start_time=now,
            end_time=one_hour_from_now,
            status="pending"  # or "active" - looking for non-completed reminders
        )
        
        # Filter by user_id
        user_reminders = [r for r in due_reminders if r.user_id == user_id]
        
        return ReminderListResponse(
            reminders=[ReminderResponse.model_validate(r) for r in user_reminders],
            total=len(user_reminders),
            page=1,
            page_size=len(user_reminders)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching due reminders: {str(e)}"
        )


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "detail": str(exc.detail) if hasattr(exc, 'detail') else "Resource not found",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc.detail) if hasattr(exc, 'detail') else "An internal error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
