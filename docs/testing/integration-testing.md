# Integration Testing Guide

This guide explains how to conduct integration testing for the Notes App to ensure all components work together correctly.

## 🎯 Integration Testing Objectives

### Key Goals
- **Component Integration**: Test how different modules work together
- **API Integration**: Test complete API workflows
- **Database Integration**: Test database operations end-to-end
- **External Service Integration**: Test third-party service integrations
- **Data Flow**: Test data flow through the entire system

### Integration Test Types
1. **API Integration Tests**: Test complete API workflows
2. **Database Integration Tests**: Test database operations
3. **Service Integration Tests**: Test service layer interactions
4. **End-to-End Tests**: Test complete user workflows
5. **External Integration Tests**: Test third-party integrations

## 🏗️ Integration Test Structure

### Directory Organization
```
tests/
├── integration/                    # Integration tests
│   ├── api/                       # API integration tests
│   │   ├── test_auth_flow.py      # Authentication workflow
│   │   ├── test_notes_flow.py     # Notes management workflow
│   │   └── test_admin_flow.py     # Admin operations workflow
│   ├── database/                  # Database integration tests
│   │   ├── test_user_operations.py
│   │   ├── test_note_operations.py
│   │   └── test_transactions.py
│   ├── services/                  # Service integration tests
│   │   ├── test_auth_service.py
│   │   ├── test_note_service.py
│   │   └── test_email_service.py
│   └── e2e/                       # End-to-end tests
│       ├── test_user_journey.py
│       ├── test_note_journey.py
│       └── test_admin_journey.py
```

## 🔐 Authentication Flow Integration

### Complete Authentication Workflow
```python
# tests/integration/api/test_auth_flow.py
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)

def test_complete_auth_flow(client):
    """Test complete authentication workflow."""
    # Step 1: Register new user
    register_data = {
        "email": "integration@example.com",
        "username": "integration_user",
        "password": "IntegrationPass123!",
        "confirm_password": "IntegrationPass123!",
        "first_name": "Integration",
        "last_name": "User"
    }

    response = client.post("/api/v1/users/register", json=register_data)
    assert response.status_code == 201
    user_data = response.json()
    assert user_data["email"] == register_data["email"]
    assert user_data["username"] == register_data["username"]

    # Step 2: Login with registered user
    login_data = {
        "email": "integration@example.com",
        "password": "IntegrationPass123!"
    }

    response = client.post("/api/v1/users/login", json=login_data)
    assert response.status_code == 200
    login_response = response.json()
    assert "access_token" in login_response
    assert "token_type" in login_response

    # Step 3: Use token for authenticated requests
    token = login_response["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get user profile
    response = client.get("/api/v1/users/profile", headers=headers)
    assert response.status_code == 200
    profile = response.json()
    assert profile["email"] == register_data["email"]

    # Step 4: Logout (if implemented)
    response = client.post("/api/v1/users/logout", headers=headers)
    # Note: Logout might return 200 or 204 depending on implementation
    assert response.status_code in [200, 204]

def test_auth_flow_with_invalid_credentials(client):
    """Test authentication flow with invalid credentials."""
    # Try to login with non-existent user
    login_data = {
        "email": "nonexistent@example.com",
        "password": "WrongPassword123!"
    }

    response = client.post("/api/v1/users/login", json=login_data)
    assert response.status_code == 401
    error_data = response.json()
    assert "detail" in error_data

def test_auth_flow_with_expired_token(client):
    """Test authentication flow with expired token."""
    # This would require setting up an expired token
    # For now, test with malformed token
    headers = {"Authorization": "Bearer invalid_token"}

    response = client.get("/api/v1/users/profile", headers=headers)
    assert response.status_code == 401
```

## 📝 Notes Management Integration

