# Structured Logging Implementation Guide

This guide provides comprehensive instructions for implementing structured logging in any Python project, following production-ready best practices.

## Overview

This implementation transforms traditional text-based logs into structured data formats (JSON) that are machine-readable and queryable, following production-ready specifications. The enhanced logging system provides:

- **Correlation ID tracking** for request tracing
- **Comprehensive metadata** including file, line, function, user ID, and process time
- **Layer-specific logging** for API, service, and repository operations
- **Request/response logging** with process time tracking
- **Structured JSON output** for easy parsing and analysis
- **Context management** for request-scoped information
- **Environment-aware formatting**: Human-readable logs for development, JSON for production
- **Cross-platform color support**: Enhanced readability in development

## Benefits of Structured Logging

### Traditional vs Structured Logging

```python
# Traditional logging (hard to parse and query)
logger.info("User john_doe logged in from IP 192.168.1.1 at 2024-01-15 10:30:45")

# Structured logging (machine-readable and queryable)
logger.info("User login successful",
    user_id="john_doe",
    ip_address="192.168.1.1",
    timestamp="2024-01-15T10:30:45Z",
    action="login")
```

## Key Features

### 1. Correlation ID Tracking
Every request gets a unique correlation ID that flows through all log entries, enabling easy request tracing across all application layers.

```json
{
  "correlation_id": "68715d28-833b-47d2-869f-260d7786d0da",
  "event": "API request: POST /api/v1/tasks/create",
  "user_id": "38511350-8031-7036-57a2-cceb5bb135ca"
}
```

### 2. Comprehensive Metadata
Each log entry includes detailed metadata:
- **File and line information** for debugging
- **Function name** for context
- **User ID** for user tracking
- **Request ID** for request tracing
- **Process time** in milliseconds
- **AWS X-Ray trace ID** (when available)

### 3. Layer-Specific Logging

#### API Layer (`APILogger`)
```python
api_logger = APILogger("notes")
api_logger.log_request("POST", "/api/v1/notes", user_id=user_id)
api_logger.log_response("POST", "/api/v1/notes", 201, note_id=note.id)
```

#### Service Layer (`ServiceLogger`)
```python
service_logger = ServiceLogger("note_management")
service_logger.log_operation("create_note", owner_id=owner_id, title=title)
service_logger.log_success("create_note", note_id=note.id, owner_id=owner_id)
```

#### Repository Layer (`RepositoryLogger`)
```python
repo_logger = RepositoryLogger("note_repository")
repo_logger.log_query("INSERT", "notes", owner_id=owner_id, title=title)
repo_logger.log_success("create", note_id=note.id, owner_id=owner_id)
```

### 4. Request Context Management
The system automatically manages request context using Python's `contextvars`:

```python
from src.core.logging import set_request_context, clear_logging_context

# Set request context
set_request_context(
    correlation_id_val="uuid-here",
    user_id_val="user-123",
    request_id_val="req-123",
    xray_id_val="xray-123"
)

# Context is automatically included in all log entries
# Clear context when request completes
clear_logging_context()
```

### 5. Middleware Integration
The `LoggingMiddleware` automatically:
- Generates correlation IDs for each request
- Tracks request start time for process time calculation
- Logs request and response details
- Manages context cleanup

## Log Entry Examples

### API Request Log
```json
{
  "router": "notes",
  "method": "POST",
  "path": "/api/v1/notes",
  "user_id": "38511350-8031-7036-57a2-cceb5bb135ca",
  "title": "Complete task 2",
  "is_public": false,
  "event": "API request: POST /api/v1/notes",
  "logger": "src.api.routers.notes",
  "level": "info",
  "timestamp": "2025-09-29T10:08:35.130193Z",
  "file": "stdlib.py",
  "line": 247,
  "function": "_proxy_to_logger",
  "correlation_id": "68715d28-833b-47d2-869f-260d7786d0da",
  "request_id": "3f1f8163-00c8-43dc-ab72-6ada4fc8905f",
  "process_time_ms": 0.19
}
```

### Service Operation Log
```json
{
  "service": "note_management",
  "operation": "create_note",
  "owner_id": 278,
  "title": "Complete task 2",
  "is_public": false,
  "event": "Service operation: create_note",
  "logger": "src.services.note_management",
  "level": "info",
  "timestamp": "2025-09-29T10:08:35.130934Z",
  "file": "stdlib.py",
  "line": 247,
  "function": "_proxy_to_logger",
  "correlation_id": "68715d28-833b-47d2-869f-260d7786d0da",
  "user_id": "38511350-8031-7036-57a2-cceb5bb135ca",
  "request_id": "3f1f8163-00c8-43dc-ab72-6ada4fc8905f",
  "process_time_ms": 0.9
}
```

### Repository Query Log
```json
{
  "repository": "note_repository",
  "operation": "INSERT",
  "table": "notes",
  "owner_id": 278,
  "title": "Complete task 2",
  "task_id": 2842,
  "event": "Database query: INSERT",
  "logger": "src.repositories.note_repository",
  "level": "debug",
  "timestamp": "2025-09-29T10:08:35.131575Z",
  "file": "stdlib.py",
  "line": 247,
  "function": "_proxy_to_logger",
  "correlation_id": "68715d28-833b-47d2-869f-260d7786d0da",
  "user_id": "38511350-8031-7036-57a2-cceb5bb135ca",
  "request_id": "3f1f8163-00c8-43dc-ab72-6ada4fc8905f",
  "process_time_ms": 1.54
}
```

