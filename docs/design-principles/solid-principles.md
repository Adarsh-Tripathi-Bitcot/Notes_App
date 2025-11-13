# SOLID Principles in Notes App

## Overview

The Notes App strictly adheres to the SOLID principles of object-oriented design, ensuring maintainable, scalable, and robust code. This document explains how each SOLID principle is implemented throughout the application.

## SOLID Principles

### 1. Single Responsibility Principle (SRP)

**Definition**: A class should have only one reason to change.

#### Implementation in Notes App

##### User Repository
```python
class UserRepository:
    """Single responsibility: User data access operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

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

**Why this follows SRP**:
- Only handles user data access operations
- Single reason to change: changes to user data access logic
- No business logic or presentation concerns

##### Authentication Service
```python
class AuthenticationService:
    """Single responsibility: User authentication and authorization."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repository = UserRepository(db)

    def register_user(self, user_data: UserCreate) -> User:
        """Register a new user."""
        pass

    def login_user(self, login_data: UserLogin) -> TokenResponse:
        """Authenticate user and return token."""
        pass

    def verify_token(self, token: str) -> Optional[User]:
        """Verify JWT token."""
        pass

    def hash_password(self, password: str) -> str:
        """Hash password using BCrypt."""
        pass

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash."""
        pass
```

**Why this follows SRP**:
- Only handles authentication and authorization
- Single reason to change: changes to authentication logic
- No data access or presentation concerns

### 2. Open/Closed Principle (OCP)

**Definition**: Software entities should be open for extension but closed for modification.

#### Implementation in Notes App

##### Base Repository Pattern
```python
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List, Dict, Any

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """Base repository that is open for extension but closed for modification."""

    def __init__(self, db: Session, model_class: type[T]) -> None:
        self.db = db
        self.model_class = model_class

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> T:
        """Create a new entity."""
        pass

    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """Get entity by ID."""
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities."""
        pass

    @abstractmethod
    def update(self, entity_id: int, data: Dict[str, Any]) -> Optional[T]:
        """Update entity."""
        pass

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Delete entity."""
        pass

class UserRepository(BaseRepository[User]):
    """User repository extending base repository."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, User)

    def create(self, data: Dict[str, Any]) -> User:
        """Create a new user."""
        # Implementation
        pass

    def get_by_id(self, entity_id: int) -> Optional[User]:
        """Get user by ID."""
        # Implementation
        pass

    # ... other methods

class NoteRepository(BaseRepository[Note]):
    """Note repository extending base repository."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, Note)

    def create(self, data: Dict[str, Any]) -> Note:
        """Create a new note."""
        # Implementation
        pass

    # ... other methods
```

**Why this follows OCP**:
- Base repository is closed for modification
- New repositories can extend base repository
- No need to modify existing code to add new entities

##### Service Layer Extension
```python
class BaseService(ABC):
    """Base service that is open for extension but closed for modification."""

    def __init__(self, db: Session) -> None:
        self.db = db

    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> None:
        """Validate input data."""
        pass

    @abstractmethod
    def process_data(self, data: Dict[str, Any]) -> Any:
        """Process input data."""
        pass

class AuthenticationService(BaseService):
    """Authentication service extending base service."""

    def validate_data(self, data: Dict[str, Any]) -> None:
        """Validate authentication data."""
        # Implementation
        pass

    def process_data(self, data: Dict[str, Any]) -> Any:
        """Process authentication data."""
        # Implementation
        pass

class NoteManagementService(BaseService):
    """Note management service extending base service."""

    def validate_data(self, data: Dict[str, Any]) -> None:
        """Validate note data."""
        # Implementation
        pass

    def process_data(self, data: Dict[str, Any]) -> Any:
        """Process note data."""
        # Implementation
        pass
```

### 3. Liskov Substitution Principle (LSP)

**Definition**: Objects of a superclass should be replaceable with objects of a subclass without breaking the application.

#### Implementation in Notes App

##### Repository Substitution
```python
def process_entities(repository: BaseRepository[User]) -> List[User]:
    """Process entities using any repository that extends BaseRepository."""
    return repository.get_all()

# All of these work without breaking the application
user_repo = UserRepository(db)
note_repo = NoteRepository(db)

# User repository can be substituted
users = process_entities(user_repo)

# Note repository can be substituted (if it extends BaseRepository[Note])
notes = process_entities(note_repo)
```

##### Service Substitution
```python
def process_service_data(service: BaseService, data: Dict[str, Any]) -> Any:
    """Process data using any service that extends BaseService."""
    service.validate_data(data)
    return service.process_data(data)

