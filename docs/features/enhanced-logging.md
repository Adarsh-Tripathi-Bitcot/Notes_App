# Enhanced Structured Logging

This document describes the enhanced structured logging system implemented in the Notes App, which provides comprehensive logging capabilities with metadata, context management, and environment-based configuration.

## Overview

The enhanced logging system builds upon the existing structured logging implementation to provide:

- **Enhanced Metadata**: File names, line numbers, function names, and optional tracing IDs
- **Colored Logs**: Development-friendly colored console output
- **Context Management**: Global and request-level context for tracing
- **Environment-based Configuration**: Smart defaults based on environment
- **Per-module Log Levels**: Fine-grained control over logging per module
- **JSON and Text Formats**: Flexible output formats for different environments

## Features

### 1. Enhanced Metadata

The logging system automatically includes:

- **File Information**: Source file name and line number
- **Function Information**: Function name where the log was called
- **Tracing IDs**: Optional X-Ray ID, User ID, and Request ID
- **Timestamp**: ISO format timestamp
- **Log Level**: Standard log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### 2. Colored Logs for Development

In development environment, logs are displayed with colors:

- **DEBUG**: Blue
- **INFO**: Green
- **WARNING**: Yellow
- **ERROR**: Red
- **CRITICAL**: Bold Red

### 3. Context Management

The system supports both global and request-level context:

```python
from src.core.logging import set_logging_context, clear_logging_context

# Set global context
set_logging_context(
    user_id="user-123",
    request_id="req-456",
    xray_id="xray-789"
)

# Clear context
clear_logging_context()
```

### 4. Environment-based Configuration

Log levels are automatically set based on environment:

- **Development**: DEBUG
- **Testing**: INFO
- **Staging**: WARNING
- **Production**: ERROR

### 5. Per-module Log Levels

Different modules can have different log levels:

```python
# In .env file
MODULE_LOG_LEVELS={"src.api": "DEBUG", "src.core": "INFO", "src.services": "WARNING"}
```

### 6. Flexible Output Formats

- **JSON Format**: Structured JSON output for production and monitoring
- **Text Format**: Human-readable text output for development

### 7. Service Layer Integration

The logging system integrates seamlessly with service layers:

```python
from src.core.logging import get_logger

class UserService:
    """User service with integrated structured logging."""

    def __init__(self):
        self.logger = get_logger(__name__)

    async def get_user(self, user_id: str):
        """Get user by ID with comprehensive logging."""
        self.logger.info("Fetching user", user_id=user_id)

        try:
            user = await self.repository.get(user_id)
            if user:
                self.logger.info("User found",
                    user_id=user_id,
                    user_email=user.email,
                    user_status=user.status)
            else:
                self.logger.warning("User not found", user_id=user_id)
            return user

        except Exception as e:
            self.logger.error("Failed to fetch user",
                user_id=user_id,
                error=str(e),
                error_type=e.__class__.__name__,
                exc_info=True)
            raise
```

## Configuration

### Environment Variables

```bash
# Logging Configuration
LOG_LEVEL=DEBUG                    # Override environment-based default
LOG_FORMAT=json                    # json or text
ENABLE_COLORED_LOGS=true          # Enable colored logs in development
ENABLE_FILE_LINE_INFO=true        # Enable file and line number info
ENABLE_XRAY_TRACING=false         # Enable AWS X-Ray tracing

# Per-module log level overrides
MODULE_LOG_LEVELS={"src.api": "DEBUG", "src.core": "INFO"}

# Testing Configuration
AUTH_BYPASS=false                 # Enable authentication bypass for testing
TEST_USER_ID=test-user-123        # Test user ID for bypass
TEST_USER_EMAIL=test@example.com  # Test user email for bypass
TEST_USER_USERNAME=testuser       # Test user username for bypass
```

### Configuration Class

The logging configuration is managed through the `Settings` class in `src/core/config.py`:

