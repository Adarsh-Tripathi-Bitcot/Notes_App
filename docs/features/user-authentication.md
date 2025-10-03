# User Authentication Features

This document describes the comprehensive user authentication and security features implemented in the Notes App.

## Overview

The authentication system provides secure user management with JWT-based authentication, password security, and comprehensive user operations.

## Key Features

### 1. JWT Token Authentication
- **Secure token generation** with configurable expiration
- **Token refresh mechanism** for extended sessions
- **Automatic token validation** on protected endpoints
- **User context extraction** from JWT payload

### 2. User Registration & Management
- **User registration** with email validation
- **Password hashing** using bcrypt
- **User profile management** (update, deactivate)
- **Email uniqueness validation**

### 3. Security Features
- **Password strength validation**
- **Secure password hashing** with salt
- **JWT secret key management**
- **Authentication bypass** for testing

## API Endpoints

### Authentication Endpoints
- `POST /api/v1/users/register` - User registration
- `POST /api/v1/users/login` - User login
- `POST /api/v1/users/refresh` - Token refresh
- `POST /api/v1/users/logout` - User logout

### User Management Endpoints
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update user profile
- `POST /api/v1/users/change-password` - Change password
- `DELETE /api/v1/users/me` - Deactivate account

## Security Implementation

### Password Security
```python
# Password hashing with bcrypt
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Password verification
is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash)
```

### JWT Token Management
```python
# Token generation
payload = {
    "user_id": user.id,
    "email": user.email,
    "exp": datetime.utcnow() + timedelta(hours=24)
}
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
```

## Configuration

### Environment Variables
```bash
# JWT Configuration
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Security Configuration
BCRYPT_ROUNDS=12
PASSWORD_MIN_LENGTH=8
```

## Usage Examples

### User Registration
```python
# Register new user
user_data = {
    "email": "user@example.com",
    "password": "SecurePassword123",
    "full_name": "John Doe"
}
response = client.post("/api/v1/users/register", json=user_data)
```

### User Login
```python
# Login and get token
login_data = {
    "email": "user@example.com",
    "password": "SecurePassword123"
}
response = client.post("/api/v1/users/login", json=login_data)
token = response.json()["access_token"]
```

### Protected Endpoint Access
```python
# Use token for authenticated requests
headers = {"Authorization": f"Bearer {token}"}
response = client.get("/api/v1/users/me", headers=headers)
```

## Benefits

1. **Security**: Robust password hashing and JWT token management
2. **Scalability**: Stateless authentication suitable for distributed systems
3. **Flexibility**: Configurable token expiration and security settings
4. **User Experience**: Seamless login/logout with token refresh
5. **Testing**: Authentication bypass mode for development/testing

## Testing

The authentication system includes comprehensive tests:
- User registration and validation
- Login and token generation
- Password security and hashing
- JWT token validation and refresh
- Protected endpoint access

Run the tests with:
```bash
python -m pytest tests/api/test_auth.py -v
```
