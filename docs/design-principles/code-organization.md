# Code Organization in Notes App

## Overview

The Notes App follows a well-structured, modular organization that promotes maintainability, scalability, and team collaboration. This document explains the code organization principles, structure, and best practices used throughout the application.

## Organization Principles

### 1. Separation of Concerns
Each module and component has a single, well-defined responsibility:
- **API Layer**: HTTP request/response handling
- **Service Layer**: Business logic and orchestration
- **Repository Layer**: Data access and persistence
- **Model Layer**: Data structures and entities
- **Core Layer**: Infrastructure and configuration

### 2. Modular Design
Code is organized into logical, cohesive modules that can be developed, tested, and maintained independently.

### 3. Clear Dependencies
Dependencies flow in one direction, from high-level modules to low-level modules, following the Dependency Inversion Principle.

### 4. Consistent Naming
All modules, classes, functions, and variables follow consistent naming conventions.

## Project Structure

```
Notes_App/
├── src/                          # Source code
│   ├── core/                     # Core infrastructure
│   │   ├── __init__.py          # Package initialization
│   │   ├── config.py            # Configuration management
│   │   ├── database.py          # Database setup
│   │   ├── error_handler.py     # Error handling
│   │   ├── exceptions.py        # Custom exceptions
│   │   ├── logging.py           # Logging configuration
│   │   └── secrets_loader.py    # Secret management
│   ├── api/                      # API layer
│   │   ├── __init__.py          # Package initialization
│   │   ├── main.py              # FastAPI app setup
│   │   └── routers/             # API routers
│   │       ├── __init__.py      # Package initialization
│   │       ├── user_router.py   # User endpoints
│   │       └── notes_router.py  # Notes endpoints
│   ├── models/                   # Database models
│   │   ├── __init__.py          # Package initialization
│   │   ├── user.py              # User model
│   │   └── note.py              # Note model
│   ├── schemas/                  # Pydantic schemas
│   │   ├── __init__.py          # Package initialization
│   │   ├── user.py              # User schemas
│   │   └── note.py              # Note schemas
│   ├── repositories/             # Data access layer
│   │   ├── __init__.py          # Package initialization
│   │   ├── user_repository.py   # User repository
│   │   └── note_repository.py   # Note repository
│   ├── services/                 # Business logic layer
│   │   ├── __init__.py          # Package initialization
│   │   ├── authentication.py    # Auth service
│   │   └── note_management.py   # Note service
│   └── validators/               # Custom validators
│       ├── __init__.py          # Package initialization
│       └── custom_validators.py # Custom validation logic
├── tests/                        # Test suite
│   ├── __init__.py              # Package initialization
│   ├── conftest.py              # Test configuration
│   ├── api/                     # API tests
│   │   ├── __init__.py          # Package initialization
│   │   ├── test_auth.py         # Auth API tests
│   │   └── test_notes.py        # Notes API tests
│   ├── unit/                    # Unit tests
│   │   ├── __init__.py          # Package initialization
│   │   ├── test_auth_service.py # Auth service tests
│   │   └── test_note_service.py # Note service tests
│   └── integration/             # Integration tests
│       ├── __init__.py          # Package initialization
│       ├── test_database.py     # Database tests
│       └── test_services.py     # Service integration tests
├── migrations/                   # Database migrations
│   ├── alembic.ini              # Alembic configuration
│   ├── env.py                   # Migration environment
│   └── migration_handler.py     # Migration management
├── docs/                         # Documentation
│   ├── architecture-patterns/   # Architecture documentation
│   ├── clean-code/              # Clean code guidelines
│   ├── design-principles/       # Design principles
│   ├── developer_guidelines/    # Developer resources
│   └── step1/                   # Project phases
├── requirements/                 # Dependencies
│   └── requirements.txt         # Production dependencies
├── dev_requirements.txt         # Development dependencies
├── .pre-commit-config.yaml      # Pre-commit hooks
├── pyproject.toml               # Project configuration
├── pytest.ini                  # Pytest configuration
├── env.example                  # Environment variables template
├── run.py                       # Application runner script
└── README.md                    # Project documentation
```

## Layer Organization

### 1. Core Layer (`src/core/`)

**Purpose**: Infrastructure and configuration management

**Files**:
- `config.py`: Application configuration using Pydantic BaseSettings
- `database.py`: Database connection and session management
- `error_handler.py`: Global error handling middleware
- `exceptions.py`: Custom exception classes
- `logging.py`: Logging configuration and setup
- `secrets_loader.py`: Secret management utilities

**Organization Principles**:
- Single responsibility per file
- No business logic
- Infrastructure concerns only
- Used by all other layers