# All services can be substituted
auth_service = AuthenticationService(db)
note_service = NoteManagementService(db)

# Authentication service can be substituted
result1 = process_service_data(auth_service, auth_data)

# Note service can be substituted
result2 = process_service_data(note_service, note_data)
```

##### Exception Hierarchy
```python
class NotesAppException(Exception):
    """Base exception that can be substituted by any subclass."""

    def __init__(self, message: str, error_code: Optional[str] = None) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code

class ValidationError(NotesAppException):
    """Validation error that can be substituted for base exception."""

    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(message, "VALIDATION_ERROR")

class AuthenticationError(NotesAppException):
    """Authentication error that can be substituted for base exception."""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message, "AUTHENTICATION_ERROR")

# All exceptions can be substituted
def handle_exception(exc: NotesAppException) -> str:
    """Handle any exception that extends NotesAppException."""
    return f"Error: {exc.message} (Code: {exc.error_code})"

# These all work without breaking the application
handle_exception(ValidationError("Invalid input"))
handle_exception(AuthenticationError("Invalid credentials"))
```

### 4. Interface Segregation Principle (ISP)

**Definition**: Clients should not be forced to depend on interfaces they don't use.

#### Implementation in Notes App

##### Segregated Repository Interfaces
```python
class ReadOnlyRepository(ABC):
    """Interface for read-only operations."""

    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """Get entity by ID."""
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities."""
        pass

class WriteOnlyRepository(ABC):
    """Interface for write-only operations."""

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> T:
        """Create a new entity."""
        pass

    @abstractmethod
    def update(self, entity_id: int, data: Dict[str, Any]) -> Optional[T]:
        """Update entity."""
        pass

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Delete entity."""
        pass

class FullRepository(ReadOnlyRepository, WriteOnlyRepository):
    """Interface for full CRUD operations."""
    pass

class UserRepository(FullRepository[User]):
    """User repository implementing full interface."""

    def get_by_id(self, entity_id: int) -> Optional[User]:
        """Get user by ID."""
        pass

    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users."""
        pass

    def create(self, data: Dict[str, Any]) -> User:
        """Create a new user."""
        pass

    def update(self, entity_id: int, data: Dict[str, Any]) -> Optional[User]:
        """Update user."""
        pass

    def delete(self, entity_id: int) -> bool:
        """Delete user."""
        pass
```

**Why this follows ISP**:
- Clients can depend only on the interfaces they need
- Read-only clients don't need write operations
- Write-only clients don't need read operations

##### Segregated Service Interfaces
```python
class AuthenticationInterface(ABC):
    """Interface for authentication operations."""

    @abstractmethod
    def login_user(self, login_data: UserLogin) -> TokenResponse:
        """Login user."""
        pass

    @abstractmethod
    def verify_token(self, token: str) -> Optional[User]:
        """Verify token."""
        pass

class UserManagementInterface(ABC):
    """Interface for user management operations."""

    @abstractmethod
    def register_user(self, user_data: UserCreate) -> User:
        """Register user."""
        pass

    @abstractmethod
    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Update user."""
        pass

class AuthenticationService(AuthenticationInterface, UserManagementInterface):
    """Service implementing both interfaces."""

    def login_user(self, login_data: UserLogin) -> TokenResponse:
        """Login user."""
        pass

    def verify_token(self, token: str) -> Optional[User]:
        """Verify token."""
        pass

    def register_user(self, user_data: UserCreate) -> User:
        """Register user."""
        pass

    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Update user."""
        pass
```

### 5. Dependency Inversion Principle (DIP)

**Definition**: High-level modules should not depend on low-level modules. Both should depend on abstractions.

#### Implementation in Notes App

##### Service Layer Dependencies
```python
# High-level module (Service) depends on abstraction (Repository Interface)
class AuthenticationService:
    """High-level module that depends on abstractions."""

    def __init__(self, user_repository: UserRepositoryInterface) -> None:
        self.user_repository = user_repository  # Depends on abstraction

    def register_user(self, user_data: UserCreate) -> User:
        """Register user using repository abstraction."""
        return self.user_repository.create(user_data.dict())

# Low-level module (Repository) implements abstraction
class UserRepository(UserRepositoryInterface):
    """Low-level module that implements abstraction."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, user_data: dict) -> User:
        """Create user in database."""
        # Implementation
        pass

# Both depend on the same abstraction
class UserRepositoryInterface(ABC):
    """Abstraction that both high and low-level modules depend on."""

    @abstractmethod
    def create(self, user_data: dict) -> User:
        """Create user."""
        pass
