"""
Structured Logging Implementation Guide

A comprehensive structured logging system with environment-aware configuration,
correlation tracking, and context management following mentor's specifications.

This module provides structured logging configuration using structlog
for consistent, searchable, and well-formatted log messages with
enhanced metadata including file/line numbers, correlation IDs, and User IDs.
"""

import inspect
import logging
import sys
import uuid
from contextvars import ContextVar
from pathlib import Path
from typing import Optional

import structlog
from colorama import Fore, Style
from colorama import init as colorama_init

from .config import settings

# Initialize colorama for cross-platform color support
colorama_init()

# Context variables for request tracking
correlation_id: ContextVar[str] = ContextVar("correlation_id", default=None)
user_id: ContextVar[str] = ContextVar("user_id", default=None)
user_email: ContextVar[str] = ContextVar("user_email", default=None)
user_username: ContextVar[str] = ContextVar("user_username", default=None)
user_full_name: ContextVar[str] = ContextVar("user_full_name", default=None)
user_display_name: ContextVar[str] = ContextVar("user_display_name", default=None)
request_path: ContextVar[str] = ContextVar("request_path", default=None)
request_method: ContextVar[str] = ContextVar("request_method", default=None)

# Global variable to cache project root
_PROJECT_ROOT = None


def get_project_root() -> Path:
    """
    Detect project root by looking for common indicators.

    Returns:
        Path: Project root directory
    """
    global _PROJECT_ROOT
    if _PROJECT_ROOT is not None:
        return _PROJECT_ROOT

    current_path = Path(__file__).resolve()

    # Look for common project root indicators
    indicators = [".git", "setup.py", "pyproject.toml", "requirements.txt"]

    for parent in [current_path] + list(current_path.parents):
        if any((parent / indicator).exists() for indicator in indicators):
            _PROJECT_ROOT = parent
            return _PROJECT_ROOT

    # Fallback to current file's parent directory
    _PROJECT_ROOT = current_path.parent
    return _PROJECT_ROOT


def get_relative_path(file_path: str) -> str:
    """
    Convert absolute file path to relative path from project root.

    Args:
        file_path: Absolute file path

    Returns:
        str: Relative path from project root
    """
    try:
        abs_path = Path(file_path).resolve()
        project_root = get_project_root()
        return str(abs_path.relative_to(project_root))
    except (ValueError, OSError):
        # Fallback to filename only if relative path calculation fails
        return Path(file_path).name


def add_caller_info_processor(logger, method_name, event_dict):
    """
    Add file and line number information to log entries.

    This processor inspects the call stack to find the original caller
    outside of logging framework internals.
    """
    try:
        stack = inspect.stack()
        # Find first frame that's not in logging internals
        for frame_info in stack:
            filename = frame_info.filename
            func_name = frame_info.function

            # Skip internal frames
            skip_patterns = [
                "structlog",
                "logging",
                "site-packages",
                "/venv/",
                "src/core/logging.py",
            ]
            if any(pattern in filename for pattern in skip_patterns):
                continue
            if func_name == "add_caller_info_processor":
                continue

            # Found user code
            event_dict["filename"] = get_relative_path(filename)
            event_dict["lineno"] = frame_info.lineno
            break
    except Exception:
        # Don't add caller info if there's any error
        pass

    return event_dict


def add_context_processor(_, __, event_dict):
    """
    Add context variables to log entries.

    This processor adds correlation ID, user information, and request information
    to every log entry automatically based on configuration settings.
    """
    # Always add correlation ID
    event_dict["correlation_id"] = correlation_id.get() or "N/A"

    # Add user context if enabled
    if settings.enable_user_context:
        event_dict["user_id"] = user_id.get() or "anonymous"

        # Add user details based on configuration
        if settings.show_user_email:
            event_dict["user_email"] = user_email.get() or "N/A"
        if settings.show_user_username:
            event_dict["user_username"] = user_username.get() or "N/A"
        if settings.show_user_full_name:
            event_dict["user_full_name"] = user_full_name.get() or "N/A"
        if settings.show_user_display_name:
            event_dict["user_display_name"] = user_display_name.get() or "N/A"
    else:
        event_dict["user_id"] = "disabled"

    # Add request context if enabled
    if settings.enable_request_context:
        event_dict["request_path"] = request_path.get() or "N/A"
        event_dict["request_method"] = request_method.get() or "N/A"
    else:
        event_dict["request_path"] = "disabled"
        event_dict["request_method"] = "disabled"

    return event_dict


