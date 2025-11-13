# Test Structure Guide

This guide explains how tests are organized, structured, and maintained in the Notes App.

## 📁 Test Organization

### Directory Structure
```
tests/
├── unit/                           # Unit tests (590 tests)
│   ├── test_admin_router.py        # Admin router comprehensive tests
│   ├── test_auth_bypass.py         # Authentication bypass tests
│   ├── test_auth_service.py        # Authentication service tests
│   ├── test_config.py              # Configuration tests
│   ├── test_core_functionality.py  # Core functionality tests
│   ├── test_database.py            # Database connection tests
│   ├── test_error_handler.py       # Error handling tests
│   ├── test_exceptions.py          # Custom exception tests
│   ├── test_logging.py             # Basic logging tests
│   ├── test_logging_router.py      # Logging router tests
│   ├── test_logging_utils.py       # Logging utilities tests
│   ├── test_middleware.py          # Basic middleware tests
│   ├── test_middleware_extended.py # Extended middleware tests
│   ├── test_models.py              # Database model tests
│   ├── test_note_repository.py     # Note repository tests
│   ├── test_schemas.py             # Pydantic schema tests
│   ├── test_secrets_loader.py      # Secrets management tests
│   ├── test_user_repository.py     # User repository tests
│   └── test_validation.py          # Input validation tests
└── api/                            # API integration tests (40 tests)
    ├── test_admin_router.py        # Admin API endpoint tests
    ├── test_auth.py                # Authentication API tests
    └── test_notes.py               # Notes API endpoint tests
```

## 🏗️ Test File Naming Conventions

### Naming Pattern
- **Format**: `test_<module_name>.py`
- **Examples**:
  - `test_validation.py` - Tests for validation module
  - `test_admin_router.py` - Tests for admin router
  - `test_middleware_extended.py` - Extended middleware tests

### Special Naming
- **`test_<module>_extended.py`**: Comprehensive tests for complex modules

## 🧪 Test Class Structure

### Standard Test Class Pattern
```python
"""
Unit tests for <module_name> module.
"""

from unittest.mock import Mock, patch
import pytest
from <module> import <function_or_class>

class Test<ClassName>:
    """Test <class_name> functionality."""

    def test_<method_name>_<scenario>(self):
        """Test <method_name> with <scenario>."""
        # Arrange
        # Act
        # Assert
```

### Example: Validation Tests
```python
class TestValidateEmail:
    """Test email validation functionality."""

    def test_validate_email_valid(self):
        """Test valid email addresses."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "test+tag@example.org"
        ]

        for email in valid_emails:
            result = validate_email(email)
            assert result.is_valid is True
            assert result.normalized_email == email.lower()

    def test_validate_email_invalid_format(self):
        """Test invalid email formats."""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "test@",
            "test..test@example.com"
        ]

        for email in invalid_emails:
            with pytest.raises(ValidationError):
                validate_email(email)
```

## 📋 Test Method Naming

### Naming Convention
- **Format**: `test_<method_name>_<scenario>`
- **Examples**:
  - `test_validate_email_valid` - Test valid email validation
  - `test_validate_email_invalid_format` - Test invalid email format
  - `test_get_user_by_id_success` - Test successful user retrieval
  - `test_get_user_by_id_not_found` - Test user not found scenario

### Scenario Types
- **`_success`**: Successful operation
- **`_error`**: Error handling
- **`_invalid_<type>`**: Invalid input handling
- **`_with_<condition>`**: Specific condition testing
- **`_empty_<type>`**: Empty input handling
- **`_none_<type>`**: None input handling

## 🔧 Test Fixtures

### Pytest Fixtures
```python
@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User"
    }

@pytest.fixture
def mock_database():
    """Mock database for testing."""
    with patch('src.core.database.SessionLocal') as mock:
        yield mock
```

### FastAPI Test Fixtures
```python
@pytest.fixture
def app():
    """Create FastAPI app for testing."""
    app = FastAPI()
    app.include_router(admin_router, prefix="/api/v1/admin")
    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)
```

## 🎭 Mocking Patterns

### Database Mocking
```python
def test_get_user_success(self, mock_database):
    """Test successful user retrieval."""
    # Arrange
    mock_user = Mock()
    mock_user.id = 1
    mock_user.email = "test@example.com"
    mock_database.return_value.query.return_value.filter.return_value.first.return_value = mock_user

    # Act
    result = get_user_by_id(1)

    # Assert
    assert result.id == 1
    assert result.email == "test@example.com"
```