```

##### API Layer Dependencies
```python
# High-level module (API) depends on abstraction (Service Interface)
@router.post("/register")
async def register_user(
    user_data: UserCreate,
    auth_service: AuthenticationServiceInterface = Depends(get_auth_service)
) -> UserResponse:
    """Register user using service abstraction."""
    return auth_service.register_user(user_data)

# Service implements abstraction
class AuthenticationService(AuthenticationServiceInterface):
    """Service that implements abstraction."""

    def register_user(self, user_data: UserCreate) -> User:
        """Register user."""
        # Implementation
        pass

# Both depend on the same abstraction
class AuthenticationServiceInterface(ABC):
    """Abstraction that both API and Service depend on."""

    @abstractmethod
    def register_user(self, user_data: UserCreate) -> User:
        """Register user."""
        pass
```

##### Database Dependencies
```python
# High-level module (Service) depends on abstraction (Database Interface)
class NoteManagementService:
    """High-level module that depends on database abstraction."""

    def __init__(self, db: DatabaseInterface) -> None:
        self.db = db  # Depends on abstraction

    def create_note(self, note_data: NoteCreate) -> Note:
        """Create note using database abstraction."""
        return self.db.create_note(note_data)

# Low-level module (Database) implements abstraction
class PostgreSQLDatabase(DatabaseInterface):
    """Low-level module that implements database abstraction."""

    def create_note(self, note_data: NoteCreate) -> Note:
        """Create note in PostgreSQL."""
        # Implementation
        pass

# Both depend on the same abstraction
class DatabaseInterface(ABC):
    """Abstraction that both high and low-level modules depend on."""

    @abstractmethod
    def create_note(self, note_data: NoteCreate) -> Note:
        """Create note."""
        pass
```

## SOLID Principles Benefits

### 1. Maintainability
- **Single Responsibility**: Easy to understand and modify individual components
- **Open/Closed**: Easy to extend functionality without modifying existing code
- **Liskov Substitution**: Easy to replace implementations without breaking functionality
- **Interface Segregation**: Easy to modify interfaces without affecting unrelated clients
- **Dependency Inversion**: Easy to change implementations without affecting high-level modules

### 2. Testability
- **Single Responsibility**: Easy to test individual components in isolation
- **Open/Closed**: Easy to test new functionality without affecting existing tests
- **Liskov Substitution**: Easy to test with mock implementations
- **Interface Segregation**: Easy to test with minimal mock interfaces
- **Dependency Inversion**: Easy to test with mock dependencies

### 3. Scalability
- **Single Responsibility**: Easy to scale individual components
- **Open/Closed**: Easy to add new features without affecting existing code
- **Liskov Substitution**: Easy to swap implementations for different environments
- **Interface Segregation**: Easy to scale specific functionality
- **Dependency Inversion**: Easy to scale with different implementations

### 4. Flexibility
- **Single Responsibility**: Easy to change individual components
- **Open/Closed**: Easy to add new functionality
- **Liskov Substitution**: Easy to replace implementations
- **Interface Segregation**: Easy to change specific functionality
- **Dependency Inversion**: Easy to change implementations

## SOLID Principles Testing

### 1. Single Responsibility Testing
```python
def test_user_repository_single_responsibility():
    """Test that UserRepository only handles user data access."""
    repo = UserRepository(mock_db)

    # Test that it can handle user data access
    user = repo.create(user_data)
    assert isinstance(user, User)

    # Test that it doesn't handle business logic
    with pytest.raises(AttributeError):
        repo.validate_password("password")
```

### 2. Open/Closed Testing
```python
def test_repository_extension():
    """Test that repositories can be extended without modification."""
    # Test base repository
    base_repo = BaseRepository(mock_db, User)

    # Test extended repository
    user_repo = UserRepository(mock_db)

    # Both should work with the same interface
    assert hasattr(base_repo, 'create')
    assert hasattr(user_repo, 'create')
```

### 3. Liskov Substitution Testing
```python
def test_repository_substitution():
    """Test that repositories can be substituted."""
    def process_repository(repo: BaseRepository[User]) -> List[User]:
        return repo.get_all()

    # Test with different repository implementations
    user_repo = UserRepository(mock_db)
    note_repo = NoteRepository(mock_db)

    # Both should work without breaking the application
    users = process_repository(user_repo)
    notes = process_repository(note_repo)

    assert isinstance(users, list)
    assert isinstance(notes, list)
```

### 4. Interface Segregation Testing
```python
def test_interface_segregation():
    """Test that clients only depend on interfaces they use."""
    # Test read-only client
    read_only_client = ReadOnlyClient(UserRepository(mock_db))
    users = read_only_client.get_users()

    # Test write-only client
    write_only_client = WriteOnlyClient(UserRepository(mock_db))
    user = write_only_client.create_user(user_data)

    # Both should work with their specific interfaces
    assert isinstance(users, list)
    assert isinstance(user, User)
