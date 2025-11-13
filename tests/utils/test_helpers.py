"""
Enhanced test utilities for better test isolation.

This module provides utilities for creating isolated test environments
and managing test data without external dependencies.
"""

import os
from contextlib import contextmanager
from typing import Any, Dict, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.main import app
from src.core.database import Base, get_db
from src.core.logging import clear_logging_context, set_logging_context


class IsolatedTestEnvironment:
    """Test environment manager for isolated testing."""

    def __init__(self):
        self.original_env = {}
        self.test_db_url = "sqlite:///:memory:"
        self.test_engine = None
        self.test_session = None
        self.client = None

    def setup(self):
        """Set up test environment."""
        # Set test environment variables
        self.original_env = os.environ.copy()
        os.environ.update(
            {
                "ENVIRONMENT": "testing",
                "AUTH_BYPASS": "true",
                "LOG_LEVEL": "DEBUG",
                "LOG_FORMAT": "text",
                "TEST_USER_ID": "test-user-123",
                "TEST_USER_EMAIL": "test@example.com",
                "TEST_USER_USERNAME": "testuser",
            }
        )

        # Create test database
        self.test_engine = create_engine(
            self.test_db_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

        # Create test session maker
        TestingSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.test_engine
        )

        # Create tables
        Base.metadata.create_all(bind=self.test_engine)

        # Create test client
        self.client = self._create_test_client(TestingSessionLocal)

    def teardown(self):
        """Tear down test environment."""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)

        # Clean up database
        if self.test_engine:
            Base.metadata.drop_all(bind=self.test_engine)
            self.test_engine.dispose()

        # Clear logging context
        clear_logging_context()

    def _create_test_client(self, session_maker):
        """Create test client with database session override."""

        def override_get_db():
            session = session_maker()
            try:
                yield session
            finally:
                session.close()

        app.dependency_overrides[get_db] = override_get_db
        return TestClient(app)


@contextmanager
def isolated_test_environment() -> Generator[IsolatedTestEnvironment, None, None]:
    """Context manager for isolated test environment."""
    env = IsolatedTestEnvironment()
    try:
        env.setup()
        yield env
    finally:
        env.teardown()


class TestDataFactory:
    """Factory for creating test data."""

    @staticmethod
    def create_user_data(
        email: str = "test@example.com",
        username: str = "testuser",
        first_name: str = "Test",
        last_name: str = "User",
        password: str = "TestPassword123!",
        is_active: bool = True,
        is_verified: bool = True,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create user data for testing."""
        return {
            "email": email,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "password": password,
            "is_active": is_active,
            "is_verified": is_verified,
            **kwargs,
        }

    @staticmethod
    def create_note_data(
        title: str = "Test Note",
        content: str = "This is test note content.",
        summary: str = "Test note summary",
        is_public: bool = False,
        is_pinned: bool = False,
        owner_id: str = "test-user-123",
        status: str = "active",
        **kwargs,
    ) -> Dict[str, Any]:
        """Create note data for testing."""
        return {
            "title": title,
            "content": content,
            "summary": summary,
            "is_public": is_public,
            "is_pinned": is_pinned,
            "owner_id": owner_id,
            "status": status,
            **kwargs,
        }

    @staticmethod
    def create_api_request_data(
        method: str = "GET",
        path: str = "/api/v1/test",
        user_id: str = "test-user-123",
        request_id: str = "req-123",
        **kwargs,
    ) -> Dict[str, Any]:
        """Create API request data for testing."""
        return {
            "method": method,
            "path": path,
            "user_id": user_id,
            "request_id": request_id,
            **kwargs,
        }


class TestLoggingHelper:
    """Helper for test logging operations."""

    @staticmethod
    def setup_test_logging():
        """Set up logging for tests."""
        set_logging_context(
            user_id="test-user-123",
            request_id="test-request-123",
            xray_id="test-xray-123",
        )

    @staticmethod
    def clear_test_logging():
        """Clear test logging context."""
        clear_logging_context()


@pytest.fixture
def test_env():
    """Fixture for isolated test environment."""
    with isolated_test_environment() as env:
        yield env


@pytest.fixture
def test_client(test_env):
    """Fixture for test client."""
    return test_env.client


@pytest.fixture
def test_user_data():
    """Fixture for test user data."""
    return TestDataFactory.create_user_data()


@pytest.fixture
def test_note_data():
    """Fixture for test note data."""
    return TestDataFactory.create_note_data()


@pytest.fixture
def test_api_request_data():
    """Fixture for test API request data."""
    return TestDataFactory.create_api_request_data()


@pytest.fixture
def test_logging_context():
    """Fixture for test logging context."""
    TestLoggingHelper.setup_test_logging()
    yield
    TestLoggingHelper.clear_test_logging()


# Enhanced test markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.api = pytest.mark.api
pytest.mark.slow = pytest.mark.slow
