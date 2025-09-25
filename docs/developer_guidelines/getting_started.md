# Getting Started with Notes App

This guide will help you set up the Notes App development environment and get started with development.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+**: [Download Python](https://www.python.org/downloads/)
- **PostgreSQL 12+**: [Download PostgreSQL](https://www.postgresql.org/download/)
- **Git**: [Download Git](https://git-scm.com/downloads)
- **pip**: Usually comes with Python

## Quick Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Notes_App
```

### 2. Create Virtual Environment

#### Option 1: Using virtualenv (Recommended)

```bash
# Install virtualenv if not already installed
pip install virtualenv

# Create virtual environment
virtualenv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### Option 2: Using Python's built-in venv

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### Option 3: Using the provided activation script

```bash
# Make the script executable (first time only)
chmod +x activate.sh

# Activate virtual environment
./activate.sh
```

### 3. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements/requirements.txt

# Install development dependencies
pip install -r dev_requirements.txt

# Verify installation
python -c "import fastapi; import sqlalchemy; import pydantic; print('All core packages imported successfully!')"
```

### 4. Virtual Environment Management

#### Activation Methods

**Method 1: Using activation script (Easiest)**
```bash
./activate.sh
```

**Method 2: Manual activation**
```bash
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

**Method 3: Using run.py script**
```bash
python run.py dev     # Automatically activates venv and starts dev server
python run.py test    # Automatically activates venv and runs tests
```

#### Deactivation

```bash
# Deactivate virtual environment
deactivate
```

#### Verification

```bash
# Check Python version
python --version

# Check pip version
pip --version

# List installed packages
pip list

# Check specific packages
python -c "import fastapi; print('FastAPI version:', fastapi.__version__)"
```

#### Package Management

```bash
# Install a new package
pip install package_name

# Install with version specification
pip install package_name==1.0.0

# Install from requirements
pip install -r requirements/requirements.txt

# Update requirements freeze
pip freeze > requirements_freeze.txt

# Uninstall a package
pip uninstall package_name
```

#### Virtual Environment Files

- `venv/` - Virtual environment directory
- `activate.sh` - Easy activation script
- `requirements_freeze.txt` - Exact package versions
- `requirements/requirements.txt` - Production dependencies
- `dev_requirements.txt` - Development dependencies

### 4. Set Up Environment Variables

#### Option 1: Create .env file manually

Create a `.env` file in the project root with the following content:

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

#### Option 2: Copy from example

```bash
# Copy example environment file
cp env.example .env

# Edit .env with your configuration
# Update DATABASE_URL with your PostgreSQL credentials
```

### 5. Database Setup

#### Prerequisites

- **PostgreSQL 12+** installed and running
- **Database created** named `Notes_App`
- **User credentials** configured (username: `postgres`, password: `root`)

#### Database Connection Test

```bash
# Test database connection
python test_db_connection.py
```

This script will:
- Verify database connectivity
- Check PostgreSQL version
- Confirm database name
- Display connection status
- Verify all required tables exist

#### Manual Database Setup (if needed)

```sql
-- Connect to PostgreSQL as superuser
psql -U postgres

-- Create database
CREATE DATABASE "Notes_App";

-- Create user (if not exists)
CREATE USER postgres WITH PASSWORD 'root';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE "Notes_App" TO postgres;

-- Connect to the database
\c "Notes_App"
```

#### Run Database Migrations

```bash
# Apply database migrations to create tables
python migrations/migration_handler.py upgrade

# Or use alembic directly
alembic -c migrations/alembic.ini upgrade head
```

#### Verify Database Setup

```bash
# Run comprehensive database test
python test_db_connection.py

# Expected output:
# ✅ Database connection successful!
# ✅ All required tables present
# ✅ Users table accessible
# ✅ Notes table accessible
```

### 5. Set Up Database

```bash
# Create database (replace with your database name)
createdb notes_app_db

# Run migrations
python migrations/migration_handler.py create-db
python migrations/migration_handler.py upgrade
```

### 6. Run the Application

```bash
# Start the development server
uvicorn src.api.main:app --reload

# The API will be available at http://localhost:8000
# API documentation at http://localhost:8000/docs
```

## Development Workflow

### 1. Code Quality Setup

```bash
# Install pre-commit hooks
pre-commit install

# Run code quality checks manually
black src/ tests/
flake8 src/ tests/
mypy src/
```

### 2. Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test types
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests
pytest tests/api/          # API tests
```

### 3. Database Migrations

```bash
# Create a new migration
python migrations/migration_handler.py create-migration --message "Add new feature"

# Apply migrations
python migrations/migration_handler.py upgrade

# Rollback migrations
python migrations/migration_handler.py downgrade
```

## Project Structure

```
Notes_App/
├── src/                    # Source code
│   ├── core/              # Core infrastructure
│   ├── api/               # API layer
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   ├── repositories/      # Data access layer
│   ├── services/          # Business logic layer
│   └── validators/        # Custom validators
├── tests/                 # Test suite
├── migrations/            # Database migrations
├── docs/                  # Documentation
├── requirements/          # Dependencies
└── README.md             # Project overview
```

## Common Commands

### Development

```bash
# Start development server
uvicorn src.api.main:app --reload

# Run tests
pytest

# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type check
mypy src/
```

### Database

```bash
# Check database connection
python migrations/migration_handler.py check-connection

# Create database
python migrations/migration_handler.py create-db

# Run migrations
python migrations/migration_handler.py upgrade

# Show migration history
python migrations/migration_handler.py history
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/api/test_auth.py

# Run tests with specific marker
pytest -m unit
pytest -m integration
pytest -m api
```

## Environment Configuration

### Required Environment Variables

```bash
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/notes_app_db

# JWT Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=60

# Application
APP_NAME=Notes App
DEBUG=true
ENVIRONMENT=development

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Optional Environment Variables

```bash
# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# Security
BCRYPT_ROUNDS=12
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check PostgreSQL is running
   - Verify DATABASE_URL is correct
   - Ensure database exists

2. **Import Errors**
   - Activate virtual environment
   - Install dependencies
   - Check Python path

3. **Migration Errors**
   - Check database connection
   - Verify migration files
   - Check for conflicts

4. **Test Failures**
   - Check database setup
   - Verify test data
   - Check environment variables

### Getting Help

- Check the [API Documentation](http://localhost:8000/docs) when running the app
- Review the [Code Standards](code_standards.md) for coding guidelines
- Check the [Git Workflow](git_workflow.md) for collaboration guidelines
- Create an issue in the repository for bugs or questions

## Next Steps

1. **Explore the Code**: Start with the [API layer](src/api/) and work your way down
2. **Read the Tests**: Tests provide excellent examples of how to use the code
3. **Check Documentation**: Each module has detailed docstrings
4. **Follow Standards**: Adhere to the coding standards and practices
5. **Contribute**: Make improvements and submit pull requests

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [Pytest Documentation](https://docs.pytest.org/)

Happy coding! 🚀
