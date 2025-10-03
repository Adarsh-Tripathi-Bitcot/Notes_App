# Complete API Endpoints Documentation

## Overview

This document provides comprehensive documentation for all API endpoints in the Notes App, including request/response schemas, authentication requirements, and usage examples.

## Authentication

The Notes App uses **HTTPBearer** authentication with JWT tokens. All protected endpoints require a valid JWT token in the Authorization header.

### Authentication Header Format
```
Authorization: Bearer <your_jwt_token>
```

## User Endpoints

### 1. User Registration
**POST** `/api/v1/users/register`

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "SecurePassword123!",
  "confirm_password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

### 2. User Login
**POST** `/api/v1/users/login`

Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 3. Get Current User
**GET** `/api/v1/users/me`

Get current authenticated user information.

**Headers:** `Authorization: Bearer <token>`

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

### 4. User Statistics
**GET** `/api/v1/users/me/stats`

Get user statistics including note counts.

**Headers:** `Authorization: Bearer <token>`

**Response (200 OK):**
```json
{
  "total_notes": 25,
  "active_notes": 20,
  "archived_notes": 5,
  "public_notes": 3,
  "pinned_notes": 2
}
```

## Notes Endpoints

### 1. Get All Notes
**GET** `/api/v1/notes/`

Get paginated list of user's notes with optional filtering and search.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page` (int, optional): Page number (default: 1)
- `per_page` (int, optional): Notes per page (default: 10, max: 100)
- `status` (string, optional): Filter by status (`active`, `archived`, `deleted`)
- `search` (string, optional): Search query for title and content

**Example Request:**
```
GET /api/v1/notes/?page=1&per_page=10&status=active&search=important
```

**Response (200 OK):**
```json
{
  "notes": [
    {
      "id": 1,
      "title": "Important Note",
      "content": "This is an important note",
      "summary": "Summary of the note",
      "status": "active",
      "is_public": false,
      "is_pinned": true,
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "per_page": 10,
  "total_pages": 3
}
```

### 2. Create Note
**POST** `/api/v1/notes/`

Create a new note.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "title": "New Note",
  "content": "This is the content of the note",
  "summary": "Optional summary",
  "is_public": false,
  "is_pinned": false
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "title": "New Note",
  "content": "This is the content of the note",
  "summary": "Optional summary",
  "status": "active",
  "is_public": false,
  "is_pinned": false,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

### 3. Get Note by ID
**GET** `/api/v1/notes/{note_id}`

Get a specific note by ID.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `note_id` (int): Note ID

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Note Title",
  "content": "Note content",
  "summary": "Note summary",
  "status": "active",
  "is_public": false,
  "is_pinned": false,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

### 4. Update Note
**PUT** `/api/v1/notes/{note_id}`

Update an existing note.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `note_id` (int): Note ID

