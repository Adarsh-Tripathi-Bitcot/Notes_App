# Service Layer Design in Notes App

## Overview

The Service Layer in the Notes App acts as the business logic layer, orchestrating operations between the API layer and the data access layer. It encapsulates business rules, validation, and coordination logic while maintaining clean separation of concerns.

## What is the Service Layer?

The Service Layer is a design pattern that encapsulates business logic and provides a clean interface for the presentation layer (API) to interact with the data access layer (Repositories). It serves as the middle layer in the Clean Architecture pattern.

## Benefits of Service Layer

- **Business Logic Centralization**: All business rules in one place
- **Reusability**: Services can be used by multiple API endpoints
- **Testability**: Easy to unit test business logic
- **Maintainability**: Changes to business logic don't affect other layers
- **Transaction Management**: Handle complex business operations
- **Validation**: Centralized input validation and business rules

## Service Layer Architecture

```
API Layer (Controllers)
    ↓
Service Layer (Business Logic)
    ↓
Repository Layer (Data Access)
    ↓
Database Layer
```

## Service Layer Implementation

### 1. Authentication Service

```python
class AuthenticationService:
    """Service for user authentication and authorization."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)

    def register_user(self, user_data: UserCreate) -> User:
        """Register a new user with business validation."""
        # Business rule: Check if user already exists
        existing_user = self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise ValidationError("User with this email already exists")

        # Business rule: Validate password strength
        if not self._validate_password_strength(user_data.password):
            raise ValidationError("Password does not meet strength requirements")

        # Business rule: Hash password
        hashed_password = self.get_password_hash(user_data.password)

        # Create user with business logic
        user_dict = {
            "email": user_data.email,
            "username": user_data.username,
            "hashed_password": hashed_password,
            "is_active": True,
            "is_verified": False,
        }

        return self.user_repository.create(user_dict)

    def authenticate_user(self, login_data: UserLogin) -> Optional[User]:
        """Authenticate user with business rules."""
        # Get user by email
        user = self.user_repository.get_by_email(login_data.email)
        if not user:
            return None

        # Business rule: Check if user is active
        if not user.is_active:
            return None

        # Business rule: Verify password
        if not self.verify_password(login_data.password, user.hashed_password):
            return None

        # Business rule: Update last login
        user.update_last_login()
        self.db.commit()

        return user

    def login_user(self, login_data: UserLogin) -> TokenResponse:
        """Login user and return JWT token."""
        user = self.authenticate_user(login_data)
        if not user:
            raise AuthenticationError("Invalid email or password")

        # Business rule: Create JWT token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
        }

        access_token = self.create_access_token(token_data)
        expires_in = settings.jwt_expiry_minutes * 60

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in
        )

    def _validate_password_strength(self, password: str) -> bool:
        """Validate password strength according to business rules."""
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

### 2. Note Management Service

```python
class NoteManagementService:
    """Service for note management operations."""

    def __init__(self, db: Session):
        self.db = db
        self.note_repository = NoteRepository(db)

    def create_note(self, note_data: NoteCreate, owner_id: int) -> Note:
        """Create a new note with business validation."""
        # Business rule: Validate note content
        if not note_data.title.strip():
            raise ValidationError("Note title cannot be empty")

        if not note_data.content.strip():
            raise ValidationError("Note content cannot be empty")

        # Business rule: Auto-generate summary if not provided
        summary = note_data.summary
        if not summary:
            summary = self._generate_summary(note_data.content)

        # Business rule: Set default status
        note_dict = {
            "title": note_data.title,
            "content": note_data.content,
            "summary": summary,
            "is_public": note_data.is_public,
            "is_pinned": note_data.is_pinned,
            "owner_id": owner_id,
            "status": NoteStatus.ACTIVE,
        }

        return self.note_repository.create(note_dict)

    def update_note(self, note_id: int, note_data: NoteUpdate, owner_id: int) -> Optional[Note]:
        """Update note with business validation."""
        # Business rule: Check ownership
        note = self.note_repository.get_by_id(note_id, owner_id)
        if not note:
            raise NotFoundError("Note not found")

        # Business rule: Validate updates
        update_data = {}
        for field, value in note_data.dict(exclude_unset=True).items():
            if value is not None:
                if field == "title" and not value.strip():
                    raise ValidationError("Note title cannot be empty")
                if field == "content" and not value.strip():
                    raise ValidationError("Note content cannot be empty")
                update_data[field] = value

        # Business rule: Auto-generate summary if content is updated
        if "content" in update_data and "summary" not in update_data:
            update_data["summary"] = self._generate_summary(update_data["content"])

        return self.note_repository.update(note_id, update_data, owner_id)

    def delete_note(self, note_id: int, owner_id: int) -> bool:
        """Delete note with business validation."""
        # Business rule: Check ownership
        note = self.note_repository.get_by_id(note_id, owner_id)
        if not note:
            raise NotFoundError("Note not found")

        # Business rule: Soft delete (set status to DELETED)
        return self.note_repository.delete(note_id, owner_id)

    def search_notes(self, search_request: NoteSearchRequest, owner_id: int) -> Tuple[List[Note], int]:
        """Search notes with business logic."""
        # Business rule: Validate search parameters
        if search_request.page < 1:
            search_request.page = 1

        if search_request.per_page < 1 or search_request.per_page > 100:
            search_request.per_page = 10

        # Business rule: Sanitize search query
        search_query = search_request.query
        if search_query:
            search_query = search_query.strip()
            if len(search_query) < 2:
                search_query = None

        # Execute search with business logic
        notes = self.note_repository.get_by_owner(
            owner_id=owner_id,
            skip=(search_request.page - 1) * search_request.per_page,
            limit=search_request.per_page,
            status=search_request.status,
            is_public=search_request.is_public,
            is_pinned=search_request.is_pinned,
            search_query=search_query,
            order_by="created_at",
            order_direction="desc"
        )

        total = self.note_repository.count_by_owner(
            owner_id=owner_id,
            status=search_request.status,
            is_public=search_request.is_public,
            is_pinned=search_request.is_pinned,
            search_query=search_query
        )

        return notes, total

    def _generate_summary(self, content: str, max_length: int = 200) -> str:
        """Generate note summary with business rules."""
        if not content:
            return ""

        # Business rule: Simple summary generation
        summary = content.strip()
        if len(summary) <= max_length:
            return summary

        # Business rule: Truncate at word boundary
        summary = summary[:max_length - 3].strip()
        last_space = summary.rfind(' ')
        if last_space > max_length // 2:
            summary = summary[:last_space]

        return summary + "..."
