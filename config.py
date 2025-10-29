"""
Production configuration for Railway deployment
"""
import os
from typing import Optional

class Settings:
    """Application settings - auto-detects environment"""
    
    def __init__(self):
        # Database - get from environment
        database_url = os.getenv("DATABASE_URL", "sqlite:///./reminders.db")
        
        # Fix Railway's postgres:// to postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        self.DATABASE_URL = database_url
        
        # OpenAI
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        
        # Email (optional)
        self.SMTP_HOST = os.getenv("SMTP_HOST")
        self.SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
        self.SMTP_USERNAME = os.getenv("SMTP_USERNAME")
        self.SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
        self.SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL")
        self.SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Reminder App")
        
        # App config
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        self.PORT = int(os.getenv("PORT", "8001"))
        
        # CORS (allow all for now - can restrict later)
        self.ALLOWED_ORIGINS = [
            "http://localhost:3000",
            "http://localhost:8001",
            "http://127.0.0.1:8001",
            "*"  # Allow all for testing - restrict in production later
        ]

settings = Settings()
