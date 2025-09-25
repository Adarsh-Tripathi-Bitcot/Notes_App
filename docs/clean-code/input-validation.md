# Input Validation in Notes App

## Overview

The Notes App implements comprehensive input validation using Pydantic to ensure data integrity, security, and user experience. This document explains the validation strategy, patterns, and best practices used throughout the application.

## Validation Strategy

### 1. Multi-Layer Validation

```
API Layer (Pydantic Schemas)
    ↓
Service Layer (Business Rules)
    ↓
Repository Layer (Database Constraints)
    ↓
Database Layer (Schema Validation)
```

### 2. Validation Types

- **Type Validation**: Data type checking
- **Format Validation**: Email, URL, date format validation
- **Range Validation**: Length, size, numeric range validation
- **Business Rule Validation**: Domain-specific validation rules
- **Security Validation**: Input sanitization and security checks

## Pydantic Schema Validation

### 1. User Validation Schemas

```python
class UserCreate(BaseModel):
    """Schema for user creation with comprehensive validation."""

    email: EmailStr = Field(..., description="User email address")
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        description="Username"
    )
    first_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="First name"
    )
    last_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Last name"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User password"
    )
    confirm_password: str = Field(..., description="Password confirmation")
    bio: Optional[str] = Field(
        None,
        max_length=500,
        description="User biography"
    )

    @validator('username')
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        """Validate username format and rules."""
        if v is not None:
            # Check for valid characters
            if not v.replace('_', '').replace('-', '').isalnum():
                raise ValueError(
                    'Username can only contain letters, numbers, underscores, and hyphens'
                )

            # Check for valid start/end
            if v.startswith(('_', '-')) or v.endswith(('_', '-')):
                raise ValueError(
                    'Username cannot start or end with underscore or hyphen'
                )

            # Check for reserved words
            reserved_words = ['admin', 'api', 'www', 'mail', 'root']
            if v.lower() in reserved_words:
                raise ValueError('Username is reserved')

        return v

    @validator('password')
    def validate_password(cls, v: str) -> str:
        """Validate password strength according to security requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')

        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')

        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')

        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')

        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            raise ValueError('Password must contain at least one special character')

        # Check for common passwords
        common_passwords = ['password', '123456', 'qwerty', 'abc123']
        if v.lower() in common_passwords:
            raise ValueError('Password is too common')

        return v

    @validator('confirm_password')
    def validate_confirm_password(cls, v: str, values: dict) -> str:
        """Validate password confirmation matches."""
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

    @validator('email')
    def validate_email_domain(cls, v: str) -> str:
        """Validate email domain is not from disposable email services."""
        disposable_domains = [
            '10minutemail.com', 'tempmail.org', 'guerrillamail.com'
        ]

        domain = v.split('@')[1].lower()
        if domain in disposable_domains:
            raise ValueError('Disposable email addresses are not allowed')

        return v
```

### 2. Note Validation Schemas

```python
class NoteCreate(BaseModel):
    """Schema for note creation with validation."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Note title"
    )
    content: str = Field(
        ...,
        min_length=1,
        description="Note content"
    )
    summary: Optional[str] = Field(
        None,
        max_length=500,
        description="Note summary"
    )
    is_public: bool = Field(
        default=False,
        description="Whether the note is public"
    )
    is_pinned: bool = Field(
        default=False,
        description="Whether the note is pinned"
    )

    @validator('title')
    def validate_title(cls, v: str) -> str:
        """Validate note title."""
        if not v.strip():
            raise ValueError('Title cannot be empty')

        # Check for excessive whitespace
        if len(v) != len(v.strip()):
            raise ValueError('Title cannot have leading or trailing whitespace')

        # Check for HTML tags
        if '<' in v and '>' in v:
            raise ValueError('Title cannot contain HTML tags')

        return v.strip()

    @validator('content')
    def validate_content(cls, v: str) -> str:
        """Validate note content."""
        if not v.strip():
            raise ValueError('Content cannot be empty')

        # Check content length
        if len(v) > 100000:  # 100KB limit
            raise ValueError('Content is too long (maximum 100,000 characters)')

        # Check for malicious content
        malicious_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'data:text/html',
        ]

        for pattern in malicious_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError('Content contains potentially malicious code')

        return v.strip()

    @validator('summary')
    def validate_summary(cls, v: Optional[str]) -> Optional[str]:
        """Validate note summary."""
        if v is not None:
            if not v.strip():
                return None

            if len(v) > 500:
                raise ValueError('Summary is too long (maximum 500 characters)')

            return v.strip()
        return None
```

