# Code Standards in Notes App

## Overview

The Notes App follows strict code standards to ensure consistency, readability, and maintainability across the entire codebase. This document outlines the coding standards, style guidelines, and best practices used throughout the application.

## Code Style Guidelines

### 1. Python Style Guide (PEP 8)

The project strictly adheres to PEP 8 style guidelines with some project-specific modifications.

#### Line Length
- **Maximum line length**: 88 characters (Black formatter default)
- **Soft limit**: 80 characters for comments and docstrings
- **Hard limit**: 88 characters for code

#### Indentation
- **Use spaces, not tabs**: 4 spaces per indentation level
- **Continuation lines**: Align with opening delimiter or use hanging indent

```python
# Good: Hanging indent
def long_function_name(
    parameter_one: str,
    parameter_two: int,
    parameter_three: bool,
    parameter_four: Optional[str] = None,
) -> str:
    """Function with hanging indent."""
    return f"{parameter_one}_{parameter_two}_{parameter_three}"

# Good: Aligned with opening delimiter
def another_function(
    param1: str,
    param2: int,
    param3: bool,
) -> str:
    """Function with aligned parameters."""
    return f"{param1}_{param2}_{param3}"
```

#### Blank Lines
- **Top-level functions and classes**: 2 blank lines
- **Methods inside classes**: 1 blank line
- **Logical sections**: 1 blank line

```python
import os
import sys
from typing import Optional, List, Dict, Any


class UserRepository:
    """User repository for data access operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_user(self, user_data: dict) -> User:
        """Create a new user."""
        pass

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        pass


class NoteRepository:
    """Note repository for data access operations."""

    def __init__(self, db: Session) -> None:
        self.db = db
```

### 2. Naming Conventions

#### Variables and Functions
- **Snake case**: `user_data`, `create_user`, `get_user_by_id`
- **Descriptive names**: `hashed_password`, `is_active`, `created_at`
- **Boolean prefix**: `is_`, `has_`, `can_`, `should_`

```python
# Good: Clear, descriptive names
user_email = "user@example.com"
is_user_active = True
has_permission = False
can_edit_note = True
should_validate_password = True

# Bad: Unclear, abbreviated names
email = "user@example.com"
active = True
perm = False
edit = True
val = True
```

#### Classes
- **Pascal case**: `UserRepository`, `AuthenticationService`, `NoteManagementService`
- **Descriptive names**: `UserRepository`, `NoteRepository`, `ErrorHandler`
- **Consistent suffixes**: `Repository`, `Service`, `Router`, `Handler`

```python
# Good: Clear, descriptive class names
class UserRepository:
    """User repository for data access operations."""
    pass

class AuthenticationService:
    """Authentication service for user management."""
    pass

class NoteManagementService:
    """Note management service for note operations."""
    pass

# Bad: Unclear, abbreviated class names
class UserRepo:
    """User repository."""
    pass

class AuthSvc:
    """Authentication service."""
    pass

class NoteMgr:
    """Note manager."""
    pass
```

#### Constants
- **UPPER_CASE**: `DEFAULT_PAGE_SIZE`, `MAX_RETRY_ATTEMPTS`, `JWT_SECRET_KEY`
- **Descriptive names**: `DEFAULT_PAGE_SIZE`, `MAX_PASSWORD_LENGTH`, `TOKEN_EXPIRY_MINUTES`

```python
# Good: Clear, descriptive constants
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100
JWT_SECRET_KEY = "your-secret-key"
TOKEN_EXPIRY_MINUTES = 60
MAX_PASSWORD_LENGTH = 128
MIN_PASSWORD_LENGTH = 8

# Bad: Unclear, abbreviated constants
PAGE_SIZE = 10
MAX_SIZE = 100
SECRET = "your-secret-key"
EXPIRY = 60
MAX_PASS = 128
MIN_PASS = 8
```

#### Private Methods and Variables
- **Single underscore prefix**: `_validate_password`, `_hash_password`, `_user_data`
- **Double underscore prefix**: `__private_method`, `__private_variable` (use sparingly)

```python
class AuthenticationService:
    """Authentication service for user management."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self._user_repository = UserRepository(db)
        self.__secret_key = "secret"  # Use sparingly

    def register_user(self, user_data: UserCreate) -> User:
        """Register a new user."""
        self._validate_password_strength(user_data.password)
        hashed_password = self._hash_password(user_data.password)
        return self._user_repository.create({
            "email": user_data.email,
            "hashed_password": hashed_password,
        })

    def _validate_password_strength(self, password: str) -> None:
        """Validate password strength."""
        if len(password) < 8:
            raise ValidationError("Password too short")

    def _hash_password(self, password: str) -> str:
        """Hash password using BCrypt."""
        return pwd_context.hash(password)
```

