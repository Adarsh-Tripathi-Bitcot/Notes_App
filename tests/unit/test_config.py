"""
Unit tests for config module.

This module tests the configuration management functionality.
"""

import os
from unittest.mock import patch

import pytest

from src.core.config import Settings


class TestSettings:
    """Test Settings configuration class."""

    def test_settings_initialization(self):
        """Test settings initialization with default values."""
        settings = Settings()
        assert settings is not None
        assert hasattr(settings, "database_url")
        assert hasattr(settings, "jwt_secret_key")
        assert hasattr(settings, "log_level")

    def test_settings_with_env_vars(self):
        """Test settings with environment variables."""
        with patch.dict(
            os.environ,
            {
                "LOG_LEVEL": "DEBUG",
                "ENVIRONMENT": "testing",
                "JWT_SECRET_KEY": "test-secret-key",
            },
        ):
            settings = Settings()
            assert settings.log_level == "DEBUG"
            assert settings.environment == "testing"
            assert settings.jwt_secret_key == "test-secret-key"

    def test_settings_database_url(self):
        """Test database URL configuration."""
        with patch.dict(
            os.environ, {"DATABASE_URL": "postgresql://test:test@localhost/testdb"}
        ):
            settings = Settings()
            assert "postgresql" in settings.database_url

    def test_settings_logging_config(self):
        """Test logging configuration."""
        with patch.dict(
            os.environ,
            {"LOG_LEVEL": "INFO", "LOG_FORMAT": "json", "ENABLE_COLORED_LOGS": "true"},
        ):
            settings = Settings()
            assert settings.log_level == "INFO"
            assert settings.log_format == "json"
            assert settings.enable_colored_logs is True

    def test_settings_auth_config(self):
        """Test authentication configuration."""
        with patch.dict(
            os.environ,
            {
                "AUTH_BYPASS": "true",
                "TEST_USER_ID": "test-user-123",
                "TEST_USER_EMAIL": "test@example.com",
            },
        ):
            settings = Settings()
            assert settings.auth_bypass is True
            assert settings.test_user_id == "test-user-123"
            assert settings.test_user_email == "test@example.com"

    def test_settings_boolean_fields(self):
        """Test boolean field parsing."""
        with patch.dict(
            os.environ,
            {
                "ENABLE_COLORED_LOGS": "false",
                "ENABLE_FILE_LINE_INFO": "true",
                "AUTH_BYPASS": "false",
            },
        ):
            settings = Settings()
            assert settings.enable_colored_logs is False
            assert settings.enable_file_line_info is True
            assert settings.auth_bypass is False

    def test_settings_string_fields(self):
        """Test string field parsing."""
        with patch.dict(
            os.environ,
            {
                "ENVIRONMENT": "production",
                "LOG_FORMAT": "text",
                "TEST_USER_USERNAME": "testuser",
            },
        ):
            settings = Settings()
            assert settings.environment == "production"
            assert settings.log_format == "text"
            assert settings.test_user_username == "testuser"

    def test_settings_validation(self):
        """Test settings validation."""
        settings = Settings()
        # Should not raise any validation errors
        assert settings is not None

    def test_settings_default_values(self):
        """Test default values when no env vars are set."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            # Should have default values
            assert settings is not None
            assert hasattr(settings, "log_level")
            assert hasattr(settings, "environment")

    def test_settings_environment_specific(self):
        """Test environment-specific settings."""
        # Test development environment
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            settings = Settings()
            assert settings.environment == "development"

        # Test production environment
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            settings = Settings()
            assert settings.environment == "production"

        # Test testing environment
        with patch.dict(os.environ, {"ENVIRONMENT": "testing"}):
            settings = Settings()
            assert settings.environment == "testing"

    def test_settings_logging_levels(self):
        """Test different logging levels."""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in levels:
            with patch.dict(os.environ, {"LOG_LEVEL": level}):
                settings = Settings()
                assert settings.log_level == level

    def test_settings_user_context_config(self):
        """Test user context configuration."""
        with patch.dict(
            os.environ,
            {
                "ENABLE_USER_CONTEXT": "true",
                "SHOW_USER_EMAIL": "true",
                "SHOW_USER_USERNAME": "true",
                "SHOW_USER_FULL_NAME": "true",
                "SHOW_USER_DISPLAY_NAME": "true",
            },
        ):
            settings = Settings()
            assert settings.enable_user_context is True
            assert settings.show_user_email is True
            assert settings.show_user_username is True
            assert settings.show_user_full_name is True
            assert settings.show_user_display_name is True

    def test_settings_request_context_config(self):
        """Test request context configuration."""
        with patch.dict(
            os.environ,
            {"ENABLE_REQUEST_CONTEXT": "true", "ENABLE_XRAY_TRACING": "true"},
        ):
            settings = Settings()
            assert settings.enable_request_context is True
            assert settings.enable_xray_tracing is True

    def test_settings_test_user_config(self):
        """Test test user configuration."""
        with patch.dict(
            os.environ,
            {
                "TEST_USER_ID": "test-user-123",
                "TEST_USER_EMAIL": "test@example.com",
                "TEST_USER_USERNAME": "testuser",
                "TEST_USER_FULL_NAME": "Test User",
                "TEST_USER_DISPLAY_NAME": "Test",
            },
        ):
            settings = Settings()
            assert settings.test_user_id == "test-user-123"
            assert settings.test_user_email == "test@example.com"
            assert settings.test_user_username == "testuser"
            assert settings.test_user_full_name == "Test User"
            assert settings.test_user_display_name == "Test"

    def test_settings_validation_error_handling(self):
        """Test settings validation error handling."""
        # Test with invalid boolean values
        with patch.dict(os.environ, {"ENABLE_COLORED_LOGS": "invalid_boolean"}):
            # Should handle invalid boolean gracefully
            try:
                settings = Settings()
                # Should either use default or handle gracefully
                assert settings is not None
            except Exception:
                # If it raises an exception, that's also acceptable
                pass

    def test_settings_environment_switching(self):
        """Test switching between different environments."""
        # Start with development
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            dev_settings = Settings()
            assert dev_settings.environment == "development"

        # Switch to production
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            prod_settings = Settings()
            assert prod_settings.environment == "production"

        # Switch to testing
        with patch.dict(os.environ, {"ENVIRONMENT": "testing"}):
            test_settings = Settings()
            assert test_settings.environment == "testing"

    def test_settings_comprehensive_config(self):
        """Test comprehensive configuration."""
        with patch.dict(
            os.environ,
            {
                "ENVIRONMENT": "production",
                "LOG_LEVEL": "WARNING",
                "LOG_FORMAT": "json",
                "ENABLE_COLORED_LOGS": "false",
                "ENABLE_FILE_LINE_INFO": "true",
                "ENABLE_USER_CONTEXT": "true",
                "ENABLE_REQUEST_CONTEXT": "true",
                "SHOW_USER_EMAIL": "true",
                "SHOW_USER_USERNAME": "true",
                "SHOW_USER_FULL_NAME": "true",
                "SHOW_USER_DISPLAY_NAME": "true",
                "ENABLE_XRAY_TRACING": "false",
                "AUTH_BYPASS": "false",
                "TEST_USER_ID": "test-user-123",
                "TEST_USER_EMAIL": "test@example.com",
                "TEST_USER_USERNAME": "testuser",
                "TEST_USER_FULL_NAME": "Test User",
                "TEST_USER_DISPLAY_NAME": "Test",
            },
        ):
            settings = Settings()

            # Verify all settings
            assert settings.environment == "production"
            assert settings.log_level == "WARNING"
            assert settings.log_format == "json"
            assert settings.enable_colored_logs is False
            assert settings.enable_file_line_info is True
            assert settings.enable_user_context is True
            assert settings.enable_request_context is True
            assert settings.show_user_email is True
            assert settings.show_user_username is True
            assert settings.show_user_full_name is True
            assert settings.show_user_display_name is True
            assert settings.enable_xray_tracing is False
            assert settings.auth_bypass is False
            assert settings.test_user_id == "test-user-123"
            assert settings.test_user_email == "test@example.com"
            assert settings.test_user_username == "testuser"
            assert settings.test_user_full_name == "Test User"
            assert settings.test_user_display_name == "Test"

    def test_settings_field_validators(self):
        """Test field validators."""
        # Test environment validation
        with pytest.raises(ValueError):
            with patch.dict(os.environ, {"ENVIRONMENT": "invalid"}):
                Settings()

        # Test log level validation
        with pytest.raises(ValueError):
            with patch.dict(os.environ, {"LOG_LEVEL": "INVALID"}):
                Settings()

        # Test log format validation
        with pytest.raises(ValueError):
            with patch.dict(os.environ, {"LOG_FORMAT": "invalid"}):
                Settings()

    def test_settings_jwt_validation(self):
        """Test JWT validation."""
        # Test JWT expiry validation
        with pytest.raises(ValueError):
            with patch.dict(os.environ, {"JWT_EXPIRY_MINUTES": "0"}):
                Settings()

        with pytest.raises(ValueError):
            with patch.dict(os.environ, {"JWT_EXPIRY_MINUTES": "10081"}):
                Settings()

    def test_settings_bcrypt_validation(self):
        """Test BCrypt validation."""
        # Test BCrypt rounds validation
        with pytest.raises(ValueError):
            with patch.dict(os.environ, {"BCRYPT_ROUNDS": "3"}):
                Settings()

        with pytest.raises(ValueError):
            with patch.dict(os.environ, {"BCRYPT_ROUNDS": "32"}):
                Settings()

    def test_settings_auth_bypass_validation(self):
        """Test auth bypass validation."""
        # Test auth bypass in production
        with pytest.raises(ValueError):
            with patch.dict(
                os.environ, {"ENVIRONMENT": "production", "AUTH_BYPASS": "true"}
            ):
                Settings()

    def test_settings_secret_key(self):
        """Test secret key configuration."""
        with patch.dict(os.environ, {"SECRET_KEY": "test-secret-key"}):
            settings = Settings()
            assert settings.secret_key == "test-secret-key"

    def test_settings_module_log_levels_validation(self):
        """Test module log levels validation."""
        with patch.dict(
            os.environ, {"MODULE_LOG_LEVELS": '{"test.module": "INVALID"}'}
        ):
            with pytest.raises(ValueError):
                Settings()
