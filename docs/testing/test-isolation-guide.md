# Test Isolation Guide

This guide outlines the requirements and best practices for ensuring complete test isolation from external dependencies in the Notes App.

## 🎯 Test Isolation Policy

### External Dependencies MUST NOT Be Used

Tests **MUST NOT** depend on:

- ❌ **Cloud Services**: AWS, GCP, Azure, Cloudflare
- ❌ **External Databases**: Redis, MongoDB, PostgreSQL (use in-memory SQLite)
- ❌ **External APIs**: OpenAI, Stripe, Twilio, SendGrid, etc.
- ❌ **File System**: Reading/writing actual files (use mocks)
- ❌ **Network Calls**: HTTP requests, socket connections
- ❌ **Environment Files**: `.env` files (use environment variable mocks)
- ❌ **Running Services**: Server instances, external processes
- ❌ **System Resources**: Real file paths, system calls

### Required Practices

✅ **DO:**
- Use in-memory SQLite for database tests
- Mock all external service calls
- Use environment variable patches
- Create isolated test fixtures
- Use dependency injection for testability
- Run tests in complete isolation

❌ **DON'T:**
- Make actual HTTP requests
- Connect to real databases
- Read from actual files
- Depend on environment variables
- Require server to be running
- Use external service credentials

## 🏗️ Isolation Architecture

### Test Environment Setup

The test environment is completely isolated through:

1. **Environment Variable Isolation**
   ```python
   @pytest.fixture(scope="session", autouse=True)
   def test_environment():
       # Completely isolated environment variables
       test_env = {
           "ENVIRONMENT": "testing",
           "DATABASE_URL": "sqlite:///:memory:",
           "JWT_SECRET_KEY": "test-secret-key-for-testing-only",
           # ... all other variables mocked
       }
   ```

2. **External Service Mocking**
   ```python
   @pytest.fixture(autouse=True)
   def mock_external_services():
       # Mock all potential external services
       with patch("httpx.AsyncClient"), \
            patch("requests.get"), \
            patch("redis.Redis"), \
            patch("openai.OpenAI"):
           yield
   ```

3. **File System Mocking**
   ```python
   @pytest.fixture(autouse=True)
   def mock_file_operations():
       # Mock all file operations
       with patch("builtins.open"), \
            patch("pathlib.Path.exists"), \
            patch("os.path.exists"):
           yield
   ```

4. **Network Call Prevention**
   ```python
   @pytest.fixture(autouse=True)
   def prevent_network_calls():
       # Prevent any network calls
       with patch("socket.socket", side_effect=ConnectionError):
           yield
   ```

## 📋 Validation Checklist

### Before Writing Tests

- [ ] No external service imports
- [ ] No file system dependencies
- [ ] No network call dependencies
- [ ] No environment variable dependencies
- [ ] Use in-memory database only
- [ ] Mock all external dependencies

### Test Implementation

- [ ] Use `@pytest.fixture` for test data
- [ ] Use `unittest.mock` for external services
- [ ] Use `patch.dict(os.environ, ...)` for environment variables
- [ ] Use in-memory SQLite for database tests
- [ ] Use `TestClient` for API testing
- [ ] Use `AsyncMock` for async operations

### Test Validation

Run the validation script to ensure isolation:

```bash
python scripts/validate_test_isolation.py
```

This script checks for:
- External dependency imports
- Network call patterns
- File system operations
- Environment variable usage
- Proper fixture setup

## 🚀 Running Isolated Tests

### Install Test Dependencies

```bash
pip install -r tests/requirements-test.txt
```

### Run All Tests

```bash
# Run all tests with isolation
python -m pytest

# Run with coverage
python -m pytest --cov=src --cov-report=html

# Run specific test categories
python -m pytest -m unit
python -m pytest -m api
```

### Validate Isolation

```bash
# Validate test isolation
python scripts/validate_test_isolation.py

# Run tests with isolation check
python -m pytest --tb=short --maxfail=1
```

## 🔧 Common Patterns

### Mocking External Services

```python
def test_user_service_with_mocked_external_api():
    """Test user service with mocked external API."""
    with patch("httpx.AsyncClient") as mock_client:
        # Configure mock response
        mock_client.return_value.__aenter__.return_value.get.return_value.json.return_value = {
            "status": "success"
        }

        # Test your service
        result = user_service.call_external_api()
        assert result["status"] == "success"
```

### Environment Variable Mocking

```python
def test_config_with_mocked_env():
    """Test configuration with mocked environment variables."""
    with patch.dict(os.environ, {"DATABASE_URL": "sqlite:///:memory:"}):
        settings = Settings()
        assert "sqlite" in settings.database_url
```

### Database Testing

```python
def test_user_creation(db_session):
    """Test user creation with in-memory database."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123!"
    }

    user = User(**user_data)
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.email == "test@example.com"
```

## 🚨 Troubleshooting

### Common Issues

1. **Tests failing due to external calls**
   - Check if you're using `requests`, `httpx`, or other HTTP clients
   - Ensure all external services are mocked
   - Use the validation script to identify issues

2. **Environment variable issues**
   - Use `patch.dict(os.environ, ...)` for environment variables
   - Don't rely on actual `.env` files
   - Use the `test_environment` fixture

3. **Database connection issues**
   - Use in-memory SQLite only
   - Don't connect to real databases
   - Use the `db_session` fixture

4. **File system issues**
   - Mock all file operations
   - Don't read/write actual files
   - Use the `mock_file_operations` fixture

### Debugging Isolation Issues

```bash
# Run tests with detailed output
python -m pytest -v -s --tb=long

# Check for external dependencies
python scripts/validate_test_isolation.py

# Run specific test with isolation
python -m pytest tests/unit/test_specific.py -v
```

## 📊 Benefits of Test Isolation

### Performance
- ✅ **Fast Execution**: No network delays
- ✅ **Parallel Execution**: Tests don't interfere with each other
- ✅ **Consistent Timing**: Predictable execution times

### Reliability
- ✅ **No Flaky Tests**: No dependency on external services
- ✅ **Offline Testing**: Works without internet connection
- ✅ **Consistent Results**: Same results every time

### Maintainability
- ✅ **Easy Setup**: No external service configuration
- ✅ **Portable**: Run anywhere without setup
- ✅ **Debuggable**: Clear failure reasons

### Security
- ✅ **No Credentials**: No API keys or secrets in tests
- ✅ **No Data Leakage**: No real data in tests
- ✅ **Safe Testing**: No impact on production services

## 🎯 Best Practices Summary

1. **Always mock external dependencies**
2. **Use in-memory databases only**
3. **Mock environment variables**
4. **Prevent network calls**
5. **Use isolated test fixtures**
6. **Validate isolation regularly**
7. **Keep tests fast and reliable**
8. **Document isolation requirements**

Remember: **Tests should be fast, reliable, and completely isolated from external dependencies.**
