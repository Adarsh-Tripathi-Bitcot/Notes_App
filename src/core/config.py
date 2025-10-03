"""
Configuration management using Pydantic BaseSettings.

This module provides centralized configuration management for the Notes App,
following the principle of configuration as code and environment-based settings.
"""

from typing import Dict, List

from pydantic import Field, field_validator
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

    # Enhanced Logging Configuration
    log_level: str = Field(
        default="", description="Logging level (empty for environment-based default)"
    )
    log_format: str = Field(default="text", description="Log format (json or text)")
    module_log_levels: Dict[str, str] = Field(
        default_factory=dict, description="Per-module log level overrides"
    )
    enable_colored_logs: bool = Field(
        default=True, description="Enable colored logs in development"
    )
    enable_file_line_info: bool = Field(
        default=True, description="Enable file and line number in logs"
    )
    enable_user_context: bool = Field(
        default=True, description="Enable user context in logs"
    )
    enable_request_context: bool = Field(
        default=True, description="Enable request context in logs"
    )
    show_user_email: bool = Field(default=True, description="Show user email in logs")
    show_user_username: bool = Field(
        default=True, description="Show user username in logs"
    )
    show_user_full_name: bool = Field(
        default=True, description="Show user full name in logs"
    )
    show_user_display_name: bool = Field(
        default=True, description="Show user display name in logs"
    )
    enable_xray_tracing: bool = Field(
        default=False, description="Enable AWS X-Ray tracing"
    )

    # Testing Configuration
    auth_bypass: bool = Field(
        default=False, description="Enable authentication bypass for testing"
    )
    test_user_id: str = Field(
        default="test-user-123", description="Test user ID for bypass"
    )
    test_user_email: str = Field(
        default="test@example.com", description="Test user email for bypass"
    )
    test_user_username: str = Field(
        default="testuser", description="Test user username for bypass"
    )
    test_user_full_name: str = Field(
        default="Test User", description="Test user full name for bypass"
    )
    test_user_display_name: str = Field(
        default="Test", description="Test user display name for bypass"
    )
    secret_key: str = Field(default="", description="Secret key for application")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        allowed_environments = ["development", "testing", "staging", "production"]
        if v not in allowed_environments:
            raise ValueError(f"Environment must be one of: {allowed_environments}")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str, info) -> str:
        """Validate log level value and set environment-based default."""
        if not v:
            # Set default based on environment
            environment = info.data.get("environment", "development")
            if environment == "development":
                return "DEBUG"
            elif environment == "testing":
                return "INFO"
            elif environment == "staging":
                return "WARNING"
            else:  # production
                return "ERROR"

        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of: {allowed_levels}")
        return v.upper()

    @field_validator("log_format")
    @classmethod
    def validate_log_format(cls, v: str) -> str:
        """Validate log format value."""
        allowed_formats = ["json", "text"]
        if v not in allowed_formats:
            raise ValueError(f"Log format must be one of: {allowed_formats}")
        return v

    @field_validator("module_log_levels")
    @classmethod
    def validate_module_log_levels(cls, v: Dict[str, str]) -> Dict[str, str]:
        """Validate module log levels."""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for module, level in v.items():
            if level.upper() not in allowed_levels:
                raise ValueError(
                    f"Module {module} log level must be one of: {allowed_levels}"
                )
        return {module: level.upper() for module, level in v.items()}

    @field_validator("jwt_expiry_minutes")
    @classmethod
    def validate_jwt_expiry(cls, v: int) -> int:
        """Validate JWT expiry minutes."""
        if v <= 0:
            raise ValueError("JWT expiry minutes must be positive")
        if v > 10080:  # 7 days
            raise ValueError("JWT expiry minutes cannot exceed 7 days")
        return v

    @field_validator("bcrypt_rounds")
    @classmethod
    def validate_bcrypt_rounds(cls, v: int) -> int:
        """Validate BCrypt rounds."""
        if v < 4 or v > 31:
            raise ValueError("BCrypt rounds must be between 4 and 31")
        return v

    @field_validator("auth_bypass")
    @classmethod
    def validate_auth_bypass(cls, v: bool, info) -> bool:
        """Validate authentication bypass setting."""
        environment = info.data.get("environment", "development")
        if v and environment not in ["testing", "development"]:
            raise ValueError(
                "Authentication bypass only allowed in testing/development"
            )
        return v


# Global settings instance
settings = Settings()
