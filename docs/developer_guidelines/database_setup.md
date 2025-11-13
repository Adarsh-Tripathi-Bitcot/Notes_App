# Database Setup Guide

## Overview

This guide provides comprehensive instructions for setting up the PostgreSQL database for the Notes App project. The database is used to store user accounts, notes, and other application data.

## Prerequisites

Before setting up the database, ensure you have:

- **PostgreSQL 12+** installed and running
- **Database server** accessible on localhost:5432 (default)
- **Administrative access** to create databases and users
- **Python virtual environment** activated

## Database Configuration

### 1. Environment Variables

The database connection is configured through environment variables in the `.env` file:

```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:root@localhost:5432/Notes_App

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=60

# Application Configuration
APP_NAME=Notes App
DEBUG=true
ENVIRONMENT=development

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# Security
BCRYPT_ROUNDS=12
```

### 2. Database URL Format

The `DATABASE_URL` follows this format:
```
postgresql://username:password@host:port/database_name
```

**Example:**
```
postgresql://postgres:root@localhost:5432/Notes_App
```

## Database Setup Methods

### Method 1: Using psql (Command Line)

```bash
# Connect to PostgreSQL as superuser
psql -U postgres

# Create database
CREATE DATABASE "Notes_App";

# Create user (if not exists)
CREATE USER postgres WITH PASSWORD 'root';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE "Notes_App" TO postgres;

# Connect to the database
\c "Notes_App"

# Exit psql
\q
```

### Method 2: Using createdb Command

```bash
# Create database using createdb command
createdb -U postgres Notes_App

# Set password for user (if needed)
psql -U postgres -c "ALTER USER postgres PASSWORD 'root';"
```

### Method 3: Using pgAdmin (GUI)

1. Open pgAdmin
2. Connect to your PostgreSQL server
3. Right-click on "Databases" → "Create" → "Database"
4. Enter database name: `Notes_App`
5. Click "Save"

## Database Migration Setup

### 1. Initialize Alembic (if not already done)

```bash
# Navigate to migrations directory
cd migrations

# Initialize alembic (if needed)
alembic init migrations

# Update alembic.ini to point to correct script location
# Edit alembic.ini and change:
# script_location = migrations/migrations
```

### 2. Configure Migration Environment

The migration environment is configured in `migrations/migrations/env.py`:

```python
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import our models and settings
from src.core.database import Base
from src.core.config import settings

# Import all models to ensure they are registered with Base
from src.models.user import User
from src.models.note import Note

# Set the database URL from our settings
config.set_main_option("sqlalchemy.url", settings.database_url)

# Set target metadata
target_metadata = Base.metadata
```

### 3. Create and Apply Migrations

```bash
# Create initial migration
alembic -c migrations/alembic.ini revision --autogenerate -m "Initial migration"

# Apply migrations
alembic -c migrations/alembic.ini upgrade head

# Or use the migration handler
python migrations/migration_handler.py upgrade
```

## Database Testing

### 1. Connection Test Script

Use the provided test script to verify your database setup:

```bash

```

**Expected Output:**
```
🚀 Notes App Database Connection Test
==================================================

1️⃣ Testing database connection...
🔗 Testing connection to: postgresql://postgres:root@localhost:5432/Notes_App
✅ Database connection successful!

2️⃣ Getting database information...
📊 Database: Notes_App
📊 Version: PostgreSQL 17.5 (Ubuntu 17.5-1.pgdg22.04+1)

3️⃣ Checking database tables...
✅ Found 3 tables:
  - alembic_version
  - notes
  - users

4️⃣ Verifying required tables...
✅ All required tables present

5️⃣ Checking table structures...
📋 USERS table structure:
  - id: integer NOT NULL
  - email: character varying NOT NULL
  - username: character varying NULL
  - hashed_password: character varying NOT NULL
  - is_active: boolean NOT NULL
  - is_verified: boolean NOT NULL
  - first_name: character varying NULL
  - last_name: character varying NULL
  - bio: text NULL
  - created_at: timestamp with time zone NOT NULL
  - updated_at: timestamp with time zone NOT NULL
  - last_login: timestamp with time zone NULL

📋 NOTES table structure:
  - id: integer NOT NULL
  - title: character varying NOT NULL
  - content: text NOT NULL
  - summary: text NULL
  - status: USER-DEFINED NOT NULL
  - is_public: boolean NOT NULL
  - is_pinned: boolean NOT NULL
  - owner_id: integer NOT NULL
  - created_at: timestamp with time zone NOT NULL
  - updated_at: timestamp with time zone NOT NULL

6️⃣ Testing table access...
✅ Users table accessible (count: 0)
✅ Notes table accessible (count: 0)

==================================================
🎉 All database tests passed!
✅ Your database is properly configured and ready to use.
```

### 2. Manual Database Verification

```bash
# Connect to database
psql -U postgres -d Notes_App

# List all tables
\dt

# Check table structure
\d users
\d notes

# Check data
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM notes;

# Exit
\q
```

## Database Schema

### Users Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | integer | PRIMARY KEY, NOT NULL | Unique user identifier |
| email | varchar | UNIQUE, NOT NULL | User email address |
| username | varchar | UNIQUE, NULL | Username (optional) |
| hashed_password | varchar | NOT NULL | Hashed password |
| is_active | boolean | NOT NULL | Account active status |
| is_verified | boolean | NOT NULL | Email verification status |
| first_name | varchar | NULL | User's first name |
| last_name | varchar | NULL | User's last name |
| bio | text | NULL | User biography |
| created_at | timestamp | NOT NULL | Account creation time |
| updated_at | timestamp | NOT NULL | Last update time |
| last_login | timestamp | NULL | Last login time |

