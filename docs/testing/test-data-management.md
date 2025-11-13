# Test Data Management

This guide explains how to manage test data, fixtures, and test databases in the Notes App.

## 📊 Test Data Strategy

### Data Categories
1. **Static Test Data**: Fixed data for consistent testing
2. **Dynamic Test Data**: Generated data for specific scenarios
3. **Fixture Data**: Reusable data across multiple tests
4. **Mock Data**: Simulated data for external dependencies

## 🏗️ Test Data Organization

### Directory Structure
```
tests/
├── fixtures/                    # Test fixtures
│   ├── __init__.py
│   ├── users.py                # User test data
│   ├── notes.py                # Note test data
│   ├── database.py             # Database fixtures
│   └── api.py                  # API test data
├── data/                       # Static test data
│   ├── valid_emails.txt
│   ├── invalid_emails.txt
│   ├── sample_users.json
│   └── test_notes.json
└── factories/                   # Data factories
    ├── __init__.py
    ├── user_factory.py
    └── note_factory.py
```

## 📝 Static Test Data

### Test Data Classes
```python
# tests/fixtures/users.py
class UserTestData:
    """Static user test data."""

    VALID_USERS = [
        {
            "email": "test@example.com",
            "username": "testuser",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User"
        },
        {
            "email": "admin@example.com",
            "username": "admin",
            "password": "AdminPassword456!",
            "first_name": "Admin",
            "last_name": "User"
        }
    ]

    INVALID_USERS = [
        {
            "email": "invalid-email",
            "username": "a",  # Too short
            "password": "weak",
            "first_name": "",
            "last_name": ""
        }
    ]

    EDGE_CASE_USERS = [
        {
            "email": "a@b.co",  # Minimum valid email
            "username": "abc",  # Minimum valid username
            "password": "Test123!",  # Minimum valid password
            "first_name": "A",
            "last_name": "B"
        }
    ]

class NoteTestData:
    """Static note test data."""

    VALID_NOTES = [
        {
            "title": "Test Note",
            "content": "This is a test note.",
            "summary": "Test note summary",
            "tags": ["test", "example"]
        },
        {
            "title": "Another Note",
            "content": "This is another test note with more content.",
            "summary": "Another test note",
            "tags": ["test", "another"]
        }
    ]

    INVALID_NOTES = [
        {
            "title": "",  # Empty title
            "content": "x",  # Too short
            "summary": "",
            "tags": []
        }
    ]
```

### Validation Test Data
```python
# tests/fixtures/validation.py
class ValidationTestData:
    """Validation test data."""

    VALID_EMAILS = [
        "test@example.com",
        "user.name@domain.co.uk",
        "test+tag@example.org",
        "admin@subdomain.example.com",
        "a@b.co"  # Minimum valid
    ]

    INVALID_EMAILS = [
        "invalid-email",
        "@example.com",
        "test@",
        "test..test@example.com",
        "test@.com",
        "test@example.",
        ""  # Empty
    ]

    VALID_PASSWORDS = [
        "TestPassword123!",
        "SecurePass456@",
        "MyPassword789#",
        "Complex123$",
        "StrongPass999&"
    ]

    INVALID_PASSWORDS = [
        "weak",           # Too short
        "123456",         # No letters
        "password",       # No numbers/symbols
        "PASSWORD",       # No lowercase
        "Password",       # No numbers/symbols
        "Password123",    # No symbols
        ""                # Empty
    ]

    VALID_USERNAMES = [
        "testuser",
        "user123",
        "test_user",
        "user-name",
        "abc"  # Minimum valid
    ]

    INVALID_USERNAMES = [
        "a",              # Too short
        "ab",             # Too short
        "user@name",      # Invalid character
        "user name",      # Space
        "user.name",      # Dot
        ""                # Empty
    ]
```

## 🏭 Data Factories