### 3. Type Hints

#### Function Signatures
- **Always use type hints**: All function parameters and return types
- **Use Optional for nullable types**: `Optional[str]`, `Optional[User]`
- **Use Union for multiple types**: `Union[str, int]`, `Union[User, None]`
- **Use List, Dict for collections**: `List[User]`, `Dict[str, Any]`

```python
# Good: Complete type hints
def create_user(
    user_data: UserCreate,
    db: Session,
    validate: bool = True
) -> User:
    """Create a new user with type safety."""
    pass

def get_user_by_id(
    user_id: int,
    db: Session
) -> Optional[User]:
    """Get user by ID with type safety."""
    pass

def get_users_paginated(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> Tuple[List[User], int]:
    """Get paginated users with type safety."""
    pass

# Bad: Missing type hints
def create_user(user_data, db, validate=True):
    """Create a new user."""
    pass

def get_user_by_id(user_id, db):
    """Get user by ID."""
    pass
```

#### Class Attributes
- **Type hint class attributes**: All class attributes should have type hints
- **Use ClassVar for class variables**: `ClassVar[str]`, `ClassVar[int]`

```python
# Good: Type hinted class attributes
class UserRepository:
    """User repository for data access operations."""

    def __init__(self, db: Session) -> None:
        self.db: Session = db
        self.user_repository: UserRepository = UserRepository(db)
        self.default_page_size: int = 10
        self.max_page_size: int = 100

    def create_user(self, user_data: dict) -> User:
        """Create a new user."""
        pass

# Bad: Missing type hints
class UserRepository:
    """User repository for data access operations."""

    def __init__(self, db):
        self.db = db
        self.user_repository = UserRepository(db)
        self.default_page_size = 10
        self.max_page_size = 100
```

### 4. Docstrings

#### Function Docstrings
- **Use Google style**: Consistent with project documentation
- **Include all sections**: Args, Returns, Raises, Examples
- **Be descriptive**: Clear, concise descriptions

```python
def create_user(
    user_data: UserCreate,
    db: Session,
    validate: bool = True
) -> User:
    """
    Create a new user in the database.

    This function creates a new user with the provided data, validates
    the input if requested, and returns the created user entity.

    Args:
        user_data: User creation data containing email, username, and password.
        db: Database session for the operation.
        validate: Whether to validate the user data before creation.

    Returns:
        User: The created user entity with generated ID and timestamps.

    Raises:
        ValidationError: If user data validation fails.
        ConflictError: If user with email already exists.
        DatabaseError: If database operation fails.

    Examples:
        >>> user_data = UserCreate(
        ...     email="user@example.com",
        ...     username="user",
        ...     password="password123"
        ... )
        >>> user = create_user(user_data, db)
        >>> print(user.email)
        user@example.com
    """
    pass
```

#### Class Docstrings
- **Use Google style**: Consistent with project documentation
- **Include class description**: What the class does
- **Include attributes**: Key class attributes
- **Include methods**: Key class methods
- **Include examples**: Usage examples

```python
class UserRepository:
    """
    Repository for user data access operations.

    This class provides methods for creating, reading, updating,
    and deleting user entities in the database. It implements
    the repository pattern to abstract database operations.

    Attributes:
        db (Session): Database session for operations.
        default_page_size (int): Default number of users per page.
        max_page_size (int): Maximum number of users per page.

    Methods:
        create_user(user_data: dict) -> User: Create a new user.
        get_user_by_id(user_id: int) -> Optional[User]: Get user by ID.
        get_user_by_email(email: str) -> Optional[User]: Get user by email.
        update_user(user_id: int, user_data: dict) -> Optional[User]: Update user.
        delete_user(user_id: int) -> bool: Delete user.

    Examples:
        >>> repo = UserRepository(db)
        >>> user = repo.create_user({"email": "user@example.com"})
        >>> user = repo.get_user_by_id(1)
    """
    pass
```

### 5. Import Organization

#### Import Order
1. **Standard library imports**: `import os`, `import sys`
2. **Third-party imports**: `from fastapi import APIRouter`, `from sqlalchemy.orm import Session`
3. **Local imports**: `from src.core.database import get_db`, `from src.models.user import User`

```python
# Good: Organized imports
import os
import sys
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from src.core.database import get_db
from src.models.user import User
from src.schemas.user import UserCreate, UserResponse
from src.services.authentication import AuthenticationService

# Bad: Unorganized imports
from src.services.authentication import AuthenticationService
from fastapi import APIRouter, Depends, HTTPException
import os
from src.models.user import User
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
```