### 3. Search and Filter Validation

```python
class NoteSearchRequest(BaseModel):
    """Schema for note search requests with validation."""

    query: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Search query"
    )
    status: Optional[NoteStatus] = Field(
        None,
        description="Filter by status"
    )
    is_public: Optional[bool] = Field(
        None,
        description="Filter by public status"
    )
    is_pinned: Optional[bool] = Field(
        None,
        description="Filter by pinned status"
    )
    created_after: Optional[datetime] = Field(
        None,
        description="Filter by creation date (after)"
    )
    created_before: Optional[datetime] = Field(
        None,
        description="Filter by creation date (before)"
    )
    page: int = Field(
        default=1,
        ge=1,
        description="Page number"
    )
    per_page: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of notes per page"
    )

    @validator('query')
    def validate_query(cls, v: Optional[str]) -> Optional[str]:
        """Validate search query."""
        if v is not None:
            if not v.strip():
                return None

            # Check for SQL injection patterns
            sql_patterns = [
                r'union\s+select',
                r'drop\s+table',
                r'delete\s+from',
                r'insert\s+into',
                r'update\s+set',
            ]

            for pattern in sql_patterns:
                if re.search(pattern, v, re.IGNORECASE):
                    raise ValueError('Search query contains invalid characters')

            return v.strip()
        return None

    @validator('created_after', 'created_before')
    def validate_date_range(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Validate date range."""
        if v is not None:
            # Check if date is not too far in the past
            if v < datetime(1900, 1, 1):
                raise ValueError('Date cannot be before 1900')

            # Check if date is not in the future
            if v > datetime.utcnow():
                raise ValueError('Date cannot be in the future')

        return v

    @validator('created_before')
    def validate_date_consistency(cls, v: Optional[datetime], values: dict) -> Optional[datetime]:
        """Validate date consistency."""
        if v is not None and 'created_after' in values and values['created_after'] is not None:
            if v <= values['created_after']:
                raise ValueError('created_before must be after created_after')

        return v
```

## Custom Validators

### 1. Email Validation

```python
def validate_email_format(email: str) -> str:
    """Custom email validation with additional checks."""
    # Basic email format validation
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        raise ValueError('Invalid email format')

    # Check for consecutive dots
    if '..' in email:
        raise ValueError('Email cannot contain consecutive dots')

    # Check for valid local part length
    local_part = email.split('@')[0]
    if len(local_part) > 64:
        raise ValueError('Email local part is too long')

    return email.lower()
```

### 2. Password Strength Validation

```python
def validate_password_strength(password: str) -> str:
    """Comprehensive password strength validation."""
    errors = []

    # Length check
    if len(password) < 8:
        errors.append('Password must be at least 8 characters long')

    if len(password) > 128:
        errors.append('Password must be no more than 128 characters long')

    # Character type checks
    if not any(c.isupper() for c in password):
        errors.append('Password must contain at least one uppercase letter')

    if not any(c.islower() for c in password):
        errors.append('Password must contain at least one lowercase letter')

    if not any(c.isdigit() for c in password):
        errors.append('Password must contain at least one digit')

    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append('Password must contain at least one special character')

    # Common password check
    common_passwords = [
        'password', '123456', 'qwerty', 'abc123', 'password123',
        'admin', 'letmein', 'welcome', 'monkey', 'dragon'
    ]

    if password.lower() in common_passwords:
        errors.append('Password is too common')

    # Sequential character check
    if re.search(r'(.)\1{2,}', password):
        errors.append('Password cannot contain more than 2 consecutive identical characters')

    # Keyboard pattern check
    keyboard_patterns = [
        'qwerty', 'asdfgh', 'zxcvbn', '123456', 'abcdef'
    ]

    for pattern in keyboard_patterns:
        if pattern in password.lower():
            errors.append('Password contains common keyboard patterns')

    if errors:
        raise ValueError('; '.join(errors))

    return password
```