### User Factory
```python
# tests/factories/user_factory.py
import factory
from faker import Faker
from src.models.user import User

fake = Faker()

class UserFactory(factory.Factory):
    """Factory for creating test users."""

    class Meta:
        model = User

    email = factory.LazyFunction(lambda: fake.email())
    username = factory.LazyFunction(lambda: fake.user_name())
    password = factory.LazyFunction(lambda: fake.password())
    first_name = factory.LazyFunction(lambda: fake.first_name())
    last_name = factory.LazyFunction(lambda: fake.last_name())
    is_active = True
    created_at = factory.LazyFunction(lambda: fake.date_time())
    updated_at = factory.LazyFunction(lambda: fake.date_time())

# Usage examples
def test_user_creation():
    """Test user creation with factory."""
    user = UserFactory()
    assert user.email is not None
    assert user.username is not None

def test_user_with_specific_data():
    """Test user with specific data."""
    user = UserFactory(email="test@example.com")
    assert user.email == "test@example.com"
```

### Note Factory
```python
# tests/factories/note_factory.py
import factory
from faker import Faker
from src.models.note import Note

fake = Faker()

class NoteFactory(factory.Factory):
    """Factory for creating test notes."""

    class Meta:
        model = Note

    title = factory.LazyFunction(lambda: fake.sentence(nb_words=3))
    content = factory.LazyFunction(lambda: fake.text(max_nb_chars=500))
    summary = factory.LazyFunction(lambda: fake.sentence(nb_words=10))
    tags = factory.LazyFunction(lambda: fake.words(nb=3))
    is_public = False
    created_at = factory.LazyFunction(lambda: fake.date_time())
    updated_at = factory.LazyFunction(lambda: fake.date_time())

# Usage examples
def test_note_creation():
    """Test note creation with factory."""
    note = NoteFactory()
    assert note.title is not None
    assert note.content is not None

def test_note_with_specific_title():
    """Test note with specific title."""
    note = NoteFactory(title="Test Note")
    assert note.title == "Test Note"
```

## 🔧 Pytest Fixtures

### Database Fixtures
```python
# tests/fixtures/database.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.database import Base
from src.models.user import User
from src.models.note import Note

@pytest.fixture(scope="function")
def test_db():
    """Create test database."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    yield session

    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture
def sample_user(test_db):
    """Create sample user in test database."""
    user = User(
        email="test@example.com",
        username="testuser",
        password="hashed_password",
        first_name="Test",
        last_name="User"
    )
    test_db.add(user)
    test_db.commit()
    return user

@pytest.fixture
def sample_note(test_db, sample_user):
    """Create sample note in test database."""
    note = Note(
        title="Test Note",
        content="This is a test note.",
        summary="Test note summary",
        user_id=sample_user.id
    )
    test_db.add(note)
    test_db.commit()
    return note
```

### API Fixtures
```python
# tests/fixtures/api.py
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    """Get authentication headers."""
    # Register test user
    response = client.post("/api/v1/users/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123!",
        "confirm_password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User"
    })

    # Login to get token
    response = client.post("/api/v1/users/login", json={
        "email": "test@example.com",
        "password": "TestPassword123!"
    })

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

## 🎭 Mock Data

### External Service Mocks
```python
# tests/fixtures/mocks.py
from unittest.mock import Mock, patch
import pytest

@pytest.fixture
def mock_email_service():
    """Mock email service."""
    with patch('src.services.email_service.send_email') as mock:
        mock.return_value = True
        yield mock

@pytest.fixture
def mock_database():
    """Mock database operations."""
    with patch('src.core.database.SessionLocal') as mock:
        mock_session = Mock()
        mock.return_value = mock_session
        yield mock_session

@pytest.fixture
def mock_redis():
    """Mock Redis cache."""
    with patch('src.core.cache.redis_client') as mock:
        mock.get.return_value = None
        mock.set.return_value = True
        yield mock
