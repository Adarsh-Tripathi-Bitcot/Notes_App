"""
Configuration management using Pydantic BaseSettings.

This module provides centralized configuration management for the Notes App,
following the principle of configuration as code and environment-based settings.
"""

from typing import List

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings using Pydantic BaseSettings.

    This class manages all configuration settings for the Notes App,
    including database, JWT, logging, and other application settings.
    """

    # Application Configuration
    app_name: str = Field(default="Notes App", description="Application name")
    debug: bool = Field(default=False, description="Enable debug mode")
    environment: str = Field(default="development", description="Environment name")

    # Database Configuration
    database_url: str = Field(..., description="PostgreSQL database URL")

    # JWT Configuration
    jwt_secret_key: str = Field(..., description="Secret key for JWT tokens")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiry_minutes: int = Field(
        default=60, description="JWT token expiry in minutes"
    )

    # Security Configuration
    bcrypt_rounds: int = Field(default=12, description="BCrypt hashing rounds")

    # CORS Configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins",
    )

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json or text)")

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @validator("environment")
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        allowed_environments = ["development", "testing", "staging", "production"]
        if v not in allowed_environments:
            raise ValueError(f"Environment must be one of: {allowed_environments}")
        return v

    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level value."""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of: {allowed_levels}")
        return v.upper()

    @validator("log_format")
    def validate_log_format(cls, v: str) -> str:
        """Validate log format value."""
        allowed_formats = ["json", "text"]
        if v not in allowed_formats:
            raise ValueError(f"Log format must be one of: {allowed_formats}")
        return v

    @validator("jwt_expiry_minutes")
    def validate_jwt_expiry(cls, v: int) -> int:
        """Validate JWT expiry minutes."""
        if v <= 0:
            raise ValueError("JWT expiry minutes must be positive")
        if v > 10080:  # 7 days
            raise ValueError("JWT expiry minutes cannot exceed 7 days")
        return v

    @validator("bcrypt_rounds")
    def validate_bcrypt_rounds(cls, v: int) -> int:
        """Validate BCrypt rounds."""
        if v < 4 or v > 31:
            raise ValueError("BCrypt rounds must be between 4 and 31")
        return v


# Global settings instance
settings = Settings()
