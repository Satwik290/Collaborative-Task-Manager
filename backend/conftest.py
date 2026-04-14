"""
Pytest configuration and fixtures.
Sets up in-memory SQLite database for tests.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import SessionLocal
from models import Base
from app import create_app


@pytest.fixture
def test_db():
    """
    Create in-memory SQLite database for testing.
    Torn down after each test.
    """
    # Create in-memory database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    
    TestSessionLocal = sessionmaker(bind=engine)
    db = TestSessionLocal()
    
    yield db
    
    db.close()


@pytest.fixture
def app():
    """
    Create Flask app configured for testing.
    """
    app = create_app({"TESTING": True})
    yield app


@pytest.fixture
def client(app, test_db):
    """
    Flask test client.
    """
    # Patch database.get_db to use test database
    import database
    original_get_db = database.get_db
    database.get_db = lambda: test_db
    
    with app.test_client() as client:
        yield client
    
    # Restore original
    database.get_db = original_get_db
