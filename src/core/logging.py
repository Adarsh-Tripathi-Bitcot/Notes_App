"""
Logging configuration and utilities for the Notes App.

This module provides structured logging configuration using structlog
for consistent, searchable, and well-formatted log messages.
"""

import logging
import sys
from typing import Any, Dict, Optional

import structlog
from structlog.types import Processor

from .config import settings


def configure_logging() -> None:
    """
    Configure structured logging for the application.

    Sets up structlog with appropriate processors and formatters
    based on the application configuration.
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level),
    )

    # Configure structlog processors
    processors: list[Processor] = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    # Add JSON formatter for production
    if settings.log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


class LogContext:
    """
    Context manager for adding structured context to log messages.

    This allows for consistent logging context across the application
    by providing a way to add common fields to all log messages.
    """

    def __init__(self, logger: structlog.BoundLogger, **context: Any) -> None:
        """
        Initialize log context.

        Args:
            logger: Logger instance
            **context: Context fields to add to all log messages
        """
        self.logger = logger
        self.context = context

    def __enter__(self) -> structlog.BoundLogger:
        """Enter context and return bound logger."""
        return self.logger.bind(**self.context)

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context."""
        pass


def log_function_call(
    logger: structlog.BoundLogger, function_name: str, **kwargs: Any
) -> LogContext:
    """
    Create a log context for function calls.

    Args:
        logger: Logger instance
        function_name: Name of the function being called
        **kwargs: Additional context fields

    Returns:
        Log context manager
    """
    context = {"function": function_name, **kwargs}
    return LogContext(logger, **context)


def log_api_request(
    logger: structlog.BoundLogger,
    method: str,
    path: str,
    user_id: Optional[str] = None,
    **kwargs: Any,
) -> LogContext:
    """
    Create a log context for API requests.

    Args:
        logger: Logger instance
        method: HTTP method
        path: Request path
        user_id: Optional user ID
        **kwargs: Additional context fields

    Returns:
        Log context manager
    """
    context = {"type": "api_request", "method": method, "path": path, **kwargs}

    if user_id:
        context["user_id"] = user_id

    return LogContext(logger, **context)


def log_database_operation(
    logger: structlog.BoundLogger, operation: str, table: str, **kwargs: Any
) -> LogContext:
    """
    Create a log context for database operations.

    Args:
        logger: Logger instance
        operation: Database operation (SELECT, INSERT, UPDATE, DELETE)
        table: Database table name
        **kwargs: Additional context fields

    Returns:
        Log context manager
    """
    context = {
        "type": "database_operation",
        "operation": operation,
        "table": table,
        **kwargs,
    }
    return LogContext(logger, **context)


def log_error(
    logger: structlog.BoundLogger,
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Log an error with structured context.

    Args:
        logger: Logger instance
        error: Exception to log
        context: Optional additional context
    """
    error_context = {
        "error_type": type(error).__name__,
        "error_message": str(error),
    }

    if hasattr(error, "error_code"):
        error_context["error_code"] = error.error_code

    if hasattr(error, "details"):
        error_context["error_details"] = error.details

    if context:
        error_context.update(context)

    logger.error("An error occurred", **error_context)
