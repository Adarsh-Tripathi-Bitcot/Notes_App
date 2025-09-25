# Quick Reference Guide

## Virtual Environment Commands

### Setup
```bash
# Install virtualenv
pip install virtualenv

# Create virtual environment
virtualenv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Use activation script
./activate.sh
```

### Management
```bash
# Deactivate
deactivate

# Check if active
echo $VIRTUAL_ENV

# Check Python version
python --version

# List packages
pip list

# Install packages
pip install package_name
pip install -r requirements/requirements.txt
```

### Development
```bash
# Start development server
python run.py dev

# Run tests
python run.py test

# Format code
python run.py format

# Run linting
python run.py lint
```

## Project Structure

```
Notes_App/
├── venv/                    # Virtual environment
├── src/                     # Source code
├── tests/                   # Test files
├── docs/                    # Documentation
├── requirements/            # Dependencies
├── migrations/              # Database migrations
├── activate.sh              # Activation script
├── run.py                   # Project runner
└── README.md               # Project documentation
```

## Common Commands

### Database
```bash

# Create migration
python migrations/migration_handler.py create-migration --message "Description"

# Apply migrations
python migrations/migration_handler.py upgrade

# Rollback migrations
python migrations/migration_handler.py downgrade

# Using alembic directly
alembic -c migrations/alembic.ini upgrade head
alembic -c migrations/alembic.ini downgrade -1
alembic -c migrations/alembic.ini revision --autogenerate -m "Description"
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_file.py

# Run specific test
pytest tests/test_file.py::test_function
```

### Code Quality
```bash
# Format code
black src/

# Sort imports
isort src/

# Run linter
flake8 src/

# Type checking
mypy src/

# Run all quality checks
pre-commit run --all-files
```

## Environment Variables

```bash
# Copy environment template
cp env.example .env

# Required variables
DATABASE_URL=postgresql://username:password@localhost:5432/notes_app_db
JWT_SECRET_KEY=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=60
DEBUG=true
ENVIRONMENT=development
```

## API Endpoints

### User Management
- `POST /api/v1/users/register` - User registration
- `POST /api/v1/users/login` - User login
- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/me` - Update user profile

### Note Management
- `POST /api/v1/notes/` - Create note
- `GET /api/v1/notes/` - Get user's notes
- `GET /api/v1/notes/{id}` - Get specific note
- `PUT /api/v1/notes/{id}` - Update note
- `DELETE /api/v1/notes/{id}` - Delete note

### System
- `GET /health` - Health check
- `GET /docs` - API documentation
- `GET /redoc` - Alternative API docs

## Troubleshooting

### Virtual Environment Issues
```bash
# Virtual environment not activating
rm -rf venv/
virtualenv venv
source venv/bin/activate

# Packages not found
which python  # Should point to venv/bin/python
pip list      # Check installed packages

# Permission denied on activate.sh
chmod +x activate.sh
```

### Database Issues
```bash
# Database connection failed
# Check DATABASE_URL in .env file
# Ensure PostgreSQL is running
# Check database exists

# Migration issues
python migrations/migration_handler.py upgrade
```

### Import Issues
```bash
# Module not found
# Check if virtual environment is active
# Check PYTHONPATH
# Reinstall packages
pip install -r requirements/requirements.txt
```

## Useful Links

- [Getting Started Guide](getting_started.md)
- [Virtual Environment Setup](virtual_environment_setup.md)
- [Code Standards](code_standards.md)
- [Git Workflow](git_workflow.md)
- [API Documentation](../step4/04_api_documentation.md)
- [Testing Guide](../step4/05_testing_summary.md)
