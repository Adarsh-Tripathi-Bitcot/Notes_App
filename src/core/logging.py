"""
Professional Structured Logging System

A comprehensive, production-ready structured logging system with:
- Environment-dependent configuration
- Advanced correlation tracking
- Performance monitoring
- Security event logging
- Database operation tracking
- Log sampling and filtering
- Professional error handling
"""

import inspect
import logging
import random
import sys
import time
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

# Context variables for comprehensive request tracking
correlation_id: ContextVar[str] = ContextVar("correlation_id", default=None)
user_id: ContextVar[str] = ContextVar("user_id", default=None)
user_email: ContextVar[str] = ContextVar("user_email", default=None)
user_username: ContextVar[str] = ContextVar("user_username", default=None)
user_full_name: ContextVar[str] = ContextVar("user_full_name", default=None)
user_display_name: ContextVar[str] = ContextVar("user_display_name", default=None)
request_path: ContextVar[str] = ContextVar("request_path", default=None)
request_method: ContextVar[str] = ContextVar("request_method", default=None)
request_id: ContextVar[str] = ContextVar("request_id", default=None)
session_id: ContextVar[str] = ContextVar("session_id", default=None)

# Performance tracking context
operation_start_time: ContextVar[float] = ContextVar(
    "operation_start_time", default=None
)
operation_name: ContextVar[str] = ContextVar("operation_name", default=None)

# Global variables
_PROJECT_ROOT = None
_LOGGING_CONFIGURED = False
_LOGGERS = {}


def get_project_root() -> Path:
    """Detect project root by looking for common indicators."""
    global _PROJECT_ROOT
    if _PROJECT_ROOT is not None:
        return _PROJECT_ROOT

    current_path = Path(__file__).resolve()
    indicators = [".git", "setup.py", "pyproject.toml", "requirements.txt"]

    for parent in [current_path] + list(current_path.parents):
        if any((parent / indicator).exists() for indicator in indicators):
            _PROJECT_ROOT = parent
            return _PROJECT_ROOT

    _PROJECT_ROOT = current_path.parent
    return _PROJECT_ROOT


def get_relative_path(file_path: str) -> str:
    """Convert absolute file path to relative path from project root."""
    try:
        abs_path = Path(file_path).resolve()
        project_root = get_project_root()
        return str(abs_path.relative_to(project_root))
    except (ValueError, OSError):
        return Path(file_path).name


def add_caller_info_processor(logger, method_name, event_dict):
    """Add file and line number information to log entries."""
    if not getattr(settings, "enable_file_line_info", True):
        return event_dict

    try:
        stack = inspect.stack()
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
                "src/core/middleware.py",
            ]
            if any(pattern in filename for pattern in skip_patterns):
                continue
            if func_name in ["add_caller_info_processor", "log_function_call"]:
                continue

            # Found user code
            event_dict["filename"] = get_relative_path(filename)
            event_dict["lineno"] = frame_info.lineno
            event_dict["function"] = func_name
            break
    except Exception:
        pass

    return event_dict


def add_context_processor(_, __, event_dict):
    """Add comprehensive context variables to log entries."""
    # Always add correlation ID
    event_dict["correlation_id"] = correlation_id.get() or "N/A"
    event_dict["request_id"] = request_id.get() or "N/A"
    event_dict["session_id"] = session_id.get() or "N/A"

    # Add user context if enabled
    if getattr(settings, "enable_user_context", True):
        event_dict["user_id"] = user_id.get() or "anonymous"

        # Add user details based on configuration
        if getattr(settings, "show_user_email", True):
            event_dict["user_email"] = user_email.get() or "N/A"
        if getattr(settings, "show_user_username", True):
            event_dict["user_username"] = user_username.get() or "N/A"
        if getattr(settings, "show_user_full_name", True):
            event_dict["user_full_name"] = user_full_name.get() or "N/A"
        if getattr(settings, "show_user_display_name", True):
            event_dict["user_display_name"] = user_display_name.get() or "N/A"
    else:
        event_dict["user_id"] = "disabled"

    # Add request context if enabled
    if getattr(settings, "enable_request_context", True):
        event_dict["request_path"] = request_path.get() or "N/A"
        event_dict["request_method"] = request_method.get() or "N/A"
    else:
        event_dict["request_path"] = "disabled"
        event_dict["request_method"] = "disabled"

    # Add performance context if enabled (guard missing attribute)
    if getattr(settings, "enable_performance_logging", False):
        start_time = operation_start_time.get()
        if start_time:
            event_dict["operation_duration_ms"] = round(
                (time.time() - start_time) * 1000, 2
            )
        event_dict["operation_name"] = operation_name.get() or "N/A"

    return event_dict


