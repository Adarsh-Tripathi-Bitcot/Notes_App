"""
Unit tests for error handler module.

This module tests error handling functionality
in the error handler module.
"""

from unittest.mock import Mock

import pytest
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from src.core.error_handler import (
    create_error_response,
    general_exception_handler,
    http_exception_handler,
    notes_app_exception_handler,
    setup_error_handlers,
    sqlalchemy_exception_handler,
    validation_exception_handler,
)
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


class TestCreateErrorResponse:
    """Test create_error_response function."""

    def test_create_error_response_basic(self):
        """Test basic error response creation."""
        response = create_error_response(status_code=400, message="Test error")

        assert isinstance(response, dict)
        assert response["error"]["message"] == "Test error"
        assert response["error"]["status_code"] == 400

    def test_create_error_response_with_error_code(self):
        """Test error response with error code."""
        response = create_error_response(
            status_code=422, message="Validation failed", error_code="VALIDATION_ERROR"
        )

        assert response["error"]["message"] == "Validation failed"
        assert response["error"]["status_code"] == 422
        assert response["error"]["code"] == "VALIDATION_ERROR"

    def test_create_error_response_with_details(self):
        """Test error response with details."""
        response = create_error_response(
            status_code=422,
            message="Validation failed",
            details={"errors": ["Field is required", "Invalid format"]},
        )

        assert response["error"]["message"] == "Validation failed"
        assert response["error"]["details"]["errors"] == [
            "Field is required",
            "Invalid format",
        ]

    def test_create_error_response_complete(self):
        """Test error response with all parameters."""
        response = create_error_response(
            status_code=500,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details={"trace_id": "12345"},
        )

        assert response["error"]["message"] == "Internal server error"
        assert response["error"]["status_code"] == 500
        assert response["error"]["code"] == "INTERNAL_ERROR"
        assert response["error"]["details"]["trace_id"] == "12345"


class TestNotesAppExceptionHandler:
    """Test notes_app_exception_handler function."""

    @pytest.mark.asyncio
    async def test_notes_app_exception_handler_validation_error(self):
        """Test handling of validation error."""
        request = Mock(spec=Request)
        request.url.path = "/test"
        request.method = "POST"

        error = ValidationError("Invalid input", field="email")
        error.error_code = "VALIDATION_ERROR"

        response = await notes_app_exception_handler(request, error)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 422
        content = response.body.decode()
        assert "Invalid input" in content

    @pytest.mark.asyncio
    async def test_notes_app_exception_handler_authentication_error(self):
        """Test handling of authentication error."""
        request = Mock(spec=Request)
        request.url.path = "/test"
        request.method = "POST"

        error = AuthenticationError("Invalid credentials")
        error.error_code = "AUTHENTICATION_ERROR"

        response = await notes_app_exception_handler(request, error)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 401
        content = response.body.decode()
        assert "Invalid credentials" in content

    @pytest.mark.asyncio
    async def test_notes_app_exception_handler_authorization_error(self):
        """Test handling of authorization error."""
        request = Mock(spec=Request)
        request.url.path = "/test"
        request.method = "POST"

        error = AuthorizationError("Access denied", resource="Note")
        error.error_code = "AUTHORIZATION_ERROR"

        response = await notes_app_exception_handler(request, error)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 403
        content = response.body.decode()
        assert "Access denied" in content

    @pytest.mark.asyncio
    async def test_notes_app_exception_handler_not_found_error(self):
        """Test handling of not found error."""
        request = Mock(spec=Request)
        request.url.path = "/test"
        request.method = "GET"

        error = NotFoundError(resource="User", identifier="123")
        error.error_code = "NOT_FOUND"

        response = await notes_app_exception_handler(request, error)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 404
        content = response.body.decode()
        assert "User" in content

    @pytest.mark.asyncio
    async def test_notes_app_exception_handler_conflict_error(self):
        """Test handling of conflict error."""
        request = Mock(spec=Request)
        request.url.path = "/test"
        request.method = "POST"

        error = ConflictError("Resource already exists", resource="User")
        error.error_code = "CONFLICT"

        response = await notes_app_exception_handler(request, error)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 409
        content = response.body.decode()
        assert "Resource already exists" in content

    @pytest.mark.asyncio
    async def test_notes_app_exception_handler_database_error(self):
        """Test handling of database error."""
        request = Mock(spec=Request)
        request.url.path = "/test"
        request.method = "POST"

        error = DatabaseError("Connection failed", operation="SELECT")
        error.error_code = "DATABASE_ERROR"

        response = await notes_app_exception_handler(request, error)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        content = response.body.decode()
        assert "Connection failed" in content

    @pytest.mark.asyncio
    async def test_notes_app_exception_handler_external_service_error(self):
        """Test handling of external service error."""
        request = Mock(spec=Request)
        request.url.path = "/test"
        request.method = "POST"

        error = ExternalServiceError("Service unavailable", service="EmailService")
        error.error_code = "EXTERNAL_SERVICE_ERROR"

        response = await notes_app_exception_handler(request, error)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 502
        content = response.body.decode()
        assert "Service unavailable" in content

    @pytest.mark.asyncio
    async def test_notes_app_exception_handler_unknown_error_code(self):
        """Test handling of unknown error code."""
        request = Mock(spec=Request)
        request.url.path = "/test"
        request.method = "POST"

        error = NotesAppException("Unknown error")
        error.error_code = "UNKNOWN_ERROR"

        response = await notes_app_exception_handler(request, error)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        content = response.body.decode()
        assert "Unknown error" in content


