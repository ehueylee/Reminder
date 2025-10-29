"""
Production configuration for Railway deployment
"""
import os
from typing import Optional

class Settings:
    """Application settings - auto-detects environment"""
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./reminders.db"  # Fallback for local dev
    )
    
    # Fix Railway's postgres:// to postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Email (optional)
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: Optional[str] = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    SMTP_FROM_EMAIL: Optional[str] = os.getenv("SMTP_FROM_EMAIL")
    SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "Reminder App")
    
    # App config
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    PORT: int = int(os.getenv("PORT", "8001"))
    
    # CORS (allow all for now - can restrict later)
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8001",
        "http://127.0.0.1:8001",
        "*"  # Allow all for testing - restrict in production later
    ]

settings = Settings()
