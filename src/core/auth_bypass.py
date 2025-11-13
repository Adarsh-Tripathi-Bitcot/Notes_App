"""
Authentication bypass utilities for testing.

This module provides utilities to bypass authentication during testing
while maintaining security in production environments.
"""

import os
from typing import Optional

from .config import settings


class AuthBypass:
    """
    Authentication bypass utility for testing.

    This class provides methods to bypass authentication during testing
    while ensuring security in production environments.
    """

    @staticmethod
    def is_bypass_enabled() -> bool:
        """
        Check if authentication bypass is enabled.

        Returns:
            True if bypass is enabled, False otherwise
        """
        # Only allow bypass in testing and development environments
        if settings.environment == "production":
            return False

        # Check both settings and environment variable
        return (
            settings.auth_bypass or os.getenv("AUTH_BYPASS", "false").lower() == "true"
        )

    @staticmethod
    def get_test_user_id() -> Optional[str]:
        """
        Get test user ID for bypass authentication.

        Returns:
            Test user ID if bypass is enabled, None otherwise
        """
        if not AuthBypass.is_bypass_enabled():
            return None

        # Check settings first, then environment variable
        if hasattr(settings, "test_user_id"):
            return settings.test_user_id

        return os.getenv("TEST_USER_ID", "test-user-123")

    @staticmethod
    def get_test_user_email() -> Optional[str]:
        """
        Get test user email for bypass authentication.

        Returns:
            Test user email if bypass is enabled, None otherwise
        """
        if not AuthBypass.is_bypass_enabled():
            return None

        # Check settings first, then environment variable
        if hasattr(settings, "test_user_email"):
            return settings.test_user_email

        return os.getenv("TEST_USER_EMAIL", "test@example.com")

    @staticmethod
    def get_test_user_username() -> Optional[str]:
        """
        Get test user username for bypass authentication.

        Returns:
            Test user username if bypass is enabled, None otherwise
        """
        if not AuthBypass.is_bypass_enabled():
            return None

        # Check settings first, then environment variable
        if hasattr(settings, "test_user_username"):
            return settings.test_user_username

        return os.getenv("TEST_USER_USERNAME", "testuser")


def create_test_user_context() -> dict:
    """
    Create test user context for bypass authentication.

    Returns:
        Dictionary containing test user information
    """
    if not AuthBypass.is_bypass_enabled():
        return {}

    username = AuthBypass.get_test_user_username()
    return {
        "user_id": AuthBypass.get_test_user_id(),
        "email": AuthBypass.get_test_user_email(),
        "username": username,
        "full_name": "Test User",
        "display_name": username,
        "is_test_user": True,
    }