def add_security_processor(_, __, event_dict):
    """Add security-related context to log entries."""
    if not getattr(settings, "enable_security_logging", False):
        return event_dict

    # Add security context
    event_dict["security_event"] = event_dict.get("security_event", False)
    event_dict["risk_level"] = event_dict.get("risk_level", "LOW")
    event_dict["event_type"] = event_dict.get("event_type", "GENERAL")

    return event_dict


def add_performance_processor(_, __, event_dict):
    """Add performance metrics to log entries."""
    if not getattr(settings, "enable_performance_logging", False):
        return event_dict

    # Add performance metrics
    event_dict["memory_usage_mb"] = event_dict.get("memory_usage_mb", 0)
    event_dict["cpu_usage_percent"] = event_dict.get("cpu_usage_percent", 0)

    return event_dict


def log_sampling_processor(_, __, event_dict):
    """Apply log sampling for high-volume operations."""
    if not getattr(settings, "enable_log_sampling", False):
        return event_dict

    # Check if this log should be sampled
    sampling_rate = getattr(settings, "log_sampling_rate", 0.1)
    if random.random() > sampling_rate:
        event_dict["sampled"] = True
    else:
        event_dict["sampled"] = False

    return event_dict


def setup_logging(log_level: str = None, environment: str = None) -> None:
    """Configure professional structured logging system."""
    global _LOGGING_CONFIGURED

    if _LOGGING_CONFIGURED:
        return

    # Use settings if not provided
    log_level = log_level or getattr(settings, "log_level", "INFO")
    environment = environment or getattr(settings, "environment", "development")

    # Convert string log level to numeric constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Determine output format based on environment and settings
    is_production = environment.lower() in ["production", "prod"]
    log_format = getattr(settings, "log_format", "text")
    use_json = is_production or log_format.lower() == "json"

    # Configure structlog processors in the correct order
    processors = [
        # 1. Context Variables: Merge context variables
        structlog.contextvars.merge_contextvars,
        # 2. Custom Context: Add our custom context
        add_context_processor,
        # 3. Caller Info: Add file/line numbers
        add_caller_info_processor,
        # 4. Security: Add security context
        add_security_processor,
        # 5. Performance: Add performance metrics
        add_performance_processor,
        # 6. Log Sampling: Apply sampling for high-volume operations
        log_sampling_processor,
        # 7. Log Level: Add log level
        structlog.processors.add_log_level,
        # 8. Timestamp: Add timestamp
        structlog.processors.TimeStamper(fmt="iso"),
        # 9. Stack Info: Render stack traces
        structlog.processors.StackInfoRenderer(),
        # 10. Exception Info: Set exception info
        structlog.dev.set_exc_info,
    ]

    # 11. Renderer: Environment-specific output format
    if use_json:
        # Production: JSON output for machine parsing
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Development: Human-readable output with colors
        # Force colors in development unless explicitly disabled
        enable_colors = True
        if hasattr(settings, "enable_colored_logs"):
            enable_colors = settings.enable_colored_logs

        processors.append(
            structlog.dev.ConsoleRenderer(
                colors=enable_colors, pad_event=30, sort_keys=True
            )
        )

    # Configure structlog with proper filtering
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(numeric_level),
        logger_factory=structlog.PrintLoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )

    # Configure standard Python logging
    _configure_standard_logging(numeric_level, is_production)

    # Apply module-specific log levels
    _apply_module_log_levels()

    _LOGGING_CONFIGURED = True

    # Logging configured silently


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

    # Suppress noisy third-party logs
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.dialects").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.orm").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("passlib").setLevel(logging.WARNING)


def _apply_module_log_levels() -> None:
    """Apply module-specific log levels."""
    module_log_levels = getattr(settings, "module_log_levels", {})
    for module, level in module_log_levels.items():
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        logging.getLogger(module).setLevel(numeric_level)


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance with caching."""
    if name not in _LOGGERS:
        _LOGGERS[name] = structlog.get_logger(name)
    return _LOGGERS[name]


def get_standard_logger(name: str) -> logging.Logger:
    """Get a standard Python logger (for compatibility)."""
    return logging.getLogger(name)


def add_correlation_context(**kwargs) -> None:
    """Add correlation context to current execution context."""
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
    if "request_id" in kwargs:
        request_id.set(kwargs["request_id"])
    if "session_id" in kwargs:
        session_id.set(kwargs["session_id"])


def generate_correlation_id() -> str:
    """Generate a unique correlation ID."""
    return str(uuid.uuid4())


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())


def generate_session_id() -> str:
    """Generate a unique session ID."""
    return str(uuid.uuid4())


class RequestLoggingContext:
    """Context manager for request-scoped logging context."""

    def __init__(self, **context_vars):
        """Initialize context manager."""
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
            elif key == "request_id":
                self.tokens[key] = request_id.set(value)
            elif key == "session_id":
                self.tokens[key] = session_id.set(value)
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
            elif key == "request_id":
                request_id.reset(token)
            elif key == "session_id":
                session_id.reset(token)


class PerformanceLoggingContext:
    """Context manager for performance logging."""

    def __init__(self, operation_name: str, logger: structlog.BoundLogger):
        """Initialize performance logging context."""
        self.operation_name = operation_name
        self.logger = logger
        self.start_time = None

    def __enter__(self):
        """Start performance tracking."""
        self.start_time = time.time()
        operation_start_time.set(self.start_time)
        operation_name.set(self.operation_name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Log performance metrics."""
        if self.start_time:
            duration = time.time() - self.start_time
            self.logger.info(
                "Operation completed",
                operation=self.operation_name,
                duration_ms=round(duration * 1000, 2),
                success=exc_type is None,
            )
        operation_start_time.set(None)
        operation_name.set(None)


