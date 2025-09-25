"""
Secrets and sensitive data management.

This module provides utilities for loading and managing sensitive configuration
data such as JWT secrets, database credentials, and other secrets.
"""


from .config import settings
from .logging import get_logger

logger = get_logger(__name__)


def load_jwt_secret() -> str:
    """
    Load JWT secret key from environment or configuration.

    Returns:
        JWT secret key

    Raises:
        ValueError: If JWT secret key is not found or is invalid
    """
    secret = settings.jwt_secret_key

    if not secret:
        raise ValueError("JWT_SECRET_KEY is required but not set")

    if len(secret) < 32:
        logger.warning("JWT secret key is shorter than recommended (32 characters)")

    return secret


def load_database_url() -> str:
    """
    Load database URL from environment or configuration.

    Returns:
        Database URL

    Raises:
        ValueError: If database URL is not found or is invalid
    """
    database_url = settings.database_url

    if not database_url:
        raise ValueError("DATABASE_URL is required but not set")

    # Validate database URL format
    if not database_url.startswith(("postgresql://", "postgresql+asyncpg://")):
        raise ValueError("DATABASE_URL must be a valid PostgreSQL URL")

    return database_url


def get_environment() -> str:
    """
    Get the current environment.

    Returns:
        Environment name (development, testing, staging, production)
    """
    return settings.environment


def is_development() -> bool:
    """
    Check if the application is running in development mode.

    Returns:
        True if in development mode, False otherwise
    """
    return settings.environment == "development"


def is_production() -> bool:
    """
    Check if the application is running in production mode.

    Returns:
        True if in production mode, False otherwise
    """
    return settings.environment == "production"


def is_testing() -> bool:
    """
    Check if the application is running in testing mode.

    Returns:
        True if in testing mode, False otherwise
    """
    return settings.environment == "testing"


def get_debug_mode() -> bool:
    """
    Get debug mode setting.

    Returns:
        True if debug mode is enabled, False otherwise
    """
    return settings.debug


def validate_secrets() -> bool:
    """
    Validate that all required secrets are present and valid.

    Returns:
        True if all secrets are valid, False otherwise
    """
    try:
        load_jwt_secret()
        load_database_url()
        return True
    except ValueError as e:
        logger.error("Secret validation failed", error=str(e))
        return False


def get_cors_origins() -> list[str]:
    """
    Get CORS origins from configuration.

    Returns:
        List of allowed CORS origins
    """
    return settings.cors_origins


def get_bcrypt_rounds() -> int:
    """
    Get BCrypt rounds from configuration.

    Returns:
        Number of BCrypt rounds
    """
    return settings.bcrypt_rounds


def get_jwt_config() -> dict[str, any]:
    """
    Get JWT configuration.

    Returns:
        Dictionary containing JWT configuration
    """
    return {
        "secret_key": load_jwt_secret(),
        "algorithm": settings.jwt_algorithm,
        "expiry_minutes": settings.jwt_expiry_minutes,
    }


def get_database_config() -> dict[str, any]:
    """
    Get database configuration.

    Returns:
        Dictionary containing database configuration
    """
    return {
        "url": load_database_url(),
        "echo": settings.debug,
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }


def get_logging_config() -> dict[str, any]:
    """
    Get logging configuration.

    Returns:
        Dictionary containing logging configuration
    """
    return {
        "level": settings.log_level,
        "format": settings.log_format,
    }
