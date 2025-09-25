# Repository Pattern in Notes App

## Overview

The Repository Pattern is a design pattern that abstracts data access logic and provides a more object-oriented view of the persistence layer. In the Notes App, we use this pattern to create a clean separation between business logic and data access.

## What is the Repository Pattern?

The Repository Pattern encapsulates the logic needed to access data sources, centralizing common data access functionality, providing better maintainability, and decoupling the infrastructure or technology used to access databases from the domain model layer.

## Benefits

- **Abstraction**: Hides data access implementation details
- **Testability**: Easy to mock for unit testing
- **Flexibility**: Easy to change data sources
- **Consistency**: Standardized data access patterns
- **Maintainability**: Centralized data access logic

## Repository Pattern Implementation

### 1. Base Repository Interface

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

T = TypeVar('T')

class BaseRepository(ABC):
    """Base repository interface for common CRUD operations."""

    @abstractmethod
    def create(self, data: dict) -> T:
        """Create a new entity."""
        pass

    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """Get entity by ID."""
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination."""
        pass

    @abstractmethod
    def update(self, entity_id: int, data: dict) -> Optional[T]:
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
```

### 2. User Repository Implementation

```python
class UserRepository:
    """Repository for user-related database operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, user_data: dict) -> User:
        """Create a new user."""
        try:
            user = User(**user_data)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError as e:
            self.db.rollback()
            raise ConflictError("User with this email already exists")

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db.query(User).filter(User.username == username).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """Get all users with optional filtering."""
        query = self.db.query(User)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        return query.offset(skip).limit(limit).all()

    def update(self, user_id: int, update_data: dict) -> Optional[User]:
        """Update user by ID."""
        user = self.get_by_id(user_id)
        if not user:
            return None

        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: int) -> bool:
        """Delete user by ID."""
        user = self.get_by_id(user_id)
        if not user:
            return False

        self.db.delete(user)
        self.db.commit()
        return True

    def exists(self, user_id: int) -> bool:
        """Check if user exists."""
        return self.db.query(User).filter(User.id == user_id).first() is not None

    def count(self, is_active: Optional[bool] = None) -> int:
        """Count users with optional filtering."""
        query = self.db.query(User)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        return query.count()