class SecurityLoggingContext:
    """Context manager for security event logging."""

    def __init__(
        self,
        event_type: str,
        risk_level: str = "MEDIUM",
        logger: structlog.BoundLogger = None,
    ):
        """Initialize security logging context."""
        self.event_type = event_type
        self.risk_level = risk_level
        self.logger = logger or get_logger(__name__)

    def __enter__(self):
        """Set security context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Log security event."""
        self.logger.warning(
            "Security event",
            security_event=True,
            event_type=self.event_type,
            risk_level=self.risk_level,
            success=exc_type is None,
            error=str(exc_val) if exc_val else None,
        )


# Compatibility functions to maintain existing API
def configure_logging() -> None:
    """Configure logging using settings from config."""
    setup_logging(
        log_level=getattr(settings, "log_level", "INFO"),
        environment=getattr(settings, "environment", "development"),
    )


def set_log_level(level: str, module: Optional[str] = None) -> None:
    """Set log level for a specific module or globally."""
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
    """Get current log level for a specific module or root logger."""
    if module:
        logger = logging.getLogger(module)
    else:
        logger = logging.getLogger()

    return logging.getLevelName(logger.level)


def clear_logging_context() -> None:
    """Clear all logging context variables."""
    user_id.set(None)
    user_email.set(None)
    user_username.set(None)
    user_full_name.set(None)
    user_display_name.set(None)
    request_path.set(None)
    request_method.set(None)
    request_id.set(None)
    session_id.set(None)
    correlation_id.set(None)
    operation_start_time.set(None)
    operation_name.set(None)


def set_logging_context(**kwargs) -> None:
    """Set logging context variables from keyword arguments."""
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
    if "request_id" in kwargs:
        request_id.set(kwargs["request_id"])
    if "session_id" in kwargs:
        session_id.set(kwargs["session_id"])
    if "correlation_id" in kwargs:
        correlation_id.set(kwargs["correlation_id"])
    if "operation_start_time" in kwargs:
        operation_start_time.set(kwargs["operation_start_time"])
    if "operation_name" in kwargs:
        operation_name.set(kwargs["operation_name"])


def get_correlation_id() -> Optional[str]:
    """Get the current correlation ID."""
    return correlation_id.get()


def get_user_id() -> Optional[str]:
    """Get the current user ID."""
    return user_id.get()


def list_configured_modules() -> dict:
    """List all configured modules and their log levels."""
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


# Enhanced logging utilities
def log_api_request(logger, method: str, path: str, **kwargs):
    """Create a log context for API requests."""
    context = {
        "type": "api_request",
        "method": method,
        "path": path,
        "timestamp": time.time(),
        **kwargs,
    }
    return RequestLoggingContext(**context)


def log_function_call(logger, function_name: str, **kwargs):
    """Create a log context for function calls."""
    context = {"function": function_name, "timestamp": time.time(), **kwargs}
    return RequestLoggingContext(**context)


def log_database_operation(logger, operation: str, table: str, **kwargs):
    """Create a log context for database operations."""
    context = {
        "type": "database_operation",
        "operation": operation,
        "table": table,
        "timestamp": time.time(),
        **kwargs,
    }
    return RequestLoggingContext(**context)


def log_performance(operation_name: str, logger: structlog.BoundLogger = None):
    """Create a performance logging context."""
    if not logger:
        logger = get_logger(__name__)
    return PerformanceLoggingContext(operation_name, logger)


def log_security_event(
    event_type: str, risk_level: str = "MEDIUM", logger: structlog.BoundLogger = None
):
    """Create a security event logging context."""
    if not logger:
        logger = get_logger(__name__)
    return SecurityLoggingContext(event_type, risk_level, logger)


# Legacy compatibility
class LogContext:
    """Legacy context manager for backward compatibility."""

    def __init__(self, logger, **context):
        self.logger = logger
        self.context = context

    def __enter__(self):
        return self.logger.bind(**self.context)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
