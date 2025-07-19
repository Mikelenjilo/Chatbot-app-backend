"""
Database connection and session management.
This file sets up SQLAlchemy to work with SQLite.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings


# Create the SQLAlchemy engine
# SQLite doesn't support multiple threads by default, so we add check_same_thread=False
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}  # Only needed for SQLite
)

# Create a SessionLocal class - each instance will be a database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class - all our database models will inherit from this
Base = declarative_base()


def get_db() -> Session:
    """
    Dependency function to get a database session.
    This will be used in FastAPI endpoints to get a database connection.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine) 