class TestHttpExceptionHandler:
    """Test http_exception_handler function."""

    @pytest.mark.asyncio
    async def test_http_exception_handler_basic(self):
        """Test basic HTTP exception handling."""
        request = Mock(spec=Request)
        request.url.path = "/test"
        request.method = "GET"

        error = HTTPException(status_code=400, detail="Bad request")
        response = await http_exception_handler(request, error)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        content = response.body.decode()
        assert "Bad request" in content

    @pytest.mark.asyncio
    async def test_http_exception_handler_different_status_codes(self):
        """Test HTTP exception with different status codes."""
        request = Mock(spec=Request)
        request.url.path = "/test"
        request.method = "GET"

        # Test 404
        error = HTTPException(status_code=404, detail="Not found")
        response = await http_exception_handler(request, error)
        assert response.status_code == 404

        # Test 500
        error = HTTPException(status_code=500, detail="Internal server error")
        response = await http_exception_handler(request, error)
        assert response.status_code == 500


class TestValidationExceptionHandler:
    """Test validation_exception_handler function."""

    @pytest.mark.asyncio
    async def test_validation_exception_handler_basic(self):
        """Test basic validation exception handling."""
        request = Mock(spec=Request)
        request.url.path = "/test"
        request.method = "POST"

        # Create a mock validation error
        error = RequestValidationError([])
        error.errors = Mock(
            return_value=[
                {
                    "loc": ("field1",),
                    "msg": "Field is required",
                    "type": "value_error.missing",
                },
                {"loc": ("field2",), "msg": "Invalid format", "type": "value_error"},
            ]
        )

        response = await validation_exception_handler(request, error)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 422
        content = response.body.decode()
        assert "Validation failed" in content
        assert "field1" in content
        assert "field2" in content


class TestSqlAlchemyExceptionHandler:
    """Test sqlalchemy_exception_handler function."""

    @pytest.mark.asyncio
    async def test_sqlalchemy_exception_handler_basic(self):
        """Test basic SQLAlchemy exception handling."""
        request = Mock(spec=Request)
        request.url.path = "/test"
        request.method = "POST"

        error = SQLAlchemyError("Database connection failed")
        response = await sqlalchemy_exception_handler(request, error)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        content = response.body.decode()
        assert "Database operation failed" in content


class TestGeneralExceptionHandler:
    """Test general_exception_handler function."""

    @pytest.mark.asyncio
    async def test_general_exception_handler_basic(self):
        """Test basic general exception handling."""
        request = Mock(spec=Request)
        request.url.path = "/test"
        request.method = "POST"

        error = ValueError("Invalid value")
        response = await general_exception_handler(request, error)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        content = response.body.decode()
        assert "An unexpected error occurred" in content

    @pytest.mark.asyncio
    async def test_general_exception_handler_unknown_exception(self):
        """Test handling of unknown exception."""
        request = Mock(spec=Request)
        request.url.path = "/test"
        request.method = "POST"

        error = Exception("Unknown error")
        response = await general_exception_handler(request, error)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        content = response.body.decode()
        assert "An unexpected error occurred" in content


class TestSetupErrorHandlers:
    """Test setup_error_handlers function."""

    def test_setup_error_handlers(self):
        """Test setting up error handlers."""
        mock_app = Mock()
        setup_error_handlers(mock_app)

        # Verify that exception handlers were added
        assert mock_app.add_exception_handler.called
        call_args = mock_app.add_exception_handler.call_args_list

        # Check that all expected exception types are handled
        exception_types = [args[0][0] for args in call_args]
        assert NotesAppException in exception_types
        assert HTTPException in exception_types
        assert RequestValidationError in exception_types
        assert SQLAlchemyError in exception_types
        assert Exception in exception_types

    def test_setup_error_handlers_with_existing_handlers(self):
        """Test setting up error handlers when app already has handlers."""
        mock_app = Mock()
        # Mock existing handlers
        mock_app.exception_handlers = {NotesAppException: Mock()}

        setup_error_handlers(mock_app)

        # Should still add all handlers
        assert mock_app.add_exception_handler.called
        call_count = mock_app.add_exception_handler.call_count
        assert call_count == 5  # Should add all 5 exception handlers


class TestErrorHandlerIntegration:
    """Test error handler integration scenarios."""

    def test_error_response_structure(self):
        """Test that error responses have consistent structure."""
        response = create_error_response(
            status_code=422,
            message="Test error",
            error_code="TEST_ERROR",
            details={"field": "test_field"},
        )

        # Check response structure
        assert "error" in response
        assert "message" in response["error"]
        assert "status_code" in response["error"]
        assert "code" in response["error"]
        assert "details" in response["error"]
        assert response["error"]["message"] == "Test error"
        assert response["error"]["details"]["field"] == "test_field"

    def test_error_response_with_none_details(self):
        """Test error response when details is None."""
        response = create_error_response(
            status_code=500, message="Test error", details=None
        )

        assert response["error"]["message"] == "Test error"
        assert "details" not in response["error"]

    def test_error_response_with_empty_details(self):
        """Test error response when details is empty."""
        response = create_error_response(
            status_code=500, message="Test error", details={}
        )

        assert response["error"]["message"] == "Test error"
        # Empty details should not be included in the response
        assert "details" not in response["error"]

    def test_error_response_unicode_handling(self):
        """Test error response with unicode characters."""
        response = create_error_response(
            status_code=500, message="Test error with unicode: ñáéíóú"
        )

        assert "ñáéíóú" in response["error"]["message"]
