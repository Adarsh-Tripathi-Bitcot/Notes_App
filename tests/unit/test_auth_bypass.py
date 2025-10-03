"""
Unit tests for auth bypass module.

This module tests the authentication bypass functionality
for testing and development environments.
"""

from unittest.mock import patch

from src.core.auth_bypass import AuthBypass, create_test_user_context


class TestAuthBypass:
    """Test authentication bypass functionality."""

    def test_create_test_user_context(self):
        """Test creating test user context."""
        with patch("src.core.auth_bypass.settings") as mock_settings:
            mock_settings.environment = "testing"
            mock_settings.auth_bypass = True
            mock_settings.test_user_id = "test-user-123"
            mock_settings.test_user_email = "test@example.com"
            mock_settings.test_user_username = "testuser"

            context = create_test_user_context()

            assert context is not None
            assert context["user_id"] == "test-user-123"
            assert context["email"] == "test@example.com"
            assert context["username"] == "testuser"
            assert context["full_name"] == "Test User"
            assert context["display_name"] == "testuser"
            assert context["is_test_user"] is True

    def test_create_test_user_context_with_none_values(self):
        """Test creating test user context with None values."""
        with patch("src.core.auth_bypass.settings") as mock_settings:
            mock_settings.environment = "testing"
            mock_settings.auth_bypass = True
            mock_settings.test_user_id = "test-user-123"
            mock_settings.test_user_email = "test@example.com"
            mock_settings.test_user_username = None

            context = create_test_user_context()

            assert context is not None
            assert context["user_id"] == "test-user-123"
            assert context["email"] == "test@example.com"
            assert context["username"] is None
            assert context["full_name"] == "Test User"
            assert context["display_name"] is None
            assert context["is_test_user"] is True

    def test_create_test_user_context_consistency(self):
        """Test test user context creation consistency."""
        with patch("src.core.auth_bypass.settings") as mock_settings:
            mock_settings.environment = "testing"
            mock_settings.auth_bypass = True
            mock_settings.test_user_id = "test-user-123"
            mock_settings.test_user_email = "test@example.com"
            mock_settings.test_user_username = "testuser"

            context1 = create_test_user_context()
            context2 = create_test_user_context()

            # Should be consistent
            assert context1 == context2
            assert context1["user_id"] == context2["user_id"]
            assert context1["email"] == context2["email"]
            assert context1["username"] == context2["username"]

    def test_create_test_user_context_bypass_disabled(self):
        """Test creating test user context when bypass is disabled."""
        with patch("src.core.auth_bypass.settings") as mock_settings:
            mock_settings.environment = "production"
            mock_settings.auth_bypass = False

            context = create_test_user_context()

            assert context == {}

    def test_auth_bypass_is_bypass_enabled(self):
        """Test AuthBypass.is_bypass_enabled method."""
        with patch("src.core.auth_bypass.settings") as mock_settings:
            # Test with testing environment and auth_bypass enabled
            mock_settings.environment = "testing"
            mock_settings.auth_bypass = True
            assert AuthBypass.is_bypass_enabled() is True

            # Test with testing environment and auth_bypass disabled but env var enabled
            mock_settings.auth_bypass = False
            with patch("os.getenv", return_value="true"):
                assert AuthBypass.is_bypass_enabled() is True

            # Test with production environment
            mock_settings.environment = "production"
            mock_settings.auth_bypass = True
            with patch("os.getenv", return_value="true"):
                assert AuthBypass.is_bypass_enabled() is False

    def test_auth_bypass_get_test_user_id(self):
        """Test AuthBypass.get_test_user_id method."""
        with patch("src.core.auth_bypass.settings") as mock_settings:
            mock_settings.environment = "testing"
            mock_settings.auth_bypass = True
            mock_settings.test_user_id = "test-user-456"

            assert AuthBypass.get_test_user_id() == "test-user-456"

            # Test when bypass is disabled
            mock_settings.environment = "production"
            mock_settings.auth_bypass = False
            assert AuthBypass.get_test_user_id() is None

    def test_auth_bypass_get_test_user_email(self):
        """Test AuthBypass.get_test_user_email method."""
        with patch("src.core.auth_bypass.settings") as mock_settings:
            mock_settings.environment = "testing"
            mock_settings.auth_bypass = True
            mock_settings.test_user_email = "test@test.com"

            assert AuthBypass.get_test_user_email() == "test@test.com"

            # Test when bypass is disabled
            mock_settings.environment = "production"
            mock_settings.auth_bypass = False
            assert AuthBypass.get_test_user_email() is None

    def test_auth_bypass_get_test_user_username(self):
        """Test AuthBypass.get_test_user_username method."""
        with patch("src.core.auth_bypass.settings") as mock_settings:
            mock_settings.environment = "testing"
            mock_settings.auth_bypass = True
            mock_settings.test_user_username = "testuser123"

            assert AuthBypass.get_test_user_username() == "testuser123"

            # Test when bypass is disabled
            mock_settings.environment = "production"
            mock_settings.auth_bypass = False
            assert AuthBypass.get_test_user_username() is None