```

## Service Layer Patterns

### 1. Transaction Management

```python
class NoteManagementService:
    def create_note_with_tags(self, note_data: NoteCreate, tags: List[str], owner_id: int) -> Note:
        """Create note with tags in a transaction."""
        try:
            # Start transaction
            note = self.note_repository.create(note_data, owner_id)

            # Create tags
            for tag_name in tags:
                tag = self.tag_repository.create({"name": tag_name})
                self.note_tag_repository.create({
                    "note_id": note.id,
                    "tag_id": tag.id
                })

            # Commit transaction
            self.db.commit()
            return note

        except Exception as e:
            # Rollback on error
            self.db.rollback()
            raise DatabaseError(f"Failed to create note with tags: {str(e)}")
```

### 2. Business Rule Validation

```python
class UserService:
    def update_user_profile(self, user_id: int, profile_data: UserUpdate) -> User:
        """Update user profile with business validation."""
        # Business rule: Check if user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        # Business rule: Validate email uniqueness
        if "email" in profile_data.dict(exclude_unset=True):
            existing_user = self.user_repository.get_by_email(profile_data.email)
            if existing_user and existing_user.id != user_id:
                raise ValidationError("Email already in use")

        # Business rule: Validate username uniqueness
        if "username" in profile_data.dict(exclude_unset=True):
            existing_user = self.user_repository.get_by_username(profile_data.username)
            if existing_user and existing_user.id != user_id:
                raise ValidationError("Username already in use")

        # Apply updates
        update_data = profile_data.dict(exclude_unset=True)
        return self.user_repository.update(user_id, update_data)
```

### 3. Complex Business Operations

```python
class NoteManagementService:
    def archive_old_notes(self, owner_id: int, days_old: int = 365) -> int:
        """Archive notes older than specified days."""
        # Business rule: Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)

        # Business rule: Get old notes
        old_notes = self.note_repository.get_notes_older_than(owner_id, cutoff_date)

        # Business rule: Archive notes
        archived_count = 0
        for note in old_notes:
            if note.status == NoteStatus.ACTIVE:
                note.status = NoteStatus.ARCHIVED
                archived_count += 1

        # Commit changes
        self.db.commit()
        return archived_count

    def get_note_statistics(self, owner_id: int) -> NoteStats:
        """Get comprehensive note statistics."""
        # Business rule: Calculate various statistics
        stats = self.note_repository.get_stats(owner_id)

        # Business rule: Calculate additional metrics
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)

        # Business rule: Get time-based statistics
        created_today = self.note_repository.count_notes_created_after(owner_id, today)
        created_this_week = self.note_repository.count_notes_created_after(owner_id, week_start)
        created_this_month = self.note_repository.count_notes_created_after(owner_id, month_start)

        return NoteStats(
            total_notes=stats["total_notes"],
            active_notes=stats["active_notes"],
            archived_notes=stats["archived_notes"],
            public_notes=stats["public_notes"],
            pinned_notes=stats["pinned_notes"],
            created_today=created_today,
            created_this_week=created_this_week,
            created_this_month=created_this_month,
        )
```

## Service Layer Best Practices

### 1. Single Responsibility

```python
# Good: Each service has one responsibility
class AuthenticationService:
    """Handles user authentication and authorization."""
    pass

class NoteManagementService:
    """Handles note CRUD operations and business logic."""
    pass

class UserManagementService:
    """Handles user profile management."""
    pass

