# Error Handling in Notes App

## Overview

The Notes App implements a comprehensive error handling strategy that provides consistent, informative, and user-friendly error responses across the entire application. This document explains the error handling approach, patterns, and best practices used throughout the system.

## Error Handling Strategy

### 1. Layered Error Handling

```
API Layer (HTTP Errors)
    ↓
Service Layer (Business Logic Errors)
    ↓
Repository Layer (Data Access Errors)
    ↓
Database Layer (Database Errors)
```

### 2. Error Categories

- **Validation Errors**: Input validation failures
- **Authentication Errors**: Authentication and authorization failures
- **Business Logic Errors**: Domain-specific business rule violations
- **Data Access Errors**: Database and persistence layer errors
- **System Errors**: Unexpected system-level errors

## Custom Exception Hierarchy

### Base Exception Class

```python
class NotesAppException(Exception):
    """Base exception class for all Notes App exceptions."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
```

### Specific Exception Types

```python
class ValidationError(NotesAppException):
    """Raised when input validation fails."""
    def __init__(self, message: str = "Validation failed", field: Optional[str] = None, **kwargs):
        super().__init__(message, "VALIDATION_ERROR", kwargs.get("details", {}))

class AuthenticationError(NotesAppException):
    """Raised when authentication fails."""
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, "AUTHENTICATION_ERROR", kwargs.get("details", {}))

class AuthorizationError(NotesAppException):
    """Raised when authorization fails."""
    def __init__(self, message: str = "Authorization failed", **kwargs):
        super().__init__(message, "AUTHORIZATION_ERROR", kwargs.get("details", {}))

class NotFoundError(NotesAppException):
    """Raised when a requested resource is not found."""
    def __init__(self, resource: str, identifier: Optional[str] = None, **kwargs):
        message = f"{resource} not found"
        if identifier:
            message += f" with identifier: {identifier}"
        super().__init__(message, "NOT_FOUND", kwargs.get("details", {}))

class ConflictError(NotesAppException):
    """Raised when a resource conflict occurs."""
    def __init__(self, message: str = "Resource conflict", **kwargs):
        super().__init__(message, "CONFLICT", kwargs.get("details", {}))

class DatabaseError(NotesAppException):
    """Raised when a database operation fails."""
    def __init__(self, message: str = "Database operation failed", **kwargs):
        super().__init__(message, "DATABASE_ERROR", kwargs.get("details", {}))
```

## Global Error Handler

### FastAPI Error Handler

```python
async def notes_app_exception_handler(
    request: Request,
    exc: NotesAppException
) -> JSONResponse:
    """Handle custom NotesAppException instances."""

    # Log the error
    log_error(logger, exc, {"path": request.url.path, "method": request.method})

    # Determine status code based on error type
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

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

    return JSONResponse(
        status_code=status_code,
        content=create_error_response(
            status_code=status_code,
            message=exc.message,
            error_code=exc.error_code,
            details=exc.details
        )
    )
```

### Standardized Error Response Format

```python
def create_error_response(
    status_code: int,
    message: str,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a standardized error response."""
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
```

## Error Handling Patterns

### 1. Service Layer Error Handling

```python
class AuthenticationService:
    def register_user(self, user_data: UserCreate) -> User:
        try:
            # Check if user already exists
            existing_user = self.user_repository.get_by_email(user_data.email)
            if existing_user:
                raise ValidationError(
                    message="User with this email already exists",
                    field="email",
                    value=user_data.email
                )

            # Validate password strength
            if not self._validate_password_strength(user_data.password):
                raise ValidationError(
                    message="Password does not meet strength requirements",
                    field="password"
                )

            # Create user
            return self.user_repository.create(user_dict)

        except ValidationError:
            raise  # Re-raise validation errors
        except IntegrityError as e:
            raise ConflictError(
                message="User creation failed due to data conflict",
                details={"error": str(e)}
            )
        except Exception as e:
            logger.error("Unexpected error in user registration", error=str(e))
            raise ValidationError(
                message="User registration failed",
                details={"error": "Internal server error"}
            )
```

### 2. Repository Layer Error Handling