### 3. Content Sanitization

```python
def sanitize_content(content: str) -> str:
    """Sanitize content to remove potentially harmful elements."""
    # Remove HTML tags
    content = re.sub(r'<[^>]+>', '', content)

    # Remove script tags and their content
    content = re.sub(r'<script.*?>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)

    # Remove javascript: URLs
    content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)

    # Remove data: URLs
    content = re.sub(r'data:', '', content, flags=re.IGNORECASE)

    # Normalize whitespace
    content = re.sub(r'\s+', ' ', content)

    return content.strip()
```

## Service Layer Validation

### 1. Business Rule Validation

```python
class AuthenticationService:
    def register_user(self, user_data: UserCreate) -> User:
        """Register user with business rule validation."""
        # Check if user already exists
        existing_user = self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise ValidationError(
                message="User with this email already exists",
                field="email",
                value=user_data.email
            )

        # Check username uniqueness if provided
        if user_data.username:
            existing_user = self.user_repository.get_by_username(user_data.username)
            if existing_user:
                raise ValidationError(
                    message="User with this username already exists",
                    field="username",
                    value=user_data.username
                )

        # Additional business rules
        self._validate_user_registration_rules(user_data)

        # Create user
        return self.user_repository.create(user_dict)

    def _validate_user_registration_rules(self, user_data: UserCreate) -> None:
        """Validate additional business rules for user registration."""
        # Check for suspicious patterns
        if self._contains_suspicious_patterns(user_data.email):
            raise ValidationError("Email contains suspicious patterns")

        # Check for rate limiting
        if self._is_rate_limited(user_data.email):
            raise ValidationError("Too many registration attempts")

    def _contains_suspicious_patterns(self, email: str) -> bool:
        """Check for suspicious patterns in email."""
        suspicious_patterns = [
            r'[<>]',  # HTML tags
            r'javascript:',  # JavaScript
            r'data:',  # Data URLs
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, email, re.IGNORECASE):
                return True

        return False
```

### 2. Data Integrity Validation

```python
class NoteManagementService:
    def create_note(self, note_data: NoteCreate, owner_id: int) -> Note:
        """Create note with data integrity validation."""
        # Validate owner exists
        owner = self.user_repository.get_by_id(owner_id)
        if not owner:
            raise ValidationError("Owner not found")

        # Validate note limits
        self._validate_note_limits(owner_id)

        # Sanitize content
        sanitized_content = sanitize_content(note_data.content)
        sanitized_title = sanitize_content(note_data.title)

        # Create note with sanitized data
        note_dict = {
            "title": sanitized_title,
            "content": sanitized_content,
            "summary": note_data.summary,
            "is_public": note_data.is_public,
            "is_pinned": note_data.is_pinned,
            "owner_id": owner_id,
            "status": NoteStatus.ACTIVE,
        }

        return self.note_repository.create(note_dict)

    def _validate_note_limits(self, owner_id: int) -> None:
        """Validate note creation limits."""
        # Check total note count
        total_notes = self.note_repository.count_by_owner(owner_id)
        if total_notes >= 1000:  # Business rule: max 1000 notes per user
            raise ValidationError("Maximum note limit reached")

        # Check daily note creation limit
        today = datetime.utcnow().date()
        today_notes = self.note_repository.count_notes_created_after(
            owner_id,
            datetime.combine(today, datetime.min.time())
        )

        if today_notes >= 50:  # Business rule: max 50 notes per day
            raise ValidationError("Daily note creation limit reached")
```

## API Layer Validation

### 1. Request Validation

```python
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Register user with API-level validation."""
    try:
        # Pydantic validation happens automatically
        user = auth_service.register_user(user_data)
        return user

    except ValidationError as e:
        # Handle validation errors
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": e.message,
                "field": getattr(e, 'field', None),
                "code": e.error_code
            }
        )
```

