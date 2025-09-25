# Abstractions and Interfaces in Notes App

## Overview

The Notes App implements a comprehensive abstraction layer using interfaces and abstract base classes to promote loose coupling, testability, and maintainability. This document explains the abstraction strategy, interface design, and implementation patterns used throughout the application.

## Abstraction Strategy

### 1. Interface Segregation
Each interface represents a specific, cohesive set of operations, ensuring clients only depend on what they actually use.

### 2. Dependency Inversion
High-level modules depend on abstractions, not concrete implementations, enabling easy substitution and testing.

### 3. Single Responsibility
Each interface has a single, well-defined responsibility, making the system more maintainable and understandable.

## Core Interfaces

### 1. Repository Interfaces

#### Base Repository Interface
```python
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List, Dict, Any
from sqlalchemy.orm import Session

T = TypeVar('T')

class BaseRepositoryInterface(ABC, Generic[T]):
    """Base interface for all repository operations."""

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> T:
        """Create a new entity."""
        pass

    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """Get entity by ID."""
        pass

    @abstractmethod
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[T]:
        """Get all entities with pagination."""
        pass

    @abstractmethod
    def update(
        self,
        entity_id: int,
        data: Dict[str, Any]
    ) -> Optional[T]:
        """Update entity by ID."""
        pass

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Delete entity by ID."""
        pass

    @abstractmethod
    def exists(self, entity_id: int) -> bool:
        """Check if entity exists."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Count total entities."""
        pass
```

#### User Repository Interface
```python
class UserRepositoryInterface(BaseRepositoryInterface[User]):
    """Interface for user repository operations."""

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        pass

    @abstractmethod
    def get_active_users(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get all active users."""
        pass

    @abstractmethod
    def count_active_users(self) -> int:
        """Count active users."""
        pass

    @abstractmethod
    def update_last_login(self, user_id: int) -> None:
        """Update user's last login timestamp."""
        pass
```

#### Note Repository Interface
```python
class NoteRepositoryInterface(BaseRepositoryInterface[Note]):
    """Interface for note repository operations."""

    @abstractmethod
    def get_by_owner(
        self,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[NoteStatus] = None,
        is_public: Optional[bool] = None,
        is_pinned: Optional[bool] = None,
        search_query: Optional[str] = None
    ) -> List[Note]:
        """Get notes by owner with filtering."""
        pass

    @abstractmethod
    def get_public_notes(
        self,
        skip: int = 0,
        limit: int = 100,
        search_query: Optional[str] = None
    ) -> List[Note]:
        """Get public notes."""
        pass

    @abstractmethod
    def count_by_owner(
        self,
        owner_id: int,
        status: Optional[NoteStatus] = None,
        is_public: Optional[bool] = None,
        is_pinned: Optional[bool] = None,
        search_query: Optional[str] = None
    ) -> int:
        """Count notes by owner with filtering."""
        pass

    @abstractmethod
    def get_stats(self, owner_id: int) -> Dict[str, int]:
        """Get note statistics for owner."""
        pass

    @abstractmethod
    def bulk_update_status(
        self,
        note_ids: List[int],
        status: NoteStatus
    ) -> int:
        """Bulk update note status."""
        pass
```

### 2. Service Interfaces

#### Authentication Service Interface
```python
class AuthenticationServiceInterface(ABC):
    """Interface for authentication service operations."""

    @abstractmethod
    def register_user(self, user_data: UserCreate) -> User:
        """Register a new user."""
        pass

    @abstractmethod
    def login_user(self, login_data: UserLogin) -> TokenResponse:
        """Login user and return JWT token."""
        pass

    @abstractmethod
    def verify_token(self, token: str) -> Optional[User]:
        """Verify JWT token and return user."""
        pass

    @abstractmethod
    def refresh_token(self, token: str) -> Optional[TokenResponse]:
        """Refresh JWT token."""
        pass

    @abstractmethod
    def logout_user(self, user_id: int) -> None:
        """Logout user and invalidate token."""
        pass

    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Hash password using BCrypt."""
        pass

    @abstractmethod
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash."""
        pass
```