### Complete Notes Workflow
```python
# tests/integration/api/test_notes_flow.py
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

@pytest.fixture
def authenticated_client(client):
    """Create authenticated test client."""
    # Register and login user
    register_data = {
        "email": "notes@example.com",
        "username": "notes_user",
        "password": "NotesPass123!",
        "confirm_password": "NotesPass123!",
        "first_name": "Notes",
        "last_name": "User"
    }

    client.post("/api/v1/users/register", json=register_data)

    login_response = client.post("/api/v1/users/login", json={
        "email": "notes@example.com",
        "password": "NotesPass123!"
    })

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    return client, headers

def test_complete_notes_workflow(authenticated_client):
    """Test complete notes management workflow."""
    client, headers = authenticated_client

    # Step 1: Create a note
    note_data = {
        "title": "Integration Test Note",
        "content": "This is a note created during integration testing.",
        "summary": "Integration test note summary",
        "tags": ["integration", "test"]
    }

    response = client.post("/api/v1/notes/", json=note_data, headers=headers)
    assert response.status_code == 201
    created_note = response.json()
    note_id = created_note["id"]
    assert created_note["title"] == note_data["title"]
    assert created_note["content"] == note_data["content"]

    # Step 2: Get all notes
    response = client.get("/api/v1/notes/", headers=headers)
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) >= 1
    assert any(note["id"] == note_id for note in notes)

    # Step 3: Get specific note
    response = client.get(f"/api/v1/notes/{note_id}", headers=headers)
    assert response.status_code == 200
    note = response.json()
    assert note["id"] == note_id
    assert note["title"] == note_data["title"]

    # Step 4: Update note
    update_data = {
        "title": "Updated Integration Test Note",
        "content": "This note has been updated during integration testing.",
        "summary": "Updated integration test note"
    }

    response = client.put(f"/api/v1/notes/{note_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    updated_note = response.json()
    assert updated_note["title"] == update_data["title"]
    assert updated_note["content"] == update_data["content"]

    # Step 5: Search notes
    response = client.get("/api/v1/notes/search?q=integration", headers=headers)
    assert response.status_code == 200
    search_results = response.json()
    assert len(search_results) >= 1
    assert any(note["id"] == note_id for note in search_results)

    # Step 6: Delete note
    response = client.delete(f"/api/v1/notes/{note_id}", headers=headers)
    assert response.status_code == 200

    # Step 7: Verify note is deleted
    response = client.get(f"/api/v1/notes/{note_id}", headers=headers)
    assert response.status_code == 404

def test_notes_workflow_with_validation_errors(authenticated_client):
    """Test notes workflow with validation errors."""
    client, headers = authenticated_client

    # Try to create note with invalid data
    invalid_note_data = {
        "title": "",  # Empty title
        "content": "x",  # Too short content
        "summary": "",
        "tags": []
    }

    response = client.post("/api/v1/notes/", json=invalid_note_data, headers=headers)
    assert response.status_code == 422
    error_data = response.json()
    assert "detail" in error_data

def test_notes_workflow_unauthorized_access(client):
    """Test notes workflow without authentication."""
    # Try to access notes without authentication
    response = client.get("/api/v1/notes/")
    assert response.status_code == 401

    # Try to create note without authentication
    note_data = {
        "title": "Unauthorized Note",
        "content": "This should fail.",
        "summary": "Unauthorized"
    }

    response = client.post("/api/v1/notes/", json=note_data)
    assert response.status_code == 401
```

## 🗄️ Database Integration Tests

