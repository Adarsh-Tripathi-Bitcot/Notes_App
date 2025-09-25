# RESTful API Design in Notes App

## Overview

The Notes App follows REST (Representational State Transfer) principles to create a clean, intuitive, and maintainable API. This document explains how RESTful design is implemented throughout the application.

## REST Principles

### 1. Stateless
Each request contains all necessary information to process it. The server doesn't store client context between requests.

```python
# Each request is independent
@router.post("/login")
async def login(login_data: UserLogin):
    # No server-side session state
    return auth_service.login_user(login_data)
```

### 2. Client-Server Architecture
Clear separation between client and server responsibilities.

```python
# Server provides data and business logic
@router.get("/notes/{note_id}")
async def get_note(note_id: int, current_user: User = Depends(get_current_user)):
    return note_service.get_note(note_id, current_user.id)
```

### 3. Uniform Interface
Consistent interface design across all resources.

```python
# Consistent URL patterns
GET    /api/v1/notes/          # List notes
POST   /api/v1/notes/          # Create note
GET    /api/v1/notes/{id}      # Get specific note
PUT    /api/v1/notes/{id}      # Update note
DELETE /api/v1/notes/{id}      # Delete note
```

### 4. Layered System
API is organized in layers with clear responsibilities.

```
Client → API Gateway → Application → Database
```

## Resource Design

### 1. Resource Naming

**Good Resource Names**:
```
/api/v1/users          # Collection of users
/api/v1/users/123      # Specific user
/api/v1/notes          # Collection of notes
/api/v1/notes/456      # Specific note
```

**Bad Resource Names**:
```
/api/v1/getUsers       # Verb in URL
/api/v1/user           # Singular for collection
/api/v1/notes/123/edit # Action in URL
```

### 2. HTTP Methods

| Method | Purpose | Example |
|--------|---------|---------|
| GET | Retrieve resource(s) | `GET /api/v1/notes` |
| POST | Create new resource | `POST /api/v1/notes` |
| PUT | Update entire resource | `PUT /api/v1/notes/123` |
| PATCH | Partial update | `PATCH /api/v1/notes/123` |
| DELETE | Remove resource | `DELETE /api/v1/notes/123` |

### 3. Status Codes

```python
# Success responses
200 OK              # Successful GET, PUT, PATCH
201 Created         # Successful POST
204 No Content      # Successful DELETE

# Client error responses
400 Bad Request     # Invalid request data
401 Unauthorized    # Authentication required
403 Forbidden       # Insufficient permissions
404 Not Found       # Resource not found
422 Unprocessable Entity # Validation errors

# Server error responses
500 Internal Server Error # Server error
```

## API Endpoints Design

### 1. User Management

```python
# User registration
POST /api/v1/users/register
{
    "email": "user@example.com",
    "username": "username",
    "password": "password123",
    "confirm_password": "password123"
}

# User login
POST /api/v1/users/login
{
    "email": "user@example.com",
    "password": "password123"
}

# Get current user
GET /api/v1/users/me
Authorization: Bearer <token>

# Update user profile
PUT /api/v1/users/me
Authorization: Bearer <token>
{
    "first_name": "John",
    "last_name": "Doe"
}

# Change password
PUT /api/v1/users/me/password
Authorization: Bearer <token>
{
    "current_password": "oldpassword",
    "new_password": "newpassword123",
    "confirm_password": "newpassword123"
}
```

### 2. Note Management

```python
# Create note
POST /api/v1/notes/
Authorization: Bearer <token>
{
    "title": "My Note",
    "content": "Note content",
    "is_public": false,
    "is_pinned": false
}

# Get user's notes
GET /api/v1/notes/?page=1&per_page=10&status=active
Authorization: Bearer <token>

# Get specific note
GET /api/v1/notes/123
Authorization: Bearer <token>

# Update note
PUT /api/v1/notes/123
Authorization: Bearer <token>
{
    "title": "Updated Title",
    "content": "Updated content"
}

# Update note status
PUT /api/v1/notes/123/status
Authorization: Bearer <token>
{
    "status": "archived"
}

# Delete note
DELETE /api/v1/notes/123
Authorization: Bearer <token>

# Search notes
POST /api/v1/notes/search
Authorization: Bearer <token>
{
    "query": "search term",
    "status": "active",
    "page": 1,
    "per_page": 10
}

# Bulk operations
POST /api/v1/notes/bulk-action
Authorization: Bearer <token>
{
    "note_ids": [1, 2, 3],
    "action": "archive"
}
```