#### Note Management Service Interface
```python
class NoteManagementServiceInterface(ABC):
    """Interface for note management service operations."""

    @abstractmethod
    def create_note(
        self,
        note_data: NoteCreate,
        owner_id: int
    ) -> Note:
        """Create a new note."""
        pass

    @abstractmethod
    def get_note(
        self,
        note_id: int,
        owner_id: int
    ) -> Optional[Note]:
        """Get note by ID for owner."""
        pass

    @abstractmethod
    def get_notes(
        self,
        owner_id: int,
        page: int = 1,
        per_page: int = 10,
        status: Optional[NoteStatus] = None,
        search: Optional[str] = None
    ) -> PaginatedResponse[Note]:
        """Get paginated notes for owner."""
        pass

    @abstractmethod
    def update_note(
        self,
        note_id: int,
        note_data: NoteUpdate,
        owner_id: int
    ) -> Optional[Note]:
        """Update note for owner."""
        pass

    @abstractmethod
    def delete_note(
        self,
        note_id: int,
        owner_id: int
    ) -> bool:
        """Delete note for owner."""
        pass

    @abstractmethod
    def search_notes(
        self,
        search_request: NoteSearchRequest,
        owner_id: int
    ) -> PaginatedResponse[Note]:
        """Search notes for owner."""
        pass

    @abstractmethod
    def get_note_stats(self, owner_id: int) -> NoteStats:
        """Get note statistics for owner."""
        pass
```

### 3. Database Interfaces

#### Database Connection Interface
```python
class DatabaseInterface(ABC):
    """Interface for database operations."""

    @abstractmethod
    def get_session(self) -> Session:
        """Get database session."""
        pass

    @abstractmethod
    def close_session(self, session: Session) -> None:
        """Close database session."""
        pass

    @abstractmethod
    def begin_transaction(self) -> None:
        """Begin database transaction."""
        pass

    @abstractmethod
    def commit_transaction(self) -> None:
        """Commit database transaction."""
        pass

    @abstractmethod
    def rollback_transaction(self) -> None:
        """Rollback database transaction."""
        pass
```

#### Migration Interface
```python
class MigrationInterface(ABC):
    """Interface for database migration operations."""

    @abstractmethod
    def create_migration(self, message: str) -> str:
        """Create a new migration."""
        pass

    @abstractmethod
    def upgrade_database(self, revision: str = "head") -> None:
        """Upgrade database to revision."""
        pass

    @abstractmethod
    def downgrade_database(self, revision: str) -> None:
        """Downgrade database to revision."""
        pass

    @abstractmethod
    def get_current_revision(self) -> str:
        """Get current database revision."""
        pass

    @abstractmethod
    def get_migration_history(self) -> List[str]:
        """Get migration history."""
        pass
```

### 4. Validation Interfaces

#### Input Validator Interface
```python
class InputValidatorInterface(ABC):
    """Interface for input validation operations."""

    @abstractmethod
    def validate_user_data(self, user_data: Dict[str, Any]) -> None:
        """Validate user input data."""
        pass

    @abstractmethod
    def validate_note_data(self, note_data: Dict[str, Any]) -> None:
        """Validate note input data."""
        pass

    @abstractmethod
    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        pass

    @abstractmethod
    def validate_password(self, password: str) -> bool:
        """Validate password strength."""
        pass

    @abstractmethod
    def sanitize_input(self, input_str: str) -> str:
        """Sanitize input string."""
        pass
```

