"""
Unit tests for authentication service.

This module contains unit tests for the AuthenticationService class,
testing individual methods in isolation.
"""

from datetime import timedelta
from unittest.mock import Mock, patch

import pytest

from src.core.exceptions import AuthenticationError, NotFoundError, ValidationError
from src.services.authentication import AuthenticationService


class TestAuthenticationService:
    """Test AuthenticationService class."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock()

    @pytest.fixture
    def auth_service(self, mock_db):
        """Create AuthenticationService instance with mock database."""
        service = AuthenticationService(mock_db)
        # Replace the repository with a mock
        service.user_repository = Mock()
        return service

    def test_verify_password_success(self, auth_service):
        """Test successful password verification."""
        plain_password = "testpassword123"
        hashed_password = auth_service.get_password_hash(plain_password)

        result = auth_service.verify_password(plain_password, hashed_password)
        assert result is True

    def test_verify_password_failure(self, auth_service):
        """Test password verification with wrong password."""
        plain_password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed_password = auth_service.get_password_hash(plain_password)

        result = auth_service.verify_password(wrong_password, hashed_password)
        assert result is False

    def test_get_password_hash(self, auth_service):
        """Test password hashing."""
        password = "testpassword123"
        hashed = auth_service.get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # BCrypt hash format

    def test_create_access_token(self, auth_service):
        """Test JWT token creation."""
        data = {"sub": "123", "email": "test@example.com"}
        token = auth_service.create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_expiry(self, auth_service):
        """Test JWT token creation with custom expiry."""
        data = {"sub": "123", "email": "test@example.com"}
        expires_delta = timedelta(minutes=30)
        token = auth_service.create_access_token(data, expires_delta)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_valid(self, auth_service):
        """Test valid token verification."""
        data = {"sub": "123", "email": "test@example.com"}
        token = auth_service.create_access_token(data)

        payload = auth_service.verify_token(token)
        assert payload is not None
        assert payload["sub"] == "123"
        assert payload["email"] == "test@example.com"

    def test_verify_token_invalid(self, auth_service):
        """Test invalid token verification."""
        invalid_token = "invalid.token.here"

        payload = auth_service.verify_token(invalid_token)
        assert payload is None

    def test_verify_token_expired(self, auth_service):
        """Test expired token verification."""
        data = {"sub": "123", "email": "test@example.com"}
        # Create token with very short expiry
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = auth_service.create_access_token(data, expires_delta)

        payload = auth_service.verify_token(token)
        assert payload is None

    def test_register_user_success(self, auth_service, mock_db):
        """Test successful user registration."""
        # Setup mocks
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = "test@example.com"

        auth_service.user_repository.get_by_email.return_value = None
        auth_service.user_repository.get_by_username.return_value = None
        auth_service.user_repository.create.return_value = mock_user

        # Test data
        user_data = Mock()
        user_data.email = "test@example.com"
        user_data.username = "testuser"
        user_data.first_name = "Test"
        user_data.last_name = "User"
        user_data.bio = "Test bio"
        user_data.password = "testpassword123"

        # Test registration
        result = auth_service.register_user(user_data)

        # Verify calls
        auth_service.user_repository.get_by_email.assert_called_once_with(
            "test@example.com"
        )
        auth_service.user_repository.get_by_username.assert_called_once_with("testuser")
        auth_service.user_repository.create.assert_called_once()

        # Verify result
        assert result == mock_user

    @patch("src.services.authentication.UserRepository")
    def test_register_user_duplicate_email(
        self, mock_repo_class, auth_service, mock_db
    ):
        """Test user registration with duplicate email."""
        # Setup mocks
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_by_email.return_value = Mock()  # User exists

        # Test data
        user_data = Mock()
        user_data.email = "test@example.com"
        user_data.username = "testuser"
        user_data.password = "testpassword123"

        # Test registration
        with pytest.raises(ValidationError) as exc_info:
            auth_service.register_user(user_data)

        assert "User with this email already exists" in str(exc_info.value)

    def test_register_user_duplicate_username(self, auth_service, mock_db):
        """Test user registration with duplicate username."""
        # Setup mocks
        auth_service.user_repository.get_by_email.return_value = None
        auth_service.user_repository.get_by_username.return_value = (
            Mock()
        )  # Username exists

        # Test data
        user_data = Mock()
        user_data.email = "test@example.com"
        user_data.username = "testuser"
        user_data.password = "testpassword123"

        # Test registration
        with pytest.raises(ValidationError) as exc_info:
            auth_service.register_user(user_data)

        assert "User with this username already exists" in str(exc_info.value)

    def test_authenticate_user_success(self, auth_service, mock_db):
        """Test successful user authentication."""
        # Setup mocks
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.is_active = True
        mock_user.hashed_password = "hashed_password"
        mock_user.update_last_login = Mock()

        auth_service.user_repository.get_by_email.return_value = mock_user

        # Mock password verification
        with patch.object(auth_service, "verify_password", return_value=True):
            # Test data
            login_data = Mock()
            login_data.email = "test@example.com"
            login_data.password = "testpassword123"

            # Test authentication
            result = auth_service.authenticate_user(login_data)

            # Verify result
            assert result == mock_user
            mock_user.update_last_login.assert_called_once()
            mock_db.commit.assert_called_once()

    @patch("src.services.authentication.UserRepository")
    def test_authenticate_user_not_found(self, mock_repo_class, auth_service, mock_db):
        """Test user authentication with non-existent user."""
        # Setup mocks
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_by_email.return_value = None

        # Test data
        login_data = Mock()
        login_data.email = "nonexistent@example.com"
        login_data.password = "testpassword123"

        # Test authentication
        result = auth_service.authenticate_user(login_data)

        # Verify result
        assert result is None

    @patch("src.services.authentication.UserRepository")
    def test_authenticate_user_inactive(self, mock_repo_class, auth_service, mock_db):
        """Test user authentication with inactive user."""
        # Setup mocks
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        mock_user = Mock()
        mock_user.is_active = False

        mock_repo.get_by_email.return_value = mock_user

        # Test data
        login_data = Mock()
        login_data.email = "test@example.com"
        login_data.password = "testpassword123"

        # Test authentication
        result = auth_service.authenticate_user(login_data)

        # Verify result
        assert result is None

    @patch("src.services.authentication.UserRepository")
    def test_authenticate_user_wrong_password(
        self, mock_repo_class, auth_service, mock_db
    ):
        """Test user authentication with wrong password."""
        # Setup mocks
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        mock_user = Mock()
        mock_user.is_active = True
        mock_user.hashed_password = "hashed_password"

        mock_repo.get_by_email.return_value = mock_user

        # Mock password verification
        with patch.object(auth_service, "verify_password", return_value=False):
            # Test data
            login_data = Mock()
            login_data.email = "test@example.com"
            login_data.password = "wrongpassword"

            # Test authentication
            result = auth_service.authenticate_user(login_data)

            # Verify result
            assert result is None

    def test_get_current_user_success(self, auth_service, mock_db):
        """Test successful current user retrieval."""
        # Setup mocks
        mock_user = Mock()
        mock_user.id = 1
        mock_user.is_active = True

        # Mock the repository
        auth_service.user_repository.get_by_id.return_value = mock_user

        # Mock token verification
        with patch.object(
            auth_service,
            "verify_token",
            return_value={"sub": "1", "email": "test@example.com"},
        ):
            # Test token
            token = "valid.token.here"

            # Test get current user
            result = auth_service.get_current_user(token)

            # Verify result
            assert result == mock_user
            auth_service.user_repository.get_by_id.assert_called_once_with(1)

    @patch("src.services.authentication.UserRepository")
    def test_get_current_user_invalid_token(
        self, mock_repo_class, auth_service, mock_db
    ):
        """Test current user retrieval with invalid token."""
        # Setup mocks
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        # Mock token verification
        with patch.object(auth_service, "verify_token", return_value=None):
            # Test token
            token = "invalid.token.here"

            # Test get current user
            result = auth_service.get_current_user(token)

            # Verify result
            assert result is None

    def test_get_current_user_inactive(self, auth_service, mock_db):
        """Test current user retrieval with inactive user."""
        # Setup mocks
        mock_user = Mock()
        mock_user.is_active = False

        # Mock the repository
        auth_service.user_repository.get_by_id.return_value = mock_user

        # Mock token verification
        with patch.object(
            auth_service,
            "verify_token",
            return_value={"sub": "1", "email": "test@example.com"},
        ):
            # Test token
            token = "valid.token.here"

            # Test get current user
            result = auth_service.get_current_user(token)

            # Verify result
            assert result is None

    def test_change_password_success(self, auth_service, mock_db):
        """Test successful password change."""
        # Setup mocks
        mock_user = Mock()
        mock_user.id = 1
        mock_user.hashed_password = "old_hashed_password"

        auth_service.user_repository.get_by_id.return_value = mock_user
        auth_service.user_repository.update.return_value = mock_user

        # Mock password verification
        with patch.object(auth_service, "verify_password", return_value=True):
            # Test password change
            result = auth_service.change_password(1, "oldpassword", "newpassword")

            # Verify result
            assert result is True
            auth_service.user_repository.update.assert_called_once()

    def test_change_password_user_not_found(self, auth_service, mock_db):
        """Test password change with non-existent user."""
        # Setup mocks
        auth_service.user_repository.get_by_id.return_value = None

        # Test password change
        with pytest.raises(NotFoundError):
            auth_service.change_password(999, "oldpassword", "newpassword")

    @patch("src.services.authentication.UserRepository")
    def test_change_password_wrong_current(
        self, mock_repo_class, auth_service, mock_db
    ):
        """Test password change with wrong current password."""
        # Setup mocks
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        mock_user = Mock()
        mock_user.id = 1
        mock_user.hashed_password = "old_hashed_password"

        mock_repo.get_by_id.return_value = mock_user

        # Mock password verification
        with patch.object(auth_service, "verify_password", return_value=False):
            # Test password change
            with pytest.raises(AuthenticationError) as exc_info:
                auth_service.change_password(1, "wrongpassword", "newpassword")

            assert "Current password is incorrect" in str(exc_info.value)

    def test_login_user_success(self, auth_service, mock_db):
        """Test successful user login."""
        # Setup mocks
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.is_active = True
        mock_user.hashed_password = "hashed_password"
        mock_user.update_last_login = Mock()

        auth_service.user_repository.get_by_email.return_value = mock_user

        # Mock password verification and token creation
        with patch.object(
            auth_service, "verify_password", return_value=True
        ), patch.object(auth_service, "create_access_token", return_value="mock_token"):
            # Test data
            login_data = Mock()
            login_data.email = "test@example.com"
            login_data.password = "testpassword123"

            # Test login
            result = auth_service.login_user(login_data)

            # Verify result
            assert result is not None
            assert hasattr(result, "access_token")
            assert hasattr(result, "token_type")
            assert result.token_type == "bearer"
            mock_user.update_last_login.assert_called_once()
            mock_db.commit.assert_called_once()

    def test_login_user_failure(self, auth_service, mock_db):
        """Test user login failure."""
        # Setup mocks
        auth_service.user_repository.get_by_email.return_value = None

        # Test data
        login_data = Mock()
        login_data.email = "nonexistent@example.com"
        login_data.password = "testpassword123"

        # Test login
        with pytest.raises(AuthenticationError) as exc_info:
            auth_service.login_user(login_data)

        # Verify result
        assert "Invalid email or password" in str(exc_info.value)

    def test_refresh_token_success(self, auth_service):
        """Test successful token refresh."""
        # Mock token verification
        with patch.object(
            auth_service,
            "verify_token",
            return_value={"sub": "1", "email": "test@example.com"},
        ), patch.object(auth_service, "create_access_token", return_value="new_token"):
            # Test token
            token = "valid.token.here"

            # Test refresh
            result = auth_service.refresh_token(token)

            # Verify result
            assert result is not None
            assert hasattr(result, "access_token")
            assert hasattr(result, "token_type")
            assert result.token_type == "bearer"

    def test_refresh_token_invalid(self, auth_service):
        """Test token refresh with invalid token."""
        # Mock token verification
        with patch.object(auth_service, "verify_token", return_value=None):
            # Test token
            token = "invalid.token.here"

            # Test refresh
            result = auth_service.refresh_token(token)

            # Verify result
            assert result is None

    def test_deactivate_user_success(self, auth_service, mock_db):
        """Test successful user deactivation."""
        # Setup mocks
        mock_user = Mock()
        mock_user.id = 1
        mock_user.is_active = True
        mock_user.deactivate = Mock()

        auth_service.user_repository.get_by_id.return_value = mock_user

        # Test deactivation
        result = auth_service.deactivate_user(1)

        # Verify result
        assert result is True
        mock_user.deactivate.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_deactivate_user_not_found(self, auth_service, mock_db):
        """Test user deactivation with non-existent user."""
        # Setup mocks
        auth_service.user_repository.get_by_id.return_value = None

        # Test deactivation
        with pytest.raises(NotFoundError) as exc_info:
            auth_service.deactivate_user(999)

        # Verify result
        assert "User" in str(exc_info.value)

    def test_verify_user_success(self, auth_service):
        """Test successful user verification."""
        # Setup mocks
        mock_user = Mock()
        mock_user.id = 1
        mock_user.is_active = True

        auth_service.user_repository.get_by_id.return_value = mock_user

        # Test verification
        result = auth_service.verify_user(1)

        # Verify result
        assert result is True

    def test_verify_user_not_found(self, auth_service):
        """Test user verification with non-existent user."""
        # Setup mocks
        auth_service.user_repository.get_by_id.return_value = None

        # Test verification
        with pytest.raises(NotFoundError) as exc_info:
            auth_service.verify_user(999)

        # Verify result
        assert "User" in str(exc_info.value)

    def test_verify_user_success_inactive(self, auth_service, mock_db):
        """Test user verification with inactive user (still succeeds)."""
        # Setup mocks
        mock_user = Mock()
        mock_user.id = 1
        mock_user.is_active = False
        mock_user.verify = Mock()

        auth_service.user_repository.get_by_id.return_value = mock_user

        # Test verification
        result = auth_service.verify_user(1)

        # Verify result
        assert result is True
        mock_user.verify.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_register_user_database_error(self, auth_service, mock_db):
        """Test user registration with database error."""
        # Setup mocks
        auth_service.user_repository.get_by_email.return_value = None
        auth_service.user_repository.get_by_username.return_value = None
        auth_service.user_repository.create.side_effect = Exception("Database error")

        # Test data
        user_data = Mock()
        user_data.email = "test@example.com"
        user_data.username = "testuser"
        user_data.password = "testpassword123"

        # Test registration
        with pytest.raises(ValidationError) as exc_info:
            auth_service.register_user(user_data)

        assert "Failed to register user" in str(exc_info.value)

    def test_authenticate_user_database_error(self, auth_service, mock_db):
        """Test user authentication with database error."""
        # Setup mocks
        auth_service.user_repository.get_by_email.side_effect = Exception(
            "Database error"
        )

        # Test data
        login_data = Mock()
        login_data.email = "test@example.com"
        login_data.password = "testpassword123"

        # Test authentication
        result = auth_service.authenticate_user(login_data)

        # Verify result
        assert result is None

    def test_change_password_database_error(self, auth_service, mock_db):
        """Test password change with database error."""
        # Setup mocks
        mock_user = Mock()
        mock_user.id = 1
        mock_user.hashed_password = "old_hashed_password"

        auth_service.user_repository.get_by_id.return_value = mock_user
        auth_service.user_repository.update.side_effect = Exception("Database error")

        # Mock password verification
        with patch.object(auth_service, "verify_password", return_value=True):
            # Test password change
            with pytest.raises(Exception):
                auth_service.change_password(1, "oldpassword", "newpassword")

    def test_deactivate_user_database_error(self, auth_service, mock_db):
        """Test user deactivation with database error."""
        # Setup mocks
        mock_user = Mock()
        mock_user.id = 1
        mock_user.is_active = True
        mock_user.deactivate = Mock()

        auth_service.user_repository.get_by_id.return_value = mock_user
        mock_db.commit.side_effect = Exception("Database error")

        # Test deactivation
        with pytest.raises(AuthenticationError) as exc_info:
            auth_service.deactivate_user(1)

        # Verify result
        assert "Failed to deactivate user" in str(exc_info.value)