### 2. Model Layer (`src/models/`)

**Purpose**: Database entities and data structures

**Files**:
- `user.py`: User database model
- `note.py`: Note database model

**Organization Principles**:
- One model per file
- SQLAlchemy ORM models
- Database schema definition
- No business logic

### 3. Schema Layer (`src/schemas/`)

**Purpose**: Data validation and serialization

**Files**:
- `user.py`: User Pydantic schemas
- `note.py`: Note Pydantic schemas

**Organization Principles**:
- One entity per file
- Pydantic models
- Request/response validation
- Data transformation

### 4. Repository Layer (`src/repositories/`)

**Purpose**: Data access abstraction

**Files**:
- `user_repository.py`: User data access operations
- `note_repository.py`: Note data access operations

**Organization Principles**:
- One entity per file
- Database operations only
- No business logic
- Abstract data access

### 5. Service Layer (`src/services/`)

**Purpose**: Business logic and orchestration

**Files**:
- `authentication.py`: User authentication and authorization
- `note_management.py`: Note business logic and operations

**Organization Principles**:
- One domain per file
- Business logic only
- Orchestrates repositories
- No data access details

### 6. API Layer (`src/api/`)

**Purpose**: HTTP request/response handling

**Files**:
- `main.py`: FastAPI application setup
- `routers/user_router.py`: User API endpoints
- `routers/notes_router.py`: Notes API endpoints

**Organization Principles**:
- One domain per router
- HTTP concerns only
- Delegates to services
- No business logic

## Module Organization

### 1. Single Responsibility per Module

Each module has a single, well-defined responsibility:

```python
# src/repositories/user_repository.py
class UserRepository:
    """Single responsibility: User data access operations."""

    def create(self, user_data: dict) -> User:
        """Create a new user."""
        pass

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        pass

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass

    def update(self, user_id: int, update_data: dict) -> Optional[User]:
        """Update user."""
        pass

    def delete(self, user_id: int) -> bool:
        """Delete user."""
        pass
```

### 2. Consistent File Structure

Each file follows a consistent structure:

```python
# Standard file structure
"""
Module docstring describing the module's purpose.
"""

# Imports
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

# Constants
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# Classes
class UserRepository:
    """Class docstring describing the class's purpose."""

    def __init__(self, db: Session) -> None:
        """Initialize the repository."""
        self.db = db

    def create(self, user_data: dict) -> User:
        """Create a new user."""
        # Implementation
        pass

# Functions
def helper_function() -> None:
    """Helper function docstring."""
    pass

# Module-level code
if __name__ == "__main__":
    # Module execution code
    pass
```

### 3. Import Organization

Imports are organized in a consistent order:

```python
# 1. Standard library imports
import os
import sys
from typing import Optional, List, Dict, Any
from datetime import datetime

# 2. Third-party imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

# 3. Local imports
from src.core.database import get_db
from src.models.user import User
from src.schemas.user import UserCreate, UserResponse
from src.services.authentication import AuthenticationService
```

## Naming Conventions

### 1. File Naming

- **Snake case**: `user_repository.py`, `note_management.py`
- **Descriptive names**: `authentication.py`, `error_handler.py`
- **Consistent suffixes**: `_repository.py`, `_service.py`, `_router.py`

### 2. Class Naming

- **Pascal case**: `UserRepository`, `AuthenticationService`
- **Descriptive names**: `NoteManagementService`, `ErrorHandler`
- **Consistent suffixes**: `Repository`, `Service`, `Router`

### 3. Function Naming

- **Snake case**: `create_user`, `get_user_by_id`
- **Descriptive names**: `validate_password_strength`, `hash_password`
- **Verb-noun pattern**: `create_user`, `update_note`, `delete_note`

### 4. Variable Naming

- **Snake case**: `user_data`, `note_id`, `is_active`
- **Descriptive names**: `hashed_password`, `created_at`
- **Boolean prefix**: `is_active`, `is_public`, `has_permission`

## Dependency Organization

### 1. Dependency Flow

Dependencies flow in one direction:

```
API Layer → Service Layer → Repository Layer → Model Layer
    ↓           ↓              ↓
Core Layer ← Core Layer ← Core Layer
```

### 2. Circular Dependency Prevention

```python
# Good: One-way dependency
# API Layer
from src.services.authentication import AuthenticationService

# Service Layer
from src.repositories.user_repository import UserRepository

# Repository Layer
from src.models.user import User

# Bad: Circular dependency
# API Layer
from src.services.authentication import AuthenticationService

# Service Layer
from src.api.routers.user_router import UserRouter  # Circular!
```

### 3. Interface Segregation

