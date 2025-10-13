# Testing Best Practices

This guide outlines the best practices for writing, maintaining, and organizing tests in the Notes App.

## 🎯 Testing Principles

### 1. Test Pyramid
```
    /\
   /  \     E2E Tests (Few)
  /____\
 /      \   Integration Tests (Some)
/________\
/          \ Unit Tests (Many)
/____________\
```

- **Unit Tests**: Fast, isolated, many
- **Integration Tests**: Medium speed, component interaction, some
- **E2E Tests**: Slow, full system, few

### 2. FIRST Principles
- **Fast**: Tests should run quickly
- **Independent**: Tests should not depend on each other
- **Repeatable**: Tests should produce consistent results
- **Self-Validating**: Tests should have clear pass/fail criteria
- **Timely**: Tests should be written close to the code they test

## 📝 Writing Good Tests

### Test Structure (AAA Pattern)
```python
def test_validate_email_valid():
    """Test valid email validation."""
    # Arrange - Set up test data and mocks
    valid_email = "test@example.com"

    # Act - Execute the function being tested
    result = validate_email(valid_email)

    # Assert - Verify the expected outcome
    assert result.is_valid is True
    assert result.normalized_email == valid_email.lower()
```

### Descriptive Test Names
```python
# ❌ Bad
def test_email():
def test_validation():
def test_error():

# ✅ Good
def test_validate_email_with_valid_format():
def test_validate_email_with_invalid_format():
def test_validate_email_with_empty_string():
def test_validate_email_with_none_value():
```

### Single Responsibility
```python
# ❌ Bad - Testing multiple things
def test_user_validation():
    """Test user validation."""
    # Test email validation
    # Test password validation
    # Test username validation
    # Test name validation

# ✅ Good - One test per scenario
def test_validate_email_valid():
    """Test valid email validation."""

def test_validate_password_strong():
    """Test strong password validation."""

def test_validate_username_valid():
    """Test valid username validation."""
```

## 🎭 Mocking Best Practices

### When to Mock
- **External Dependencies**: Database, APIs, file system
- **Slow Operations**: Network calls, file I/O
- **Unpredictable Behavior**: Random numbers, timestamps
- **Side Effects**: Logging, notifications

### When NOT to Mock
- **Simple Data Structures**: Lists, dictionaries
- **Pure Functions**: Mathematical operations
- **Business Logic**: Core application logic

### Mocking Patterns
```python
# ✅ Good - Mock external dependencies
@patch('src.core.database.SessionLocal')
def test_get_user_success(mock_session):
    """Test successful user retrieval."""
    # Mock database session
    mock_user = Mock()
    mock_user.id = 1
    mock_session.return_value.query.return_value.filter.return_value.first.return_value = mock_user

    result = get_user_by_id(1)
    assert result.id == 1

# ❌ Bad - Mocking business logic
@patch('src.services.authentication.hash_password')
def test_register_user(mock_hash):
    """Test user registration."""
    # Don't mock core business logic
    mock_hash.return_value = "fake_hash"
```

### Async Mocking
```python
@pytest.mark.asyncio
async def test_async_database_operation():
    """Test async database operation."""
    with patch('src.core.database.async_engine') as mock_engine:
        # Mock async context manager
        mock_conn = AsyncMock()
        mock_engine.begin.return_value.__aenter__.return_value = mock_conn
        mock_conn.execute.return_value = None

        result = await async_operation()
        assert result is not None
```

## 📊 Test Data Management

### Test Data Organization
```python
class TestData:
    """Centralized test data."""

    # Valid test data
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

### Fixture Usage
```python
@pytest.fixture
def sample_user():
    """Sample user for testing."""
    return User(
        id=1,
        email="test@example.com",
        username="testuser",
        first_name="Test",
        last_name="User"
    )

@pytest.fixture
def mock_database():
    """Mock database for testing."""
    with patch('src.core.database.SessionLocal') as mock:
        yield mock
```

### Parameterized Tests
```python
@pytest.mark.parametrize("email,expected", [
    ("test@example.com", True),
    ("invalid-email", False),
    ("@example.com", False),
    ("test@", False),
])
def test_validate_email_format(email, expected):
    """Test email format validation."""
    result = validate_email(email)
    assert result.is_valid == expected
```

## 🔍 Assertion Best Practices

### Clear Assertions
```python
# ❌ Bad - Unclear assertion
def test_user_creation():
    result = create_user(user_data)
    assert result

# ✅ Good - Clear assertion
def test_user_creation():
    result = create_user(user_data)
    assert result.id is not None
    assert result.email == user_data["email"]
    assert result.username == user_data["username"]
```

### Specific Assertions
```python
# ❌ Bad - Generic assertion
def test_validation_error():
    with pytest.raises(Exception):
        validate_email("invalid")

# ✅ Good - Specific assertion
def test_validation_error():
    with pytest.raises(ValidationError) as exc_info:
        validate_email("invalid")
    assert "Invalid email format" in str(exc_info.value)
```

### Multiple Assertions
```python
def test_user_response():
    """Test user response structure."""
    user = create_user(user_data)

    # Test all required fields
    assert user.id is not None
    assert user.email == user_data["email"]
    assert user.username == user_data["username"]
    assert user.first_name == user_data["first_name"]
    assert user.last_name == user_data["last_name"]
    assert user.created_at is not None
    assert user.updated_at is not None
