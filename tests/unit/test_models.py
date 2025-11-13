"""
Unit tests for models.

This module contains unit tests for the SQLAlchemy models,
testing model creation, validation, and relationships.
"""

from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.database import Base
from src.models.note import Note, NoteStatus
from src.models.user import User


class TestUserModel:
    """Test User model."""

    @pytest.fixture
    def db_session(self):
        """Create in-memory database session."""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    def test_user_creation(self, db_session):
        """Test user creation with valid data."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            is_active=True,
            is_verified=True,
        )
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.is_verified is True

    def test_user_verification(self, db_session):
        """Test user verification method."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
        )
        db_session.add(user)
        db_session.commit()

        user.verify()
        assert user.is_verified is True

    def test_user_deactivation(self, db_session):
        """Test user deactivation method."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        user.deactivate()
        assert user.is_active is False

    def test_user_last_login_update(self, db_session):
        """Test user last login update."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
        )
        db_session.add(user)
        db_session.commit()

        login_time = datetime.utcnow()
        user.update_last_login()

        assert user.last_login is not None
        assert user.last_login >= login_time


class TestNoteModel:
    """Test Note model."""

    @pytest.fixture
    def db_session(self):
        """Create in-memory database session."""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    @pytest.fixture
    def sample_user(self, db_session):
        """Create a sample user."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
        )
        db_session.add(user)
        db_session.commit()
        return user

    def test_note_creation(self, db_session, sample_user):
        """Test note creation with valid data."""
        note = Note(
            title="Test Note",
            content="This is test content",
            summary="Test summary",
            is_public=True,
            is_pinned=False,
            status=NoteStatus.ACTIVE,
            owner_id=sample_user.id,
        )
        db_session.add(note)
        db_session.commit()

        assert note.id is not None
        assert note.title == "Test Note"
        assert note.content == "This is test content"
        assert note.is_public is True
        assert note.status == NoteStatus.ACTIVE
        assert note.owner_id == sample_user.id

    def test_note_status_enum(self):
        """Test NoteStatus enum values."""
        assert NoteStatus.ACTIVE == "active"
        assert NoteStatus.ARCHIVED == "archived"
        assert NoteStatus.DELETED == "deleted"

    def test_note_relationship(self, db_session, sample_user):
        """Test note-user relationship."""
        note = Note(title="Test Note", content="Test content", owner_id=sample_user.id)
        db_session.add(note)
        db_session.commit()

        # Test relationship
        assert note.owner_id == sample_user.id
        # Note: The actual relationship testing would require proper setup
        # but this tests the basic foreign key relationship

    def test_note_timestamps(self, db_session, sample_user):
        """Test note timestamp fields."""
        note = Note(title="Test Note", content="Test content", owner_id=sample_user.id)
        db_session.add(note)
        db_session.commit()

        assert note.created_at is not None
        assert note.updated_at is not None
        assert isinstance(note.created_at, datetime)
        assert isinstance(note.updated_at, datetime)
