# Enhanced Logging Testing Guide

This guide provides comprehensive instructions for testing the enhanced structured logging functionality implemented in the Notes App.

## Overview

The enhanced logging system includes:
- **Structured JSON/Text Logging**: Consistent, searchable log messages
- **Enhanced Metadata**: File names, line numbers, function names, tracing IDs
- **Colored Development Logs**: Development-friendly colored console output
- **Context Management**: Global and request-level context for tracing
- **Dynamic Configuration**: Runtime log level management
- **Environment-based Defaults**: Smart defaults based on environment
- **Per-module Control**: Fine-grained logging control per module

## Prerequisites

1. **Environment Setup**: Ensure the virtual environment is activated
2. **Dependencies**: All required packages are installed
3. **Database**: PostgreSQL database is running and accessible
4. **Configuration**: Environment variables are properly set

## Testing Environment Setup

### 1. Environment Configuration

Create a `.env` file with the following configuration for testing:

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/notes_app_db

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=60

# Application Configuration
APP_NAME=Notes App
DEBUG=true
ENVIRONMENT=development

# Enhanced Logging Configuration
LOG_LEVEL=DEBUG
LOG_FORMAT=json
ENABLE_COLORED_LOGS=true
ENABLE_FILE_LINE_INFO=true
ENABLE_XRAY_TRACING=false

# Testing Configuration
AUTH_BYPASS=false
TEST_USER_ID=test-user-123
TEST_USER_EMAIL=test@example.com
TEST_USER_USERNAME=testuser

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# Security
BCRYPT_ROUNDS=12
```

### 2. Start the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Start the application
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

## Testing Scenarios

### 1. Basic Structured Logging

#### Test JSON Format Logging

```bash
# Set environment for JSON logging
export LOG_FORMAT=json
export LOG_LEVEL=DEBUG

# Start the application
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

**Expected Output:**
```json
{
  "event": "Application started successfully",
  "level": "info",
  "timestamp": "2024-01-15T10:30:00.123456Z",
  "logger": "src.api.main",
  "file": "main.py",
  "line": 45,
  "function": "startup_event"
}
```

#### Test Text Format Logging

```bash
# Set environment for text logging
export LOG_FORMAT=text
export LOG_LEVEL=DEBUG

# Start the application
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

**Expected Output:**
```
2024-01-15T10:30:00.123456Z [info     ] Application started successfully
    logger=src.api.main file=main.py line=45 function=startup_event
```

### 2. Colored Development Logs

#### Test Colored Console Output

```bash
# Set environment for colored logs
export ENVIRONMENT=development
export LOG_FORMAT=text
export ENABLE_COLORED_LOGS=true
export LOG_LEVEL=DEBUG

# Start the application
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

**Expected Output:**
- **DEBUG**: Blue colored text
- **INFO**: Green colored text
- **WARNING**: Yellow colored text
- **ERROR**: Red colored text
- **CRITICAL**: Bold red colored text

### 3. Enhanced Metadata Testing

#### Test File and Line Information

```bash
# Set environment for enhanced metadata
export ENABLE_FILE_LINE_INFO=true
export LOG_LEVEL=DEBUG

# Start the application and make API requests
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

**Test with API Requests:**
```bash
# Register a user
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPassword123!",
    "confirm_password": "TestPassword123!",
    "first_name": "Test",
    "last_name": "User"
  }'
```

**Expected Log Output:**
```json
{
  "event": "User registered successfully",
  "level": "info",
  "timestamp": "2024-01-15T10:30:00.123456Z",
  "logger": "src.services.authentication",
  "file": "authentication.py",
  "line": 150,
  "function": "register_user",
  "user_id": "1",
  "email": "test@example.com"
}
```

### 4. Context Management Testing

#### Test Global Context

```bash
# Start the application
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

**Test with Context:**
```bash
# Login to get a token
curl -X POST "http://localhost:8000/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'
```

**Expected Log Output with Context:**
```json
{
  "event": "User logged in successfully",
  "level": "info",
  "timestamp": "2024-01-15T10:30:00.123456Z",
  "logger": "src.services.authentication",
  "file": "authentication.py",
  "line": 275,
  "function": "login_user",
  "user_id": "1",
  "email": "test@example.com",
  "request_id": "req-123",
  "xray_id": "xray-456"
}
```

### 5. Dynamic Log Level Management

#### Test Runtime Log Level Changes

```bash
# Start the application
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

**Test Log Level API Endpoints:**

1. **Get Current Log Level:**
```bash
curl -X GET "http://localhost:8000/api/v1/logging/status"
```

2. **Set Global Log Level:**
```bash
curl -X POST "http://localhost:8000/api/v1/logging/set-level" \
  -H "Content-Type: application/json" \
  -d '{
    "level": "WARNING"
  }'
```

3. **Set Module-specific Log Level:**
```bash
curl -X POST "http://localhost:8000/api/v1/logging/set-level" \
  -H "Content-Type: application/json" \
  -d '{
    "level": "DEBUG",
    "module": "src.api"
  }'
```

4. **Get Module Log Level:**
```bash
curl -X GET "http://localhost:8000/api/v1/logging/level/src.api"
```

5. **List All Configured Modules:**
```bash
curl -X GET "http://localhost:8000/api/v1/logging/modules"
```

6. **Reset Log Levels:**
```bash
curl -X POST "http://localhost:8000/api/v1/logging/reset"
```

### 6. Environment-based Configuration Testing

#### Test Development Environment

```bash
export ENVIRONMENT=development
export LOG_LEVEL=""
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

**Expected:** Log level should be automatically set to DEBUG

#### Test Production Environment

