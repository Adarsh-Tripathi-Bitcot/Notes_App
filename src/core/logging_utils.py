"""
Enhanced Logging Utilities

Professional logging utilities for different components:
- Service layer logging
- Repository layer logging
- API layer logging
- Database operation logging
- Performance monitoring
- Security event logging
"""


from .logging import get_logger


class ServiceLogger:
    """Professional logger for service layer operations."""

    def __init__(self, service_name: str):
        """Initialize service logger."""
        self.service_name = service_name
        self.logger = get_logger(f"services.{service_name}")

    def log_operation(self, operation: str, **kwargs):
        """Log service operation start."""
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
            error=str(error),
            error_type=error.__class__.__name__,
            status="error",
            **kwargs,
        )

    def log_warning(self, operation: str, message: str, **kwargs):
        """Log service operation warning."""
        self.logger.warning(
            "Service operation warning",
            service=self.service_name,
            operation=operation,
            message=message,
            **kwargs,
        )


class RepositoryLogger:
    """Professional logger for repository layer operations."""

    def __init__(self, repository_name: str):
        """Initialize repository logger."""
        self.repository_name = repository_name
        self.logger = get_logger(f"repositories.{repository_name}")

    def log_query(self, operation: str, table: str, **kwargs):
        """Log database query."""
        self.logger.debug(
            f"Database query: {operation}",
            repository=self.repository_name,
            operation=operation,
            table=table,
            **kwargs,
        )

    def log_success(self, operation: str, **kwargs):
        """Log successful database operation."""
        self.logger.debug(
            f"Repository operation completed: {operation}",
            repository=self.repository_name,
            operation=operation,
            status="success",
            **kwargs,
        )

    def log_error(self, operation: str, error: Exception, **kwargs):
        """Log database operation error."""
        self.logger.error(
            f"Repository operation failed: {operation}",
            repository=self.repository_name,
            operation=operation,
            error=str(error),
            error_type=error.__class__.__name__,
            status="error",
            **kwargs,
        )

    def log_slow_query(self, operation: str, duration_ms: float, **kwargs):
        """Log slow database query."""
        self.logger.warning(
            "Slow database query detected",
            repository=self.repository_name,
            operation=operation,
            duration_ms=duration_ms,
            **kwargs,
        )


class APILogger:
    """Professional logger for API layer operations."""

    def __init__(self, api_name: str):
        """Initialize API logger."""
        self.api_name = api_name
        self.router_name = api_name  # For backward compatibility with tests
        self.logger = get_logger(f"api.{api_name}")

    def log_request(self, method: str, path: str, **kwargs):
        """Log API request."""
        self.logger.info(
            f"API request: {method} {path}",
            api=self.api_name,
            router=self.router_name,
            method=method,
            path=path,
            **kwargs,
        )

    def log_response(self, method: str, path: str, status_code: int, **kwargs):
        """Log API response."""
        self.logger.info(
            f"API response: {method} {path} - {status_code}",
            api=self.api_name,
            router=self.router_name,
            method=method,
            path=path,
            status_code=status_code,
            **kwargs,
        )

    def log_error(self, method: str, path: str, error: Exception, **kwargs):
        """Log API error."""
        self.logger.error(
            f"API error: {method} {path}",
            api=self.api_name,
            router=self.router_name,
            method=method,
            path=path,
            error=str(error),
            error_type=error.__class__.__name__,
            **kwargs,
        )

    def log_validation_error(
        self, method: str, path: str, validation_errors: list, **kwargs
    ):
        """Log API validation error."""
        self.logger.warning(
            "API validation error",
            api=self.api_name,
            method=method,
            path=path,
            validation_errors=validation_errors,
            **kwargs,
        )


class PerformanceLogger:
    """Professional logger for performance monitoring."""

    def __init__(self, component_name: str):
        """Initialize performance logger."""
        self.component_name = component_name
        self.logger = get_logger(f"performance.{component_name}")

    def log_operation_time(self, operation: str, duration_ms: float, **kwargs):
        """Log operation execution time."""
        self.logger.info(
            "Operation performance",
            component=self.component_name,
            operation=operation,
            duration_ms=duration_ms,
            **kwargs,
        )

    def log_slow_operation(
        self, operation: str, duration_ms: float, threshold_ms: float, **kwargs
    ):
        """Log slow operation."""
        self.logger.warning(
            "Slow operation detected",
            component=self.component_name,
            operation=operation,
            duration_ms=duration_ms,
            threshold_ms=threshold_ms,
            **kwargs,
        )

    def log_memory_usage(self, operation: str, memory_mb: float, **kwargs):
        """Log memory usage."""
        self.logger.info(
            "Memory usage",
            component=self.component_name,
            operation=operation,
            memory_mb=memory_mb,
            **kwargs,
        )


class SecurityLogger:
    """Professional logger for security events."""

    def __init__(self, component_name: str):
        """Initialize security logger."""
        self.component_name = component_name
        self.logger = get_logger(f"security.{component_name}")

    def log_authentication_attempt(self, user_id: str, success: bool, **kwargs):
        """Log authentication attempt."""
        level = "info" if success else "warning"
        getattr(self.logger, level)(
            "Authentication attempt",
            component=self.component_name,
            user_id=user_id,
            success=success,
            **kwargs,
        )

    def log_authorization_failure(self, user_id: str, resource: str, **kwargs):
        """Log authorization failure."""
        self.logger.warning(
            "Authorization failure",
            component=self.component_name,
            user_id=user_id,
            resource=resource,
            **kwargs,
        )

    def log_security_event(self, event_type: str, risk_level: str, **kwargs):
        """Log security event."""
        self.logger.warning(
            "Security event",
            component=self.component_name,
            event_type=event_type,
            risk_level=risk_level,
            **kwargs,
        )

    def log_suspicious_activity(self, activity_type: str, **kwargs):
        """Log suspicious activity."""
        self.logger.error(
            "Suspicious activity detected",
            component=self.component_name,
            activity_type=activity_type,
            **kwargs,
        )


