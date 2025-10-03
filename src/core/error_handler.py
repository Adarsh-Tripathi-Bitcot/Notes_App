"""
Global error handling and response formatting.

This module provides centralized error handling for the FastAPI application,
ensuring consistent error responses and proper logging of errors.
"""

from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from .exceptions import NotesAppException
from .logging import get_logger

logger = get_logger(__name__)


def create_error_response(
    status_code: int,
    message: str,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a standardized error response.

    Args:
        status_code: HTTP status code
        message: Error message
        error_code: Optional error code
        details: Optional additional details

    Returns:
        Standardized error response dictionary
    """
    response = {
        "error": {
            "message": message,
            "status_code": status_code,
        }
    }

    if error_code:
        response["error"]["code"] = error_code

    if details:
        response["error"]["details"] = details

    return response


async def notes_app_exception_handler(
    request: Request, exc: NotesAppException
) -> JSONResponse:
    """
    Handle custom NotesAppException instances.

    Args:
        request: FastAPI request object
        exc: NotesAppException instance

    Returns:
        JSON error response
    """
    # Log the error
    logger.error(
        "NotesApp exception occurred",
        error=exc.message,
        error_code=exc.error_code,
        error_details=exc.details,
        path=request.url.path,
        method=request.method,
    )

    # Determine status code based on error type
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    if isinstance(exc, (NotesAppException,)):
        if hasattr(exc, "error_code"):
            if exc.error_code == "VALIDATION_ERROR":
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            elif exc.error_code == "AUTHENTICATION_ERROR":
                status_code = status.HTTP_401_UNAUTHORIZED
            elif exc.error_code == "AUTHORIZATION_ERROR":
                status_code = status.HTTP_403_FORBIDDEN
            elif exc.error_code == "NOT_FOUND":
                status_code = status.HTTP_404_NOT_FOUND
            elif exc.error_code == "CONFLICT":
                status_code = status.HTTP_409_CONFLICT
            elif exc.error_code == "DATABASE_ERROR":
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            elif exc.error_code == "EXTERNAL_SERVICE_ERROR":
                status_code = status.HTTP_502_BAD_GATEWAY

    return JSONResponse(
        status_code=status_code,
        content=create_error_response(
            status_code=status_code,
            message=exc.message,
            error_code=exc.error_code,
            details=exc.details,
        ),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle FastAPI HTTPException instances.

    Args:
        request: FastAPI request object
        exc: HTTPException instance

    Returns:
        JSON error response
    """
    # Log the error
    logger.warning(
        "HTTP exception occurred",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
        method=request.method,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            status_code=exc.status_code,
            message=str(exc.detail),
            error_code="HTTP_ERROR",
        ),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors.

    Args:
        request: FastAPI request object
        exc: RequestValidationError instance

    Returns:
        JSON error response
    """
    # Log the validation error
    logger.warning(
        "Validation error occurred",
        errors=exc.errors(),
        path=request.url.path,
        method=request.method,
    )

    # Format validation errors
    formatted_errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        formatted_errors.append(
            {"field": field, "message": error["msg"], "type": error["type"]}
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Validation failed",
            error_code="VALIDATION_ERROR",
            details={"validation_errors": formatted_errors},
        ),
    )


async def sqlalchemy_exception_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    """
    Handle SQLAlchemy database errors.

    Args:
        request: FastAPI request object
        exc: SQLAlchemyError instance

    Returns:
        JSON error response
    """
    # Log the database error
    logger.error(
        "Database error occurred",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        method=request.method,
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Database operation failed",
            error_code="DATABASE_ERROR",
            details={"error_type": type(exc).__name__},
        ),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle general exceptions that are not caught by specific handlers.

    Args:
        request: FastAPI request object
        exc: Exception instance

    Returns:
        JSON error response
    """
    # Log the error
    logger.error(
        "Unhandled exception occurred",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        method=request.method,
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred",
            error_code="INTERNAL_SERVER_ERROR",
        ),
    )


def setup_error_handlers(app: FastAPI) -> None:
    """
    Set up all error handlers for the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    # Custom exception handlers
    app.add_exception_handler(NotesAppException, notes_app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    logger.info("Error handlers configured successfully")
