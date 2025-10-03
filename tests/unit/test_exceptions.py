"""
Unit tests for exceptions module.

This module tests the custom exception classes and error handling.
"""


from src.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    DatabaseError,
    ExternalServiceError,
    NotesAppException,
    NotFoundError,
    ValidationError,
)


class TestNotesAppException:
    """Test base NotesAppException class."""

    def test_notes_app_exception_basic(self):
        """Test basic exception creation."""
        exc = NotesAppException("Test error")
        assert str(exc) == "Test error"
        assert exc.message == "Test error"

    def test_notes_app_exception_with_details(self):
        """Test exception with details."""
        details = {"field": "value", "code": 123}
        exc = NotesAppException("Test error", details=details)
        assert str(exc) == "Test error"
        assert exc.message == "Test error"
        assert exc.details == details

    def test_notes_app_exception_inheritance(self):
        """Test exception inheritance."""
        exc = NotesAppException("Test error")
        assert isinstance(exc, Exception)
        assert isinstance(exc, NotesAppException)


class TestValidationError:
    """Test ValidationError class."""

    def test_validation_error_basic(self):
        """Test basic validation error."""
        exc = ValidationError("Validation failed")
        assert str(exc) == "Validation failed"
        assert exc.message == "Validation failed"
        assert isinstance(exc, NotesAppException)

    def test_validation_error_with_field(self):
        """Test validation error with field."""
        exc = ValidationError("Invalid email", field="email")
        assert str(exc) == "Invalid email"
        assert exc.field == "email"


class TestAuthenticationError:
    """Test AuthenticationError class."""

    def test_authentication_error_basic(self):
        """Test basic authentication error."""
        exc = AuthenticationError("Authentication failed")
        assert str(exc) == "Authentication failed"
        assert isinstance(exc, NotesAppException)

    def test_authentication_error_with_code(self):
        """Test authentication error with error code."""
        exc = AuthenticationError("Invalid credentials", error_code="AUTH_001")
        assert exc.error_code == "AUTH_001"


class TestAuthorizationError:
    """Test AuthorizationError class."""

    def test_authorization_error_basic(self):
        """Test basic authorization error."""
        exc = AuthorizationError("Access denied")
        assert str(exc) == "Access denied"
        assert isinstance(exc, NotesAppException)

    def test_authorization_error_with_resource(self):
        """Test authorization error with resource."""
        exc = AuthorizationError("Access denied", resource="note_123")
        assert exc.resource == "note_123"


class TestNotFoundError:
    """Test NotFoundError class."""

    def test_not_found_error_basic(self):
        """Test basic not found error."""
        exc = NotFoundError("Resource not found")
        assert str(exc) == "Resource not found"
        assert isinstance(exc, NotesAppException)

    def test_not_found_error_with_resource(self):
        """Test not found error with resource."""
        exc = NotFoundError("User not found", resource="user_123")
        assert exc.resource == "user_123"

    def test_not_found_error_with_resource_and_identifier(self):
        """Test not found error with resource and identifier."""
        exc = NotFoundError(resource="User", identifier="123")
        assert exc.resource == "User"
        assert "User not found with identifier: 123" in str(exc)


class TestConflictError:
    """Test ConflictError class."""

    def test_conflict_error_basic(self):
        """Test basic conflict error."""
        exc = ConflictError("Resource already exists")
        assert str(exc) == "Resource already exists"
        assert isinstance(exc, NotesAppException)

    def test_conflict_error_with_resource(self):
        """Test conflict error with resource."""
        exc = ConflictError("Email already exists", resource="email@example.com")
        assert exc.resource == "email@example.com"


class TestDatabaseError:
    """Test DatabaseError class."""

    def test_database_error_basic(self):
        """Test basic database error."""
        exc = DatabaseError("Database error")
        assert str(exc) == "Database error"
        assert isinstance(exc, NotesAppException)

    def test_database_error_with_operation(self):
        """Test database error with operation."""
        exc = DatabaseError("Query failed", operation="SELECT")
        assert exc.operation == "SELECT"


class TestExternalServiceError:
    """Test ExternalServiceError class."""

    def test_external_service_error_basic(self):
        """Test basic external service error."""
        exc = ExternalServiceError("Service unavailable")
        assert str(exc) == "Service unavailable"
        assert isinstance(exc, NotesAppException)

    def test_external_service_error_with_service(self):
        """Test external service error with service name."""
        exc = ExternalServiceError("API error", service="payment_gateway")
        assert exc.service == "payment_gateway"
        assert "payment_gateway: API error" in str(exc)


class TestExceptionHierarchy:
    """Test exception hierarchy and inheritance."""

    def test_exception_inheritance(self):
        """Test that all custom exceptions inherit from NotesAppException."""
        exceptions = [
            ValidationError("test"),
            AuthenticationError("test"),
            AuthorizationError("test"),
            NotFoundError("test"),
            ConflictError("test"),
            DatabaseError("test"),
            ExternalServiceError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, NotesAppException)
            assert isinstance(exc, Exception)

    def test_exception_message_handling(self):
        """Test exception message handling."""
        message = "Test error message"
        exc = NotesAppException(message)
        assert str(exc) == message
        assert exc.message == message

    def test_exception_details_handling(self):
        """Test exception details handling."""
        details = {"key1": "value1", "key2": "value2"}
        exc = NotesAppException("Test error", details=details)
        assert exc.details == details

    def test_exception_with_none_values(self):
        """Test exception with None values."""
        exc = NotesAppException("Test error", details=None)
        assert exc.details == {}

    def test_exception_string_representation(self):
        """Test exception string representation."""
        exc = NotesAppException("Test error")
        assert "Test error" in str(exc)
        assert "NotesAppException" in repr(exc)

    def test_exception_with_empty_message(self):
        """Test exception with empty message."""
        exc = NotesAppException("")
        assert str(exc) == ""
        assert exc.message == ""

    def test_exception_with_unicode_message(self):
        """Test exception with unicode message."""
        message = "Test error with unicode: 测试"
        exc = NotesAppException(message)
        assert str(exc) == message
        assert exc.message == message

    def test_exception_error_codes(self):
        """Test exception error codes."""
        assert ValidationError("test").error_code == "VALIDATION_ERROR"
        assert AuthenticationError("test").error_code == "AUTH_001"
        assert AuthorizationError("test").error_code == "AUTHORIZATION_ERROR"
        assert NotFoundError("test").error_code == "NOT_FOUND"
        assert ConflictError("test").error_code == "CONFLICT"
        assert DatabaseError("test").error_code == "DATABASE_ERROR"
        assert ExternalServiceError("test").error_code == "EXTERNAL_SERVICE_ERROR"