```python
# Good: Segregated interfaces
class UserRepositoryInterface(ABC):
    @abstractmethod
    def create(self, user_data: dict) -> User:
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        pass

class UserRepository(UserRepositoryInterface):
    def create(self, user_data: dict) -> User:
        pass

    def get_by_id(self, user_id: int) -> Optional[User]:
        pass

# Bad: Fat interface
class UserRepository(ABC):
    @abstractmethod
    def create(self, user_data: dict) -> User:
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def send_email(self, user: User, message: str) -> None:
        pass  # Not related to data access
```

## Code Organization Best Practices

### 1. Keep Files Small

```python
# Good: Small, focused file
# src/repositories/user_repository.py
class UserRepository:
    """User data access operations."""

    def create(self, user_data: dict) -> User:
        pass

    def get_by_id(self, user_id: int) -> Optional[User]:
        pass

    def get_by_email(self, email: str) -> Optional[User]:
        pass

# Bad: Large, unfocused file
# src/repositories/user_repository.py
class UserRepository:
    """User data access operations."""

    def create(self, user_data: dict) -> User:
        pass

    def get_by_id(self, user_id: int) -> Optional[User]:
        pass

    def get_by_email(self, email: str) -> Optional[User]:
        pass

    def send_email(self, user: User, message: str) -> None:
        pass  # Not related to data access

    def validate_password(self, password: str) -> bool:
        pass  # Not related to data access
```

### 2. Use Consistent Patterns

```python
# Good: Consistent pattern across repositories
class UserRepository:
    def create(self, data: dict) -> User:
        pass

    def get_by_id(self, id: int) -> Optional[User]:
        pass

    def update(self, id: int, data: dict) -> Optional[User]:
        pass

    def delete(self, id: int) -> bool:
        pass

class NoteRepository:
    def create(self, data: dict) -> Note:
        pass

    def get_by_id(self, id: int) -> Optional[Note]:
        pass

    def update(self, id: int, data: dict) -> Optional[Note]:
        pass

    def delete(self, id: int) -> bool:
        pass
```

### 3. Group Related Functionality

```python
# Good: Related functionality grouped
class AuthenticationService:
    """Authentication and authorization operations."""

    def register_user(self, user_data: UserCreate) -> User:
        pass

    def login_user(self, login_data: UserLogin) -> TokenResponse:
        pass

    def verify_token(self, token: str) -> Optional[User]:
        pass

    def hash_password(self, password: str) -> str:
        pass

    def verify_password(self, password: str, hashed: str) -> bool:
        pass

# Bad: Unrelated functionality mixed
class UserService:
    """User operations."""

    def create_user(self, user_data: UserCreate) -> User:
        pass

    def send_email(self, user: User, message: str) -> None:
        pass  # Not related to user operations

    def log_activity(self, user: User, activity: str) -> None:
        pass  # Not related to user operations
```

### 4. Use Clear Module Boundaries

```python
# Good: Clear module boundaries
# src/services/authentication.py
class AuthenticationService:
    """Authentication service."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repository = UserRepository(db)  # Clear dependency

    def register_user(self, user_data: UserCreate) -> User:
        # Business logic
        pass

# Bad: Unclear module boundaries
# src/services/authentication.py
class AuthenticationService:
    """Authentication service."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repository = UserRepository(db)
        self.email_service = EmailService()  # Unclear dependency
        self.logging_service = LoggingService()  # Unclear dependency
```

## Testing Organization

### 1. Mirror Source Structure

```
src/
├── services/
│   └── authentication.py
└── repositories/
    └── user_repository.py

tests/
├── unit/
│   ├── test_authentication.py
│   └── test_user_repository.py
└── integration/
    ├── test_services.py
    └── test_repositories.py
```

### 2. Test File Naming

- **Test prefix**: `test_authentication.py`, `test_user_repository.py`
- **Descriptive names**: `test_user_registration.py`, `test_note_creation.py`
- **Consistent suffixes**: `_test.py`, `_spec.py`

### 3. Test Class Organization

```python
class TestUserRepository:
    """Test user repository functionality."""

    def test_create_user(self):
        """Test user creation."""
        pass

    def test_get_user_by_id(self):
        """Test getting user by ID."""
        pass

    def test_get_user_by_email(self):
        """Test getting user by email."""
        pass

    def test_update_user(self):
        """Test user update."""
        pass

    def test_delete_user(self):
        """Test user deletion."""
        pass
```

## Documentation Organization

### 1. Module Documentation