```python
class UserRepository:
    def create(self, user_data: dict) -> User:
        try:
            user = User(**user_data)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user

        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e.orig)

            if "email" in error_msg.lower():
                raise ConflictError(
                    message="User with this email already exists",
                    details={"field": "email", "value": user_data.get("email")}
                )
            elif "username" in error_msg.lower():
                raise ConflictError(
                    message="User with this username already exists",
                    details={"field": "username", "value": user_data.get("username")}
                )
            else:
                raise DatabaseError(
                    message="Failed to create user due to data conflict",
                    details={"error": error_msg}
                )

        except Exception as e:
            self.db.rollback()
            logger.error("Database error in user creation", error=str(e))
            raise DatabaseError(
                message="Failed to create user",
                details={"error": str(e)}
            )
```

### 3. API Layer Error Handling

```python
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    try:
        user = auth_service.register_user(user_data)
        logger.info("User registered successfully", user_id=user.id, email=user.email)
        return user

    except ValidationError as e:
        logger.warning("User registration failed: validation error", error=e.message)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.message
        )
    except ConflictError as e:
        logger.warning("User registration failed: conflict error", error=e.message)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message
        )
    except Exception as e:
        logger.error("User registration failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )
```

## Error Logging Strategy

### Structured Logging

```python
def log_error(
    logger: structlog.BoundLogger,
    error: Exception,
    context: Optional[Dict[str, Any]] = None
) -> None:
    """Log an error with structured context."""
    error_context = {
        "error_type": type(error).__name__,
        "error_message": str(error),
    }

    if hasattr(error, 'error_code'):
        error_context["error_code"] = error.error_code

    if hasattr(error, 'details'):
        error_context["error_details"] = error.details

    if context:
        error_context.update(context)

    logger.error("An error occurred", **error_context)
```

### Error Context Management

```python
class LogContext:
    """Context manager for adding structured context to log messages."""

    def __init__(self, logger: structlog.BoundLogger, **context: Any):
        self.logger = logger
        self.context = context

    def __enter__(self) -> structlog.BoundLogger:
        return self.logger.bind(**self.context)

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        pass

# Usage
def create_note(self, note_data: NoteCreate, owner_id: int) -> Note:
    with log_function_call(logger, "create_note", owner_id=owner_id):
        try:
            # Business logic
            pass
        except Exception as e:
            log_error(logger, e, {"owner_id": owner_id, "operation": "create_note"})
            raise
```

## Error Response Examples

### 1. Validation Error

```json
{
    "error": {
        "message": "Validation failed",
        "status_code": 422,
        "code": "VALIDATION_ERROR",
        "details": {
            "validation_errors": [
                {
                    "field": "email",
                    "message": "Invalid email format",
                    "type": "value_error.email"
                },
                {
                    "field": "password",
                    "message": "Password must be at least 8 characters long",
                    "type": "value_error.min_length"
                }
            ]
        }
    }
}
```

### 2. Authentication Error

```json
{
    "error": {
        "message": "Invalid email or password",
        "status_code": 401,
        "code": "AUTHENTICATION_ERROR",
        "details": {
            "email": "user@example.com"
        }
    }
}
```

### 3. Not Found Error

```json
{
    "error": {
        "message": "Note not found with identifier: 123",
        "status_code": 404,
        "code": "NOT_FOUND",
        "details": {
            "resource": "Note",
            "identifier": "123"
        }
    }
}
```

### 4. Conflict Error

```json
{
    "error": {
        "message": "User with this email already exists",
        "status_code": 409,
        "code": "CONFLICT",
        "details": {
            "field": "email",
            "value": "user@example.com"
        }
    }
}
```

## Error Handling Best Practices

### 1. Fail Fast

```python
def validate_user_data(user_data: UserCreate) -> None:
    """Validate user data early and fail fast."""
    if not user_data.email:
        raise ValidationError("Email is required", field="email")

    if not user_data.password:
        raise ValidationError("Password is required", field="password")

    if len(user_data.password) < 8:
        raise ValidationError("Password must be at least 8 characters", field="password")
```

### 2. Specific Error Messages

```python
# Good: Specific error message
raise ValidationError("Password must contain at least one uppercase letter", field="password")

# Bad: Generic error message
raise ValidationError("Invalid input")
```