### Request Completion Log
```json
{
  "request_method": "POST",
  "request_path": "/api/v1/notes",
  "process_time_ms": 102.63,
  "status_code": 201,
  "event": "Request completed",
  "logger": "src.core.middleware",
  "level": "info",
  "timestamp": "2025-09-29T10:08:35.232638Z",
  "file": "stdlib.py",
  "line": 247,
  "function": "_proxy_to_logger",
  "correlation_id": "68715d28-833b-47d2-869f-260d7786d0da",
  "user_id": "38511350-8031-7036-57a2-cceb5bb135ca",
  "request_id": "3f1f8163-00c8-43dc-ab72-6ada4fc8905f"
}
```

## Installation & Dependencies

### Required Packages

```bash
pip install structlog colorama contextvars pathlib
```

### Optional Dependencies

```bash
pip install fastapi starlette  # For web framework integration
pip install boto3              # For AWS services integration
```

## Configuration

### Environment Variables
```bash
# Logging Configuration
LOG_LEVEL=DEBUG                    # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_FORMAT=json                   # Log format (json or text)
ENABLE_COLORED_LOGS=true          # Enable colored logs in development
ENABLE_FILE_LINE_INFO=true        # Enable file and line number in logs
ENABLE_XRAY_TRACING=false         # Enable AWS X-Ray tracing

# Per-module log level overrides (optional)
MODULE_LOG_LEVELS={"src.api": "DEBUG", "src.core": "WARNING"}
```

### Log Level Configuration
The system supports environment-based log level defaults:
- **Development**: DEBUG
- **Testing**: INFO
- **Staging**: WARNING
- **Production**: ERROR

## Usage Examples

### Basic Logging
```python
from src.core.logging import get_logger

logger = get_logger(__name__)
logger.info("Operation completed", user_id=user_id, result=result)
```

### Service Layer Logging
```python
from src.core.logging_utils import ServiceLogger

service_logger = ServiceLogger("note_management")
service_logger.log_operation("create_note", owner_id=owner_id, title=title)
service_logger.log_success("create_note", note_id=note.id, owner_id=owner_id)
```

### Repository Layer Logging
```python
from src.core.logging_utils import RepositoryLogger

repo_logger = RepositoryLogger("note_repository")
repo_logger.log_query("INSERT", "notes", owner_id=owner_id, title=title)
repo_logger.log_success("create", note_id=note.id, owner_id=owner_id)
```

### API Layer Logging
```python
from src.core.logging_utils import APILogger

api_logger = APILogger("notes")
api_logger.log_request("POST", "/api/v1/notes", user_id=user_id)
api_logger.log_response("POST", "/api/v1/notes", 201, note_id=note.id)
```

## Benefits

1. **Request Tracing**: Correlation IDs enable tracking requests across all layers
2. **Debugging**: File, line, and function information aid in debugging
3. **Performance Monitoring**: Process time tracking helps identify bottlenecks
4. **User Tracking**: User ID context for security and analytics
5. **Structured Data**: JSON format enables easy parsing and analysis
6. **Layer Separation**: Clear separation between API, service, and repository logs
7. **Context Management**: Automatic context propagation and cleanup

## Best Practices

### Do's

- **Log in English**: Use clear and concise English for log messages
- **Include context**: Add relevant contextual information to make logs useful
- **Use appropriate levels**: Use log levels correctly (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Structure your data**: Use key-value pairs for machine readability
- **Include correlation IDs**: Always use correlation tracking for distributed systems

### Don'ts

- **Don't log sensitive data**: Avoid passwords, API keys, or personal information
- **Don't log too much**: Balance verbosity with performance and storage costs
- **Don't use string formatting**: Use structured parameters instead of string interpolation
- **Don't ignore errors**: Always log exceptions with proper context

### Example Implementation

```python
# ✅ Good - Structured with context
logger.info("Payment processed",
    user_id=user.id,
    amount=payment.amount,
    currency=payment.currency,
    transaction_id=payment.id,
    duration_ms=45.2)

# ❌ Bad - Unstructured string
logger.info(f"Payment of ${payment.amount} processed for user {user.id}")
```

## Testing

The enhanced logging system includes comprehensive tests:
- Context management testing
- Metadata inclusion verification
- Log level filtering tests
- Performance and thread safety tests

Run the tests with:
```bash
python -m pytest tests/test_enhanced_logging.py -v
```

## Troubleshooting

### Common Issues

1. **Missing correlation IDs**: Ensure middleware is properly configured
2. **No colored output**: Check environment settings and colorama installation
3. **Missing file info**: Verify caller info processor is enabled
4. **JSON parsing errors**: Validate structured data before logging

### Performance Considerations

- Use appropriate log levels to reduce I/O overhead
- Consider async logging for high-throughput applications
- Implement log rotation for production environments
- Monitor log storage and processing costs

## Demonstration

A demonstration script is available to showcase the logging features:
```bash
python demo_enhanced_logging.py
```

This script simulates a complete request flow and shows the structured logging output that matches your reference image style.