#### Import Style
- **Use absolute imports**: `from src.models.user import User`
- **Avoid wildcard imports**: `from src.models import *`
- **Group related imports**: Group by module or functionality

```python
# Good: Absolute imports
from src.models.user import User
from src.models.note import Note
from src.schemas.user import UserCreate, UserResponse
from src.schemas.note import NoteCreate, NoteResponse

# Bad: Wildcard imports
from src.models import *
from src.schemas import *
```

### 6. Error Handling

#### Exception Handling
- **Use specific exceptions**: `ValidationError`, `ConflictError`, `DatabaseError`
- **Include context**: Error messages should be descriptive
- **Log errors**: Log errors with appropriate level and context

```python
# Good: Specific exception handling
def create_user(user_data: UserCreate, db: Session) -> User:
    """Create a new user with proper error handling."""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ConflictError("User with this email already exists")

        # Create user
        user = User(**user_data.dict())
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    except IntegrityError as e:
        db.rollback()
        logger.error("Database integrity error in user creation", error=str(e))
        raise DatabaseError("Failed to create user due to data conflict")
    except Exception as e:
        db.rollback()
        logger.error("Unexpected error in user creation", error=str(e))
        raise DatabaseError("Failed to create user")

# Bad: Generic exception handling
def create_user(user_data: UserCreate, db: Session) -> User:
    """Create a new user with poor error handling."""
    try:
        user = User(**user_data.dict())
        db.add(user)
        db.commit()
        return user
    except Exception as e:
        raise Exception("Error creating user")  # Too generic
```

#### Custom Exceptions
- **Inherit from appropriate base class**: `Exception`, `ValueError`, `RuntimeError`
- **Include error codes**: For API error responses
- **Include context**: Additional error details

```python
# Good: Custom exception with context
class ValidationError(Exception):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        error_code: str = "VALIDATION_ERROR"
    ) -> None:
        super().__init__(message)
        self.message = message
        self.field = field
        self.error_code = error_code

class ConflictError(Exception):
    """Raised when a resource conflict occurs."""

    def __init__(
        self,
        message: str,
        resource: Optional[str] = None,
        error_code: str = "CONFLICT"
    ) -> None:
        super().__init__(message)
        self.message = message
        self.resource = resource
        self.error_code = error_code

# Bad: Generic exception
class AppError(Exception):
    """Generic application error."""
    pass
```

### 7. Code Organization

#### Function Length
- **Keep functions short**: Maximum 50 lines per function
- **Single responsibility**: Each function should do one thing
- **Extract complex logic**: Move complex logic to separate functions

```python
# Good: Short, focused function
def create_user(user_data: UserCreate, db: Session) -> User:
    """Create a new user."""
    _validate_user_data(user_data)
    _check_user_exists(user_data.email, db)
    hashed_password = _hash_password(user_data.password)

    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def _validate_user_data(user_data: UserCreate) -> None:
    """Validate user data."""
    if not user_data.email:
        raise ValidationError("Email is required")
    if not user_data.password:
        raise ValidationError("Password is required")

def _check_user_exists(email: str, db: Session) -> None:
    """Check if user already exists."""
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise ConflictError("User with this email already exists")

def _hash_password(password: str) -> str:
    """Hash password using BCrypt."""
    return pwd_context.hash(password)

# Bad: Long, unfocused function
def create_user(user_data: UserCreate, db: Session) -> User:
    """Create a new user."""
    # Validate user data
    if not user_data.email:
        raise ValidationError("Email is required")
    if not user_data.password:
        raise ValidationError("Password is required")

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise ConflictError("User with this email already exists")

    # Hash password
    hashed_password = pwd_context.hash(user_data.password)

    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
    )

    # Save to database
    db.add(user)
    db.commit()
    db.refresh(user)

    # Log user creation
    logger.info(f"User created: {user.email}")

    # Send welcome email
    send_welcome_email(user.email)

    # Update user statistics
    update_user_statistics()

    return user
```

#### Class Organization
- **Group related methods**: Group methods by functionality
- **Use consistent order**: `__init__`, public methods, private methods
- **Keep classes focused**: Single responsibility principle

```python
# Good: Well-organized class
class UserRepository:
    """User repository for data access operations."""

    def __init__(self, db: Session) -> None:
        """Initialize user repository."""
        self.db = db

    # Public methods
    def create_user(self, user_data: dict) -> User:
        """Create a new user."""
        pass

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        pass

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass

    def update_user(self, user_id: int, user_data: dict) -> Optional[User]:
        """Update user."""
        pass

    def delete_user(self, user_id: int) -> bool:
        """Delete user."""
        pass

    # Private methods
    def _validate_user_data(self, user_data: dict) -> None:
        """Validate user data."""
        pass

    def _check_user_exists(self, email: str) -> bool:
        """Check if user exists."""
        pass
```