### 3. Error Context

```python
# Good: Include context in error
raise NotFoundError("Note", str(note_id), details={"user_id": user_id, "operation": "get_note"})

# Bad: No context
raise NotFoundError("Note not found")
```

### 4. Error Recovery

```python
def get_note_with_fallback(self, note_id: int, owner_id: int) -> Optional[Note]:
    """Get note with fallback strategy."""
    try:
        return self.note_repository.get_by_id(note_id, owner_id)
    except DatabaseError as e:
        logger.warning("Database error, trying cache", error=str(e))
        return self.cache.get(f"note:{note_id}")
    except Exception as e:
        logger.error("Unexpected error", error=str(e))
        return None
```

## Testing Error Handling

### 1. Unit Testing

```python
def test_register_user_duplicate_email():
    """Test user registration with duplicate email."""
    # Setup
    auth_service = AuthenticationService(mock_db)
    mock_repo.get_by_email.return_value = User(id=1, email="test@example.com")

    # Execute & Assert
    with pytest.raises(ValidationError) as exc_info:
        auth_service.register_user(user_data)

    assert "email already exists" in str(exc_info.value)
    assert exc_info.value.error_code == "VALIDATION_ERROR"
```

### 2. Integration Testing

```python
def test_register_user_api_error():
    """Test user registration API error handling."""
    response = client.post("/api/v1/users/register", json=duplicate_user_data)

    assert response.status_code == 409
    data = response.json()
    assert data["error"]["code"] == "CONFLICT"
    assert "email already exists" in data["error"]["message"]
```

### 3. Error Response Testing

```python
def test_error_response_format():
    """Test error response format."""
    response = client.get("/api/v1/notes/99999")

    assert response.status_code == 404
    data = response.json()

    assert "error" in data
    assert "message" in data["error"]
    assert "status_code" in data["error"]
    assert "code" in data["error"]
```

## Error Monitoring and Alerting

### 1. Error Metrics

```python
# Track error rates by type
error_counter = Counter("app_errors_total", "Total number of errors", ["error_type", "endpoint"])

def track_error(error_type: str, endpoint: str):
    error_counter.labels(error_type=error_type, endpoint=endpoint).inc()
```

### 2. Error Alerting

```python
# Alert on high error rates
def check_error_rate():
    if error_rate > 0.05:  # 5% error rate
        send_alert("High error rate detected", {"error_rate": error_rate})
```

## Common Error Handling Anti-Patterns

### 1. Silent Failures

❌ **Wrong**: Silent failure
```python
def get_user(self, user_id: int):
    try:
        return self.db.query(User).filter(User.id == user_id).first()
    except Exception:
        return None  # Silent failure
```

✅ **Correct**: Explicit error handling
```python
def get_user(self, user_id: int) -> Optional[User]:
    try:
        return self.db.query(User).filter(User.id == user_id).first()
    except Exception as e:
        logger.error("Database error in get_user", error=str(e), user_id=user_id)
        raise DatabaseError("Failed to retrieve user")
```

### 2. Generic Error Messages

❌ **Wrong**: Generic error
```python
except Exception as e:
    raise Exception("Something went wrong")
```

✅ **Correct**: Specific error
```python
except IntegrityError as e:
    raise ConflictError("User with this email already exists")
except Exception as e:
    raise DatabaseError("Failed to create user")
```

### 3. Error Swallowing

❌ **Wrong**: Swallowing errors
```python
try:
    risky_operation()
except Exception:
    pass  # Error swallowed
```

✅ **Correct**: Proper error handling
```python
try:
    risky_operation()
except Exception as e:
    logger.error("Operation failed", error=str(e))
    raise
```

## Conclusion

The error handling strategy in the Notes App provides:

- **Consistency**: Standardized error responses across the application
- **Clarity**: Clear and informative error messages
- **Traceability**: Comprehensive error logging and monitoring
- **User Experience**: User-friendly error messages
- **Maintainability**: Centralized error handling logic
- **Debugging**: Rich error context for troubleshooting

By implementing a comprehensive error handling strategy, the Notes App ensures robust error management while providing excellent developer and user experiences.
