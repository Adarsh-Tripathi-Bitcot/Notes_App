# Note Management Features

This document describes the comprehensive note management system implemented in the Notes App.

## Overview

The note management system provides full CRUD operations for notes with advanced features like search, filtering, pagination, and status management.

## Key Features

### 1. Note CRUD Operations
- **Create notes** with title, content, and metadata
- **Read notes** with pagination and filtering
- **Update notes** with validation
- **Delete notes** with soft delete support

### 2. Advanced Search & Filtering
- **Text search** across title and content
- **Status filtering** (active, archived, deleted)
- **Date range filtering** for creation/update dates
- **Public/private note filtering**

### 3. Note Organization
- **Note status management** (active, archived, deleted)
- **Pinning system** for important notes
- **Public/private visibility** controls
- **Auto-generated summaries**

### 4. Pagination & Performance
- **Configurable page sizes** (1-100 items)
- **Efficient database queries** with proper indexing
- **Response metadata** for pagination navigation

## API Endpoints

### Note Management Endpoints
- `POST /api/v1/notes/` - Create new note
- `GET /api/v1/notes/` - List notes with pagination/filtering
- `GET /api/v1/notes/{note_id}` - Get specific note
- `PUT /api/v1/notes/{note_id}` - Update note
- `DELETE /api/v1/notes/{note_id}` - Delete note

### Advanced Operations
- `POST /api/v1/notes/search` - Advanced search
- `POST /api/v1/notes/bulk-action` - Bulk operations
- `GET /api/v1/notes/stats` - Note statistics

## Data Models

### Note Schema
```python
class Note:
    id: int
    title: str
    content: str
    summary: str
    is_public: bool
    is_pinned: bool
    status: NoteStatus
    owner_id: int
    created_at: datetime
    updated_at: datetime
```

### Note Status Enum
```python
class NoteStatus(Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
```

## Usage Examples

### Create Note
```python
note_data = {
    "title": "My Important Note",
    "content": "This is the content of my note...",
    "is_public": False,
    "is_pinned": True
}
response = client.post("/api/v1/notes/", json=note_data)
```

### Search Notes
```python
search_params = {
    "query": "important",
    "status": "active",
    "is_public": False,
    "page": 1,
    "per_page": 10
}
response = client.get("/api/v1/notes/", params=search_params)
```

### Update Note
```python
update_data = {
    "title": "Updated Title",
    "content": "Updated content...",
    "is_pinned": False
}
response = client.put("/api/v1/notes/123", json=update_data)
```

## Advanced Features

### Auto-Generated Summaries
```python
# Automatic summary generation from content
def generate_summary(content: str, max_length: int = 150) -> str:
    # Extract first sentence or truncate content
    sentences = content.split('.')
    if sentences[0]:
        return sentences[0][:max_length] + "..."
    return content[:max_length] + "..."
```

### Bulk Operations
```python
# Bulk status update
bulk_action = {
    "action": "archive",
    "note_ids": [1, 2, 3, 4, 5]
}
response = client.post("/api/v1/notes/bulk-action", json=bulk_action)
```

### Note Statistics
```python
# Get user note statistics
response = client.get("/api/v1/notes/stats")
stats = response.json()
# Returns: total_notes, active_notes, archived_notes, public_notes
```

## Configuration

### Pagination Settings
```python
# Default pagination configuration
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100
MIN_PAGE_SIZE = 1
```

### Search Configuration
```python
# Search settings
SEARCH_MIN_QUERY_LENGTH = 2
MAX_SEARCH_RESULTS = 1000
ENABLE_FULL_TEXT_SEARCH = True
```

## Benefits

1. **Flexibility**: Comprehensive CRUD operations with advanced features
2. **Performance**: Efficient pagination and search with database optimization
3. **User Experience**: Intuitive note organization and management
4. **Scalability**: Designed to handle large numbers of notes efficiently
5. **Security**: User-specific note access with proper authorization

## Testing

The note management system includes comprehensive tests:
- CRUD operation testing
- Search and filtering functionality
- Pagination and performance testing
- Authorization and security testing
- Bulk operation testing

Run the tests with:
```bash
python -m pytest tests/api/test_notes.py -v
```
