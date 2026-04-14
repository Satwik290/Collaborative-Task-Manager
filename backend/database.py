"""
Database initialization and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base
import os


def get_database_url() -> str:
    """
    Get database URL from environment or use SQLite for development.
    """
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url
    # Development: use SQLite
    return "sqlite:///./collab_tasks.db"


def init_db(database_url: str) -> None:
    """
    Create all tables in the database.
    Safe to call multiple times (idempotent).
    """
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized: {database_url}")


def get_session(database_url: str) -> Session:
    """
    Create a new database session.
    Use in route handlers or services.
    """
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


# Global session factory
_database_url = get_database_url()
engine = create_engine(_database_url)
SessionLocal = sessionmaker(bind=engine)


from flask import g

def get_db() -> Session:
    """
    Get a database session.
    Typically used as a dependency in Flask routes.
    """
    if 'db' not in g:
        g.db = SessionLocal()
    return g.db