```

## 🚀 Performance Best Practices

### Fast Tests
```python
# ✅ Good - Fast test
def test_validate_email():
    result = validate_email("test@example.com")
    assert result.is_valid is True

# ❌ Bad - Slow test
def test_database_operation():
    # Don't use real database in unit tests
    user = database.query(User).filter(User.id == 1).first()
    assert user is not None
```

### Parallel Execution
```python
# Mark slow tests
@pytest.mark.slow
def test_large_dataset_processing():
    """Test processing large dataset."""
    # This test takes a long time
    pass

# Run tests excluding slow ones
# pytest -m "not slow"
```

### Test Isolation
```python
# ✅ Good - Isolated test
def test_user_creation():
    """Test user creation in isolation."""
    with patch('src.core.database.SessionLocal') as mock_db:
        # Test doesn't depend on external state
        result = create_user(user_data)
        assert result is not None

# ❌ Bad - Dependent test
def test_user_creation():
    """Test user creation."""
    # This test depends on previous test data
    user = get_user_by_id(1)  # Assumes user exists
    assert user is not None
```

## 📁 Test Organization

### File Structure
```
tests/
├── unit/                    # Unit tests
│   ├── test_validation.py   # One file per module
│   ├── test_auth_service.py
│   └── test_database.py
├── api/                     # Integration tests
│   ├── test_auth_api.py
│   └── test_notes_api.py
└── fixtures/                # Test fixtures
    ├── users.py
    └── notes.py
```

### Class Organization
```python
class TestValidateEmail:
    """Test email validation functionality."""

    def test_valid_emails(self):
        """Test valid email formats."""
        pass

    def test_invalid_emails(self):
        """Test invalid email formats."""
        pass

    def test_edge_cases(self):
        """Test edge cases."""
        pass

class TestValidatePassword:
    """Test password validation functionality."""

    def test_strong_passwords(self):
        """Test strong password validation."""
        pass

    def test_weak_passwords(self):
        """Test weak password validation."""
        pass
```

## 🔧 Test Maintenance

### Regular Review
- **Monthly**: Review test coverage and quality
- **Sprint End**: Review new tests and update documentation
- **Release**: Ensure all tests pass and coverage is maintained

### Test Refactoring
```python
# ❌ Bad - Duplicated test code
def test_validate_email_1():
    email = "test@example.com"
    result = validate_email(email)
    assert result.is_valid is True

def test_validate_email_2():
    email = "user@domain.com"
    result = validate_email(email)
    assert result.is_valid is True

# ✅ Good - Refactored test
@pytest.mark.parametrize("email", [
    "test@example.com",
    "user@domain.com",
    "admin@example.org"
])
def test_validate_email_valid(email):
    """Test valid email validation."""
    result = validate_email(email)
    assert result.is_valid is True
```

### Test Documentation
```python
def test_validate_email_with_special_characters():
    """
    Test email validation with special characters.

    This test verifies that email addresses containing
    special characters like dots, plus signs, and hyphens
    are properly validated.

    Test cases:
    - user.name@example.com (dot in local part)
    - user+tag@example.com (plus sign in local part)
    - user-name@example.com (hyphen in local part)
    """
    valid_emails = [
        "user.name@example.com",
        "user+tag@example.com",
        "user-name@example.com"
    ]

    for email in valid_emails:
        result = validate_email(email)
        assert result.is_valid is True
```

## 🚨 Common Anti-Patterns

### ❌ Don't Do This
```python
# Testing implementation details
def test_internal_method():
    user = User()
    assert user._hash_password("password") == "hashed"

# Testing multiple things
def test_user_validation():
    # Testing email, password, username all in one test
    pass

# Using real external dependencies
def test_database_operation():
    # Using real database in unit test
    pass

# Unclear test names
def test_thing():
    pass

# Hard-coded test data
def test_user_creation():
    user = create_user({
        "email": "hardcoded@example.com",
        "username": "hardcoded"
    })
    pass
```

### ✅ Do This Instead
```python
# Test public interface
def test_user_creation():
    user = create_user(user_data)
    assert user.email == user_data["email"]

# Test one thing at a time
def test_validate_email():
    pass

def test_validate_password():
    pass

# Mock external dependencies
@patch('src.core.database.SessionLocal')
def test_database_operation(mock_db):
    pass

# Clear, descriptive names
def test_validate_email_with_valid_format():
    pass

# Use test data classes
def test_user_creation():
    user = create_user(TestData.VALID_USER_DATA)
    pass
```

## 📋 Testing Checklist

### Before Writing Tests
- [ ] Understand the requirements
- [ ] Identify edge cases
- [ ] Plan test scenarios
- [ ] Choose appropriate test data

### While Writing Tests
- [ ] Follow AAA pattern
- [ ] Use descriptive names
- [ ] Test one thing at a time
- [ ] Mock external dependencies
- [ ] Write clear assertions

### After Writing Tests
- [ ] Run tests to ensure they pass
- [ ] Check test coverage
- [ ] Review test quality
- [ ] Update documentation
- [ ] Refactor if needed

### Regular Maintenance
- [ ] Review test coverage monthly
- [ ] Refactor duplicated test code
- [ ] Update tests when requirements change
- [ ] Remove obsolete tests
- [ ] Keep tests fast and reliable

---

**Last Updated**: October 2024
**Test Count**: 590 tests
**Coverage**: 85%