class DatabaseLogger:
    """Professional logger for database operations."""

    def __init__(self, database_name: str = "main"):
        """Initialize database logger."""
        self.database_name = database_name
        self.logger = get_logger(f"database.{database_name}")

    def log_connection(self, **kwargs):
        """Log database connection."""
        self.logger.info(
            "Database connection established", database=self.database_name, **kwargs
        )

    def log_disconnection(self, **kwargs):
        """Log database disconnection."""
        self.logger.info(
            "Database connection closed", database=self.database_name, **kwargs
        )

    def log_transaction_start(self, **kwargs):
        """Log transaction start."""
        self.logger.debug(
            "Database transaction started", database=self.database_name, **kwargs
        )

    def log_transaction_commit(self, **kwargs):
        """Log transaction commit."""
        self.logger.debug(
            "Database transaction committed", database=self.database_name, **kwargs
        )

    def log_transaction_rollback(self, **kwargs):
        """Log transaction rollback."""
        self.logger.warning(
            "Database transaction rolled back", database=self.database_name, **kwargs
        )

    def log_query_execution(self, query: str, duration_ms: float, **kwargs):
        """Log query execution."""
        self.logger.debug(
            "Database query executed",
            database=self.database_name,
            query=query[:100] + "..." if len(query) > 100 else query,
            duration_ms=duration_ms,
            **kwargs,
        )


class ApplicationLogger:
    """Professional logger for application lifecycle events."""

    def __init__(self):
        """Initialize application logger."""
        self.logger = get_logger("application")

    def log_startup(self, **kwargs):
        """Log application startup."""
        self.logger.info("Application started", **kwargs)

    def log_shutdown(self, **kwargs):
        """Log application shutdown."""
        self.logger.info("Application shutting down", **kwargs)

    def log_health_check(self, status: str, **kwargs):
        """Log health check."""
        self.logger.info("Health check", status=status, **kwargs)

    def log_configuration_loaded(self, **kwargs):
        """Log configuration loaded."""
        self.logger.info("Configuration loaded", **kwargs)

    def log_error(self, error: Exception, **kwargs):
        """Log application error."""
        self.logger.error(
            "Application error",
            error=str(error),
            error_type=error.__class__.__name__,
            **kwargs,
        )


# Convenience functions
def get_service_logger(service_name: str) -> ServiceLogger:
    """Get a service logger instance."""
    return ServiceLogger(service_name)


def get_repository_logger(repository_name: str) -> RepositoryLogger:
    """Get a repository logger instance."""
    return RepositoryLogger(repository_name)


def get_api_logger(api_name: str) -> APILogger:
    """Get an API logger instance."""
    return APILogger(api_name)


def get_performance_logger(component_name: str) -> PerformanceLogger:
    """Get a performance logger instance."""
    return PerformanceLogger(component_name)


def get_security_logger(component_name: str) -> SecurityLogger:
    """Get a security logger instance."""
    return SecurityLogger(component_name)


def get_database_logger(database_name: str = "main") -> DatabaseLogger:
    """Get a database logger instance."""
    return DatabaseLogger(database_name)


def get_application_logger() -> ApplicationLogger:
    """Get an application logger instance."""
    return ApplicationLogger()


def log_cache_operation(operation: str, key: str = None, **kwargs):
    """Log cache operations."""
    logger = get_logger(__name__)
    logger.debug(
        f"Cache operation: {operation}", operation=operation, key=key, **kwargs
    )


def log_database_session(operation: str, **kwargs):
    """Log database session operations."""
    logger = get_logger(__name__)
    logger.debug(f"Database session: {operation}", operation=operation, **kwargs)


def log_note_operation(operation: str, note_id: str = None, **kwargs):
    """Log note-related operations."""
    logger = get_logger(__name__)

    # Get user_id from context
    user_id = get_user_id()

    logger.info(
        f"Note operation: {operation}",
        operation=operation,
        note_id=note_id,
        user_id=user_id,
        **kwargs,
    )


def log_user_operation(operation: str, user_id: str = None, **kwargs):
    """Log user-related operations."""
    logger = get_logger(__name__)

    # Handle user_id_val parameter for backward compatibility
    if "user_id_val" in kwargs:
        user_id = kwargs.pop("user_id_val")

    # If no user_id provided, try to get from context
    if user_id is None:
        user_id = get_user_id()

    logger.info(
        f"User operation: {operation}", operation=operation, user_id=user_id, **kwargs
    )


def log_validation(
    validation_type: str, field: str = None, value: str = None, **kwargs
):
    """Log validation operations."""
    logger = get_logger(__name__)

    # Truncate long values for logging
    if value and len(str(value)) > 100:
        value = str(value)[:100]

    logger.debug(
        f"Validation: {validation_type}",
        validation_type=validation_type,
        validator=validation_type,
        field=field,
        value=value,
        **kwargs,
    )


def get_user_id():
    """Get current user ID from logging context."""
    from .logging import user_id

    return user_id.get()