#### Business Rule Validator Interface
```python
class BusinessRuleValidatorInterface(ABC):
    """Interface for business rule validation operations."""

    @abstractmethod
    def validate_user_registration_rules(
        self,
        user_data: UserCreate
    ) -> None:
        """Validate user registration business rules."""
        pass

    @abstractmethod
    def validate_note_creation_rules(
        self,
        note_data: NoteCreate,
        owner_id: int
    ) -> None:
        """Validate note creation business rules."""
        pass

    @abstractmethod
    def validate_note_update_rules(
        self,
        note_data: NoteUpdate,
        note_id: int,
        owner_id: int
    ) -> None:
        """Validate note update business rules."""
        pass

    @abstractmethod
    def validate_note_deletion_rules(
        self,
        note_id: int,
        owner_id: int
    ) -> None:
        """Validate note deletion business rules."""
        pass
```

## Interface Implementation

### 1. Repository Implementation

```python
class UserRepository(UserRepositoryInterface):
    """User repository implementation."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: Dict[str, Any]) -> User:
        """Create a new user."""
        try:
            user = User(**data)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError as e:
            self.db.rollback()
            raise ConflictError("User with this email already exists")

    def get_by_id(self, entity_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == entity_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db.query(User).filter(User.username == username).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get all users with pagination."""
        return self.db.query(User).offset(skip).limit(limit).all()

    def get_active_users(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get all active users."""
        return (
            self.db.query(User)
            .filter(User.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(
        self,
        entity_id: int,
        data: Dict[str, Any]
    ) -> Optional[User]:
        """Update user by ID."""
        user = self.get_by_id(entity_id)
        if not user:
            return None

        for field, value in data.items():
            if hasattr(user, field):
                setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, entity_id: int) -> bool:
        """Delete user by ID."""
        user = self.get_by_id(entity_id)
        if not user:
            return False

        self.db.delete(user)
        self.db.commit()
        return True

    def exists(self, entity_id: int) -> bool:
        """Check if user exists."""
        return self.get_by_id(entity_id) is not None

    def count(self) -> int:
        """Count total users."""
        return self.db.query(User).count()

    def count_active_users(self) -> int:
        """Count active users."""
        return self.db.query(User).filter(User.is_active == True).count()

    def update_last_login(self, user_id: int) -> None:
        """Update user's last login timestamp."""
        user = self.get_by_id(user_id)
        if user:
            user.last_login = datetime.utcnow()
            self.db.commit()
```

### 2. Service Implementation

```python
class AuthenticationService(AuthenticationServiceInterface):
    """Authentication service implementation."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repository = UserRepository(db)

    def register_user(self, user_data: UserCreate) -> User:
        """Register a new user."""
        # Check if user already exists
        existing_user = self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise ValidationError("User with this email already exists")

        # Validate password strength
        if not self._validate_password_strength(user_data.password):
            raise ValidationError("Password does not meet strength requirements")

        # Hash password
        hashed_password = self.hash_password(user_data.password)

        # Create user
        user_dict = {
            "email": user_data.email,
            "username": user_data.username,
            "hashed_password": hashed_password,
            "is_active": True,
            "is_verified": False,
        }

        return self.user_repository.create(user_dict)

    def login_user(self, login_data: UserLogin) -> TokenResponse:
        """Login user and return JWT token."""
        user = self._authenticate_user(login_data)
        if not user:
            raise AuthenticationError("Invalid email or password")

        # Create JWT token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
        }

        access_token = self._create_access_token(token_data)
        expires_in = settings.jwt_expiry_minutes * 60

        # Update last login
        self.user_repository.update_last_login(user.id)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in
        )

    def verify_token(self, token: str) -> Optional[User]:
        """Verify JWT token and return user."""
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            user_id = payload.get("sub")
            if user_id is None:
                return None

            return self.user_repository.get_by_id(int(user_id))
        except JWTError:
            return None

    def refresh_token(self, token: str) -> Optional[TokenResponse]:
        """Refresh JWT token."""
        user = self.verify_token(token)
        if not user:
            return None

        # Create new token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
        }

        access_token = self._create_access_token(token_data)
        expires_in = settings.jwt_expiry_minutes * 60

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in
        )

    def logout_user(self, user_id: int) -> None:
        """Logout user and invalidate token."""
        # In a real implementation, you might add the token to a blacklist
        # For now, we'll just update the user's last logout time
        user = self.user_repository.get_by_id(user_id)
        if user:
            user.last_logout = datetime.utcnow()
            self.db.commit()

    def hash_password(self, password: str) -> str:
        """Hash password using BCrypt."""
        return pwd_context.hash(password)

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(password, hashed)

    def _authenticate_user(self, login_data: UserLogin) -> Optional[User]:
        """Authenticate user with email and password."""
        user = self.user_repository.get_by_email(login_data.email)
        if not user or not user.is_active:
            return None

        if not self.verify_password(login_data.password, user.hashed_password):
            return None

        return user

    def _create_access_token(self, data: dict) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expiry_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    def _validate_password_strength(self, password: str) -> bool:
        """Validate password strength."""
        if len(password) < 8:
            return False
        if not any(c.isupper() for c in password):
            return False
        if not any(c.islower() for c in password):
            return False
        if not any(c.isdigit() for c in password):
            return False
        return True
```