### Notes Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | integer | PRIMARY KEY, NOT NULL | Unique note identifier |
| title | varchar | NOT NULL | Note title |
| content | text | NOT NULL | Note content |
| summary | text | NULL | Note summary |
| status | enum | NOT NULL | Note status (active/archived) |
| is_public | boolean | NOT NULL | Public visibility |
| is_pinned | boolean | NOT NULL | Pinned status |
| owner_id | integer | FOREIGN KEY, NOT NULL | Owner user ID |
| created_at | timestamp | NOT NULL | Creation time |
| updated_at | timestamp | NOT NULL | Last update time |

## Troubleshooting

### Common Issues

#### 1. Connection Refused

**Error:** `psycopg2.OperationalError: could not connect to server`

**Solutions:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL service
sudo systemctl start postgresql

# Check if port 5432 is open
netstat -tlnp | grep 5432
```

#### 2. Authentication Failed

**Error:** `psycopg2.OperationalError: FATAL: password authentication failed`

**Solutions:**
```bash
# Reset password
sudo -u postgres psql
ALTER USER postgres PASSWORD 'root';

# Check pg_hba.conf configuration
sudo nano /etc/postgresql/*/main/pg_hba.conf
# Ensure: local all postgres md5
```

#### 3. Database Does Not Exist

**Error:** `psycopg2.OperationalError: FATAL: database "Notes_App" does not exist`

**Solutions:**
```bash
# Create database
createdb -U postgres Notes_App

# Or using psql
psql -U postgres -c "CREATE DATABASE \"Notes_App\";"
```

#### 4. Permission Denied

**Error:** `psycopg2.OperationalError: FATAL: permission denied for database`

**Solutions:**
```bash
# Grant privileges
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE \"Notes_App\" TO postgres;"

# Check user permissions
psql -U postgres -c "\du"
```

#### 5. Migration Issues

**Error:** `alembic.util.exc.CommandError: Can't locate revision identified by 'head'`

**Solutions:**
```bash
# Check migration status
alembic -c migrations/alembic.ini current

# Create new migration
alembic -c migrations/alembic.ini revision --autogenerate -m "Fix migration"

# Apply migrations
alembic -c migrations/alembic.ini upgrade head
```

### Verification Commands

```bash
# Test database connection
python test_db_connection.py

# Check migration status
alembic -c migrations/alembic.ini current

# List all migrations
alembic -c migrations/alembic.ini history

# Check database tables
psql -U postgres -d Notes_App -c "\dt"

# Check table data
psql -U postgres -d Notes_App -c "SELECT COUNT(*) FROM users;"
psql -U postgres -d Notes_App -c "SELECT COUNT(*) FROM notes;"
```

## Security Considerations

### 1. Database Security

- **Use strong passwords** for database users
- **Limit database access** to application servers only
- **Enable SSL** for production connections
- **Regular backups** of database data
- **Monitor access logs** for suspicious activity

### 2. Environment Variables

- **Never commit** `.env` files to version control
- **Use different credentials** for development and production
- **Rotate secrets** regularly
- **Use environment-specific** configuration files

### 3. Connection Security

```bash
# Production database URL example
DATABASE_URL=postgresql://username:password@host:port/database?sslmode=require

# Development database URL
DATABASE_URL=postgresql://postgres:root@localhost:5432/Notes_App
```

## Performance Optimization

### 1. Database Indexes

The application automatically creates indexes for:
- Primary keys (`id` columns)
- Foreign keys (`owner_id` in notes table)
- Unique constraints (`email`, `username`)
- Search fields (`title` in notes table)

### 2. Connection Pooling

The application uses SQLAlchemy's connection pooling:
- **Pool size:** 5-20 connections (configurable)
- **Max overflow:** 10 additional connections
- **Pool timeout:** 30 seconds
- **Pool recycle:** 3600 seconds (1 hour)

### 3. Query Optimization

- Use **selective queries** to fetch only needed data
- Implement **pagination** for large result sets
- Use **database-level filtering** instead of application filtering
- Monitor **slow queries** and optimize as needed

## Backup and Recovery

### 1. Database Backup

```bash
# Create backup
pg_dump -U postgres -h localhost Notes_App > backup_$(date +%Y%m%d_%H%M%S).sql

# Compressed backup
pg_dump -U postgres -h localhost -Fc Notes_App > backup_$(date +%Y%m%d_%H%M%S).dump
```

### 2. Database Restore

```bash
# Restore from SQL file
psql -U postgres -d Notes_App < backup_file.sql

# Restore from compressed dump
pg_restore -U postgres -d Notes_App backup_file.dump
```

### 3. Automated Backups

```bash
# Add to crontab for daily backups
0 2 * * * pg_dump -U postgres -h localhost Notes_App > /backups/notes_app_$(date +\%Y\%m\%d).sql
```

## Conclusion

This database setup guide provides comprehensive instructions for:

- **Database configuration** and environment setup
- **Migration management** using Alembic
- **Testing and verification** procedures
- **Troubleshooting** common issues
- **Security considerations** and best practices
- **Performance optimization** techniques
- **Backup and recovery** procedures

Following this guide ensures your Notes App database is properly configured, secure, and ready for development and production use.