```python
class Settings(BaseSettings):
    # Enhanced Logging Configuration
    log_level: str = Field(default="", description="Logging level")
    log_format: str = Field(default="json", description="Log format")
    module_log_levels: Dict[str, str] = Field(default_factory=dict)
    enable_colored_logs: bool = Field(default=True)
    enable_file_line_info: bool = Field(default=True)
    enable_xray_tracing: bool = Field(default=False)

    # Testing Configuration
    auth_bypass: bool = Field(default=False)
    test_user_id: str = Field(default="test-user-123")
    test_user_email: str = Field(default="test@example.com")
    test_user_username: str = Field(default="testuser")
```

## Usage

### Basic Logging

```python
from src.core.logging import get_logger

logger = get_logger(__name__)

# Basic logging
logger.info("Application started")
logger.debug("Debug information", user_id="123")
logger.error("An error occurred", error_code="E001")
```

### Context Managers

```python
from src.core.logging import log_function_call, log_api_request, log_database_operation

# Function call context
with log_function_call(logger, "process_user", user_id="123"):
    logger.debug("Processing user data")

# API request context
with log_api_request(logger, "GET", "/api/v1/users", user_id="123"):
    logger.info("Handling user request")

# Database operation context
with log_database_operation(logger, "SELECT", "users", user_id="123"):
    logger.debug("Querying user data")
```

### Error Logging

```python
from src.core.logging import log_error

try:
    # Some operation
    pass
except Exception as e:
    log_error(logger, e, context={"operation": "user_creation"})
```

### Dynamic Log Level Changes

```python
from src.core.logging import set_log_level, get_current_log_level, reset_log_levels

# Set global log level
set_log_level("ERROR")

# Set module-specific log level
set_log_level("DEBUG", "src.api")

# Get current log level
current_level = get_current_log_level()

# Reset to defaults
reset_log_levels()
```

## API Endpoints

The logging system provides REST API endpoints for runtime management:

### Get Logging Status
```http
GET /api/v1/logging/status
```

### Set Log Level
```http
POST /api/v1/logging/set-level
Content-Type: application/json

{
    "level": "DEBUG",
    "module": "src.api"
}
```

### Get Module Log Level
```http
GET /api/v1/logging/level/{module_name}
```

### List Configured Modules
```http
GET /api/v1/logging/modules
```

### Reset Log Levels
```http
POST /api/v1/logging/reset
```

## Testing

### Test Isolation

The enhanced logging system includes utilities for test isolation:

```python
from tests.utils.test_helpers import TestEnvironment, TestLoggingHelper

# Isolated test environment
with TestEnvironment() as env:
    # Test with isolated environment
    pass

# Test logging context
TestLoggingHelper.setup_test_logging()
# ... test code ...
TestLoggingHelper.clear_test_logging()
```

### Authentication Bypass

For testing, authentication can be bypassed:

```python
from src.core.auth_bypass import AuthBypass, create_test_user_context

# Check if bypass is enabled
if AuthBypass.is_bypass_enabled():
    # Get test user context
    test_context = create_test_user_context()
```

## Log Output Examples

### JSON Format (Production)

```json
{
    "event": "User created successfully",
    "level": "info",
    "timestamp": "2024-01-15T10:30:00.123456Z",
    "logger": "src.services.user_service",
    "file": "user_service.py",
    "line": 45,
    "function": "create_user",
    "user_id": "user-123",
    "request_id": "req-456",
    "xray_id": "xray-789"
}
```

### Text Format (Development)

```
2024-01-15T10:30:00.123456Z [info     ] User created successfully
    logger=src.services.user_service file=user_service.py line=45 function=create_user
    user_id=user-123 request_id=req-456 xray_id=xray-789
```

## Best Practices

### 1. Use Appropriate Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General information about application flow
- **WARNING**: Something unexpected happened but the application can continue
- **ERROR**: An error occurred but the application can continue
- **CRITICAL**: A serious error occurred that might cause the application to stop

### 2. Include Relevant Context

Always include relevant context in log messages:

```python
# Good
logger.info("User login successful", user_id=user.id, email=user.email)

# Bad
logger.info("User login successful")
```

### 3. Use Context Managers