```

### API Response Mocks
```python
# tests/fixtures/api_mocks.py
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_external_api():
    """Mock external API responses."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "data": {"id": 1, "name": "Test"}
    }
    return mock_response

@pytest.fixture
def mock_failed_api():
    """Mock failed API responses."""
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.json.return_value = {
        "success": False,
        "error": "Internal server error"
    }
    return mock_response
```

## 📊 Test Data Utilities

### Data Generators
```python
# tests/utils/data_generators.py
import random
import string
from faker import Faker

fake = Faker()

def generate_email():
    """Generate random email."""
    return fake.email()

def generate_username():
    """Generate random username."""
    return fake.user_name()

def generate_password(length=12):
    """Generate random password."""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))

def generate_note_content():
    """Generate random note content."""
    return fake.text(max_nb_chars=500)

def generate_tags(count=3):
    """Generate random tags."""
    return fake.words(nb=count)
```

### Data Validators
```python
# tests/utils/data_validators.py
def validate_user_data(user_data):
    """Validate user data structure."""
    required_fields = ["email", "username", "password", "first_name", "last_name"]
    return all(field in user_data for field in required_fields)

def validate_note_data(note_data):
    """Validate note data structure."""
    required_fields = ["title", "content"]
    return all(field in note_data for field in required_fields)

def validate_api_response(response_data):
    """Validate API response structure."""
    return "success" in response_data or "error" in response_data
```

## 🔄 Test Data Cleanup

### Database Cleanup
```python
# tests/utils/cleanup.py
import pytest
from src.core.database import SessionLocal

@pytest.fixture(autouse=True)
def cleanup_database():
    """Clean up database after each test."""
    yield
    # Cleanup code here
    session = SessionLocal()
    session.query(User).delete()
    session.query(Note).delete()
    session.commit()
    session.close()
```

### File Cleanup
```python
# tests/utils/file_cleanup.py
import os
import tempfile
import pytest

@pytest.fixture
def temp_file():
    """Create temporary file for testing."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"test content")
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)
```

## 📋 Test Data Best Practices

### 1. Use Meaningful Data
```python
# ❌ Bad - Unclear data
user_data = {
    "email": "a@b.com",
    "username": "user1",
    "password": "pass123"
}

# ✅ Good - Clear, meaningful data
user_data = {
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPassword123!",
    "first_name": "Test",
    "last_name": "User"
}
```

### 2. Use Factories for Dynamic Data
```python
# ❌ Bad - Hard-coded data
def test_multiple_users():
    users = [
        {"email": "user1@example.com", "username": "user1"},
        {"email": "user2@example.com", "username": "user2"},
        {"email": "user3@example.com", "username": "user3"}
    ]

# ✅ Good - Factory-generated data
def test_multiple_users():
    users = [UserFactory() for _ in range(3)]
```

### 3. Keep Test Data Isolated
```python
# ❌ Bad - Shared mutable data
SHARED_USER_DATA = {"email": "test@example.com"}

def test_user_1():
    SHARED_USER_DATA["username"] = "user1"

def test_user_2():
    SHARED_USER_DATA["username"] = "user2"  # Affects other tests

# ✅ Good - Isolated data
@pytest.fixture
def user_data():
    return {"email": "test@example.com", "username": "testuser"}

def test_user_1(user_data):
    user_data["username"] = "user1"

def test_user_2(user_data):
    user_data["username"] = "user2"  # Independent
```

### 4. Use Appropriate Data Types
```python
# ❌ Bad - Wrong data types
user_data = {
    "email": 123,  # Should be string
    "age": "25",   # Should be integer
    "is_active": "true"  # Should be boolean
}

# ✅ Good - Correct data types
user_data = {
    "email": "test@example.com",  # String
    "age": 25,                    # Integer
    "is_active": True             # Boolean
}
```

## 🚀 Running Tests with Data

### Test Data Commands
```bash
# Run tests with specific data
pytest tests/unit/test_validation.py::TestValidateEmail -v

# Run tests with data factories
pytest tests/unit/test_user_factory.py -v

# Run tests with fixtures
pytest tests/unit/test_database.py -v

# Run tests with specific data pattern
pytest -k "test_email_validation" -v
```

### Data Debugging
```bash
# Show test data in output
pytest -s tests/unit/test_validation.py

# Debug specific test data
pytest --pdb tests/unit/test_validation.py::TestValidateEmail::test_validate_email_valid
```

---

**Last Updated**: October 2024
**Test Data Files**: 15+
**Fixtures**: 25+
**Factories**: 5+
