# Error Handling Features

This document describes the comprehensive error handling and validation system implemented in the Notes App.

## Overview

The error handling system provides robust error management with proper HTTP status codes, detailed error messages, and comprehensive validation.

## Key Features

### 1. Exception Management
- **Custom exception classes** for different error types
- **Centralized error handling** with FastAPI exception handlers
- **Structured error responses** with consistent formatting
- **Error logging** with correlation IDs and context

### 2. Input Validation
- **Pydantic model validation** for request data
- **Field-level validation** with custom validators
- **Type checking** and format validation
- **Business rule validation** at the service layer

### 3. Error Response Format
- **Consistent JSON structure** across all endpoints
- **Meaningful error messages** for developers and users
- **Error codes** for programmatic handling
- **Detailed validation errors** with field-specific messages

## Exception Hierarchy

### Base Exceptions
```python
class AppException(Exception):
    """Base application exception"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(AppException):
    """Input validation error"""
    pass

class NotFoundError(AppException):
    """Resource not found error"""
    pass

class AuthorizationError(AppException):
    """Authorization error"""
    pass

class DatabaseError(AppException):
    """Database operation error"""
    pass
```

### HTTP Exception Mapping
```python
# Exception to HTTP status code mapping
EXCEPTION_STATUS_MAP = {
    ValidationError: 422,
    NotFoundError: 404,
    AuthorizationError: 403,
    DatabaseError: 500,
    AppException: 500
}
```

## Error Response Format

### Standard Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Input validation failed",
    "details": {
      "field_errors": {
        "email": ["Invalid email format"],
        "password": ["Password must be at least 8 characters"]
      }
    }
  },
  "status": "error",
  "timestamp": "2024-01-15T10:30:00Z",
  "correlation_id": "abc-123-def-456"
}
```

### Validation Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "field_errors": {
        "title": ["This field is required"],
        "email": ["Invalid email format"],
        "password": [
          "Password must be at least 8 characters",
          "Password must contain at least one uppercase letter"
        ]
      }
    }
  },
  "status": "error"
}
```

### Not Found Error Response
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Note not found",
    "details": {
      "resource": "note",
      "resource_id": "123"
    }
  },
  "status": "error"
}
```

## Input Validation

### Pydantic Model Validation
```python
from pydantic import BaseModel, validator, Field
from typing import Optional

class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: Optional[str] = Field(None, max_length=10000)
    is_public: bool = Field(False)
    is_pinned: bool = Field(False)

    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

    @validator('content')
    def validate_content(cls, v):
        if v and len(v.strip()) < 10:
            raise ValueError('Content must be at least 10 characters')
        return v
```

### Custom Validators
```python
from pydantic import validator

class UserRegistration(BaseModel):
    email: str
    password: str
    full_name: str

    @validator('email')
    def validate_email(cls, v):
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', v):
            raise ValueError('Invalid email format')
        return v.lower()

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v
```

## Error Handling Middleware

### Global Exception Handler
```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import logging

app = FastAPI()

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    logger.error(
        "Application error occurred",
        error_code=exc.__class__.__name__,
        error_message=exc.message,
        error_details=exc.details,
        correlation_id=get_correlation_id()
    )

    status_code = EXCEPTION_STATUS_MAP.get(type(exc), 500)

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": exc.__class__.__name__.upper(),
                "message": exc.message,
                "details": exc.details
            },
            "status": "error",
            "correlation_id": get_correlation_id()
        }
    )
```

### HTTP Exception Handler
```python
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail,
                "details": {}
            },
            "status": "error",
            "correlation_id": get_correlation_id()
        }
    )
```

## Service Layer Error Handling

### Error Propagation
```python
class NoteService:
    def get_note(self, note_id: int, user_id: int) -> Note:
        try:
            note = self.note_repository.get_by_id(note_id, user_id)
            if not note:
                raise NotFoundError(
                    message="Note not found",
                    details={"note_id": note_id, "user_id": user_id}
                )
            return note
        except DatabaseError as e:
            logger.error("Database error in get_note", error=str(e))
            raise DatabaseError(
                message="Failed to retrieve note",
                details={"note_id": note_id, "original_error": str(e)}
            )
```

### Validation in Service Layer
```python
def create_note(self, note_data: NoteCreate, user_id: int) -> Note:
    # Business rule validation
    if len(note_data.title) > 200:
        raise ValidationError(
            message="Title too long",
            details={"field": "title", "max_length": 200}
        )

    # Check for duplicate titles
    existing_note = self.note_repository.get_by_title(note_data.title, user_id)
    if existing_note:
        raise ValidationError(
            message="Note with this title already exists",
            details={"field": "title", "value": note_data.title}
        )

    return self.note_repository.create(note_data.dict(), user_id)
```

## Error Logging

### Structured Error Logging
```python
import structlog

logger = structlog.get_logger(__name__)

def log_error(error: Exception, context: dict = None):
    logger.error(
        "Error occurred",
        error_type=type(error).__name__,
        error_message=str(error),
        error_details=getattr(error, 'details', {}),
        context=context or {},
        correlation_id=get_correlation_id()
    )
```

### Error Metrics
```python
def track_error_metrics(error_type: str, endpoint: str):
    # Track error rates by type and endpoint
    error_counter.labels(
        error_type=error_type,
        endpoint=endpoint
    ).inc()
```

## Benefits

1. **Consistency**: Uniform error handling across all endpoints
2. **Debugging**: Detailed error information with correlation IDs
3. **User Experience**: Clear, actionable error messages
4. **Monitoring**: Comprehensive error logging and metrics
5. **Maintainability**: Centralized error handling logic

## Testing

The error handling system includes comprehensive tests:
- Exception handling and mapping testing
- Input validation testing
- Error response format validation
- Error logging and metrics testing
- Integration testing with various error scenarios

Run the tests with:
```bash
python -m pytest tests/unit/test_error_handling.py -v
python -m pytest tests/api/test_error_scenarios.py -v
```
