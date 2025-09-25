"""
Custom exceptions for the Notes App.

This module defines custom exceptions that provide clear error handling
and meaningful error messages throughout the application.
"""

from typing import Any, Dict, Optional


class NotesAppException(Exception):
    """
    Base exception class for all Notes App exceptions.

    This provides a common base for all custom exceptions in the application,
    allowing for consistent error handling and logging.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize the exception.

        Args:
            message: Human-readable error message
            error_code: Optional error code for programmatic handling
            details: Optional additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class ValidationError(NotesAppException):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str = "Validation failed",
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs,
    ) -> None:
        """
        Initialize validation error.

        Args:
            message: Error message
            field: Field that failed validation
            value: Value that failed validation
            **kwargs: Additional error details
        """
        details = kwargs.get("details", {})
        if field is not None:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)

        super().__init__(
            message=message, error_code="VALIDATION_ERROR", details=details
        )


class AuthenticationError(NotesAppException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed", **kwargs) -> None:
        """
        Initialize authentication error.

        Args:
            message: Error message
            **kwargs: Additional error details
        """
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            details=kwargs.get("details", {}),
        )


class AuthorizationError(NotesAppException):
    """Raised when authorization fails."""

    def __init__(self, message: str = "Authorization failed", **kwargs) -> None:
        """
        Initialize authorization error.

        Args:
            message: Error message
            **kwargs: Additional error details
        """
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            details=kwargs.get("details", {}),
        )


class NotFoundError(NotesAppException):
    """Raised when a requested resource is not found."""

    def __init__(
        self, resource: str, identifier: Optional[str] = None, **kwargs
    ) -> None:
        """
        Initialize not found error.

        Args:
            resource: Type of resource not found
            identifier: Identifier of the resource
            **kwargs: Additional error details
        """
        message = f"{resource} not found"
        if identifier:
            message += f" with identifier: {identifier}"

        details = kwargs.get("details", {})
        details["resource"] = resource
        if identifier:
            details["identifier"] = identifier

        super().__init__(message=message, error_code="NOT_FOUND", details=details)


class ConflictError(NotesAppException):
    """Raised when a resource conflict occurs."""

    def __init__(self, message: str = "Resource conflict", **kwargs) -> None:
        """
        Initialize conflict error.

        Args:
            message: Error message
            **kwargs: Additional error details
        """
        super().__init__(
            message=message, error_code="CONFLICT", details=kwargs.get("details", {})
        )


class DatabaseError(NotesAppException):
    """Raised when a database operation fails."""

    def __init__(
        self,
        message: str = "Database operation failed",
        operation: Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        Initialize database error.

        Args:
            message: Error message
            operation: Database operation that failed
            **kwargs: Additional error details
        """
        details = kwargs.get("details", {})
        if operation:
            details["operation"] = operation

        super().__init__(message=message, error_code="DATABASE_ERROR", details=details)


class ExternalServiceError(NotesAppException):
    """Raised when an external service call fails."""

    def __init__(
        self, service: str, message: str = "External service error", **kwargs
    ) -> None:
        """
        Initialize external service error.

        Args:
            service: Name of the external service
            message: Error message
            **kwargs: Additional error details
        """
        details = kwargs.get("details", {})
        details["service"] = service

        super().__init__(
            message=f"{service}: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details,
        )
