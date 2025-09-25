# Notes App

A comprehensive, production-ready Notes App built with **FastAPI**, following **Clean Architecture** principles and **SOLID** design patterns. This application provides a complete notes management system with secure authentication, full CRUD operations, and advanced features.

## 🎯 Project Overview

The Notes App is a full-stack application that demonstrates modern Python development practices, clean architecture principles, and comprehensive testing strategies. It serves as both a functional notes management system and a reference implementation for building scalable, maintainable applications.

## ✅ Project Completion Status

### Core Requirements ✅ COMPLETED
- [x] **FastAPI Backend**: High-performance asynchronous API
- [x] **PostgreSQL Database**: Robust data storage with SQLAlchemy ORM
- [x] **JWT Authentication**: Secure token-based authentication using HTTPBearer
- [x] **Pydantic Validation**: Comprehensive data validation
- [x] **Clean Architecture**: Layered architecture with clear separation of concerns
- [x] **SOLID Principles**: Adherence to SOLID design principles
- [x] **Google-style Docstrings**: Comprehensive documentation

### Development Workflow ✅ COMPLETED
- [x] **Pre-commit Hooks**: Black, Flake8, MyPy, Ruff integration
- [x] **Unit Testing**: Comprehensive test coverage with pytest
- [x] **Integration Testing**: Database and API integration tests
- [x] **Error Handling**: Centralized error handling and logging
- [x] **Code Quality**: Automated code formatting and linting
- [x] **Documentation**: Complete documentation structure

## ✨ Key Features

### 🔐 Authentication & Security
- **JWT-based Authentication**: Secure token-based authentication system using HTTPBearer
- **User Registration & Login**: Complete user management with validation
- **Password Security**: BCrypt hashing with strength requirements
- **Input Validation**: Comprehensive data validation using Pydantic
- **CORS Configuration**: Secure cross-origin request handling
- **Swagger UI Integration**: Easy testing with HTTPBearer authentication in Swagger UI

### 📝 Note Management
- **Full CRUD Operations**: Create, read, update, and delete notes
- **Note Status Management**: Active, archived, and deleted statuses
- **Public/Private Notes**: Control note visibility
- **Note Pinning**: Pin important notes for quick access
- **Advanced Search**: Full-text search across notes with multiple criteria
- **Bulk Operations**: Perform actions on multiple notes simultaneously
- **Pagination**: Efficient handling of large note collections
- **Note Statistics**: Comprehensive analytics and insights
- **Search by Title**: Quick search functionality via GET parameters

### 🏗️ Architecture & Design
- **Clean Architecture**: Layered architecture with clear separation of concerns
- **SOLID Principles**: Adherence to SOLID design principles throughout
- **Repository Pattern**: Clean data access abstraction
- **Service Layer**: Business logic encapsulation
- **Dependency Injection**: Loose coupling through DI

### 🧪 Quality Assurance
- **Comprehensive Testing**: Unit, integration, and API tests
- **High Test Coverage**: Extensive test coverage with detailed reporting
- **Code Quality Tools**: Black, Flake8, MyPy, and Ruff integration
- **Pre-commit Hooks**: Automated code quality checks
- **Type Safety**: Comprehensive type hints throughout

### 📚 Documentation
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation with HTTPBearer authentication
- **Complete API Reference**: Comprehensive endpoint documentation with request/response schemas
- **Comprehensive Guides**: Detailed documentation for all aspects
- **Developer Resources**: Setup guides, coding standards, and best practices
- **Architecture Documentation**: System design and pattern explanations

