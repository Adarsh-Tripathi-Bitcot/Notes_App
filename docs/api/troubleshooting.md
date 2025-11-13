# API Troubleshooting Guide

## Overview

This document summarizes all the fixes applied to resolve issues with the Notes App API endpoints. All endpoints are now fully functional and working correctly.

## Issues Fixed

### 1. GET /api/v1/notes/stats/overview - 422 Error

**Problem**: Missing required fields in the stats response schema.

**Root Cause**: The repository's `get_stats` method was missing `created_this_week` and `created_this_month` fields that were required by the `NoteStats` Pydantic schema.

**Solution**:
- Added missing date calculations in `src/repositories/note_repository.py`
- Fixed import issues with `timedelta` in both repository and service layers
- Updated model imports in `src/models/__init__.py` to resolve relationship issues

**Files Modified**:
- `src/repositories/note_repository.py`
- `src/services/note_management.py`
- `src/models/__init__.py`

### 2. GET /api/v1/notes/ - 500 Error

**Problem**: Internal server error when retrieving paginated notes.

**Root Cause**: The service was returning `Note` objects directly instead of `NoteResponse` objects, causing serialization issues.

**Solution**:
- Updated `get_paginated_notes` method to convert `Note` objects to `NoteResponse` objects
- Fixed model relationship issues by properly importing both `User` and `Note` models

**Files Modified**:
- `src/services/note_management.py`
- `src/models/__init__.py`

### 3. POST /api/v1/notes/search - 422 Error

**Problem**: Search endpoint returning validation error.

**Root Cause**: Similar to the paginated notes issue - returning `Note` objects instead of `NoteResponse` objects.

**Solution**:
- Updated `search_notes` method to return `NoteResponse` objects
- Fixed return type annotation from `Tuple[List[Note], int]` to `Tuple[List[NoteResponse], int]`

**Files Modified**:
- `src/services/note_management.py`

### 4. POST /api/v1/notes/bulk-action - Working but needed testing

**Problem**: Endpoint was working but needed proper testing with existing notes.

**Solution**:
- Created test notes to verify bulk operations
- Confirmed all bulk actions work correctly (archive, unarchive, pin, unpin, etc.)

### 5. HTTPBearer Authentication Implementation

**Problem**: Swagger UI was asking for OAuth2 client credentials instead of JWT tokens.

**Root Cause**: Using `OAuth2PasswordBearer` with `tokenUrl` parameter, which configures OAuth2 client credentials flow.

**Solution**:
- Replaced `OAuth2PasswordBearer` with `HTTPBearer` in both user and notes routers
- Updated `get_current_user_dependency` function to extract token from `token.credentials`
- Removed OAuth2 references from documentation

**Files Modified**:
- `src/api/routers/user_router.py`
- `src/api/routers/notes_router.py`
- `docs/clean-code/type-safe-development.md`

## Technical Details

### Model Import Fix

The main issue was that SQLAlchemy couldn't resolve the `User` relationship in the `Note` model because the `User` model wasn't imported when the `Note` model was loaded.

**Solution**: Updated `src/models/__init__.py` to import both models:

```python
from .user import User
from .note import Note

__all__ = ["User", "Note"]
```

### DateTime Import Fix

Both repository and service layers had incorrect imports for `timedelta`:

**Before**:
```python
from datetime import datetime
# Later: datetime.timedelta()  # This failed
```

**After**:
```python
from datetime import datetime, timedelta
# Later: timedelta()  # This works
```

### HTTPBearer Implementation

**Before** (OAuth2PasswordBearer):
```python
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user_dependency(token: str = Depends(oauth2_scheme)):
    # Extract token directly
```

**After** (HTTPBearer):
```python
from fastapi.security import HTTPBearer
bearer_scheme = HTTPBearer()

def get_current_user_dependency(token: HTTPBearer = Depends(bearer_scheme)):
    token_string = token.credentials  # Extract from credentials
```

## Testing Results

All endpoints now work correctly:

### ✅ Working Endpoints

1. **GET /api/v1/notes/stats/overview** - Returns comprehensive statistics
2. **GET /api/v1/notes/** - Returns paginated notes with search functionality
3. **POST /api/v1/notes/search** - Advanced search with multiple criteria
4. **POST /api/v1/notes/bulk-action** - Bulk operations on multiple notes
5. **All other CRUD endpoints** - Create, read, update, delete operations

### 📊 Sample Responses

**Stats Endpoint**:
```json
{
  "total_notes": 1,
  "active_notes": 0,
  "archived_notes": 1,
  "public_notes": 0,
  "pinned_notes": 0,
  "created_today": 1,
  "created_this_week": 1,
  "created_this_month": 1
}
```

**Search Endpoint**:
```json
{
  "notes": [...],
  "total": 1,
  "page": 1,
  "per_page": 10,
  "total_pages": 1
}
```

**Bulk Action**:
```json
{
  "message": "Bulk action completed successfully",
  "affected_count": 1
}
```

## Swagger UI Authentication

The Swagger UI now works correctly with HTTPBearer authentication:

1. Click "Authorize" button
2. Enter JWT token (without "Bearer " prefix)
3. Click "Authorize"
4. All protected endpoints will work automatically

## Documentation Updates

### New Documentation Files

1. **Complete API Endpoints Documentation** (`docs/api/endpoints.md`)
   - Comprehensive API reference
   - Request/response schemas
   - Authentication instructions
   - Error handling examples

2. **API Troubleshooting Guide** (this document)
   - Detailed explanation of all fixes
   - Technical implementation details
   - Testing results

### Updated Documentation

1. **README.md** - Updated to reflect HTTPBearer authentication and new features
2. **Type Safety Documentation** - Updated examples to use HTTPBearer
3. **API Documentation Links** - Added links to comprehensive API reference

## Verification Commands

To verify all endpoints are working:

```bash
# Start the application
source venv/bin/activate
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Test endpoints (in another terminal)
curl -X POST "http://localhost:8000/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPassword123!"}'

# Use the returned token for other requests
curl -X GET "http://localhost:8000/api/v1/notes/stats/overview" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Common Issues and Solutions

### Issue: "ModuleNotFoundError: No module named 'src'"
**Solution**: Make sure you're running commands from the project root directory.

### Issue: "Database connection failed"
**Solution**:
1. Check if PostgreSQL is running
2. Verify database credentials in `.env` file
3. Run migrations: `alembic upgrade head`

### Issue: "Authentication failed"
**Solution**:
1. Make sure you're using the correct email/password
2. Check if the user exists in the database
3. Verify JWT token is not expired

### Issue: "Validation error"
**Solution**:
1. Check request body format
2. Verify all required fields are present
3. Check data types match the schema

## Conclusion

All API endpoints are now fully functional and properly documented. The application uses HTTPBearer authentication for better Swagger UI integration, and all search, statistics, and bulk operation features work as expected.

The fixes ensure:
- ✅ Proper data serialization with Pydantic schemas
- ✅ Correct model relationships and imports
- ✅ HTTPBearer authentication for better UX
- ✅ Comprehensive error handling
- ✅ Full API documentation
- ✅ Working Swagger UI integration
