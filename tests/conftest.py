"""
Pytest configuration and fixtures.

This module provides shared fixtures and configuration for all tests
in the Notes App test suite.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.main import app
from src.core.database import Base, get_db
from src.models.note import Note
from src.models.user import User

# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session maker
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session")
def test_db():
    """
    Create test database tables.
    """
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session(test_db):
    """
    Create a database session for testing.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """
    Create a test client with database session override.
    """

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """
    Create a test user.
    """
    from src.services.authentication import AuthenticationService

    auth_service = AuthenticationService(db_session)

    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "hashed_password": auth_service.get_password_hash("TestPassword123!"),
        "is_active": True,
        "is_verified": True,
    }

    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture
def test_user_token(test_user, db_session):
    """
    Create a JWT token for the test user.
    """
    from src.services.authentication import AuthenticationService

    auth_service = AuthenticationService(db_session)

    token_data = {
        "sub": str(test_user.id),
        "email": test_user.email,
        "username": test_user.username,
    }

    token = auth_service.create_access_token(token_data)
    return token


@pytest.fixture
def test_note(test_user, db_session):
    """
    Create a test note.
    """
    note_data = {
        "title": "Test Note",
        "content": "This is a test note content.",
        "summary": "Test note summary",
        "is_public": False,
        "is_pinned": False,
        "owner_id": test_user.id,
        "status": "active",
    }

    note = Note(**note_data)
    db_session.add(note)
    db_session.commit()
    db_session.refresh(note)

    return note


@pytest.fixture
def auth_headers(test_user_token):
    """
    Create authorization headers for authenticated requests.
    """
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest.fixture
def sample_user_data():
    """
    Sample user data for testing.
    """
    return {
        "email": "newuser@example.com",
        "username": "newuser",
        "first_name": "New",
        "last_name": "User",
        "password": "NewPassword123!",
        "confirm_password": "NewPassword123!",
    }


@pytest.fixture
def sample_note_data():
    """
    Sample note data for testing.
    """
    return {
        "title": "Sample Note",
        "content": "This is sample note content for testing purposes.",
        "summary": "Sample note summary",
        "is_public": False,
        "is_pinned": False,
    }


@pytest.fixture
def sample_login_data():
    """
    Sample login data for testing.
    """
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "api: API tests")
    config.addinivalue_line("markers", "slow: Slow tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "api" in str(item.fspath):
            item.add_marker(pytest.mark.api)

        # Add slow marker for tests that take more than 1 second
        if "slow" in item.name or "bulk" in item.name:
            item.add_marker(pytest.mark.slow)