### 2. Response Validation

```python
@router.get("/notes/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get note with response validation."""
    # Validate note_id
    if note_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid note ID"
        )

    note = note_service.get_note(note_id, current_user.id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    return note
```

## Validation Testing

### 1. Unit Testing

```python
def test_user_creation_validation():
    """Test user creation validation."""
    # Test valid data
    valid_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }

    user = UserCreate(**valid_data)
    assert user.email == "test@example.com"

    # Test invalid email
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(email="invalid-email", password="Password123!", confirm_password="Password123!")

    assert "email" in str(exc_info.value)

    # Test weak password
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(email="test@example.com", password="123", confirm_password="123")

    assert "password" in str(exc_info.value)
```

### 2. Integration Testing

```python
def test_note_creation_api_validation():
    """Test note creation API validation."""
    # Test valid note
    valid_note = {
        "title": "Test Note",
        "content": "Test content",
        "is_public": False
    }

    response = client.post("/api/v1/notes/", json=valid_note, headers=auth_headers)
    assert response.status_code == 201

    # Test invalid note (empty title)
    invalid_note = {
        "title": "",
        "content": "Test content"
    }

    response = client.post("/api/v1/notes/", json=invalid_note, headers=auth_headers)
    assert response.status_code == 422
    assert "title" in response.json()["detail"]
```

## Security Considerations

### 1. Input Sanitization

```python
def sanitize_input(input_str: str) -> str:
    """Sanitize input to prevent XSS and injection attacks."""
    # Remove HTML tags
    input_str = re.sub(r'<[^>]+>', '', input_str)

    # Remove script content
    input_str = re.sub(r'<script.*?>.*?</script>', '', input_str, flags=re.IGNORECASE | re.DOTALL)

    # Remove javascript: URLs
    input_str = re.sub(r'javascript:', '', input_str, flags=re.IGNORECASE)

    # Remove SQL injection patterns
    sql_patterns = [
        r'union\s+select',
        r'drop\s+table',
        r'delete\s+from',
        r'insert\s+into',
        r'update\s+set',
    ]

    for pattern in sql_patterns:
        input_str = re.sub(pattern, '', input_str, flags=re.IGNORECASE)

    return input_str.strip()
```

### 2. Rate Limiting

```python
def validate_rate_limit(identifier: str, operation: str) -> None:
    """Validate rate limiting for operations."""
    key = f"rate_limit:{operation}:{identifier}"

    # Check current count
    current_count = redis_client.get(key)
    if current_count and int(current_count) >= RATE_LIMITS[operation]:
        raise ValidationError(f"Rate limit exceeded for {operation}")

    # Increment counter
    redis_client.incr(key)
    redis_client.expire(key, RATE_LIMIT_WINDOW)
```

## Best Practices

### 1. Early Validation

```python
# Validate as early as possible
def process_user_data(user_data: dict) -> User:
    # Validate at the entry point
    validated_data = UserCreate(**user_data)

    # Process validated data
    return create_user(validated_data)
```

### 2. Specific Error Messages

```python
# Good: Specific error message
raise ValidationError("Password must contain at least one uppercase letter", field="password")

# Bad: Generic error message
raise ValidationError("Invalid input")
```

### 3. Validation Reuse

```python
# Create reusable validators
def validate_email(email: str) -> str:
    # Email validation logic
    pass

# Use in multiple schemas
class UserCreate(BaseModel):
    email: str = Field(..., validator=validate_email)

class UserUpdate(BaseModel):
    email: Optional[str] = Field(None, validator=validate_email)
```

## Conclusion

The input validation strategy in the Notes App provides:

- **Data Integrity**: Ensures data quality and consistency
- **Security**: Prevents malicious input and attacks
- **User Experience**: Provides clear validation feedback
- **Maintainability**: Centralized validation logic
- **Performance**: Early validation prevents unnecessary processing
- **Compliance**: Meets security and data quality standards

By implementing comprehensive input validation, the Notes App ensures data quality, security, and excellent user experience while maintaining clean and maintainable code.
