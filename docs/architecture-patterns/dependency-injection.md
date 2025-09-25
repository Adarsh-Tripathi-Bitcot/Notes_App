# Dependency Injection in Notes App

## Overview

Dependency Injection (DI) is a design pattern that implements Inversion of Control (IoC) for resolving dependencies. In the Notes App, we use DI to create loosely coupled, testable, and maintainable code.

## What is Dependency Injection?

Dependency Injection is a technique where an object receives its dependencies from external sources rather than creating them internally. This promotes:

- **Loose Coupling**: Classes don't create their dependencies
- **Testability**: Easy to mock dependencies for testing
- **Flexibility**: Easy to swap implementations
- **Maintainability**: Changes in dependencies don't affect dependent classes

## DI Implementation in Notes App

### 1. Constructor Injection

The primary method used in our application:

```python
class AuthenticationService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
```

**Benefits**:
- Dependencies are explicit
- Easy to test with mocks
- Clear dependency requirements

### 2. FastAPI Dependency Injection

FastAPI provides built-in DI support through its dependency system:

```python
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_auth_service(db: Session = Depends(get_db)) -> AuthenticationService:
    return AuthenticationService(db)

@router.post("/register")
async def register_user(
    user_data: UserCreate,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    return auth_service.register_user(user_data)
```

## DI Patterns Used

### 1. Service Locator Pattern

```python
# FastAPI dependency injection
def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_note_repository(db: Session = Depends(get_db)) -> NoteRepository:
    return NoteRepository(db)
```

### 2. Factory Pattern

```python
def get_auth_service(db: Session = Depends(get_db)) -> AuthenticationService:
    return AuthenticationService(db)

def get_note_service(db: Session = Depends(get_db)) -> NoteManagementService:
    return NoteManagementService(db)
```

### 3. Repository Pattern with DI

```python
class NoteManagementService:
    def __init__(self, db: Session):
        self.db = db
        self.note_repository = NoteRepository(db)
        self.user_repository = UserRepository(db)
```

## Dependency Graph

```
FastAPI App
    ├── UserRouter
    │   └── AuthenticationService
    │       └── UserRepository
    │           └── Database Session
    └── NotesRouter
        └── NoteManagementService
            ├── NoteRepository
            │   └── Database Session
            └── UserRepository
                └── Database Session
```

## Benefits of DI in Notes App

### 1. Testability

**Without DI (Hard to Test)**:
```python
class AuthenticationService:
    def __init__(self):
        self.db = SessionLocal()  # Hard to mock
        self.user_repository = UserRepository(self.db)
```

**With DI (Easy to Test)**:
```python
class AuthenticationService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)

# In tests
def test_authentication_service():
    mock_db = Mock()
    service = AuthenticationService(mock_db)
    # Easy to test with mock
```

### 2. Loose Coupling

```python
# Service doesn't know about specific database implementation
class AuthenticationService:
    def __init__(self, db: Session):  # Any Session implementation
        self.db = db
```

### 3. Configuration Flexibility

```python
# Different configurations for different environments
def get_auth_service():
    if settings.environment == "testing":
        return AuthenticationService(get_test_db())
    else:
        return AuthenticationService(get_production_db())
```

## DI Container Implementation

### FastAPI as DI Container

FastAPI acts as our DI container, managing the lifecycle of dependencies:

```python
# Dependency definitions
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_auth_service(db: Session = Depends(get_db)) -> AuthenticationService:
    return AuthenticationService(db)

# Usage in endpoints
@router.post("/login")
async def login(
    login_data: UserLogin,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    return auth_service.login_user(login_data)
```

### Dependency Lifecycle Management

1. **Request Start**: FastAPI creates dependencies
2. **Request Processing**: Dependencies are injected into endpoints
3. **Request End**: Dependencies are cleaned up

## Testing with DI

### Unit Testing

```python
@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def auth_service(mock_db):
    return AuthenticationService(mock_db)

def test_register_user(auth_service, mock_db):
    # Test with mocked dependencies
    pass
```

### Integration Testing

