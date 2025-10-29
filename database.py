"""
Database configuration and connection management.
Sets up SQLAlchemy engine and session maker.
Supports both SQLite (local dev) and PostgreSQL (production).
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from models import Base

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Try to import config for production settings
try:
    from config import settings
    DATABASE_URL = settings.DATABASE_URL
except ImportError:
    # Fallback if config.py doesn't exist (local dev)
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./reminders.db")
    # Fix Railway's postgres:// to postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create engine - works for both SQLite and PostgreSQL
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_pre_ping=True,  # Verify connections before using (important for PostgreSQL)
    echo=False  # Set to True for SQL query logging
)

# Create session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize the database by creating all tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database initialized successfully")
        print("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        print(f"❌ Database initialization failed: {e}")
        raise


def get_db():
    """
    Dependency function to get a database session.
    Use with context manager or try/finally.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
