"""
Unit tests for NoteRepository.

This module contains comprehensive unit tests for the NoteRepository class,
testing all CRUD operations, search functionality, and error handling.
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from src.core.exceptions import DatabaseError
from src.models.note import Note, NoteStatus
from src.repositories.note_repository import NoteRepository


class TestNoteRepository:
    """Test cases for NoteRepository."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mocked database session."""
        mock_session = Mock()
        mock_session.add = Mock()
        mock_session.commit = Mock()
        mock_session.refresh = Mock()
        mock_session.rollback = Mock()
        mock_session.query = Mock()
        return mock_session

    @pytest.fixture
    def note_repository(self, mock_db_session):
        """Create a NoteRepository instance with mocked database."""
        return NoteRepository(mock_db_session)

    @pytest.fixture
    def sample_note_data(self):
        """Sample note data for testing."""
        return {
            "title": "Test Note",
            "content": "This is a test note content",
            "summary": "Test summary",
            "status": NoteStatus.ACTIVE,
            "is_public": False,
            "owner_id": 1,
            "tags": ["test", "sample"],
        }

    @pytest.fixture
    def sample_note(self):
        """Sample Note instance for testing."""
        note = Mock(spec=Note)
        note.id = 1
        note.title = "Test Note"
        note.content = "This is a test note content"
        note.summary = "Test summary"
        note.status = NoteStatus.ACTIVE
        note.is_public = False
        note.owner_id = 1
        note.tags = ["test", "sample"]
        note.created_at = datetime.now()
        note.updated_at = datetime.now()
        return note

    def test_create_success(self, note_repository, mock_db_session, sample_note_data):
        """Test successful note creation."""
        # Setup
        mock_note = Mock(spec=Note)
        mock_note.id = 1
        mock_note.title = sample_note_data["title"]
        mock_note.content = sample_note_data["content"]
        mock_note.owner_id = sample_note_data["owner_id"]
        mock_note.is_public = sample_note_data["is_public"]
        mock_note.created_at = datetime.now()
        mock_note.updated_at = datetime.now()

        with patch("src.repositories.note_repository.Note") as mock_note_class:
            mock_note_class.return_value = mock_note

            result = note_repository.create(sample_note_data)

            assert result == mock_note
            mock_note_class.assert_called_once_with(**sample_note_data)
            mock_db_session.add.assert_called_once_with(mock_note)
            mock_db_session.commit.assert_called_once()
            mock_db_session.refresh.assert_called_once_with(mock_note)

    def test_create_database_error(
        self, note_repository, mock_db_session, sample_note_data
    ):
        """Test note creation with database error."""
        # Setup
        mock_db_session.add.side_effect = Exception("Database error")
        mock_db_session.rollback.return_value = None

        with patch("src.repositories.note_repository.Note") as mock_note_class:
            mock_note_class.return_value = Mock()

            with pytest.raises(DatabaseError, match="Failed to create note"):
                note_repository.create(sample_note_data)

            mock_db_session.rollback.assert_called_once()

    def test_get_by_id_success(self, note_repository, mock_db_session, sample_note):
        """Test successful note retrieval by ID."""
        # Setup
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_note

        result = note_repository.get_by_id(1, owner_id=1)

        assert result == sample_note
        mock_db_session.query.assert_called_once_with(Note)
        assert (
            mock_query.filter.call_count == 2
        )  # Called twice: once for note_id, once for owner_id
        mock_query.first.assert_called_once()

    def test_get_by_id_not_found(self, note_repository, mock_db_session):
        """Test note retrieval by ID when note not found."""
        # Setup
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        result = note_repository.get_by_id(999, owner_id=1)

        assert result is None

    def test_get_by_id_without_owner(
        self, note_repository, mock_db_session, sample_note
    ):
        """Test note retrieval by ID without owner filter."""
        # Setup
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_note

        result = note_repository.get_by_id(1)

        assert result == sample_note
        mock_db_session.query.assert_called_once_with(Note)

    def test_get_by_owner_success(self, note_repository, mock_db_session, sample_note):
        """Test successful note retrieval by owner."""
        # Setup
        mock_notes = [sample_note, Mock(spec=Note)]
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_notes

        result = note_repository.get_by_owner(owner_id=1, skip=0, limit=10)

        assert result == mock_notes
        mock_db_session.query.assert_called_once_with(Note)
        mock_query.filter.assert_called_once()
        mock_query.order_by.assert_called_once()
        mock_query.offset.assert_called_once_with(0)
        mock_query.limit.assert_called_once_with(10)
        mock_query.all.assert_called_once()

    def test_get_by_owner_with_filters(
        self, note_repository, mock_db_session, sample_note
    ):
        """Test note retrieval by owner with filters."""
        # Setup
        mock_notes = [sample_note]
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_notes

        result = note_repository.get_by_owner(
            owner_id=1,
            status=NoteStatus.ACTIVE,
            is_public=False,
            search_query="test",
            skip=0,
            limit=10,
        )

        assert result == mock_notes
        assert mock_query.filter.call_count >= 2  # Multiple filter calls

    def test_get_by_owner_database_error(self, note_repository, mock_db_session):
        """Test note retrieval by owner with database error."""
        # Setup
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.side_effect = Exception("Database error")

        with pytest.raises(DatabaseError, match="Failed to get notes by owner"):
            note_repository.get_by_owner(owner_id=1)

    def test_get_public_notes_success(
        self, note_repository, mock_db_session, sample_note
    ):
        """Test successful public notes retrieval."""
        # Setup
        mock_notes = [sample_note]
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_notes

        result = note_repository.get_public_notes(skip=0, limit=10)

        assert result == mock_notes
        mock_db_session.query.assert_called_once_with(Note)
        mock_query.filter.assert_called_once()
        mock_query.order_by.assert_called_once()
        mock_query.offset.assert_called_once_with(0)
        mock_query.limit.assert_called_once_with(10)
        mock_query.all.assert_called_once()

    def test_get_public_notes_with_search(
        self, note_repository, mock_db_session, sample_note
    ):
        """Test public notes retrieval with search query."""
        # Setup
        mock_notes = [sample_note]
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_notes

        result = note_repository.get_public_notes(search_query="test", skip=0, limit=10)

        assert result == mock_notes
        assert mock_query.filter.call_count >= 2  # Multiple filter calls

    def test_get_public_notes_database_error(self, note_repository, mock_db_session):
        """Test public notes retrieval with database error."""
        # Setup
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.side_effect = Exception("Database error")

        with pytest.raises(DatabaseError, match="Failed to get public notes"):
            note_repository.get_public_notes()

    def test_update_success(self, note_repository, mock_db_session, sample_note):
        """Test successful note update."""
        # Setup
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_note

        update_data = {"title": "Updated Title", "content": "Updated content"}

        result = note_repository.update(1, update_data, owner_id=1)

        assert result == sample_note
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(sample_note)

    def test_update_not_found(self, note_repository, mock_db_session):
        """Test note update when note not found."""
        # Setup
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        update_data = {"title": "Updated Title"}

        result = note_repository.update(999, update_data, owner_id=1)
        assert result is None

    def test_update_database_error(self, note_repository, mock_db_session, sample_note):
        """Test note update with database error."""
        # Setup
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_note
        mock_db_session.commit.side_effect = Exception("Database error")

        update_data = {"title": "Updated Title"}

        with pytest.raises(DatabaseError, match="Failed to update note"):
            note_repository.update(1, update_data, owner_id=1)

        mock_db_session.rollback.assert_called_once()

    def test_delete_success(self, note_repository, mock_db_session, sample_note):
        """Test successful note deletion."""
        # Setup
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_note

        result = note_repository.delete(1, owner_id=1)

        assert result is True
        # Soft delete: sets status to DELETED, doesn't call db.delete()
        assert sample_note.status == NoteStatus.DELETED
        mock_db_session.commit.assert_called_once()

    def test_delete_not_found(self, note_repository, mock_db_session):
        """Test note deletion when note not found."""
        # Setup
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        result = note_repository.delete(999, owner_id=1)
        assert result is False

    def test_delete_database_error(self, note_repository, mock_db_session, sample_note):
        """Test note deletion with database error."""
        # Setup
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_note
        mock_db_session.commit.side_effect = Exception("Database error")

        with pytest.raises(DatabaseError, match="Failed to delete note"):
            note_repository.delete(1, owner_id=1)

        mock_db_session.rollback.assert_called_once()

    def test_hard_delete_success(self, note_repository, mock_db_session, sample_note):
        """Test successful hard note deletion."""
        # Setup
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_note

        result = note_repository.hard_delete(1, owner_id=1)

        assert result is True
        mock_db_session.delete.assert_called_once_with(sample_note)
        mock_db_session.commit.assert_called_once()

    def test_hard_delete_not_found(self, note_repository, mock_db_session):
        """Test hard note deletion when note not found."""
        # Setup
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        result = note_repository.hard_delete(999, owner_id=1)
        assert result is False

    def test_hard_delete_database_error(
        self, note_repository, mock_db_session, sample_note
    ):
        """Test hard note deletion with database error."""
        # Setup
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_note
        mock_db_session.delete.side_effect = Exception("Database error")

        with pytest.raises(DatabaseError, match="Failed to permanently delete note"):
            note_repository.hard_delete(1, owner_id=1)

        mock_db_session.rollback.assert_called_once()

    def test_count_by_owner_success(self, note_repository, mock_db_session):
        """Test successful note count by owner."""
        # Setup
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 5

        result = note_repository.count_by_owner(owner_id=1)

        assert result == 5
        mock_db_session.query.assert_called_once_with(Note)
        mock_query.filter.assert_called_once()
        mock_query.count.assert_called_once()

    def test_count_by_owner_with_filters(self, note_repository, mock_db_session):
        """Test note count by owner with filters."""
        # Setup
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 3

        result = note_repository.count_by_owner(
            owner_id=1, status=NoteStatus.ACTIVE, is_public=False, search_query="test"
        )

        assert result == 3
        assert mock_query.filter.call_count >= 2  # Multiple filter calls

    def test_count_by_owner_database_error(self, note_repository, mock_db_session):
        """Test note count by owner with database error."""
        # Setup
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.side_effect = Exception("Database error")

        with pytest.raises(DatabaseError, match="Failed to count notes by owner"):
            note_repository.count_by_owner(owner_id=1)

    def test_count_public_notes_success(self, note_repository, mock_db_session):
        """Test successful public notes count."""
        # Setup
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 10

        result = note_repository.count_public_notes()

        assert result == 10
        mock_db_session.query.assert_called_once_with(Note)
        mock_query.filter.assert_called_once()
        mock_query.count.assert_called_once()

    def test_count_public_notes_with_search(self, note_repository, mock_db_session):
        """Test public notes count with search query."""
        # Setup
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 5

        result = note_repository.count_public_notes(search_query="test")

        assert result == 5
        assert mock_query.filter.call_count >= 2  # Multiple filter calls

    def test_count_public_notes_database_error(self, note_repository, mock_db_session):
        """Test public notes count with database error."""
        # Setup
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.side_effect = Exception("Database error")

        with pytest.raises(DatabaseError, match="Failed to count public notes"):
            note_repository.count_public_notes()

    def test_get_stats_success(self, note_repository, mock_db_session):
        """Test successful note statistics retrieval."""
        # Setup
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 10

        result = note_repository.get_stats(owner_id=1)

        assert "total_notes" in result
        assert "active_notes" in result
        assert "archived_notes" in result
        assert "public_notes" in result
        assert "pinned_notes" in result
        assert "created_this_week" in result
        assert "created_this_month" in result

    def test_get_stats_database_error(self, note_repository, mock_db_session):
        """Test note statistics retrieval with database error."""
        # Setup
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.side_effect = Exception("Database error")

        with pytest.raises(DatabaseError, match="Failed to get note stats"):
            note_repository.get_stats(owner_id=1)

    def test_bulk_update_status_success(self, note_repository, mock_db_session):
        """Test successful bulk status update."""
        # Setup
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.update.return_value = 3

        result = note_repository.bulk_update_status(
            note_ids=[1, 2, 3], status=NoteStatus.ACTIVE, owner_id=1
        )

        assert result == 3
        mock_db_session.commit.assert_called_once()

    def test_bulk_update_status_database_error(self, note_repository, mock_db_session):
        """Test bulk status update with database error."""
        # Setup
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.update.side_effect = Exception("Database error")

        with pytest.raises(DatabaseError, match="Failed to bulk update note status"):
            note_repository.bulk_update_status(
                note_ids=[1, 2, 3], status=NoteStatus.ACTIVE, owner_id=1
            )

        mock_db_session.rollback.assert_called_once()

    def test_exists_success(self, note_repository, mock_db_session):
        """Test successful note existence check."""
        # Setup
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = Mock()

        result = note_repository.exists(1, owner_id=1)

        assert result is True
        mock_db_session.query.assert_called_once_with(Note)
        assert (
            mock_query.filter.call_count == 2
        )  # Called twice: once for note_id, once for owner_id
        mock_query.first.assert_called_once()

    def test_exists_false(self, note_repository, mock_db_session):
        """Test note existence check when note doesn't exist."""
        # Setup
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        result = note_repository.exists(999, owner_id=1)

        assert result is False
        mock_db_session.query.assert_called_once_with(Note)
        assert (
            mock_query.filter.call_count == 2
        )  # Called twice: once for note_id, once for owner_id
        mock_query.first.assert_called_once()

    def test_exists_database_error(self, note_repository, mock_db_session):
        """Test note existence check with database error."""
        # Setup
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.side_effect = Exception("Database error")

        with pytest.raises(DatabaseError, match="Failed to check if note exists"):
            note_repository.exists(1, owner_id=1)