```

### 5. Dependency Inversion Testing
```python
def test_dependency_inversion():
    """Test that high-level modules depend on abstractions."""
    # Test with mock repository
    mock_repo = Mock(spec=UserRepositoryInterface)
    mock_repo.create.return_value = User(id=1, email="test@example.com")

    # Test service with mock repository
    service = AuthenticationService(mock_repo)
    user = service.register_user(user_data)

    # Service should work with any repository that implements the interface
    assert isinstance(user, User)
    mock_repo.create.assert_called_once()
```

## Common SOLID Violations

### 1. Single Responsibility Violations

❌ **Wrong**: Multiple responsibilities
```python
class UserManager:
    def create_user(self, user_data: dict) -> User:
        # User creation logic
        pass

    def send_email(self, user: User, message: str) -> None:
        # Email sending logic
        pass

    def log_activity(self, user: User, activity: str) -> None:
        # Logging logic
        pass
```

✅ **Correct**: Single responsibility
```python
class UserRepository:
    def create_user(self, user_data: dict) -> User:
        # User creation logic only
        pass

class EmailService:
    def send_email(self, user: User, message: str) -> None:
        # Email sending logic only
        pass

class LoggingService:
    def log_activity(self, user: User, activity: str) -> None:
        # Logging logic only
        pass
```

### 2. Open/Closed Violations

❌ **Wrong**: Modification required for extension
```python
class UserService:
    def process_user(self, user_data: dict, user_type: str) -> User:
        if user_type == "admin":
            # Admin logic
            pass
        elif user_type == "regular":
            # Regular user logic
            pass
        elif user_type == "premium":
            # Premium user logic
            pass
```

✅ **Correct**: Open for extension, closed for modification
```python
class BaseUserProcessor(ABC):
    @abstractmethod
    def process_user(self, user_data: dict) -> User:
        pass

class AdminUserProcessor(BaseUserProcessor):
    def process_user(self, user_data: dict) -> User:
        # Admin logic
        pass

class RegularUserProcessor(BaseUserProcessor):
    def process_user(self, user_data: dict) -> User:
        # Regular user logic
        pass

class PremiumUserProcessor(BaseUserProcessor):
    def process_user(self, user_data: dict) -> User:
        # Premium user logic
        pass
```

### 3. Liskov Substitution Violations

❌ **Wrong**: Subclass changes behavior
```python
class Rectangle:
    def set_width(self, width: int) -> None:
        self.width = width

    def set_height(self, height: int) -> None:
        self.height = height

class Square(Rectangle):
    def set_width(self, width: int) -> None:
        self.width = width
        self.height = width  # Changes behavior

    def set_height(self, height: int) -> None:
        self.height = height
        self.width = height  # Changes behavior
```

✅ **Correct**: Subclass maintains behavior
```python
class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass

class Rectangle(Shape):
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

class Square(Shape):
    def __init__(self, side: int) -> None:
        self.side = side

    def area(self) -> float:
        return self.side * self.side
```

### 4. Interface Segregation Violations

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
        pass

    @abstractmethod
    def log_activity(self, user: User, activity: str) -> None:
        pass
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

### 5. Dependency Inversion Violations

❌ **Wrong**: High-level module depends on low-level module
```python
class UserService:
    def __init__(self) -> None:
        self.db = PostgreSQLDatabase()  # Depends on concrete class

    def create_user(self, user_data: dict) -> User:
        return self.db.create_user(user_data)
```

✅ **Correct**: Both depend on abstraction
```python
class UserService:
    def __init__(self, db: DatabaseInterface) -> None:
        self.db = db  # Depends on abstraction

    def create_user(self, user_data: dict) -> User:
        return self.db.create_user(user_data)

class PostgreSQLDatabase(DatabaseInterface):
    def create_user(self, user_data: dict) -> User:
        # Implementation
        pass
```

## Conclusion

The SOLID principles in the Notes App provide:

- **Maintainability**: Easy to understand, modify, and extend code
- **Testability**: Easy to test individual components and their interactions
- **Scalability**: Easy to scale and add new functionality
- **Flexibility**: Easy to change implementations and add new features
- **Quality**: High-quality, robust, and reliable code
- **Team Collaboration**: Clear separation of concerns and responsibilities

By strictly adhering to SOLID principles, the Notes App maintains high code quality, excellent maintainability, and provides a solid foundation for future development and scaling.
