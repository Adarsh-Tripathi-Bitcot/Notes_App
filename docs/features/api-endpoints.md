# API Endpoints Features

This document describes the RESTful API design and endpoint features implemented in the Notes App.

## Overview

The API follows RESTful principles with comprehensive endpoint coverage, proper HTTP status codes, and consistent response formats.

## API Design Principles

### 1. RESTful Architecture
- **Resource-based URLs** with clear naming conventions
- **HTTP methods** used appropriately (GET, POST, PUT, DELETE)
- **Stateless communication** with JWT authentication
- **Consistent response formats** across all endpoints

### 2. API Versioning
- **Versioned endpoints** (`/api/v1/`)
- **Backward compatibility** considerations
- **Clear versioning strategy** for future updates

### 3. Response Standards
- **Consistent JSON responses** with proper structure
- **Standardized error handling** with meaningful messages
- **Pagination metadata** for list endpoints
- **Request/response logging** for debugging

## Endpoint Categories

### Authentication Endpoints
```
POST   /api/v1/users/register     # User registration
POST   /api/v1/users/login        # User login
POST   /api/v1/users/refresh      # Token refresh
POST   /api/v1/users/logout       # User logout
```

### User Management Endpoints
```
GET    /api/v1/users/me           # Get current user
PUT    /api/v1/users/me           # Update user profile
POST   /api/v1/users/change-password  # Change password
DELETE /api/v1/users/me           # Deactivate account
```

### Note Management Endpoints
```
GET    /api/v1/notes/             # List notes (paginated)
POST   /api/v1/notes/             # Create note
GET    /api/v1/notes/{id}         # Get specific note
PUT    /api/v1/notes/{id}         # Update note
DELETE /api/v1/notes/{id}         # Delete note
POST   /api/v1/notes/search       # Advanced search
POST   /api/v1/notes/bulk-action  # Bulk operations
GET    /api/v1/notes/stats        # Note statistics
```

### System Endpoints
```
GET    /health                    # Health check
GET    /                          # API information
GET    /docs                      # API documentation (dev only)
```

## Response Formats

### Success Response
```json
{
  "data": { ... },
  "message": "Operation successful",
  "status": "success"
}
```

### Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": { ... }
  },
  "status": "error"
}
```

### Paginated Response
```json
{
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 100,
    "pages": 10,
    "has_next": true,
    "has_prev": false
  },
  "status": "success"
}
```

## HTTP Status Codes

### Success Codes
- `200 OK` - Successful GET, PUT requests
- `201 Created` - Successful POST requests
- `204 No Content` - Successful DELETE requests

### Client Error Codes
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation errors

### Server Error Codes
- `500 Internal Server Error` - Server-side errors

## Request/Response Examples

### Create Note
```http
POST /api/v1/notes/
Content-Type: application/json
Authorization: Bearer <token>

{
  "title": "My Note",
  "content": "Note content...",
  "is_public": false,
  "is_pinned": true
}
```

**Response:**
```json
{
  "data": {
    "id": 123,
    "title": "My Note",
    "content": "Note content...",
    "is_public": false,
    "is_pinned": true,
    "status": "active",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "message": "Note created successfully",
  "status": "success"
}
```

### List Notes with Pagination
```http
GET /api/v1/notes/?page=1&per_page=10&status=active&search=important
Authorization: Bearer <token>
```

**Response:**
```json
{
  "data": [
    {
      "id": 123,
      "title": "Important Note",
      "summary": "This is an important note...",
      "is_public": false,
      "is_pinned": true,
      "status": "active",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 25,
    "pages": 3,
    "has_next": true,
    "has_prev": false
  },
  "status": "success"
}
```

## Error Handling

### Validation Errors
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Input validation failed",
    "details": {
      "title": ["This field is required"],
      "email": ["Invalid email format"]
    }
  },
  "status": "error"
}
```

### Authentication Errors
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required",
    "details": "Valid JWT token required"
  },
  "status": "error"
}
```

## API Documentation

### Interactive Documentation
- **Swagger UI** available at `/docs` (development only)
- **ReDoc** available at `/redoc` (development only)
- **OpenAPI schema** at `/openapi.json`

### Documentation Features
- **Interactive testing** interface
- **Request/response examples** for all endpoints
- **Authentication testing** with token input
- **Schema validation** and examples

## Benefits

1. **Consistency**: Uniform response formats and error handling
2. **Usability**: Clear, intuitive endpoint design
3. **Documentation**: Comprehensive API documentation
4. **Testing**: Built-in testing interface
5. **Scalability**: RESTful design supports future growth

## Testing

The API endpoints include comprehensive tests:
- Endpoint functionality testing
- Authentication and authorization testing
- Error handling and validation testing
- Response format validation
- Performance and load testing

Run the tests with:
```bash
python -m pytest tests/api/ -v
```