def setup_logging(log_level: str = "INFO", environment: str = "development") -> None:
    """
    Configure structured logging based on environment.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        environment: Environment type (development, production, testing)
    """
    # Convert string log level to numeric constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Determine output format based on environment
    is_production = environment.lower() in ["production", "prod", "testing", "test"]

    # Configure structlog processors
    processors = [
        structlog.contextvars.merge_contextvars,  # Merge context variables
        add_context_processor,  # Add our custom context
        add_caller_info_processor,  # Add file/line info
        structlog.processors.add_log_level,  # Add log level
        structlog.processors.StackInfoRenderer(),  # Render stack traces
        structlog.dev.set_exc_info,  # Set exception info
    ]

    # Add environment-specific renderer
    if is_production:
        # Production: JSON output for machine parsing
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Development: Human-readable output with colors
        processors.append(
            structlog.dev.ConsoleRenderer(colors=True, pad_event=25, sort_keys=True)
        )

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(numeric_level),
        logger_factory=structlog.WriteLoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )

    # Configure standard Python logging
    _configure_standard_logging(numeric_level, is_production)

    # Log successful configuration
    logger = get_logger(__name__)
    logger.info(
        "Logging configured successfully",
        environment=environment,
        log_level=log_level,
        json_output=is_production,
    )


def _configure_standard_logging(numeric_level: int, is_production: bool) -> None:
    """Configure standard Python logging to work with structlog."""
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)

    # Set formatter based on environment
    if is_production:
        # JSON formatter for production
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"logger": "%(name)s", "message": "%(message)s"}'
        )
    else:
        # Colored formatter for development
        formatter = logging.Formatter(
            f"{Fore.BLUE}%(asctime)s{Style.RESET_ALL} | "
            f"{Fore.GREEN}%(levelname)-8s{Style.RESET_ALL} | "
            f"{Fore.CYAN}%(name)s{Style.RESET_ALL} - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)

    # Suppress SQLAlchemy logs completely
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.dialects").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.orm").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        structlog.BoundLogger: Configured structured logger
    """
    return structlog.get_logger(name)


def get_standard_logger(name: str) -> logging.Logger:
    """
    Get a standard Python logger (for compatibility).

    Args:
        name: Logger name (typically __name__)

    Returns:
        logging.Logger: Standard Python logger
    """
    return logging.getLogger(name)


def add_correlation_context(**kwargs) -> None:
    """
    Add correlation context to current execution context.

    Args:
        **kwargs: Context variables (correlation_id, user_id, user_email, etc.)
    """
    if "correlation_id" in kwargs:
        correlation_id.set(kwargs["correlation_id"])
    if "user_id" in kwargs:
        user_id.set(kwargs["user_id"])
    if "user_email" in kwargs:
        user_email.set(kwargs["user_email"])
    if "user_username" in kwargs:
        user_username.set(kwargs["user_username"])
    if "user_full_name" in kwargs:
        user_full_name.set(kwargs["user_full_name"])
    if "user_display_name" in kwargs:
        user_display_name.set(kwargs["user_display_name"])
    if "request_path" in kwargs:
        request_path.set(kwargs["request_path"])
    if "request_method" in kwargs:
        request_method.set(kwargs["request_method"])


def generate_correlation_id() -> str:
    """
    Generate a unique correlation ID.

    Returns:
        str: UUID-based correlation ID
    """
    return str(uuid.uuid4())


class RequestLoggingContext:
    """
    Context manager for request-scoped logging context.

    Usage:
        with RequestLoggingContext(correlation_id="abc-123", user_id="user1"):
            logger.info("Processing request")
    """

    def __init__(self, **context_vars):
        """
        Initialize context manager.

        Args:
            **context_vars: Context variables to set
        """
        self.context_vars = context_vars
        self.tokens = {}

    def __enter__(self):
        """Set context variables and store reset tokens."""
        for key, value in self.context_vars.items():
            if key == "correlation_id":
                self.tokens[key] = correlation_id.set(value)
            elif key == "user_id":
                self.tokens[key] = user_id.set(value)
            elif key == "user_email":
                self.tokens[key] = user_email.set(value)
            elif key == "user_username":
                self.tokens[key] = user_username.set(value)
            elif key == "user_full_name":
                self.tokens[key] = user_full_name.set(value)
            elif key == "user_display_name":
                self.tokens[key] = user_display_name.set(value)
            elif key == "request_path":
                self.tokens[key] = request_path.set(value)
            elif key == "request_method":
                self.tokens[key] = request_method.set(value)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Reset context variables to previous values."""
        for key, token in self.tokens.items():
            if key == "correlation_id":
                correlation_id.reset(token)
            elif key == "user_id":
                user_id.reset(token)
            elif key == "user_email":
                user_email.reset(token)
            elif key == "user_username":
                user_username.reset(token)
            elif key == "user_full_name":
                user_full_name.reset(token)
            elif key == "user_display_name":
                user_display_name.reset(token)
            elif key == "request_path":
                request_path.reset(token)
            elif key == "request_method":
                request_method.reset(token)