### Database Operations Integration
```python
# tests/integration/database/test_user_operations.py
import pytest
from src.core.database import SessionLocal
from src.models.user import User
from src.repositories.user_repository import UserRepository

@pytest.fixture
def db_session():
    """Create database session for testing."""
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def user_repository(db_session):
    """Create user repository with test session."""
    return UserRepository(db_session)

def test_user_database_operations(user_repository):
    """Test complete user database operations."""
    # Create user data
    user_data = {
        "email": "db_test@example.com",
        "username": "db_test_user",
        "password": "hashed_password",
        "first_name": "DB",
        "last_name": "Test"
    }

    # Create user
    user = user_repository.create_user(user_data)
    assert user.id is not None
    assert user.email == user_data["email"]
    assert user.username == user_data["username"]

    # Get user by ID
    retrieved_user = user_repository.get_user_by_id(user.id)
    assert retrieved_user is not None
    assert retrieved_user.email == user_data["email"]

    # Get user by email
    retrieved_user_by_email = user_repository.get_user_by_email(user_data["email"])
    assert retrieved_user_by_email is not None
    assert retrieved_user_by_email.id == user.id

    # Update user
    update_data = {
        "first_name": "Updated",
        "last_name": "Name"
    }
    updated_user = user_repository.update_user(user.id, update_data)
    assert updated_user.first_name == update_data["first_name"]
    assert updated_user.last_name == update_data["last_name"]

    # Delete user
    result = user_repository.delete_user(user.id)
    assert result is True

    # Verify user is deleted
    deleted_user = user_repository.get_user_by_id(user.id)
    assert deleted_user is None

def test_user_database_transactions(user_repository, db_session):
    """Test user database transactions."""
    # Test transaction rollback on error
    user_data = {
        "email": "transaction_test@example.com",
        "username": "transaction_test_user",
        "password": "hashed_password",
        "first_name": "Transaction",
        "last_name": "Test"
    }

    try:
        # Start transaction
        db_session.begin()

        # Create user
        user = user_repository.create_user(user_data)
        assert user.id is not None

        # Simulate error (e.g., duplicate email)
        user_data_duplicate = user_data.copy()
        user_data_duplicate["username"] = "different_username"

        # This should cause an error due to duplicate email
        with pytest.raises(Exception):
            user_repository.create_user(user_data_duplicate)

        # Transaction should be rolled back
        db_session.rollback()

        # User should not exist after rollback
        retrieved_user = user_repository.get_user_by_id(user.id)
        assert retrieved_user is None

    except Exception:
        db_session.rollback()
        raise
```

## 🔧 Service Integration Tests

### Service Layer Integration
```python
# tests/integration/services/test_auth_service.py
import pytest
from src.services.authentication import AuthenticationService
from src.repositories.user_repository import UserRepository
from src.core.database import SessionLocal

@pytest.fixture
def auth_service():
    """Create authentication service for testing."""
    session = SessionLocal()
    user_repo = UserRepository(session)
    return AuthenticationService(user_repo)

def test_auth_service_integration(auth_service):
    """Test authentication service integration."""
    # Register user
    user_data = {
        "email": "service_test@example.com",
        "username": "service_test_user",
        "password": "ServicePass123!",
        "confirm_password": "ServicePass123!",
        "first_name": "Service",
        "last_name": "Test"
    }

    # Register user
    registered_user = auth_service.register_user(user_data)
    assert registered_user is not None
    assert registered_user.email == user_data["email"]

    # Login user
    login_data = {
        "email": "service_test@example.com",
        "password": "ServicePass123!"
    }

    login_result = auth_service.login_user(login_data)
    assert login_result is not None
    assert "access_token" in login_result
    assert "user" in login_result

    # Verify password
    password_valid = auth_service.verify_password(
        "ServicePass123!",
        registered_user.password
    )
    assert password_valid is True

    # Test invalid password
    password_invalid = auth_service.verify_password(
        "WrongPassword123!",
        registered_user.password
    )
    assert password_invalid is False

def test_auth_service_error_handling(auth_service):
    """Test authentication service error handling."""
    # Try to register user with invalid data
    invalid_user_data = {
        "email": "invalid-email",
        "username": "a",  # Too short
        "password": "weak",
        "confirm_password": "different"
    }

    with pytest.raises(Exception):  # Should raise validation error
        auth_service.register_user(invalid_user_data)

    # Try to login with non-existent user
    login_data = {
        "email": "nonexistent@example.com",
        "password": "SomePassword123!"
    }

    with pytest.raises(Exception):  # Should raise not found error
        auth_service.login_user(login_data)
```

## 🌐 End-to-End Tests