### 3. Public Notes

```python
# Get public notes
GET /api/v1/notes/public?page=1&per_page=10&search=term

# No authentication required for public notes
```

## Request/Response Design

### 1. Request Headers

```python
# Common headers
Content-Type: application/json
Authorization: Bearer <jwt_token>
Accept: application/json
```

### 2. Response Format

```python
# Success response
{
    "id": 123,
    "title": "My Note",
    "content": "Note content",
    "status": "active",
    "is_public": false,
    "is_pinned": false,
    "owner_id": 456,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}

# Error response
{
    "error": {
        "message": "Validation failed",
        "status_code": 422,
        "code": "VALIDATION_ERROR",
        "details": {
            "validation_errors": [
                {
                    "field": "email",
                    "message": "Invalid email format",
                    "type": "value_error.email"
                }
            ]
        }
    }
}

# List response with pagination
{
    "notes": [...],
    "total": 100,
    "page": 1,
    "per_page": 10,
    "total_pages": 10
}
```

### 3. Pagination

```python
# Query parameters
GET /api/v1/notes/?page=1&per_page=10&status=active&search=term

# Response
{
    "data": [...],
    "pagination": {
        "page": 1,
        "per_page": 10,
        "total": 100,
        "total_pages": 10,
        "has_next": true,
        "has_prev": false
    }
}
```

## Authentication & Authorization

### 1. JWT Authentication

```python
# Login endpoint
POST /api/v1/users/login
{
    "email": "user@example.com",
    "password": "password123"
}

# Response
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 3600
}

# Using token
GET /api/v1/notes/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### 2. Authorization Levels

```python
# Public endpoints (no authentication)
GET /api/v1/notes/public
GET /health

# User endpoints (authentication required)
GET /api/v1/users/me
POST /api/v1/notes/
GET /api/v1/notes/

# Resource-specific authorization
GET /api/v1/notes/123  # User can only access their own notes
```

## Error Handling

### 1. Standard Error Format

```python
{
    "error": {
        "message": "Human-readable error message",
        "status_code": 400,
        "code": "ERROR_CODE",
        "details": {
            "field": "additional_info"
        }
    }
}
```

### 2. Common Error Codes

```python
# Authentication errors
401 Unauthorized
{
    "error": {
        "message": "Authentication required",
        "status_code": 401,
        "code": "AUTHENTICATION_ERROR"
    }
}

# Validation errors
422 Unprocessable Entity
{
    "error": {
        "message": "Validation failed",
        "status_code": 422,
        "code": "VALIDATION_ERROR",
        "details": {
            "validation_errors": [...]
        }
    }
}

# Not found errors
404 Not Found
{
    "error": {
        "message": "Note not found",
        "status_code": 404,
        "code": "NOT_FOUND"
    }
}
```

## API Versioning

### 1. URL Versioning

```python
# Current version
/api/v1/users
/api/v1/notes

# Future version
/api/v2/users
/api/v2/notes
```

### 2. Header Versioning

```python
# Request header
Accept: application/vnd.notesapp.v1+json

# Response header
Content-Type: application/vnd.notesapp.v1+json
```

## Content Negotiation

### 1. Supported Formats

```python
# JSON (default)
Accept: application/json

# Alternative formats (future)
Accept: application/xml
Accept: text/csv
```

### 2. Response Format

```python
# JSON response
Content-Type: application/json

# Error response
Content-Type: application/json
```

## Filtering and Sorting

### 1. Query Parameters

```python
# Filtering
GET /api/v1/notes/?status=active&is_public=false

# Sorting
GET /api/v1/notes/?sort=created_at&order=desc

# Search
GET /api/v1/notes/?search=keyword

