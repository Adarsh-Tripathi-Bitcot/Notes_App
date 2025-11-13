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
        self.field = field


class AuthenticationError(NotesAppException):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed",
        error_code: str = "AUTH_001",
        **kwargs,
    ) -> None:
        """
        Initialize authentication error.

        Args:
            message: Error message
            error_code: Error code for the authentication error
            **kwargs: Additional error details
        """
        super().__init__(
            message=message,
            error_code=error_code,
            details=kwargs.get("details", {}),
        )
        self.error_code = error_code


class AuthorizationError(NotesAppException):
    """Raised when authorization fails."""

    def __init__(
        self,
        message: str = "Authorization failed",
        resource: Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        Initialize authorization error.

        Args:
            message: Error message
            resource: Resource that failed authorization
            **kwargs: Additional error details
        """
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            details=kwargs.get("details", {}),
        )
        self.resource = resource


class NotFoundError(NotesAppException):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        message: str = "Resource not found",
        resource: Optional[str] = None,
        identifier: Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        Initialize not found error.

        Args:
            message: Error message
            resource: Type of resource not found
            identifier: Identifier of the resource
            **kwargs: Additional error details
        """
        if resource and identifier:
            message = f"{resource} not found with identifier: {identifier}"
        elif resource:
            message = f"{resource} not found"

        details = kwargs.get("details", {})
        if resource:
            details["resource"] = resource
        if identifier:
            details["identifier"] = identifier

        super().__init__(message=message, error_code="NOT_FOUND", details=details)
        self.resource = resource


class ConflictError(NotesAppException):
    """Raised when a resource conflict occurs."""

    def __init__(
        self,
        message: str = "Resource conflict",
        resource: Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        Initialize conflict error.

        Args:
            message: Error message
            resource: Resource that caused the conflict
            **kwargs: Additional error details
        """
        super().__init__(
            message=message, error_code="CONFLICT", details=kwargs.get("details", {})
        )
        self.resource = resource


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
        self.operation = operation


class ExternalServiceError(NotesAppException):
    """Raised when an external service call fails."""

    def __init__(
        self,
        message: str = "Service unavailable",
        service: Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        Initialize external service error.

        Args:
            message: Error message
            service: Name of the external service
            **kwargs: Additional error details
        """
        details = kwargs.get("details", {})
        if service:
            details["service"] = service
            message = f"{service}: {message}"

        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details,
        )
        self.service = service