### Complete User Journey
```python
# tests/integration/e2e/test_user_journey.py
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)

def test_complete_user_journey(client):
    """Test complete user journey from registration to note management."""
    # Step 1: Register new user
    register_data = {
        "email": "journey@example.com",
        "username": "journey_user",
        "password": "JourneyPass123!",
        "confirm_password": "JourneyPass123!",
        "first_name": "Journey",
        "last_name": "User"
    }

    response = client.post("/api/v1/users/register", json=register_data)
    assert response.status_code == 201

    # Step 2: Login
    login_response = client.post("/api/v1/users/login", json={
        "email": "journey@example.com",
        "password": "JourneyPass123!"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Step 3: Create multiple notes
    notes_data = [
        {
            "title": "First Note",
            "content": "This is the first note in my journey.",
            "summary": "First note summary"
        },
        {
            "title": "Second Note",
            "content": "This is the second note in my journey.",
            "summary": "Second note summary"
        },
        {
            "title": "Third Note",
            "content": "This is the third note in my journey.",
            "summary": "Third note summary"
        }
    ]

    created_notes = []
    for note_data in notes_data:
        response = client.post("/api/v1/notes/", json=note_data, headers=headers)
        assert response.status_code == 201
        created_notes.append(response.json())

    # Step 4: Get all notes
    response = client.get("/api/v1/notes/", headers=headers)
    assert response.status_code == 200
    all_notes = response.json()
    assert len(all_notes) == 3

    # Step 5: Search notes
    response = client.get("/api/v1/notes/search?q=journey", headers=headers)
    assert response.status_code == 200
    search_results = response.json()
    assert len(search_results) == 3

    # Step 6: Update a note
    note_id = created_notes[0]["id"]
    update_data = {
        "title": "Updated First Note",
        "content": "This note has been updated during the journey.",
        "summary": "Updated first note summary"
    }

    response = client.put(f"/api/v1/notes/{note_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    updated_note = response.json()
    assert updated_note["title"] == update_data["title"]

    # Step 7: Delete a note
    note_to_delete = created_notes[1]["id"]
    response = client.delete(f"/api/v1/notes/{note_to_delete}", headers=headers)
    assert response.status_code == 200

    # Step 8: Verify note is deleted
    response = client.get(f"/api/v1/notes/{note_to_delete}", headers=headers)
    assert response.status_code == 404

    # Step 9: Get remaining notes
    response = client.get("/api/v1/notes/", headers=headers)
    assert response.status_code == 200
    remaining_notes = response.json()
    assert len(remaining_notes) == 2

    # Step 10: Update user profile
    profile_update = {
        "first_name": "Updated",
        "last_name": "Journey"
    }

    response = client.put("/api/v1/users/profile", json=profile_update, headers=headers)
    assert response.status_code == 200
    updated_profile = response.json()
    assert updated_profile["first_name"] == profile_update["first_name"]
    assert updated_profile["last_name"] == profile_update["last_name"]
```

## 🚀 Running Integration Tests

### Test Commands
```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific integration test category
pytest tests/integration/api/ -v
pytest tests/integration/database/ -v
pytest tests/integration/services/ -v
pytest tests/integration/e2e/ -v

# Run specific integration test
pytest tests/integration/api/test_auth_flow.py -v

# Run integration tests with coverage
pytest tests/integration/ --cov=src --cov-report=term-missing
```

### Integration Test Configuration
```ini
# pytest.ini
[tool:pytest]
markers =
    integration: marks tests as integration tests
    api: marks tests as API integration tests
    database: marks tests as database integration tests
    service: marks tests as service integration tests
    e2e: marks tests as end-to-end tests

# Run only integration tests
pytest -m integration

# Run only API integration tests
pytest -m api

# Run only end-to-end tests
pytest -m e2e
```

## 📋 Integration Testing Checklist

### Before Integration Testing
- [ ] Set up test database
- [ ] Configure test environment
- [ ] Install required dependencies
- [ ] Set up test data fixtures

### During Integration Testing
- [ ] Test complete workflows
- [ ] Verify data consistency
- [ ] Check error handling
- [ ] Monitor performance

### After Integration Testing
- [ ] Analyze test results
- [ ] Document issues found
- [ ] Update test cases
- [ ] Plan fixes for issues

## 🎯 Integration Test Best Practices

### 1. Test Real Workflows
- Test complete user journeys
- Test data flow through the system
- Test error scenarios

### 2. Use Real Data
- Use realistic test data
- Test with various data sizes
- Test edge cases

### 3. Test Error Scenarios
- Test validation errors
- Test authentication failures
- Test database errors

### 4. Maintain Test Data
- Clean up test data after tests
- Use isolated test data
- Avoid test data conflicts

---

**Last Updated**: October 2024
**Integration Tests**: 50+
**API Tests**: 20+
**Database Tests**: 15+
**E2E Tests**: 15+