### Service Mocking
```python
@patch('src.services.authentication.hash_password')
def test_register_user_success(self, mock_hash_password):
    """Test successful user registration."""
    # Arrange
    mock_hash_password.return_value = "hashed_password"
    user_data = {"email": "test@example.com", "password": "password"}

    # Act
    result = register_user(user_data)

    # Assert
    assert result.email == "test@example.com"
    mock_hash_password.assert_called_once_with("password")
```

### Async Mocking
```python
@pytest.mark.asyncio
async def test_async_operation(self):
    """Test async operation."""
    with patch('src.core.database.async_engine') as mock_engine:
        mock_conn = AsyncMock()
        mock_engine.begin.return_value.__aenter__.return_value = mock_conn
        mock_conn.execute.return_value = None

        result = await async_operation()

        assert result is not None
```

## 📊 Test Data Management

### Test Data Classes
```python
class TestData:
    """Centralized test data."""

    VALID_EMAILS = [
        "test@example.com",
        "user.name@domain.co.uk",
        "test+tag@example.org"
    ]

    INVALID_EMAILS = [
        "invalid-email",
        "@example.com",
        "test@"
    ]

    VALID_PASSWORDS = [
        "TestPassword123!",
        "SecurePass456@",
        "MyPassword789#"
    ]

    INVALID_PASSWORDS = [
        "weak",
        "123456",
        "password"
    ]
```

### Fixture Data
```python
@pytest.fixture
def valid_user_data():
    """Valid user registration data."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123!",
        "confirm_password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User"
    }

@pytest.fixture
def invalid_user_data():
    """Invalid user registration data."""
    return {
        "email": "invalid-email",
        "username": "a",  # Too short
        "password": "weak",
        "confirm_password": "different"
    }
```

## 🚀 Test Execution Patterns

### Running Specific Tests
```bash
# Run specific test file
pytest tests/unit/test_validation.py

# Run specific test class
pytest tests/unit/test_validation.py::TestValidateEmail

# Run specific test method
pytest tests/unit/test_validation.py::TestValidateEmail::test_validate_email_valid

# Run tests matching pattern
pytest -k "test_validate_email"

# Run tests with specific marker
pytest -m "not slow"
```

### Parallel Test Execution
```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto

# Run with specific number of workers
pytest -n 4
```

## 📈 Coverage Patterns

### Coverage by Module
```python
# Test all functions in a module
def test_module_comprehensive():
    """Test all functions in validation module."""
    # Test validate_email
    # Test validate_password
    # Test validate_username
    # Test validate_string_field
    # Test validate_positive_integer
    # Test validate_boolean
    # Test validate_enum_value
    # Test ValidationResult
    # Test validate_dict_fields
```

### Edge Case Testing
```python
def test_edge_cases():
    """Test edge cases and boundary conditions."""
    # Empty strings
    # None values
    # Maximum length strings
    # Minimum length strings
    # Special characters
    # Unicode characters
    # Very large numbers
    # Very small numbers
```

## 🔍 Debugging Tests

### Verbose Output
```bash
# Run with verbose output
pytest -v

# Run with extra verbose output
pytest -vv

# Show local variables on failure
pytest -l
```

### Debugging Specific Tests
```bash
# Run with pdb debugger
pytest --pdb

# Run with pdb on first failure
pytest -x --pdb

# Run with pdb on specific test
pytest tests/unit/test_validation.py::TestValidateEmail::test_validate_email_valid --pdb
```

### Test Output Analysis
```bash
# Show test output
pytest -s

# Show print statements
pytest -s --capture=no

# Show warnings
pytest -W default
```

## 📚 Best Practices

### Test Organization
1. **One test file per module**
2. **One test class per class/function group**
3. **One test method per scenario**
4. **Clear, descriptive names**
5. **Proper documentation**

### Test Quality
1. **Arrange-Act-Assert pattern**
2. **Single responsibility per test**
3. **Independent tests**
4. **Fast execution**
5. **Clear assertions**

### Maintenance
1. **Keep tests up to date**
2. **Remove obsolete tests**
3. **Refactor when needed**
4. **Document complex tests**
5. **Regular review**

---

**Last Updated**: October 2024
**Test Count**: 590 tests
**Coverage**: 85%