Use context managers for related operations:

```python
# Good
with log_api_request(logger, "POST", "/api/v1/users", user_id=user.id):
    # API logic here
    pass

# Bad
logger.info("API request started", method="POST", path="/api/v1/users")
# API logic here
logger.info("API request completed")
```

### 4. Handle Exceptions Properly

Always log exceptions with context:

```python
try:
    # Some operation
    pass
except Exception as e:
    log_error(logger, e, context={"operation": "user_creation", "user_id": user.id})
    raise
```

### 5. Use Structured Data

Use structured data instead of string formatting:

```python
# Good
logger.info("User created", user_id=user.id, email=user.email, status="active")

# Bad
logger.info(f"User {user.id} with email {user.email} created with status active")
```

## Performance Considerations

### 1. Log Level Filtering

The system automatically filters logs based on the configured log level. Ensure production environments use appropriate log levels to avoid performance impact.

### 2. Context Management

Context variables are stored in thread-local storage. Clear context when no longer needed to prevent memory leaks.

### 3. Large Context Data

Avoid logging large objects or sensitive data. Use references or IDs instead.

## Advanced Features

### Custom Processors

You can add custom processors for specific needs:

```python
def add_performance_processor(logger, method_name, event_dict):
    """Add performance metrics to logs."""
    if "start_time" in event_dict:
        duration = time.time() - event_dict["start_time"]
        event_dict["duration_ms"] = round(duration * 1000, 2)
    return event_dict
```

### Log Filtering

Filter logs based on environment or conditions:

```python
def should_log_debug(record):
    """Only log debug in development."""
    return settings.environment == "development"
```

### Metrics Integration

Integrate with monitoring systems:

```python
def add_metrics_processor(logger, method_name, event_dict):
    """Send metrics to monitoring system."""
    if event_dict.get("level") == "error":
        metrics_client.increment("errors.count")
```

### Environment-Specific Output

#### Development Mode (Colored Console)

```
[info     ] User login successful     correlation_id=abc-123 user_id=john_doe ip_address=192.168.1.1
[debug    ] Validating permissions    correlation_id=abc-123 user_id=john_doe permissions=['read', 'write']
[warning  ] Rate limit approaching    correlation_id=abc-123 current=950 limit=1000
```

#### Production Mode (JSON)

```json
{
  "event": "User login successful",
  "correlation_id": "abc-123",
  "user_id": "john_doe",
  "ip_address": "192.168.1.1",
  "timestamp": "2024-01-15T10:30:45Z",
  "level": "info",
  "filename": "auth.py",
  "lineno": 45
}
```

## Troubleshooting

### Common Issues

1. **Logs not appearing**: Check log level configuration
2. **Missing metadata**: Ensure `enable_file_line_info` is set to `true`
3. **Context not persisting**: Check if context is properly set and not cleared
4. **Performance issues**: Verify log level configuration and avoid logging in tight loops

### Debug Mode

Enable debug mode for detailed logging information:

```bash
LOG_LEVEL=DEBUG LOG_FORMAT=text python -m uvicorn src.api.main:app --reload
```

## Migration Guide

### From Basic Logging

If migrating from basic logging:

1. Update imports to use enhanced logging functions
2. Add context management where appropriate
3. Update configuration to include new settings
4. Test log output in different environments

### Configuration Updates

Update your `.env` file to include new configuration options:

```bash
# Add these new options
ENABLE_COLORED_LOGS=true
ENABLE_FILE_LINE_INFO=true
ENABLE_XRAY_TRACING=false
AUTH_BYPASS=false
TEST_USER_ID=test-user-123
TEST_USER_EMAIL=test@example.com
TEST_USER_USERNAME=testuser
```

## Future Enhancements

Potential future enhancements include:

1. **Log Aggregation**: Integration with log aggregation services
2. **Metrics**: Log-based metrics and monitoring
3. **Alerting**: Automated alerting based on log patterns
4. **Sampling**: Intelligent log sampling for high-volume applications
5. **Compression**: Log compression for storage optimization
