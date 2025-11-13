"""
Unit tests for user repository.

This module contains tests for the UserRepository class,
testing all database operations and error handling.
"""

from unittest.mock import Mock, patch

import pytest
from sqlalchemy.exc import IntegrityError

from src.core.exceptions import ConflictError, DatabaseError, NotFoundError
from src.models.user import User
from src.repositories.user_repository import UserRepository


class TestUserRepository:
    """Test UserRepository class."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock()

    @pytest.fixture
    def user_repository(self, mock_db):
        """Create UserRepository instance with mock database."""
        return UserRepository(mock_db)

    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for testing."""
        return {
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "hashed_password": "hashed_password",
            "is_active": True,
            "is_verified": True,
        }

    def test_create_success(self, user_repository, mock_db, sample_user_data):
        """Test successful user creation."""
        # Setup
        mock_user = Mock(spec=User)
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        mock_db.add.return_value = mock_user

        # Mock the User constructor
        with patch("src.repositories.user_repository.User") as mock_user_class:
            mock_user_class.return_value = mock_user

            result = user_repository.create(sample_user_data)

            assert result == mock_user
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(mock_user)

    def test_create_integrity_error_email(
        self, user_repository, mock_db, sample_user_data
    ):
        """Test user creation with email conflict."""
        # Setup
        mock_error = IntegrityError("statement", "params", "orig")
        mock_error.orig = (
            'duplicate key value violates unique constraint "users_email_key"'
        )
        mock_db.add.side_effect = mock_error
        mock_db.rollback.return_value = None

        with patch("src.repositories.user_repository.User") as mock_user_class:
            mock_user_class.return_value = Mock()

            with pytest.raises(
                ConflictError, match="User with this email already exists"
            ):
                user_repository.create(sample_user_data)

            mock_db.rollback.assert_called_once()

    def test_create_integrity_error_username(
        self, user_repository, mock_db, sample_user_data
    ):
        """Test user creation with username conflict."""
        # Setup
        mock_error = IntegrityError("statement", "params", "orig")
        mock_error.orig = (
            'duplicate key value violates unique constraint "users_username_key"'
        )
        mock_db.add.side_effect = mock_error
        mock_db.rollback.return_value = None

        with patch("src.repositories.user_repository.User") as mock_user_class:
            mock_user_class.return_value = Mock()

            with pytest.raises(
                ConflictError, match="User with this username already exists"
            ):
                user_repository.create(sample_user_data)

            mock_db.rollback.assert_called_once()

    def test_create_database_error(self, user_repository, mock_db, sample_user_data):
        """Test user creation with database error."""
        # Setup
        mock_db.add.side_effect = Exception("Database connection failed")
        mock_db.rollback.return_value = None

        with patch("src.repositories.user_repository.User") as mock_user_class:
            mock_user_class.return_value = Mock()

            with pytest.raises(DatabaseError, match="Failed to create user"):
                user_repository.create(sample_user_data)

            mock_db.rollback.assert_called_once()

    def test_get_by_id_success(self, user_repository, mock_db):
        """Test successful user retrieval by ID."""
        # Setup
        mock_user = Mock(spec=User)
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user

        result = user_repository.get_by_id(1)

        assert result == mock_user
        mock_db.query.assert_called_once_with(User)
        mock_query.filter.assert_called_once()
        mock_query.first.assert_called_once()

    def test_get_by_id_not_found(self, user_repository, mock_db):
        """Test user retrieval by ID when not found."""
        # Setup
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        result = user_repository.get_by_id(999)

        assert result is None

    def test_get_by_email_success(self, user_repository, mock_db):
        """Test successful user retrieval by email."""
        # Setup
        mock_user = Mock(spec=User)
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user

        result = user_repository.get_by_email("test@example.com")

        assert result == mock_user
        mock_db.query.assert_called_once_with(User)
        mock_query.filter.assert_called_once()
        mock_query.first.assert_called_once()

    def test_get_by_email_not_found(self, user_repository, mock_db):
        """Test user retrieval by email when not found."""
        # Setup
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        result = user_repository.get_by_email("nonexistent@example.com")

        assert result is None

    def test_get_by_username_success(self, user_repository, mock_db):
        """Test successful user retrieval by username."""
        # Setup
        mock_user = Mock(spec=User)
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user

        result = user_repository.get_by_username("testuser")

        assert result == mock_user
        mock_db.query.assert_called_once_with(User)
        mock_query.filter.assert_called_once()
        mock_query.first.assert_called_once()

    def test_get_by_username_not_found(self, user_repository, mock_db):
        """Test user retrieval by username when not found."""
        # Setup
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        result = user_repository.get_by_username("nonexistent")

        assert result is None

    def test_get_all_success(self, user_repository, mock_db):
        """Test successful retrieval of all users."""
        # Setup
        mock_users = [Mock(spec=User), Mock(spec=User)]
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_users

        result = user_repository.get_all()

        assert result == mock_users
        mock_db.query.assert_called_once_with(User)
        mock_query.offset.assert_called_once_with(0)
        mock_query.limit.assert_called_once_with(100)
        mock_query.all.assert_called_once()

    def test_get_all_with_pagination(self, user_repository, mock_db):
        """Test retrieval of all users with pagination."""
        # Setup
        mock_users = [Mock(spec=User), Mock(spec=User)]
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_users

        result = user_repository.get_all(skip=10, limit=5)

        assert result == mock_users
        mock_query.offset.assert_called_once_with(10)
        mock_query.limit.assert_called_once_with(5)

    def test_get_all_with_filters(self, user_repository, mock_db):
        """Test retrieval of all users with filters."""
        # Setup
        mock_users = [Mock(spec=User)]
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_users

        result = user_repository.get_all(is_active=True, is_verified=True)

        assert result == mock_users
        assert (
            mock_query.filter.call_count == 2
        )  # Called twice for is_active and is_verified
        mock_query.offset.assert_called_once_with(0)
        mock_query.limit.assert_called_once_with(100)
        mock_query.all.assert_called_once()

    def test_update_success(self, user_repository, mock_db):
        """Test successful user update."""
        # Setup
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        update_data = {"first_name": "Updated"}
        result = user_repository.update(1, update_data)

        assert result == mock_user
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_user)

    def test_update_not_found(self, user_repository, mock_db):
        """Test user update when user not found."""
        # Setup
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        update_data = {"first_name": "Updated"}

        with pytest.raises(NotFoundError, match="User not found with identifier: 999"):
            user_repository.update(999, update_data)

    def test_update_database_error(self, user_repository, mock_db):
        """Test user update with database error."""
        # Setup
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user
        mock_db.commit.side_effect = Exception("Database error")
        mock_db.rollback.return_value = None

        update_data = {"first_name": "Updated"}

        with pytest.raises(DatabaseError, match="Failed to update user"):
            user_repository.update(1, update_data)

        mock_db.rollback.assert_called_once()

    def test_delete_success(self, user_repository, mock_db):
        """Test successful user deletion."""
        # Setup
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user
        mock_db.delete.return_value = None
        mock_db.commit.return_value = None

        result = user_repository.delete(1)

        assert result is True
        mock_db.delete.assert_called_once_with(mock_user)
        mock_db.commit.assert_called_once()

    def test_delete_not_found(self, user_repository, mock_db):
        """Test user deletion when user not found."""
        # Setup
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        with pytest.raises(NotFoundError, match="User not found with identifier: 999"):
            user_repository.delete(999)

    def test_delete_database_error(self, user_repository, mock_db):
        """Test user deletion with database error."""
        # Setup
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user
        mock_db.delete.side_effect = Exception("Database error")
        mock_db.rollback.return_value = None

        with pytest.raises(DatabaseError, match="Failed to delete user"):
            user_repository.delete(1)

        mock_db.rollback.assert_called_once()

    def test_count_success(self, user_repository, mock_db):
        """Test successful user count."""
        # Setup
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.count.return_value = 5

        result = user_repository.count()

        assert result == 5
        mock_db.query.assert_called_once_with(User)
        mock_query.count.assert_called_once()

    def test_count_with_filters(self, user_repository, mock_db):
        """Test user count with filters."""
        # Setup
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 3

        result = user_repository.count(is_active=True)

        assert result == 3
        mock_query.filter.assert_called_once()

    def test_exists_success(self, user_repository, mock_db):
        """Test successful user existence check."""
        # Setup
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = Mock()

        result = user_repository.exists(1)

        assert result is True

    def test_exists_false(self, user_repository, mock_db):
        """Test user existence check when user doesn't exist."""
        # Setup
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        result = user_repository.exists(999)

        assert result is False

    def test_search_success(self, user_repository, mock_db):
        """Test successful user search."""
        # Setup
        mock_users = [Mock(spec=User), Mock(spec=User)]
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_users

        result = user_repository.search("test")

        assert result == mock_users
        mock_db.query.assert_called_once_with(User)
        mock_query.filter.assert_called_once()
        mock_query.offset.assert_called_once_with(0)
        mock_query.limit.assert_called_once_with(100)
        mock_query.all.assert_called_once()

    def test_search_with_pagination(self, user_repository, mock_db):
        """Test user search with pagination."""
        # Setup
        mock_users = [Mock(spec=User)]
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_users

        result = user_repository.search("test", skip=5, limit=10)

        assert result == mock_users
        mock_query.offset.assert_called_once_with(5)
        mock_query.limit.assert_called_once_with(10)

    def test_get_stats_success(self, user_repository, mock_db):
        """Test successful user statistics retrieval."""
        # Setup
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 10

        result = user_repository.get_stats()

        assert "total_users" in result
        assert result["total_users"] == 10
        mock_db.query.assert_called_with(User)

    def test_get_stats_with_filters(self, user_repository, mock_db):
        """Test user statistics with filters."""
        # Setup
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 5

        result = user_repository.get_stats(is_active=True)

        assert "total_users" in result
        assert result["total_users"] == 5