```

### 3. Note Repository Implementation

```python
class NoteRepository:
    """Repository for note-related database operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, note_data: dict) -> Note:
        """Create a new note."""
        try:
            note = Note(**note_data)
            self.db.add(note)
            self.db.commit()
            self.db.refresh(note)
            return note
        except Exception as e:
            self.db.rollback()
            raise DatabaseError("Failed to create note")

    def get_by_id(self, note_id: int, owner_id: Optional[int] = None) -> Optional[Note]:
        """Get note by ID with optional owner filtering."""
        query = self.db.query(Note).filter(Note.id == note_id)

        if owner_id is not None:
            query = query.filter(Note.owner_id == owner_id)

        return query.first()

    def get_by_owner(
        self,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[NoteStatus] = None,
        search_query: Optional[str] = None
    ) -> List[Note]:
        """Get notes by owner with filtering and pagination."""
        query = self.db.query(Note).filter(Note.owner_id == owner_id)

        if status is not None:
            query = query.filter(Note.status == status)

        if search_query:
            search_filter = or_(
                Note.title.ilike(f"%{search_query}%"),
                Note.content.ilike(f"%{search_query}%")
            )
            query = query.filter(search_filter)

        return query.offset(skip).limit(limit).all()

    def get_public_notes(
        self,
        skip: int = 0,
        limit: int = 100,
        search_query: Optional[str] = None
    ) -> List[Note]:
        """Get public notes with filtering and pagination."""
        query = self.db.query(Note).filter(
            and_(Note.is_public == True, Note.status == NoteStatus.ACTIVE)
        )

        if search_query:
            search_filter = or_(
                Note.title.ilike(f"%{search_query}%"),
                Note.content.ilike(f"%{search_query}%")
            )
            query = query.filter(search_filter)

        return query.offset(skip).limit(limit).all()

    def update(self, note_id: int, update_data: dict, owner_id: Optional[int] = None) -> Optional[Note]:
        """Update note by ID with optional owner filtering."""
        note = self.get_by_id(note_id, owner_id)
        if not note:
            return None

        for field, value in update_data.items():
            if hasattr(note, field):
                setattr(note, field, value)

        self.db.commit()
        self.db.refresh(note)
        return note

    def delete(self, note_id: int, owner_id: Optional[int] = None) -> bool:
        """Soft delete note by ID."""
        note = self.get_by_id(note_id, owner_id)
        if not note:
            return False

        note.status = NoteStatus.DELETED
        self.db.commit()
        return True

    def exists(self, note_id: int, owner_id: Optional[int] = None) -> bool:
        """Check if note exists."""
        query = self.db.query(Note).filter(Note.id == note_id)

        if owner_id is not None:
            query = query.filter(Note.owner_id == owner_id)

        return query.first() is not None

    def count_by_owner(
        self,
        owner_id: int,
        status: Optional[NoteStatus] = None,
        search_query: Optional[str] = None
    ) -> int:
        """Count notes by owner with filtering."""
        query = self.db.query(Note).filter(Note.owner_id == owner_id)

        if status is not None:
            query = query.filter(Note.status == status)

        if search_query:
            search_filter = or_(
                Note.title.ilike(f"%{search_query}%"),
                Note.content.ilike(f"%{search_query}%")
            )
            query = query.filter(search_filter)

        return query.count()

    def get_stats(self, owner_id: int) -> dict:
        """Get note statistics for owner."""
        total_notes = self.db.query(Note).filter(Note.owner_id == owner_id).count()
        active_notes = self.db.query(Note).filter(
            and_(Note.owner_id == owner_id, Note.status == NoteStatus.ACTIVE)
        ).count()
        archived_notes = self.db.query(Note).filter(
            and_(Note.owner_id == owner_id, Note.status == NoteStatus.ARCHIVED)
        ).count()

        return {
            "total_notes": total_notes,
            "active_notes": active_notes,
            "archived_notes": archived_notes,
        }
```

## Repository Pattern Benefits in Notes App

### 1. Data Access Abstraction

```python
# Service layer doesn't know about SQLAlchemy specifics
class AuthenticationService:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)

    def get_user(self, user_id: int) -> Optional[User]:
        return self.user_repository.get_by_id(user_id)
```

### 2. Easy Testing

```python
# Easy to mock repository for testing
def test_authentication_service():
    mock_repo = Mock(spec=UserRepository)
    mock_repo.get_by_id.return_value = User(id=1, email="test@example.com")

    service = AuthenticationService(mock_repo)
    user = service.get_user(1)

    assert user.email == "test@example.com"
    mock_repo.get_by_id.assert_called_once_with(1)
```

### 3. Consistent Data Access

```python
# All repositories follow the same pattern
class UserRepository:
    def create(self, data: dict) -> User: pass
    def get_by_id(self, id: int) -> Optional[User]: pass
    def update(self, id: int, data: dict) -> Optional[User]: pass
    def delete(self, id: int) -> bool: pass

class NoteRepository:
    def create(self, data: dict) -> Note: pass
    def get_by_id(self, id: int) -> Optional[Note]: pass
    def update(self, id: int, data: dict) -> Optional[Note]: pass
    def delete(self, id: int) -> bool: pass
```

## Advanced Repository Patterns

### 1. Generic Repository

```python
class GenericRepository(Generic[T]):
    def __init__(self, db: Session, model_class: Type[T]):
        self.db = db
        self.model_class = model_class

    def create(self, data: dict) -> T:
        entity = self.model_class(**data)
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def get_by_id(self, entity_id: int) -> Optional[T]:
        return self.db.query(self.model_class).filter(
            self.model_class.id == entity_id
        ).first()
```

### 2. Specification Pattern

```python
class UserSpecification:
    def __init__(self, is_active: Optional[bool] = None, is_verified: Optional[bool] = None):
        self.is_active = is_active
        self.is_verified = is_verified

    def to_query(self, query):
        if self.is_active is not None:
            query = query.filter(User.is_active == self.is_active)
        if self.is_verified is not None:
            query = query.filter(User.is_verified == self.is_verified)
        return query

class UserRepository:
    def find_by_specification(self, spec: UserSpecification) -> List[User]:
        query = self.db.query(User)
        query = spec.to_query(query)
        return query.all()
```

### 3. Unit of Work Pattern

```python
class UnitOfWork:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.note_repository = NoteRepository(db)

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()
```

## Error Handling in Repositories

### 1. Database Errors

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
            if "email" in str(e.orig):
                raise ConflictError("User with this email already exists")
            raise DatabaseError("Failed to create user")
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Unexpected error: {str(e)}")
```

### 2. Custom Exceptions

```python
class RepositoryError(Exception):
    """Base exception for repository errors."""
    pass

class ConflictError(RepositoryError):
    """Raised when a conflict occurs (e.g., duplicate email)."""
    pass

class NotFoundError(RepositoryError):
    """Raised when an entity is not found."""
    pass

class DatabaseError(RepositoryError):
    """Raised when a database operation fails."""
    pass
```

## Performance Considerations

### 1. Query Optimization

```python
class UserRepository:
    def get_user_with_notes(self, user_id: int) -> Optional[User]:
        """Get user with eager loading of notes."""
        return self.db.query(User).options(
            joinedload(User.notes)
        ).filter(User.id == user_id).first()
```

### 2. Pagination

```python
class NoteRepository:
    def get_notes_paginated(
        self,
        owner_id: int,
        page: int = 1,
        per_page: int = 10
    ) -> Tuple[List[Note], int]:
        """Get paginated notes with total count."""
        query = self.db.query(Note).filter(Note.owner_id == owner_id)

        total = query.count()
        notes = query.offset((page - 1) * per_page).limit(per_page).all()

        return notes, total
```

### 3. Bulk Operations

```python
class NoteRepository:
    def bulk_update_status(
        self,
        note_ids: List[int],
        status: NoteStatus
    ) -> int:
        """Bulk update note status."""
        updated_count = self.db.query(Note).filter(
            Note.id.in_(note_ids)
        ).update(
            {"status": status},
            synchronize_session=False
        )

        self.db.commit()
        return updated_count
```

## Testing Repositories

### 1. Unit Testing

```python
def test_user_repository_create():
    # Setup
    db = create_test_db()
    repo = UserRepository(db)
    user_data = {"email": "test@example.com", "username": "testuser"}

    # Execute
    user = repo.create(user_data)

    # Assert
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.id is not None
```

### 2. Integration Testing

```python
def test_user_repository_integration():
    # Setup
    db = create_test_db()
    repo = UserRepository(db)

    # Create user
    user = repo.create({"email": "test@example.com"})

    # Retrieve user
    retrieved_user = repo.get_by_id(user.id)

    # Assert
    assert retrieved_user.email == "test@example.com"
```

## Best Practices

### 1. Single Responsibility

```python
# Good: Each repository handles one entity type
class UserRepository:
    def create_user(self, data: dict) -> User: pass

class NoteRepository:
    def create_note(self, data: dict) -> Note: pass

# Bad: One repository handling multiple entities
class DataRepository:
    def create_user(self, data: dict) -> User: pass
    def create_note(self, data: dict) -> Note: pass
```

### 2. Consistent Interface

```python
# All repositories should have consistent method signatures
class BaseRepository:
    def create(self, data: dict) -> T: pass
    def get_by_id(self, id: int) -> Optional[T]: pass
    def update(self, id: int, data: dict) -> Optional[T]: pass
    def delete(self, id: int) -> bool: pass
```

### 3. Error Handling

```python
# Always handle database errors appropriately
def create(self, data: dict) -> T:
    try:
        # Database operation
        pass
    except IntegrityError:
        self.db.rollback()
        raise ConflictError("Entity already exists")
    except Exception:
        self.db.rollback()
        raise DatabaseError("Operation failed")
```

## Conclusion

The Repository Pattern in the Notes App provides:

- **Clean Separation**: Business logic is separated from data access
- **Testability**: Easy to mock repositories for testing
- **Consistency**: Standardized data access patterns
- **Maintainability**: Centralized data access logic
- **Flexibility**: Easy to change data sources

By implementing the Repository Pattern, the Notes App maintains clean architecture principles while providing a robust and maintainable data access layer.