## Interface Benefits

### 1. Loose Coupling
```python
# High-level module depends on abstraction
class NoteManagementService:
    def __init__(self, note_repository: NoteRepositoryInterface) -> None:
        self.note_repository = note_repository  # Depends on interface

    def create_note(self, note_data: NoteCreate, owner_id: int) -> Note:
        return self.note_repository.create(note_data.dict())

# Low-level module implements abstraction
class NoteRepository(NoteRepositoryInterface):
    def create(self, data: Dict[str, Any]) -> Note:
        # Implementation
        pass

# Easy to substitute implementations
mock_repository = Mock(spec=NoteRepositoryInterface)
service = NoteManagementService(mock_repository)
```

### 2. Testability
```python
def test_note_creation():
    """Test note creation with mock repository."""
    # Create mock repository
    mock_repo = Mock(spec=NoteRepositoryInterface)
    mock_repo.create.return_value = Note(id=1, title="Test Note")

    # Create service with mock
    service = NoteManagementService(mock_repo)

    # Test service
    note_data = NoteCreate(title="Test Note", content="Test content")
    result = service.create_note(note_data, owner_id=1)

    # Assertions
    assert result.title == "Test Note"
    mock_repo.create.assert_called_once()
```

### 3. Flexibility
```python
# Easy to switch implementations
def get_note_repository(environment: str) -> NoteRepositoryInterface:
    if environment == "testing":
        return MockNoteRepository()
    elif environment == "development":
        return SQLiteNoteRepository()
    else:
        return PostgreSQLNoteRepository()

# Service works with any implementation
repository = get_note_repository(settings.environment)
service = NoteManagementService(repository)
```

## Interface Design Best Practices

### 1. Single Responsibility
```python
# Good: Single responsibility
class UserRepositoryInterface(ABC):
    """Interface for user data access operations."""

    @abstractmethod
    def create(self, data: dict) -> User:
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        pass

# Bad: Multiple responsibilities
class UserManagerInterface(ABC):
    """Interface for user management operations."""

    @abstractmethod
    def create_user(self, data: dict) -> User:
        pass

    @abstractmethod
    def send_email(self, user: User, message: str) -> None:
        pass  # Not related to user management

    @abstractmethod
    def log_activity(self, user: User, activity: str) -> None:
        pass  # Not related to user management
```

### 2. Interface Segregation
```python
# Good: Segregated interfaces
class ReadOnlyRepositoryInterface(ABC):
    """Interface for read-only operations."""

    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[T]:
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        pass

class WriteOnlyRepositoryInterface(ABC):
    """Interface for write-only operations."""

    @abstractmethod
    def create(self, data: dict) -> T:
        pass

    @abstractmethod
    def update(self, entity_id: int, data: dict) -> Optional[T]:
        pass

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        pass

# Bad: Fat interface
class RepositoryInterface(ABC):
    """Interface for all repository operations."""

    @abstractmethod
    def create(self, data: dict) -> T:
        pass

    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[T]:
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        pass

    @abstractmethod
    def update(self, entity_id: int, data: dict) -> Optional[T]:
        pass

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        pass

    @abstractmethod
    def send_email(self, entity: T, message: str) -> None:
        pass  # Not related to repository operations

    @abstractmethod
    def log_activity(self, entity: T, activity: str) -> None:
        pass  # Not related to repository operations
```