```python
@pytest.fixture
def db_session():
    # Real database session for integration tests
    return TestingSessionLocal()

@pytest.fixture
def auth_service(db_session):
    return AuthenticationService(db_session)
```

## Common DI Patterns

### 1. Interface Segregation

```python
class UserRepositoryInterface:
    def create(self, user_data: dict) -> User:
        pass

    def get_by_id(self, user_id: int) -> Optional[User]:
        pass

class UserRepository(UserRepositoryInterface):
    def create(self, user_data: dict) -> User:
        # Implementation
        pass
```

### 2. Abstract Base Classes

```python
from abc import ABC, abstractmethod

class BaseRepository(ABC):
    def __init__(self, db: Session):
        self.db = db

    @abstractmethod
    def create(self, data: dict):
        pass
```

### 3. Configuration Injection

```python
class AuthenticationService:
    def __init__(self, db: Session, config: Settings):
        self.db = db
        self.config = config
        self.jwt_secret = config.jwt_secret_key
```

## Best Practices

### 1. Explicit Dependencies

```python
# Good: Explicit dependencies
class AuthenticationService:
    def __init__(self, db: Session, user_repo: UserRepository):
        self.db = db
        self.user_repo = user_repo

# Bad: Hidden dependencies
class AuthenticationService:
    def __init__(self):
        self.db = SessionLocal()  # Hidden dependency
```

### 2. Single Responsibility

```python
# Good: Each dependency has one responsibility
class AuthenticationService:
    def __init__(self, db: Session, password_hasher: PasswordHasher):
        self.db = db
        self.password_hasher = password_hasher

# Bad: Multiple responsibilities
class AuthenticationService:
    def __init__(self, db: Session, email_service: EmailService, logger: Logger):
        # Too many responsibilities
```

### 3. Interface-Based Design

```python
# Good: Depend on interfaces, not implementations
class AuthenticationService:
    def __init__(self, user_repo: UserRepositoryInterface):
        self.user_repo = user_repo
```

## Common Pitfalls

### 1. Service Locator Anti-Pattern

❌ **Wrong**: Using global service locator
```python
class AuthenticationService:
    def register_user(self, user_data):
        db = ServiceLocator.get_database()  # Anti-pattern
        user_repo = ServiceLocator.get_user_repository()
```

✅ **Correct**: Constructor injection
```python
class AuthenticationService:
    def __init__(self, db: Session, user_repo: UserRepository):
        self.db = db
        self.user_repo = user_repo
```

### 2. Circular Dependencies

❌ **Wrong**: Circular dependency
```python
class UserService:
    def __init__(self, note_service: NoteService):
        self.note_service = note_service

class NoteService:
    def __init__(self, user_service: UserService):  # Circular!
        self.user_service = user_service
```

✅ **Correct**: Break circular dependency
```python
class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

class NoteService:
    def __init__(self, note_repo: NoteRepository, user_repo: UserRepository):
        self.note_repo = note_repo
        self.user_repo = user_repo
```

### 3. Over-Injection

❌ **Wrong**: Too many dependencies
```python
class AuthenticationService:
    def __init__(self, db, logger, config, email_service, cache, metrics):
        # Too many dependencies
```

✅ **Correct**: Reasonable number of dependencies
```python
class AuthenticationService:
    def __init__(self, db: Session, config: Settings):
        self.db = db
        self.config = config
```

## Performance Considerations

### 1. Dependency Creation

```python
# FastAPI caches dependencies by default
def get_auth_service(db: Session = Depends(get_db)) -> AuthenticationService:
    return AuthenticationService(db)  # Created once per request
```

### 2. Memory Management

```python
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db  # Generator ensures cleanup
    finally:
        db.close()
```

## Conclusion

Dependency Injection in the Notes App provides:

- **Testability**: Easy to mock dependencies for testing
- **Flexibility**: Easy to swap implementations
- **Maintainability**: Clear dependency relationships
- **Loose Coupling**: Classes don't create their dependencies
- **Configuration**: Easy to configure for different environments

By following DI best practices, the Notes App maintains high code quality, testability, and maintainability while providing a flexible architecture for future development.
