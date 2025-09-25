"""
Unit tests for Pydantic schemas.

This module contains unit tests for the Pydantic schemas,
testing validation, serialization, and data transformation.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from src.models.note import NoteStatus
from src.schemas.note import (
    NoteBulkAction,
    NoteCreate,
    NoteResponse,
    NoteSearchRequest,
    NoteStats,
    NoteUpdate,
)
from src.schemas.user import (
    UserCreate,
    UserLogin,
    UserPasswordUpdate,
    UserResponse,
    UserUpdate,
)


class TestUserSchemas:
    """Test user-related schemas."""

    def test_user_create_valid(self):
        """Test UserCreate with valid data."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123!",
            "confirm_password": "TestPassword123!",
        }
        user = UserCreate(**user_data)

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "TestPassword123!"

    def test_user_create_invalid_email(self):
        """Test UserCreate with invalid email."""
        user_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "TestPassword123!",
            "confirm_password": "TestPassword123!",
        }

        with pytest.raises(ValidationError):
            UserCreate(**user_data)

    def test_user_create_password_mismatch(self):
        """Test UserCreate with password mismatch."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123!",
            "confirm_password": "DifferentPassword123!",
        }

        with pytest.raises(ValidationError):
            UserCreate(**user_data)

    def test_user_update_valid(self):
        """Test UserUpdate with valid data."""
        user_data = {
            "username": "newusername",
            "first_name": "New",
            "last_name": "User",
        }
        user = UserUpdate(**user_data)

        assert user.username == "newusername"
        assert user.first_name == "New"
        assert user.last_name == "User"

    def test_user_login_valid(self):
        """Test UserLogin with valid data."""
        login_data = {"email": "test@example.com", "password": "TestPassword123!"}
        login = UserLogin(**login_data)

        assert login.email == "test@example.com"
        assert login.password == "TestPassword123!"

    def test_change_password_valid(self):
        """Test ChangePassword with valid data."""
        password_data = {
            "current_password": "OldPassword123!",
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!",
        }
        change = UserPasswordUpdate(**password_data)

        assert change.current_password == "OldPassword123!"
        assert change.new_password == "NewPassword123!"

    def test_user_response_valid(self):
        """Test UserResponse with valid data."""
        user_data = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "is_active": True,
            "is_verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        user = UserResponse(**user_data)

        assert user.id == 1
        assert user.username == "testuser"
        assert user.email == "test@example.com"


class TestNoteSchemas:
    """Test note-related schemas."""

    def test_note_create_valid(self):
        """Test NoteCreate with valid data."""
        note_data = {
            "title": "Test Note",
            "content": "This is test content",
            "summary": "Test summary",
            "is_public": True,
            "is_pinned": False,
        }
        note = NoteCreate(**note_data)

        assert note.title == "Test Note"
        assert note.content == "This is test content"
        assert note.is_public is True
        assert note.is_pinned is False

    def test_note_create_invalid_title(self):
        """Test NoteCreate with invalid title."""
        note_data = {
            "title": "",  # Empty title should fail
            "content": "This is test content",
            "is_public": True,
        }

        with pytest.raises(ValidationError):
            NoteCreate(**note_data)

    def test_note_update_valid(self):
        """Test NoteUpdate with valid data."""
        note_data = {"title": "Updated Title", "content": "Updated content"}
        note = NoteUpdate(**note_data)

        assert note.title == "Updated Title"
        assert note.content == "Updated content"

    def test_note_response_valid(self):
        """Test NoteResponse with valid data."""
        note_data = {
            "id": 1,
            "title": "Test Note",
            "content": "Test content",
            "summary": "Test summary",
            "is_public": True,
            "is_pinned": False,
            "status": NoteStatus.ACTIVE,
            "owner_id": 1,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        note = NoteResponse(**note_data)

        assert note.id == 1
        assert note.title == "Test Note"
        assert note.status == NoteStatus.ACTIVE

    def test_note_search_request_valid(self):
        """Test NoteSearchRequest with valid data."""
        search_data = {"query": "test search", "status": "active", "is_public": True}
        search = NoteSearchRequest(**search_data)

        assert search.query == "test search"
        assert search.status == "active"
        assert search.is_public is True

    def test_note_search_request_invalid_query(self):
        """Test NoteSearchRequest with invalid query."""
        search_data = {"query": "", "status": "active"}  # Empty query should fail

        with pytest.raises(ValidationError):
            NoteSearchRequest(**search_data)

    def test_note_bulk_action_valid(self):
        """Test NoteBulkAction with valid data."""
        bulk_data = {"action": "archive", "note_ids": [1, 2, 3]}
        bulk = NoteBulkAction(**bulk_data)

        assert bulk.action == "archive"
        assert bulk.note_ids == [1, 2, 3]

    def test_note_bulk_action_invalid_action(self):
        """Test NoteBulkAction with invalid action."""
        bulk_data = {"action": "invalid_action", "note_ids": [1, 2, 3]}

        with pytest.raises(ValidationError):
            NoteBulkAction(**bulk_data)

    def test_note_bulk_action_empty_ids(self):
        """Test NoteBulkAction with empty note_ids."""
        bulk_data = {"action": "archive", "note_ids": []}

        with pytest.raises(ValidationError):
            NoteBulkAction(**bulk_data)

    def test_note_stats_valid(self):
        """Test NoteStats with valid data."""
        stats_data = {
            "total_notes": 15,
            "active_notes": 10,
            "archived_notes": 5,
            "public_notes": 8,
            "pinned_notes": 3,
            "created_today": 1,
            "created_this_week": 2,
            "created_this_month": 7,
        }
        stats = NoteStats(**stats_data)

        assert stats.total_notes == 15
        assert stats.active_notes == 10
        assert stats.archived_notes == 5
        assert stats.public_notes == 8
        assert stats.pinned_notes == 3
        assert stats.created_today == 1
        assert stats.created_this_week == 2
        assert stats.created_this_month == 7
