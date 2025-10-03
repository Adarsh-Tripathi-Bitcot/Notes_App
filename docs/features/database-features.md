# Database Features

This document describes the database management and data persistence features implemented in the Notes App.

## Overview

The database system provides robust data persistence with PostgreSQL, efficient querying, migration management, and data integrity features.

## Key Features

### 1. Database Management
- **PostgreSQL integration** with SQLAlchemy ORM
- **Connection pooling** for optimal performance
- **Transaction management** with rollback support
- **Database health monitoring** and connection testing

### 2. Migration System
- **Alembic-based migrations** for schema versioning
- **Automatic migration generation** from model changes
- **Migration rollback** capabilities
- **Database seeding** for development/testing

### 3. Data Models
- **User model** with authentication fields
- **Note model** with rich metadata
- **Relationship management** between entities
- **Data validation** at the database level

### 4. Query Optimization
- **Efficient pagination** with proper indexing
- **Search optimization** with full-text search capabilities
- **Query performance monitoring**
- **Database connection management**

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    username VARCHAR(100) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Notes Table
```sql
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    summary TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    is_pinned BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'active',
    owner_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes
```sql
-- Performance indexes
CREATE INDEX idx_notes_owner_id ON notes(owner_id);
CREATE INDEX idx_notes_status ON notes(status);
CREATE INDEX idx_notes_created_at ON notes(created_at);
CREATE INDEX idx_notes_is_public ON notes(is_public);

-- Full-text search index
CREATE INDEX idx_notes_search ON notes USING gin(to_tsvector('english', title || ' ' || content));
```

## Migration Management

### Creating Migrations
```bash
# Generate migration from model changes
alembic revision --autogenerate -m "Add new field to notes table"

# Create empty migration
alembic revision -m "Custom migration description"
```

### Applying Migrations
```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade +1

# Rollback migration
alembic downgrade -1
```

### Migration Files
```python
# Example migration file
def upgrade():
    op.add_column('notes', sa.Column('is_pinned', sa.Boolean(), nullable=False, server_default='false'))
    op.create_index('idx_notes_is_pinned', 'notes', ['is_pinned'])

def downgrade():
    op.drop_index('idx_notes_is_pinned', table_name='notes')
    op.drop_column('notes', 'is_pinned')
```

## Data Access Patterns

### Repository Pattern
```python
class NoteRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, note_data: dict) -> Note:
        note = Note(**note_data)
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return note

    def get_by_id(self, note_id: int, owner_id: int) -> Optional[Note]:
        return self.db.query(Note).filter(
            Note.id == note_id,
            Note.owner_id == owner_id
        ).first()

    def list_notes(self, owner_id: int, skip: int = 0, limit: int = 10) -> List[Note]:
        return self.db.query(Note).filter(
            Note.owner_id == owner_id
        ).offset(skip).limit(limit).all()
```

### Query Optimization
```python
# Efficient pagination with count
def get_notes_paginated(self, owner_id: int, page: int, per_page: int):
    query = self.db.query(Note).filter(Note.owner_id == owner_id)

    # Get total count efficiently
    total = query.count()

    # Get paginated results
    notes = query.offset((page - 1) * per_page).limit(per_page).all()

    return {
        "notes": notes,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page
    }
```

## Database Configuration

### Environment Variables
```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/notes_app
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600
```

### SQLAlchemy Configuration
```python
# Database engine configuration
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,
    echo=False  # Set to True for SQL query logging
)
```

## Data Integrity

### Constraints
```python
# Model-level constraints
class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Unique constraints
    __table_args__ = (
        UniqueConstraint('title', 'owner_id', name='unique_title_per_user'),
    )
```

### Validation
```python
# Database-level validation
class Note(Base):
    title = Column(String(255), nullable=False)
    content = Column(Text)
    is_public = Column(Boolean, default=False)
    status = Column(Enum(NoteStatus), default=NoteStatus.ACTIVE)

    # Check constraints
    __table_args__ = (
        CheckConstraint('length(title) >= 1', name='title_not_empty'),
        CheckConstraint('status IN ("active", "archived", "deleted")', name='valid_status'),
    )
```

## Performance Features

### Connection Pooling
- **Efficient connection reuse** to reduce overhead
- **Configurable pool size** based on application needs
- **Connection health monitoring** and automatic recovery
- **Timeout handling** for long-running queries

### Query Optimization
- **Proper indexing** for frequently queried fields
- **Query analysis** and performance monitoring
- **Lazy loading** for related entities
- **Batch operations** for bulk data processing

## Benefits

1. **Reliability**: Robust data persistence with ACID compliance
2. **Performance**: Optimized queries and connection management
3. **Scalability**: Designed to handle growing data volumes
4. **Maintainability**: Clean migration system and data models
5. **Data Integrity**: Comprehensive validation and constraints

## Testing

The database system includes comprehensive tests:
- Model validation and constraints testing
- Migration testing and rollback verification
- Query performance and optimization testing
- Data integrity and transaction testing
- Connection pooling and error handling testing

Run the tests with:
```bash
python -m pytest tests/unit/test_models.py -v
python -m pytest tests/unit/test_repositories.py -v
```