# Combined
GET /api/v1/notes/?status=active&sort=created_at&order=desc&page=1&per_page=10
```

### 2. Advanced Filtering

```python
# Date range
GET /api/v1/notes/?created_after=2024-01-01&created_before=2024-12-31

# Multiple values
GET /api/v1/notes/?status=active,archived

# Nested filtering
GET /api/v1/notes/?owner.is_active=true
```

## API Documentation

### 1. OpenAPI/Swagger

```python
# Auto-generated documentation
GET /docs          # Swagger UI
GET /redoc         # ReDoc
GET /openapi.json  # OpenAPI schema
```

### 2. Documentation Standards

```python
@router.post(
    "/notes/",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new note",
    description="Create a new note for the authenticated user",
    responses={
        201: {"description": "Note created successfully"},
        401: {"description": "Authentication required"},
        422: {"description": "Validation error"}
    }
)
async def create_note(
    note_data: NoteCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new note."""
    return note_service.create_note(note_data, current_user.id)
```

## Performance Considerations

### 1. Pagination

```python
# Always paginate large collections
GET /api/v1/notes/?page=1&per_page=10

# Provide total count
{
    "data": [...],
    "total": 1000,
    "page": 1,
    "per_page": 10
}
```

### 2. Caching

```python
# Cache headers
Cache-Control: public, max-age=3600
ETag: "1234567890"
Last-Modified: Wed, 01 Jan 2024 00:00:00 GMT
```

### 3. Compression

```python
# Response compression
Content-Encoding: gzip
Content-Type: application/json
```

## Security Considerations

### 1. HTTPS

```python
# Always use HTTPS in production
# Redirect HTTP to HTTPS
```

### 2. CORS

```python
# Configure CORS properly
CORS_ORIGINS = ["https://app.example.com", "https://admin.example.com"]
```

### 3. Rate Limiting

```python
# Implement rate limiting
# 100 requests per minute per user
```

## Testing API Endpoints

### 1. Unit Testing

```python
def test_create_note():
    response = client.post(
        "/api/v1/notes/",
        json={"title": "Test Note", "content": "Test content"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Note"
```

### 2. Integration Testing

```python
def test_note_crud_flow():
    # Create note
    create_response = client.post("/api/v1/notes/", json=note_data)
    note_id = create_response.json()["id"]

    # Get note
    get_response = client.get(f"/api/v1/notes/{note_id}")
    assert get_response.status_code == 200

    # Update note
    update_response = client.put(f"/api/v1/notes/{note_id}", json=update_data)
    assert update_response.status_code == 200

    # Delete note
    delete_response = client.delete(f"/api/v1/notes/{note_id}")
    assert delete_response.status_code == 204
```

## Best Practices

### 1. Consistent Naming

```python
# Use plural nouns for collections
/api/v1/users
/api/v1/notes

# Use singular nouns for specific resources
/api/v1/users/123
/api/v1/notes/456
```

### 2. HTTP Methods

```python
# Use appropriate HTTP methods
GET    # Retrieve data
POST   # Create new resources
PUT    # Update entire resource
PATCH  # Partial updates
DELETE # Remove resources
```

### 3. Status Codes

```python
# Use appropriate status codes
200 OK              # Success
201 Created         # Resource created
204 No Content      # Success with no content
400 Bad Request     # Client error
401 Unauthorized    # Authentication required
403 Forbidden       # Insufficient permissions
404 Not Found       # Resource not found
422 Unprocessable Entity # Validation error
500 Internal Server Error # Server error
```

### 4. Error Handling

```python
# Provide meaningful error messages
{
    "error": {
        "message": "Note not found",
        "status_code": 404,
        "code": "NOT_FOUND"
    }
}
```

## Conclusion

The RESTful API design in the Notes App provides:

- **Consistency**: Uniform interface across all endpoints
- **Intuitiveness**: Clear and predictable API structure
- **Scalability**: Easy to extend and maintain
- **Standards Compliance**: Follows REST principles
- **Developer Experience**: Clear documentation and error handling

By following RESTful design principles, the Notes App API is maintainable, scalable, and easy to use for both developers and clients.