### 3. Clear Method Signatures
```python
# Good: Clear method signatures
class UserRepositoryInterface(ABC):
    """Interface for user repository operations."""

    @abstractmethod
    def create_user(
        self,
        user_data: Dict[str, Any]
    ) -> User:
        """
        Create a new user.

        Args:
            user_data: Dictionary containing user data.

        Returns:
            User: The created user entity.

        Raises:
            ValidationError: If user data is invalid.
            ConflictError: If user already exists.
        """
        pass

# Bad: Unclear method signatures
class UserRepositoryInterface(ABC):
    """Interface for user repository operations."""

    @abstractmethod
    def create(self, data) -> Any:  # Unclear types
        pass  # No documentation
```

## Common Interface Issues

### 1. Interface Segregation Violations

❌ **Wrong**: Fat interface
```python
class UserInterface(ABC):
    @abstractmethod
    def create_user(self, user_data: dict) -> User:
        pass

    @abstractmethod
    def get_user(self, user_id: int) -> User:
        pass

    @abstractmethod
    def send_email(self, user: User, message: str) -> None:
        pass  # Not related to user operations

    @abstractmethod
    def log_activity(self, user: User, activity: str) -> None:
        pass  # Not related to user operations
```

✅ **Correct**: Segregated interfaces
```python
class UserRepositoryInterface(ABC):
    @abstractmethod
    def create_user(self, user_data: dict) -> User:
        pass

    @abstractmethod
    def get_user(self, user_id: int) -> User:
        pass

class EmailInterface(ABC):
    @abstractmethod
    def send_email(self, user: User, message: str) -> None:
        pass

class LoggingInterface(ABC):
    @abstractmethod
    def log_activity(self, user: User, activity: str) -> None:
        pass
```

### 2. Missing Abstractions

❌ **Wrong**: Direct dependency on concrete class
```python
class NoteManagementService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.note_repository = NoteRepository(db)  # Direct dependency

    def create_note(self, note_data: NoteCreate) -> Note:
        return self.note_repository.create(note_data.dict())
```

✅ **Correct**: Dependency on abstraction
```python
class NoteManagementService:
    def __init__(self, note_repository: NoteRepositoryInterface) -> None:
        self.note_repository = note_repository  # Depends on interface

    def create_note(self, note_data: NoteCreate) -> Note:
        return self.note_repository.create(note_data.dict())
```

### 3. Inconsistent Interface Design

❌ **Wrong**: Inconsistent interface design
```python
class UserRepositoryInterface(ABC):
    @abstractmethod
    def create_user(self, user_data: dict) -> User:
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> User:  # Inconsistent naming
        pass

    @abstractmethod
    def updateUser(self, user_id: int, user_data: dict) -> User:  # Inconsistent naming
        pass
```

✅ **Correct**: Consistent interface design
```python
class UserRepositoryInterface(ABC):
    @abstractmethod
    def create_user(self, user_data: dict) -> User:
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> User:
        pass

    @abstractmethod
    def update_user(self, user_id: int, user_data: dict) -> User:
        pass
```

## Conclusion

The abstraction and interface design in the Notes App provides:

- **Loose Coupling**: Components depend on abstractions, not concrete implementations
- **Testability**: Easy to test with mock implementations
- **Flexibility**: Easy to substitute implementations
- **Maintainability**: Clear separation of concerns
- **Scalability**: Easy to add new features and implementations
- **Quality**: High-quality, well-designed code

By implementing comprehensive abstractions and interfaces, the Notes App maintains excellent code quality, easy testing, and provides a solid foundation for future development and scaling.
