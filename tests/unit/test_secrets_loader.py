"""
Unit tests for secrets loader module.

This module contains tests for the secrets_loader module,
testing all functions for loading and validating secrets.
"""

from unittest.mock import patch

import pytest

from src.core.secrets_loader import (
    get_bcrypt_rounds,
    get_cors_origins,
    get_database_config,
    get_debug_mode,
    get_environment,
    get_jwt_config,
    get_logging_config,
    is_development,
    is_production,
    is_testing,
    load_database_url,
    load_jwt_secret,
    validate_secrets,
)


class TestSecretsLoader:
    """Test secrets loader functions."""

    def test_load_jwt_secret_success(self):
        """Test successful JWT secret loading."""
        with patch("src.core.secrets_loader.settings") as mock_settings:
            mock_settings.jwt_secret_key = "test_secret_key_that_is_long_enough"

            result = load_jwt_secret()

            assert result == "test_secret_key_that_is_long_enough"

    def test_load_jwt_secret_missing(self):
        """Test JWT secret loading when secret is missing."""
        with patch("src.core.secrets_loader.settings") as mock_settings:
            mock_settings.jwt_secret_key = None

            with pytest.raises(
                ValueError, match="JWT_SECRET_KEY is required but not set"
            ):
                load_jwt_secret()

    def test_load_jwt_secret_empty(self):
        """Test JWT secret loading when secret is empty."""
        with patch("src.core.secrets_loader.settings") as mock_settings:
            mock_settings.jwt_secret_key = ""

            with pytest.raises(
                ValueError, match="JWT_SECRET_KEY is required but not set"
            ):
                load_jwt_secret()

    def test_load_jwt_secret_short_warning(self):
        """Test JWT secret loading with short secret (warning)."""
        with patch("src.core.secrets_loader.settings") as mock_settings, patch(
            "src.core.secrets_loader.logger"
        ) as mock_logger:
            mock_settings.jwt_secret_key = "short"

            result = load_jwt_secret()

            assert result == "short"
            mock_logger.warning.assert_called_once_with(
                "JWT secret key is shorter than recommended (32 characters)"
            )

    def test_load_database_url_success(self):
        """Test successful database URL loading."""
        with patch("src.core.secrets_loader.settings") as mock_settings:
            mock_settings.database_url = "postgresql://user:pass@localhost/db"

            result = load_database_url()

            assert result == "postgresql://user:pass@localhost/db"

    def test_load_database_url_asyncpg(self):
        """Test database URL loading with asyncpg driver."""
        with patch("src.core.secrets_loader.settings") as mock_settings:
            mock_settings.database_url = "postgresql+asyncpg://user:pass@localhost/db"

            result = load_database_url()

            assert result == "postgresql+asyncpg://user:pass@localhost/db"

    def test_load_database_url_missing(self):
        """Test database URL loading when URL is missing."""
        with patch("src.core.secrets_loader.settings") as mock_settings:
            mock_settings.database_url = None

            with pytest.raises(
                ValueError, match="DATABASE_URL is required but not set"
            ):
                load_database_url()

    def test_load_database_url_empty(self):
        """Test database URL loading when URL is empty."""
        with patch("src.core.secrets_loader.settings") as mock_settings:
            mock_settings.database_url = ""

            with pytest.raises(
                ValueError, match="DATABASE_URL is required but not set"
            ):
                load_database_url()

    def test_load_database_url_invalid_format(self):
        """Test database URL loading with invalid format."""
        with patch("src.core.secrets_loader.settings") as mock_settings:
            mock_settings.database_url = "mysql://user:pass@localhost/db"

            with pytest.raises(
                ValueError, match="DATABASE_URL must be a valid PostgreSQL URL"
            ):
                load_database_url()

    def test_get_environment(self):
        """Test getting environment."""
        with patch("src.core.secrets_loader.settings") as mock_settings:
            mock_settings.environment = "testing"

            result = get_environment()

            assert result == "testing"

    def test_is_development_true(self):
        """Test development mode check when true."""
        with patch("src.core.secrets_loader.settings") as mock_settings:
            mock_settings.environment = "development"

            result = is_development()

            assert result is True

    def test_is_development_false(self):
        """Test development mode check when false."""
        with patch("src.core.secrets_loader.settings") as mock_settings:
            mock_settings.environment = "production"

            result = is_development()

            assert result is False

    def test_is_production_true(self):
        """Test production mode check when true."""
        with patch("src.core.secrets_loader.settings") as mock_settings:
            mock_settings.environment = "production"

            result = is_production()

            assert result is True

    def test_is_production_false(self):
        """Test production mode check when false."""
        with patch("src.core.secrets_loader.settings") as mock_settings:
            mock_settings.environment = "development"

            result = is_production()

            assert result is False

    def test_is_testing_true(self):
        """Test testing mode check when true."""
        with patch("src.core.secrets_loader.settings") as mock_settings:
            mock_settings.environment = "testing"

            result = is_testing()

            assert result is True

    def test_is_testing_false(self):
        """Test testing mode check when false."""
        with patch("src.core.secrets_loader.settings") as mock_settings:
            mock_settings.environment = "development"

            result = is_testing()

            assert result is False

    def test_get_debug_mode_true(self):
        """Test debug mode when enabled."""
        with patch("src.core.secrets_loader.settings") as mock_settings:
            mock_settings.debug = True

            result = get_debug_mode()

            assert result is True

    def test_get_debug_mode_false(self):
        """Test debug mode when disabled."""
        with patch("src.core.secrets_loader.settings") as mock_settings:
            mock_settings.debug = False

            result = get_debug_mode()

            assert result is False

    def test_validate_secrets_success(self):
        """Test successful secrets validation."""
        with patch("src.core.secrets_loader.load_jwt_secret") as mock_jwt, patch(
            "src.core.secrets_loader.load_database_url"
        ) as mock_db:
            mock_jwt.return_value = "secret"
            mock_db.return_value = "postgresql://test"

            result = validate_secrets()

            assert result is True
            mock_jwt.assert_called_once()
            mock_db.assert_called_once()

    def test_validate_secrets_failure(self):
        """Test secrets validation failure."""
        with patch("src.core.secrets_loader.load_jwt_secret") as mock_jwt, patch(
            "src.core.secrets_loader.load_database_url"
        ), patch("src.core.secrets_loader.logger") as mock_logger:
            mock_jwt.side_effect = ValueError("JWT secret missing")

            result = validate_secrets()

            assert result is False
            mock_logger.error.assert_called_once_with(
                "Secret validation failed", error="JWT secret missing"
            )

    def test_get_cors_origins(self):
        """Test getting CORS origins."""
        with patch("src.core.secrets_loader.settings") as mock_settings:
            mock_settings.cors_origins = [
                "http://localhost:3000",
                "https://example.com",
            ]

            result = get_cors_origins()

            assert result == ["http://localhost:3000", "https://example.com"]

    def test_get_bcrypt_rounds(self):
        """Test getting BCrypt rounds."""
        with patch("src.core.secrets_loader.settings") as mock_settings:
            mock_settings.bcrypt_rounds = 12

            result = get_bcrypt_rounds()

            assert result == 12

    def test_get_jwt_config(self):
        """Test getting JWT configuration."""
        with patch("src.core.secrets_loader.load_jwt_secret") as mock_jwt, patch(
            "src.core.secrets_loader.settings"
        ) as mock_settings:
            mock_jwt.return_value = "test_secret"
            mock_settings.jwt_algorithm = "HS256"
            mock_settings.jwt_expiry_minutes = 30

            result = get_jwt_config()

            expected = {
                "secret_key": "test_secret",
                "algorithm": "HS256",
                "expiry_minutes": 30,
            }
            assert result == expected

    def test_get_database_config(self):
        """Test getting database configuration."""
        with patch("src.core.secrets_loader.load_database_url") as mock_db, patch(
            "src.core.secrets_loader.settings"
        ) as mock_settings:
            mock_db.return_value = "postgresql://test"
            mock_settings.debug = True

            result = get_database_config()

            expected = {
                "url": "postgresql://test",
                "echo": True,
                "pool_pre_ping": True,
                "pool_recycle": 300,
            }
            assert result == expected

    def test_get_logging_config(self):
        """Test getting logging configuration."""
        with patch("src.core.secrets_loader.settings") as mock_settings:
            mock_settings.log_level = "INFO"
            mock_settings.log_format = "json"

            result = get_logging_config()

            expected = {
                "level": "INFO",
                "format": "json",
            }
            assert result == expected