```python
"""
User repository module.

This module provides data access operations for user entities.
It implements the repository pattern to abstract database operations.

Classes:
    UserRepository: Repository for user data access operations.

Functions:
    None

Constants:
    DEFAULT_PAGE_SIZE: Default number of users per page.
    MAX_PAGE_SIZE: Maximum number of users per page.

Examples:
    >>> repo = UserRepository(db)
    >>> user = repo.create({"email": "user@example.com"})
    >>> user = repo.get_by_id(1)
"""
```

### 2. Class Documentation

```python
class UserRepository:
    """
    Repository for user data access operations.

    This class provides methods for creating, reading, updating,
    and deleting user entities in the database.

    Attributes:
        db (Session): Database session for operations.

    Methods:
        create(user_data: dict) -> User: Create a new user.
        get_by_id(user_id: int) -> Optional[User]: Get user by ID.
        get_by_email(email: str) -> Optional[User]: Get user by email.
        update(user_id: int, update_data: dict) -> Optional[User]: Update user.
        delete(user_id: int) -> bool: Delete user.

    Examples:
        >>> repo = UserRepository(db)
        >>> user = repo.create({"email": "user@example.com"})
        >>> user = repo.get_by_id(1)
    """
```

### 3. Function Documentation

```python
def create(self, user_data: dict) -> User:
    """
    Create a new user in the database.

    Args:
        user_data (dict): User data dictionary containing:
            - email (str): User's email address.
            - username (str, optional): User's username.
            - password (str): User's password.

    Returns:
        User: The created user entity.

    Raises:
        ValidationError: If user data is invalid.
        ConflictError: If user with email already exists.
        DatabaseError: If database operation fails.

    Examples:
        >>> repo = UserRepository(db)
        >>> user_data = {"email": "user@example.com", "password": "password123"}
        >>> user = repo.create(user_data)
        >>> print(user.email)
        user@example.com
    """
```

## Common Organization Issues

### 1. God Classes

❌ **Wrong**: One class doing everything
```python
class UserManager:
    def create_user(self, user_data: dict) -> User:
        pass

    def get_user(self, user_id: int) -> User:
        pass

    def update_user(self, user_id: int, user_data: dict) -> User:
        pass

    def delete_user(self, user_id: int) -> bool:
        pass

    def send_email(self, user: User, message: str) -> None:
        pass

    def log_activity(self, user: User, activity: str) -> None:
        pass

    def validate_password(self, password: str) -> bool:
        pass
```

✅ **Correct**: Separated responsibilities
```python
class UserRepository:
    def create_user(self, user_data: dict) -> User:
        pass

    def get_user(self, user_id: int) -> User:
        pass

    def update_user(self, user_id: int, user_data: dict) -> User:
        pass

    def delete_user(self, user_id: int) -> bool:
        pass

class EmailService:
    def send_email(self, user: User, message: str) -> None:
        pass

class LoggingService:
    def log_activity(self, user: User, activity: str) -> None:
        pass

class PasswordValidator:
    def validate_password(self, password: str) -> bool:
        pass
```

### 2. Circular Dependencies

❌ **Wrong**: Circular dependency
```python
# src/services/authentication.py
from src.api.routers.user_router import UserRouter

class AuthenticationService:
    def __init__(self) -> None:
        self.user_router = UserRouter()

# src/api/routers/user_router.py
from src.services.authentication import AuthenticationService

class UserRouter:
    def __init__(self) -> None:
        self.auth_service = AuthenticationService()
```

✅ **Correct**: One-way dependency
```python
# src/services/authentication.py
class AuthenticationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repository = UserRepository(db)

# src/api/routers/user_router.py
from src.services.authentication import AuthenticationService

class UserRouter:
    def __init__(self, auth_service: AuthenticationService) -> None:
        self.auth_service = auth_service
```

### 3. Inconsistent Naming

❌ **Wrong**: Inconsistent naming
```python
class userRepository:  # Should be UserRepository
    def CreateUser(self, userData: dict) -> User:  # Should be create_user
        pass

    def get_user_by_id(self, userId: int) -> User:  # Should be user_id
        pass
```

✅ **Correct**: Consistent naming
```python
class UserRepository:
    def create_user(self, user_data: dict) -> User:
        pass

    def get_user_by_id(self, user_id: int) -> User:
        pass
```

## Conclusion

The code organization in the Notes App provides:

- **Maintainability**: Easy to understand and modify code
- **Scalability**: Easy to add new features and modules
- **Team Collaboration**: Clear structure for multiple developers
- **Testability**: Easy to test individual components
- **Reusability**: Easy to reuse components in different contexts
- **Quality**: High-quality, well-structured code

By following consistent organization principles, the Notes App maintains excellent code quality, easy maintenance, and provides a solid foundation for future development and scaling.