```bash
export ENVIRONMENT=production
export LOG_LEVEL=""
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

**Expected:** Log level should be automatically set to ERROR

#### Test Testing Environment

```bash
export ENVIRONMENT=testing
export LOG_LEVEL=""
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

**Expected:** Log level should be automatically set to INFO

### 7. Per-module Log Level Testing

#### Test Module-specific Configuration

```bash
export MODULE_LOG_LEVELS='{"src.api": "DEBUG", "src.core": "WARNING", "src.services": "ERROR"}'
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

**Expected:** Different modules should have different log levels

### 8. Authentication Bypass Testing

#### Test Authentication Bypass for Testing

```bash
export ENVIRONMENT=testing
export AUTH_BYPASS=true
export TEST_USER_ID=test-user-123
export TEST_USER_EMAIL=test@example.com
export TEST_USER_USERNAME=testuser

uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

**Test Bypass Functionality:**
```bash
# This should work without authentication in testing environment
curl -X GET "http://localhost:8000/api/v1/notes/"
```

### 9. Input Validation Testing

#### Test Enhanced Input Validation

```bash
# Test invalid email
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "invalid-email",
    "username": "testuser",
    "password": "TestPassword123!",
    "confirm_password": "TestPassword123!",
    "first_name": "Test",
    "last_name": "User"
  }'
```

**Expected:** Detailed validation error with field-specific information

#### Test Password Validation

```bash
# Test weak password
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "weak",
    "confirm_password": "weak",
    "first_name": "Test",
    "last_name": "User"
  }'
```

**Expected:** Password strength validation error

### 10. Test Isolation Testing

#### Test Isolated Test Environment

```bash
# Run the enhanced logging tests
python -m pytest tests/test_enhanced_logging.py -v

# Run all tests with isolation
python -m pytest tests/ -v --tb=short
```

**Expected:** All tests should pass without external dependencies

## Automated Testing

### Run All Enhanced Logging Tests

```bash
# Run enhanced logging tests
python -m pytest tests/test_enhanced_logging.py -v

# Run with coverage
python -m pytest tests/test_enhanced_logging.py --cov=src.core.logging --cov-report=html

# Run all tests
python -m pytest tests/ -v
```

### Test Specific Features

```bash
# Test structured logging
python -m pytest tests/test_enhanced_logging.py::TestEnhancedLogging::test_structured_logging_with_metadata -v

# Test colored logs
python -m pytest tests/test_enhanced_logging.py::TestEnhancedLogging::test_colored_logs_development -v

# Test context management
python -m pytest tests/test_enhanced_logging.py::TestEnhancedLogging::test_logging_context_management -v

# Test dynamic log levels
python -m pytest tests/test_enhanced_logging.py::TestEnhancedLogging::test_log_level_dynamic_changes -v
```

## Performance Testing

### Test Logging Performance

```bash
# Test with high volume logging
python -c "
import os
os.environ['LOG_LEVEL'] = 'DEBUG'
os.environ['LOG_FORMAT'] = 'json'
from src.core.logging import configure_logging, get_logger
configure_logging()
logger = get_logger(__name__)
for i in range(1000):
    logger.info(f'Performance test message {i}', iteration=i)
"
```

### Test Thread Safety

```bash
# Test multi-threaded logging
python -c "
import threading
import time
import os
os.environ['LOG_LEVEL'] = 'DEBUG'
os.environ['LOG_FORMAT'] = 'json'
from src.core.logging import configure_logging, get_logger
configure_logging()
logger = get_logger(__name__)

def log_worker(worker_id):
    for i in range(100):
        logger.info(f'Worker {worker_id} message {i}', worker_id=worker_id, iteration=i)
        time.sleep(0.001)

threads = []
for i in range(10):
    thread = threading.Thread(target=log_worker, args=(i,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()
"
```

## Troubleshooting

### Common Issues

1. **Logs not appearing**: Check LOG_LEVEL configuration
2. **Missing metadata**: Ensure ENABLE_FILE_LINE_INFO=true
3. **Context not persisting**: Check context management setup
4. **Performance issues**: Verify log level configuration
5. **Colored logs not working**: Check ENABLE_COLORED_LOGS setting

### Debug Mode

```bash
# Enable debug mode for detailed information
LOG_LEVEL=DEBUG LOG_FORMAT=text python -m uvicorn src.api.main:app --reload
```

### Log Analysis

```bash
# Filter logs by level
grep '"level":"error"' logs/app.log

# Filter logs by module
grep '"logger":"src.api"' logs/app.log

# Filter logs by user
grep '"user_id":"123"' logs/app.log
```

## Expected Results

After running all tests, you should see:

1. **Structured Logs**: Consistent JSON/text format with metadata
2. **Colored Output**: Development-friendly colored console logs
3. **Context Management**: Proper context propagation across requests
4. **Dynamic Configuration**: Runtime log level changes working
5. **Environment Defaults**: Smart defaults based on environment
6. **Per-module Control**: Different log levels for different modules
7. **Input Validation**: Comprehensive validation with detailed errors
8. **Test Isolation**: Tests running without external dependencies
9. **API Endpoints**: Logging management endpoints working correctly
10. **Performance**: Efficient logging without performance impact

## Success Criteria

- ✅ All tests pass
- ✅ Logs are properly structured and formatted
- ✅ Metadata is included in log messages
- ✅ Colored logs work in development
- ✅ Context management works correctly
- ✅ Dynamic log level changes work
- ✅ Environment-based defaults work
- ✅ Per-module configuration works
- ✅ Input validation provides detailed errors
- ✅ Test isolation works without external dependencies
- ✅ API endpoints for logging management work
- ✅ Performance is acceptable under load