# Compatibility functions to maintain existing API
def configure_logging() -> None:
    """
    Configure logging using settings from config.

    This is a compatibility wrapper around setup_logging.
    """
    setup_logging(log_level=settings.log_level, environment=settings.environment)


def set_log_level(level: str, module: Optional[str] = None) -> None:
    """
    Set log level for a specific module or globally.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        module: Optional module name. If None, sets root logger level.
    """
    level = level.upper()
    if level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        raise ValueError(f"Invalid log level: {level}")

    numeric_level = getattr(logging, level)

    if module:
        logging.getLogger(module).setLevel(numeric_level)
    else:
        # Set root logger level
        logging.getLogger().setLevel(numeric_level)

        # Also update structlog configuration
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(numeric_level),
            cache_logger_on_first_use=True,
        )


def get_current_log_level(module: Optional[str] = None) -> str:
    """
    Get current log level for a specific module or root logger.

    Args:
        module: Optional module name. If None, returns root logger level.

    Returns:
        Current log level as string.
    """
    if module:
        logger = logging.getLogger(module)
    else:
        logger = logging.getLogger()

    return logging.getLevelName(logger.level)


def generate_request_id() -> str:
    """Generate a unique request ID for tracing."""
    return str(uuid.uuid4())


def set_logging_context(
    user_id_val: Optional[str] = None,
    request_id_val: Optional[str] = None,
    xray_id_val: Optional[str] = None,
    correlation_id_val: Optional[str] = None,
) -> None:
    """
    Set global logging context for tracing.

    Args:
        user_id_val: User ID for request tracing
        request_id_val: Request ID for tracing (mapped to request_path)
        xray_id_val: X-Ray ID for AWS tracing (mapped to request_method)
        correlation_id_val: Correlation ID for request tracking
    """
    if user_id_val:
        user_id.set(user_id_val)
    if request_id_val:
        request_path.set(request_id_val)  # Map to request_path for compatibility
    if xray_id_val:
        request_method.set(xray_id_val)  # Map to request_method for compatibility
    if correlation_id_val:
        correlation_id.set(correlation_id_val)


def clear_logging_context() -> None:
    """Clear all logging context variables."""
    user_id.set(None)
    user_email.set(None)
    user_username.set(None)
    user_full_name.set(None)
    user_display_name.set(None)
    request_path.set(None)
    request_method.set(None)
    correlation_id.set(None)


def get_correlation_id() -> Optional[str]:
    """Get the current correlation ID."""
    return correlation_id.get()


def get_user_id() -> Optional[str]:
    """Get the current user ID."""
    return user_id.get()


def list_configured_modules() -> dict:
    """
    List all configured modules and their log levels.

    Returns:
        Dictionary mapping module names to their log levels.
    """
    modules = {}

    # Get all loggers
    for name in logging.Logger.manager.loggerDict:
        logger = logging.getLogger(name)
        if logger.level != logging.NOTSET:
            modules[name] = logging.getLevelName(logger.level)

    # Add root logger
    root_logger = logging.getLogger()
    if root_logger.level != logging.NOTSET:
        modules["root"] = logging.getLevelName(root_logger.level)

    return modules


def reset_log_levels() -> None:
    """Reset all log levels to their default configuration."""
    configure_logging()


# Compatibility functions for existing codebase
class LogContext:
    """
    Context manager for adding structured context to log messages.
    This is a compatibility wrapper around RequestLoggingContext.
    """

    def __init__(self, logger, **context):
        self.logger = logger
        self.context = context

    def __enter__(self):
        return self.logger.bind(**self.context)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def log_api_request(logger, method: str, path: str, **kwargs):
    """
    Create a log context for API requests.
    Compatibility function for existing code.
    """
    context = {"type": "api_request", "method": method, "path": path, **kwargs}
    return LogContext(logger, **context)


def log_function_call(logger, function_name: str, **kwargs):
    """
    Create a log context for function calls.
    Compatibility function for existing code.
    """
    context = {"function": function_name, **kwargs}
    return LogContext(logger, **context)


def log_database_operation(logger, operation: str, table: str, **kwargs):
    """
    Create a log context for database operations.
    Compatibility function for existing code.
    """
    context = {
        "type": "database_operation",
        "operation": operation,
        "table": table,
        **kwargs,
    }
    return LogContext(logger, **context)