### 8. Testing Standards

#### Test Naming
- **Descriptive test names**: `test_create_user_success`, `test_create_user_duplicate_email`
- **Test prefix**: All test functions start with `test_`
- **Test class prefix**: All test classes start with `Test`

```python
# Good: Descriptive test names
def test_create_user_success():
    """Test successful user creation."""
    pass

def test_create_user_duplicate_email():
    """Test user creation with duplicate email."""
    pass

def test_create_user_invalid_email():
    """Test user creation with invalid email."""
    pass

# Bad: Unclear test names
def test_user():
    """Test user."""
    pass

def test_create():
    """Test create."""
    pass

def test_error():
    """Test error."""
    pass
```

#### Test Organization
- **Arrange-Act-Assert**: Clear test structure
- **One assertion per test**: Each test should test one thing
- **Use descriptive assertions**: Clear assertion messages

```python
# Good: Well-organized test
def test_create_user_success():
    """Test successful user creation."""
    # Arrange
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="password123"
    )
    db = create_test_db()
    service = AuthenticationService(db)

    # Act
    user = service.register_user(user_data)

    # Assert
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.id is not None
    assert user.created_at is not None

# Bad: Poorly organized test
def test_user():
    """Test user."""
    user_data = UserCreate(email="test@example.com", username="testuser", password="password123")
    db = create_test_db()
    service = AuthenticationService(db)
    user = service.register_user(user_data)
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.id is not None
    assert user.created_at is not None
    assert user.updated_at is not None
    assert user.is_active is True
    assert user.is_verified is False
```

## Code Quality Tools

### 1. Black (Code Formatter)
```bash
# Format code
black src/

# Check formatting
black --check src/

# Format specific file
black src/services/authentication.py
```

### 2. Flake8 (Linter)
```bash
# Run linter
flake8 src/

# Run with specific configuration
flake8 --config pyproject.toml src/

# Run on specific file
flake8 src/services/authentication.py
```

### 3. MyPy (Type Checker)
```bash
# Run type checker
mypy src/

# Run with strict mode
mypy --strict src/

# Run on specific file
mypy src/services/authentication.py
```

### 4. isort (Import Sorter)
```bash
# Sort imports
isort src/

# Check import sorting
isort --check-only src/

# Sort specific file
isort src/services/authentication.py
```

### 5. Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit hooks
pre-commit run --all-files

# Run specific hook
pre-commit run black
```

## Common Code Issues

### 1. Missing Type Hints

❌ **Wrong**: Missing type hints
```python
def create_user(user_data, db):
    """Create a new user."""
    pass
```

✅ **Correct**: Complete type hints
```python
def create_user(user_data: UserCreate, db: Session) -> User:
    """Create a new user."""
    pass
```

### 2. Poor Variable Names

❌ **Wrong**: Unclear variable names
```python
def process_data(data):
    email = data.get('email')
    name = data.get('name')
    return f"{name} <{email}>"
```

✅ **Correct**: Clear variable names
```python
def process_user_data(user_data: dict) -> str:
    user_email = user_data.get('email')
    user_name = user_data.get('name')
    return f"{user_name} <{user_email}>"
```

### 3. Missing Error Handling

❌ **Wrong**: No error handling
```python
def create_user(user_data: UserCreate, db: Session) -> User:
    user = User(**user_data.dict())
    db.add(user)
    db.commit()
    return user
```

✅ **Correct**: Proper error handling
```python
def create_user(user_data: UserCreate, db: Session) -> User:
    try:
        user = User(**user_data.dict())
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError as e:
        db.rollback()
        raise ConflictError("User with this email already exists")
    except Exception as e:
        db.rollback()
        raise DatabaseError("Failed to create user")
```

### 4. Inconsistent Formatting

❌ **Wrong**: Inconsistent formatting
```python
def create_user(user_data:UserCreate,db:Session)->User:
    user=User(**user_data.dict())
    db.add(user)
    db.commit()
    return user
```

✅ **Correct**: Consistent formatting
```python
def create_user(user_data: UserCreate, db: Session) -> User:
    user = User(**user_data.dict())
    db.add(user)
    db.commit()
    return user
```

## Conclusion

The code standards in the Notes App provide:

- **Consistency**: Uniform code style across the entire codebase
- **Readability**: Clear, easy-to-understand code
- **Maintainability**: Easy to modify and extend code
- **Quality**: High-quality, well-structured code
- **Team Collaboration**: Clear standards for multiple developers
- **Automation**: Automated code quality checks

By following strict code standards, the Notes App maintains excellent code quality, consistency, and provides a solid foundation for future development and team collaboration.