### 📖 API Documentation Links
- [Complete API Endpoints Documentation](docs/api/endpoints.md) - Detailed API reference
- [API Troubleshooting Guide](docs/api/troubleshooting.md) - Common issues and fixes
- [Swagger UI](http://localhost:8000/docs) - Interactive API documentation
- [ReDoc](http://localhost:8000/redoc) - Alternative API documentation

## 🏛️ Architecture

The Notes App follows **Clean Architecture** principles with clear separation of concerns:

### Clean Architecture Layers
```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │  User Router    │  │  Notes Router   │  │  Main App   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                 Service Layer (Business Logic)             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Authentication  │  │ Note Management │  │ Validation  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                Repository Layer (Data Access)              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ User Repository │  │ Note Repository │  │ Base Repo   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                    Model Layer (Entities)                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │  User Model     │  │  Note Model     │  │ Base Model  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                    Database (PostgreSQL)                   │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Patterns
- **Repository Pattern**: Data access abstraction
- **Service Layer Pattern**: Business logic encapsulation
- **Dependency Injection**: Loose coupling
- **Factory Pattern**: Object creation
- **Strategy Pattern**: Algorithm selection

## 🛠️ Technology Stack

### Backend
- **FastAPI 0.104.1**: Modern, fast web framework
- **Python 3.8+**: Programming language
- **SQLAlchemy 2.0.23**: ORM and database toolkit
- **PostgreSQL**: Primary database
- **Alembic 1.13.1**: Database migration tool

### Authentication & Security
- **JWT (python-jose)**: Token-based authentication
- **BCrypt (passlib)**: Password hashing
- **Pydantic**: Data validation and serialization

### Testing & Quality
- **Pytest 7.4.3**: Testing framework
- **Black 23.11.0**: Code formatter
- **Flake8 6.1.0**: Linter
- **MyPy 1.7.1**: Static type checker
- **Ruff 0.1.6**: Fast linter and formatter

### Development Tools
- **Pre-commit**: Git hooks for code quality
- **isort**: Import sorting
- **coverage**: Test coverage reporting

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Notes_App
```

### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Use activation script (if available)
./activate.sh
```

### 3. Install Dependencies
```bash
# Install production dependencies
pip install -r requirements/requirements.txt

# Install development dependencies
pip install -r dev_requirements.txt
```

### 4. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

Required environment variables:
```env
DATABASE_URL=postgresql://postgres:root@localhost:5432/Notes_App
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=60
APP_NAME=Notes App
DEBUG=true
ENVIRONMENT=development
LOG_LEVEL=INFO
LOG_FORMAT=json
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
BCRYPT_ROUNDS=12
```

### 5. Database Setup
```bash
# Run database migrations
alembic upgrade head

# Verify database connection
python -c "
from src.core.database import test_connection
import asyncio
asyncio.run(test_connection())
"
```

### 6. Start Development Server
```bash
# Start the server
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Or use the run script (if available)
python run.py dev
```

### 7. Access the Application
- **API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_notes.py

# Run with verbose output
pytest -v
```

### Test Coverage
```bash
# Generate coverage report
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

## 🔧 Development Commands

### Code Formatting
```bash
# Format code with Black
black src/ tests/

# Check formatting
black --check src/ tests/
```

### Code Linting
```bash
# Run Flake8
flake8 src/ tests/

# Run MyPy type checking
mypy src/

# Run Ruff
ruff check src/ tests/
```

### Database Operations
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 📁 Project Structure

```
Notes_App/
├── src/                           # Source code
│   ├── api/                      # API layer
│   │   ├── main.py              # FastAPI application
│   │   └── routers/             # API routers
│   │       ├── user_router.py   # User endpoints
│   │       └── notes_router.py  # Notes endpoints
│   ├── core/                    # Core functionality
│   │   ├── config.py           # Configuration
│   │   ├── database.py         # Database setup
│   │   ├── exceptions.py       # Custom exceptions
│   │   └── logging.py          # Logging configuration
│   ├── models/                  # Database models
│   │   ├── user.py             # User model
│   │   └── note.py             # Note model
│   ├── repositories/            # Data access layer
│   │   ├── user_repository.py  # User data access
│   │   └── note_repository.py  # Note data access
│   ├── schemas/                 # Pydantic schemas
│   │   ├── user.py             # User schemas
│   │   └── note.py             # Note schemas
│   └── services/                # Business logic
│       ├── authentication.py   # Auth service
│       └── note_management.py  # Note service
├── tests/                       # Test files
├── docs/                        # Documentation
│   ├── api/                    # API documentation
│   ├── developer_guidelines/   # Development guides
│   ├── architecture-patterns/  # Architecture docs
│   └── clean-code/             # Code quality docs
├── requirements/               # Dependencies
│   └── requirements.txt        # Production dependencies
├── dev_requirements.txt        # Development dependencies
├── migrations/                 # Database migrations
├── venv/                       # Virtual environment
├── .env                        # Environment variables
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## 🔐 Authentication

The application uses **HTTPBearer** authentication with JWT tokens:

### Getting a Token
```bash
curl -X POST "http://localhost:8000/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

### Using the Token
```bash
curl -X GET "http://localhost:8000/api/v1/notes/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Swagger UI Authentication
1. Click "Authorize" button in Swagger UI
2. Enter your JWT token (without "Bearer " prefix)
3. Click "Authorize"
4. All protected endpoints will work automatically

## 📊 API Endpoints

### User Endpoints
- `POST /api/v1/users/register` - User registration
- `POST /api/v1/users/login` - User login
- `GET /api/v1/users/me` - Get current user
- `GET /api/v1/users/me/stats` - User statistics

### Notes Endpoints
- `GET /api/v1/notes/` - Get all notes (with pagination and search)
- `POST /api/v1/notes/` - Create note
- `GET /api/v1/notes/{id}` - Get note by ID
- `PUT /api/v1/notes/{id}` - Update note
- `DELETE /api/v1/notes/{id}` - Delete note
- `PATCH /api/v1/notes/{id}/status` - Update note status
- `POST /api/v1/notes/search` - Advanced search
- `GET /api/v1/notes/stats/overview` - Note statistics
- `POST /api/v1/notes/bulk-action` - Bulk operations
- `GET /api/v1/notes/public` - Get public notes

For detailed API documentation, see [Complete API Endpoints Documentation](docs/api/endpoints.md).

## 🚀 Deployment

### Production Environment
```bash
# Install production dependencies
pip install -r requirements/requirements.txt

# Set production environment variables
export ENVIRONMENT=production
export DEBUG=false

# Run database migrations
alembic upgrade head

# Start production server
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements/requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Format code (`black src/ tests/`)
6. Run linting (`flake8 src/ tests/`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the [docs](docs/) folder for detailed guides
- **API Issues**: See [API Troubleshooting Guide](docs/api/troubleshooting.md)
- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions

## 🗺️ Roadmap

- [ ] **Mobile App**: React Native mobile application
- [ ] **Real-time Updates**: WebSocket support for live updates
- [ ] **File Attachments**: Support for note attachments
- [ ] **Collaboration**: Shared notes and real-time editing
- [ ] **Advanced Analytics**: Detailed usage analytics
- [ ] **API Rate Limiting**: Implement rate limiting
- [ ] **Caching**: Redis caching for improved performance
- [ ] **Monitoring**: Application performance monitoring

## 🙏 Acknowledgments

- **FastAPI** team for the excellent web framework
- **SQLAlchemy** team for the powerful ORM
- **Pydantic** team for data validation
- **PostgreSQL** team for the robust database
- **All contributors** who helped make this project better

---

**Built with ❤️ using FastAPI, PostgreSQL, and modern Python practices.**