# Bad: One service handling multiple responsibilities
class DataService:
    """Handles users, notes, and everything else."""
    pass
```

### 2. Dependency Injection

```python
class NoteManagementService:
    def __init__(self, db: Session):
        self.db = db
        self.note_repository = NoteRepository(db)
        self.user_repository = UserRepository(db)
```

### 3. Error Handling

```python
class NoteManagementService:
    def create_note(self, note_data: NoteCreate, owner_id: int) -> Note:
        try:
            # Business logic
            return self.note_repository.create(note_dict)
        except ValidationError:
            raise  # Re-raise validation errors
        except Exception as e:
            # Log and wrap unexpected errors
            logger.error(f"Failed to create note: {str(e)}")
            raise ValidationError("Failed to create note")
```

### 4. Logging

```python
class NoteManagementService:
    def create_note(self, note_data: NoteCreate, owner_id: int) -> Note:
        with log_function_call(logger, "create_note", owner_id=owner_id):
            try:
                # Business logic
                note = self.note_repository.create(note_dict)
                logger.info("Note created successfully", note_id=note.id, owner_id=owner_id)
                return note
            except Exception as e:
                logger.error("Failed to create note", error=str(e), owner_id=owner_id)
                raise
```

## Testing Service Layer

### 1. Unit Testing

```python
def test_create_note_success():
    # Setup
    mock_db = Mock()
    mock_repo = Mock()
    service = NoteManagementService(mock_db)
    service.note_repository = mock_repo

    # Mock repository response
    mock_note = Note(id=1, title="Test Note", content="Test content")
    mock_repo.create.return_value = mock_note

    # Execute
    note_data = NoteCreate(title="Test Note", content="Test content")
    result = service.create_note(note_data, owner_id=1)

    # Assert
    assert result.title == "Test Note"
    mock_repo.create.assert_called_once()
```

### 2. Integration Testing

```python
def test_create_note_integration():
    # Setup
    db = create_test_db()
    service = NoteManagementService(db)

    # Execute
    note_data = NoteCreate(title="Test Note", content="Test content")
    note = service.create_note(note_data, owner_id=1)

    # Assert
    assert note.title == "Test Note"
    assert note.owner_id == 1
    assert note.status == NoteStatus.ACTIVE
```

## Service Layer vs Other Layers

### Service Layer vs Repository Layer

```python
# Repository Layer: Data access only
class UserRepository:
    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

# Service Layer: Business logic
class UserService:
    def get_user_profile(self, user_id: int) -> UserProfile:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        # Business logic: Transform data
        return UserProfile(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_verified=user.is_verified
        )
```

### Service Layer vs API Layer

```python
# API Layer: HTTP handling
@router.get("/users/{user_id}")
async def get_user(user_id: int, current_user: User = Depends(get_current_user)):
    return user_service.get_user_profile(user_id)

# Service Layer: Business logic
class UserService:
    def get_user_profile(self, user_id: int) -> UserProfile:
        # Business logic here
        pass
```

## Common Pitfalls

### 1. Business Logic in API Layer

❌ **Wrong**: Business logic in router
```python
@router.post("/notes/")
async def create_note(note_data: NoteCreate):
    # Business logic in API layer - WRONG
    if not note_data.title.strip():
        raise HTTPException(400, "Title required")

    note = Note(**note_data.dict())
    db.add(note)
    db.commit()
```

✅ **Correct**: Business logic in service
```python
@router.post("/notes/")
async def create_note(note_data: NoteCreate, current_user: User = Depends(get_current_user)):
    return note_service.create_note(note_data, current_user.id)

class NoteManagementService:
    def create_note(self, note_data: NoteCreate, owner_id: int) -> Note:
        # Business logic in service layer - CORRECT
        if not note_data.title.strip():
            raise ValidationError("Title required")
        # ... rest of business logic
```

### 2. Direct Database Access in Services

❌ **Wrong**: Direct database access
```python
class NoteManagementService:
    def get_note(self, note_id: int):
        return self.db.query(Note).filter(Note.id == note_id).first()
```

✅ **Correct**: Use repository
```python
class NoteManagementService:
    def get_note(self, note_id: int):
        return self.note_repository.get_by_id(note_id)
```

### 3. Too Many Responsibilities

❌ **Wrong**: One service doing everything
```python
class DataService:
    def create_user(self): pass
    def create_note(self): pass
    def send_email(self): pass
    def process_payment(self): pass
```

✅ **Correct**: Separate services
```python
class UserService:
    def create_user(self): pass

class NoteService:
    def create_note(self): pass

class EmailService:
    def send_email(self): pass
```

## Conclusion

The Service Layer in the Notes App provides:

- **Business Logic Centralization**: All business rules in one place
- **Clean Separation**: Clear separation between API and data access
- **Testability**: Easy to unit test business logic
- **Reusability**: Services can be used by multiple API endpoints
- **Maintainability**: Changes to business logic don't affect other layers
- **Transaction Management**: Handle complex business operations

By implementing a well-designed Service Layer, the Notes App maintains clean architecture principles while providing robust business logic handling.