**Request Body:**
```json
{
  "title": "Updated Note Title",
  "content": "Updated content",
  "summary": "Updated summary",
  "is_public": true,
  "is_pinned": true
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Updated Note Title",
  "content": "Updated content",
  "summary": "Updated summary",
  "status": "active",
  "is_public": true,
  "is_pinned": true,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

### 5. Delete Note
**DELETE** `/api/v1/notes/{note_id}`

Delete a note (soft delete - sets status to 'deleted').

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `note_id` (int): Note ID

**Response (200 OK):**
```json
{
  "message": "Note deleted successfully"
}
```

### 6. Update Note Status
**PATCH** `/api/v1/notes/{note_id}/status`

Update the status of a note.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `note_id` (int): Note ID

**Request Body:**
```json
{
  "status": "archived"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Note Title",
  "content": "Note content",
  "summary": "Note summary",
  "status": "archived",
  "is_public": false,
  "is_pinned": false,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

### 7. Advanced Note Search
**POST** `/api/v1/notes/search`

Advanced search with multiple criteria.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "query": "search term",
  "status": "active",
  "is_public": false,
  "is_pinned": true,
  "created_after": "2025-01-01T00:00:00Z",
  "created_before": "2025-12-31T23:59:59Z",
  "page": 1,
  "per_page": 10
}
```

**Response (200 OK):**
```json
{
  "notes": [
    {
      "id": 1,
      "title": "Matching Note",
      "content": "Content matching search term",
      "summary": "Summary",
      "status": "active",
      "is_public": false,
      "is_pinned": true,
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "per_page": 10,
  "total_pages": 1
}
```

### 8. Note Statistics
**GET** `/api/v1/notes/stats/overview`

Get comprehensive note statistics for the current user.

**Headers:** `Authorization: Bearer <token>`

**Response (200 OK):**
```json
{
  "total_notes": 25,
  "active_notes": 20,
  "archived_notes": 5,
  "public_notes": 3,
  "pinned_notes": 2,
  "created_today": 2,
  "created_this_week": 8,
  "created_this_month": 15
}
```

### 9. Bulk Actions
**POST** `/api/v1/notes/bulk-action`

Perform bulk actions on multiple notes.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "note_ids": [1, 2, 3, 4, 5],
  "action": "archive"
}
```

**Supported Actions:**
- `archive` - Archive multiple notes
- `unarchive` - Unarchive multiple notes
- `pin` - Pin multiple notes
- `unpin` - Unpin multiple notes
- `make_public` - Make multiple notes public
- `make_private` - Make multiple notes private
- `delete` - Delete multiple notes

**Response (200 OK):**
```json
{
  "message": "Bulk action completed successfully",
  "affected_count": 5
}
```

### 10. Get Public Notes
**GET** `/api/v1/notes/public`

Get public notes from all users.

**Query Parameters:**
- `page` (int, optional): Page number (default: 1)
- `per_page` (int, optional): Notes per page (default: 10, max: 100)
- `search` (string, optional): Search query

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Public Note",
    "content": "This is a public note",
    "summary": "Public note summary",
    "status": "active",
    "is_public": true,
    "is_pinned": false,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  }
]
```

## Logging Management Endpoints

### 1. Get Logging Status
**GET** `/api/v1/logging/status`

Get current logging configuration status.

**Response (200 OK):**
```json
{
  "message": "Logging status retrieved successfully",
  "level": "DEBUG",
  "module": "root"
}
```

### 2. Set Log Level
**POST** `/api/v1/logging/set-level`

Set log level for a specific module or globally.

**Request Body:**
```json
{
  "level": "DEBUG",
  "module": "src.api"
}
```

**Response (200 OK):**
```json
{
  "message": "Log level set to DEBUG for src.api",
  "level": "DEBUG",
  "module": "src.api"
}
```

### 3. Get Module Log Level
**GET** `/api/v1/logging/level/{module_name}`

Get current log level for a specific module.

**Path Parameters:**
- `module_name` (string): Module name (e.g., "src.api", "src.core")

**Response (200 OK):**
```json
{
  "message": "Log level for src.api is DEBUG",
  "level": "DEBUG",
  "module": "src.api"
}
```

### 4. List Configured Modules
**GET** `/api/v1/logging/modules`

List all configured modules and their log levels.

**Response (200 OK):**
```json
{
  "src.api": "DEBUG",
  "src.core": "INFO",
  "src.services": "WARNING",
  "root": "DEBUG"
}
```

### 5. Reset Log Levels
**POST** `/api/v1/logging/reset`

Reset all log levels to their default configuration.

**Response (200 OK):**
```json
{
  "message": "All log levels reset to default configuration"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": {
    "message": "Validation error",
    "status_code": 400,
    "code": "VALIDATION_ERROR",
    "details": {
      "field": "Field validation error message"
    }
  }
}
```

### 401 Unauthorized
```json
{
  "error": {
    "message": "Authentication required",
    "status_code": 401,
    "code": "AUTHENTICATION_ERROR"
  }
}
```

### 403 Forbidden
```json
{
  "error": {
    "message": "Access denied",
    "status_code": 403,
    "code": "AUTHORIZATION_ERROR"
  }
}
```

### 404 Not Found
```json
{
  "error": {
    "message": "Resource not found",
    "status_code": 404,
    "code": "NOT_FOUND_ERROR"
  }
}
```

### 422 Unprocessable Entity
```json
{
  "error": {
    "message": "Invalid input data",
    "status_code": 422,
    "code": "VALIDATION_ERROR",
    "details": {
      "field": "Field validation error message"
    }
  }
}
```

### 500 Internal Server Error
```json
{
  "error": {
    "message": "An unexpected error occurred",
    "status_code": 500,
    "code": "INTERNAL_SERVER_ERROR"
  }
}
```

## Authentication in Swagger UI

The Swagger UI now uses **HTTPBearer** authentication. To test protected endpoints:

1. Click the "Authorize" button in Swagger UI
2. Enter your JWT token in the "Value" field
3. Click "Authorize"
4. The token will be automatically included in all requests

**Note:** The token should be entered without the "Bearer " prefix - just the token itself.

## Testing with cURL

### Get JWT Token
```bash
curl -X POST "http://localhost:8000/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

### Use Token in Requests
```bash
curl -X GET "http://localhost:8000/api/v1/notes/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Rate Limiting

Currently, no rate limiting is implemented. In production, consider implementing rate limiting to prevent abuse.

## CORS Configuration

The API supports CORS for cross-origin requests. Configure allowed origins in the environment variables.

## Pagination

All list endpoints support pagination with the following parameters:
- `page`: Page number (starts from 1)
- `per_page`: Number of items per page (max 100)

The response includes pagination metadata:
- `total`: Total number of items
- `page`: Current page number
- `per_page`: Items per page
- `total_pages`: Total number of pages
