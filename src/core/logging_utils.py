"""
Enhanced logging utilities for different service layers.

This module provides specialized logging functions for repositories,
services, and API layers with structured metadata and context tracking.
"""

from typing import Any, Optional

from .logging import get_logger, get_user_id


class ServiceLogger:
    """Logger wrapper for service layer operations."""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = get_logger(f"src.services.{service_name}")

    def log_operation(self, operation: str, **kwargs):
        """Log service operation with structured metadata."""
        self.logger.info(
            f"Service operation: {operation}",
            service=self.service_name,
            operation=operation,
            **kwargs,
        )

    def log_success(self, operation: str, **kwargs):
        """Log successful service operation."""
        self.logger.info(
            f"Service operation completed: {operation}",
            service=self.service_name,
            operation=operation,
            status="success",
            **kwargs,
        )

    def log_error(self, operation: str, error: Exception, **kwargs):
        """Log service operation error."""
        self.logger.error(
            f"Service operation failed: {operation}",
            service=self.service_name,
            operation=operation,
            status="error",
            error=str(error),
            error_type=type(error).__name__,
            **kwargs,
        )


class RepositoryLogger:
    """Logger wrapper for repository layer operations."""

    def __init__(self, repository_name: str):
        self.repository_name = repository_name
        self.logger = get_logger(f"src.repositories.{repository_name}")

    def log_query(self, operation: str, table: str, **kwargs):
        """Log database query with structured metadata."""
        self.logger.debug(
            f"Database query: {operation}",
            repository=self.repository_name,
            operation=operation,
            table=table,
            **kwargs,
        )

    def log_success(self, operation: str, **kwargs):
        """Log successful repository operation."""
        self.logger.debug(
            f"Repository operation completed: {operation}",
            repository=self.repository_name,
            operation=operation,
            status="success",
            **kwargs,
        )

    def log_error(self, operation: str, error: Exception, **kwargs):
        """Log repository operation error."""
        self.logger.error(
            f"Repository operation failed: {operation}",
            repository=self.repository_name,
            operation=operation,
            status="error",
            error=str(error),
            error_type=type(error).__name__,
            **kwargs,
        )


class APILogger:
    """Logger wrapper for API layer operations."""

    def __init__(self, router_name: str):
        self.router_name = router_name
        self.logger = get_logger(f"src.api.routers.{router_name}")

    def log_request(self, method: str, path: str, **kwargs):
        """Log API request with structured metadata."""
        self.logger.info(
            f"API request: {method} {path}",
            router=self.router_name,
            method=method,
            path=path,
            **kwargs,
        )

    def log_response(self, method: str, path: str, status_code: int, **kwargs):
        """Log API response with structured metadata."""
        self.logger.info(
            f"API response: {method} {path} - {status_code}",
            router=self.router_name,
            method=method,
            path=path,
            status_code=status_code,
            **kwargs,
        )

    def log_error(self, method: str, path: str, error: Exception, **kwargs):
        """Log API error with structured metadata."""
        self.logger.error(
            f"API error: {method} {path}",
            router=self.router_name,
            method=method,
            path=path,
            error=str(error),
            error_type=type(error).__name__,
            **kwargs,
        )


def log_user_operation(operation: str, user_id_val: Optional[str] = None, **kwargs):
    """Log user-related operations with context."""
    logger = get_logger("src.operations.user")
    current_user_id = user_id_val or get_user_id()

    logger.info(
        f"User operation: {operation}",
        operation=operation,
        user_id=current_user_id,
        **kwargs,
    )


def log_note_operation(operation: str, note_id: Optional[str] = None, **kwargs):
    """Log note-related operations with context."""
    logger = get_logger("src.operations.note")
    current_user_id = get_user_id()

    logger.info(
        f"Note operation: {operation}",
        operation=operation,
        note_id=note_id,
        user_id=current_user_id,
        **kwargs,
    )


def log_validation(validator: str, field: str, value: Any, **kwargs):
    """Log validation operations."""
    logger = get_logger("src.validators")

    logger.debug(
        f"Validation: {validator}",
        validator=validator,
        field=field,
        value=str(value)[:100] if value else None,  # Truncate long values
        **kwargs,
    )


def log_cache_operation(operation: str, key: str, **kwargs):
    """Log cache operations."""
    logger = get_logger("src.cache")

    logger.debug(
        f"Cache operation: {operation}", operation=operation, key=key, **kwargs
    )


def log_database_session(operation: str, **kwargs):
    """Log database session operations."""
    logger = get_logger("src.core.database")

    logger.debug(f"Database session: {operation}", operation=operation, **kwargs)
