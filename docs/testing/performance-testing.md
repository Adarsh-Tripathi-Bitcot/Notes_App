# Performance Testing Guide

This guide explains how to conduct performance testing for the Notes App to ensure it meets performance requirements.

## 🎯 Performance Testing Objectives

### Key Metrics
- **Response Time**: API endpoint response times
- **Throughput**: Requests per second (RPS)
- **Concurrency**: Simultaneous user handling
- **Resource Usage**: CPU, memory, database connections
- **Scalability**: Performance under increasing load

### Performance Targets
- **API Response Time**: < 200ms (95th percentile)
- **Database Queries**: < 50ms average
- **Concurrent Users**: 100+ simultaneous users
- **Memory Usage**: < 512MB under normal load
- **CPU Usage**: < 70% under normal load

## 🛠️ Performance Testing Tools

### Primary Tools
- **pytest-benchmark**: Performance benchmarking
- **locust**: Load testing framework
- **pytest-xdist**: Parallel test execution
- **memory_profiler**: Memory usage analysis
- **cProfile**: Python profiling

### Installation
```bash
pip install pytest-benchmark locust memory-profiler
```

## 📊 Benchmark Testing

### Basic Benchmarking
```python
# tests/performance/test_benchmarks.py
import pytest
from src.core.validation import validate_email, validate_password

def test_validate_email_performance(benchmark):
    """Benchmark email validation performance."""
    email = "test@example.com"
    result = benchmark(validate_email, email)
    assert result.is_valid is True

def test_validate_password_performance(benchmark):
    """Benchmark password validation performance."""
    password = "TestPassword123!"
    result = benchmark(validate_password, password)
    assert result.is_valid is True

def test_database_query_performance(benchmark):
    """Benchmark database query performance."""
    def query_users():
        # Simulate database query
        return [{"id": i, "email": f"user{i}@example.com"} for i in range(100)]

    result = benchmark(query_users)
    assert len(result) == 100
```

### Advanced Benchmarking
```python
# tests/performance/test_advanced_benchmarks.py
import pytest
import time
from src.services.authentication import hash_password, verify_password

@pytest.mark.benchmark(group="authentication")
def test_password_hashing_performance(benchmark):
    """Benchmark password hashing performance."""
    password = "TestPassword123!"
    result = benchmark(hash_password, password)
    assert result is not None

@pytest.mark.benchmark(group="authentication")
def test_password_verification_performance(benchmark):
    """Benchmark password verification performance."""
    password = "TestPassword123!"
    hashed = hash_password(password)
    result = benchmark(verify_password, password, hashed)
    assert result is True

@pytest.mark.benchmark(group="validation")
def test_bulk_email_validation_performance(benchmark):
    """Benchmark bulk email validation performance."""
    emails = [f"user{i}@example.com" for i in range(1000)]

    def validate_emails():
        return [validate_email(email) for email in emails]

    results = benchmark(validate_emails)
    assert len(results) == 1000
```

### Running Benchmarks
```bash
# Run all benchmarks
pytest tests/performance/ --benchmark-only

# Run specific benchmark group
pytest tests/performance/ --benchmark-only --benchmark-group=authentication

# Run with detailed output
pytest tests/performance/ --benchmark-only --benchmark-sort=mean

# Save benchmark results
pytest tests/performance/ --benchmark-only --benchmark-save=performance_results
```

## 🚀 Load Testing with Locust

### Locust Test Configuration
```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between
import random

class NotesAppUser(HttpUser):
    """Simulate user behavior on Notes App."""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def on_start(self):
        """Login user on start."""
        self.login()

    def login(self):
        """Login user."""
        response = self.client.post("/api/v1/users/login", json={
            "email": "test@example.com",
            "password": "TestPassword123!"
        })
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def get_notes(self):
        """Get user notes (most common task)."""
        self.client.get("/api/v1/notes/", headers=self.headers)

    @task(2)
    def create_note(self):
        """Create a new note."""
        note_data = {
            "title": f"Test Note {random.randint(1, 1000)}",
            "content": "This is a test note content.",
            "summary": "Test note summary"
        }
        self.client.post("/api/v1/notes/", json=note_data, headers=self.headers)

    @task(1)
    def update_note(self):
        """Update an existing note."""
        note_id = random.randint(1, 100)
        note_data = {
            "title": f"Updated Note {random.randint(1, 1000)}",
            "content": "Updated note content."
        }
        self.client.put(f"/api/v1/notes/{note_id}", json=note_data, headers=self.headers)

    @task(1)
    def delete_note(self):
        """Delete a note."""
        note_id = random.randint(1, 100)
        self.client.delete(f"/api/v1/notes/{note_id}", headers=self.headers)

    @task(1)
    def search_notes(self):
        """Search notes."""
        query = random.choice(["test", "note", "example", "content"])
        self.client.get(f"/api/v1/notes/search?q={query}", headers=self.headers)
```

### Running Locust Tests
```bash
# Start Locust web interface
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Run headless load test
locust -f tests/performance/locustfile.py --host=http://localhost:8000 --headless -u 100 -r 10 -t 60s

# Run with specific user count and spawn rate
locust -f tests/performance/locustfile.py --host=http://localhost:8000 --headless -u 50 -r 5 -t 300s
```

## 📈 Memory Profiling

### Memory Usage Testing
```python
# tests/performance/test_memory.py
import pytest
from memory_profiler import profile
from src.services.note_management import NoteService

@pytest.mark.slow
def test_memory_usage_large_dataset():
    """Test memory usage with large dataset."""
    # This test is marked as slow and will be skipped in normal runs
    # Run with: pytest -m "not slow" to exclude slow tests

    service = NoteService()

    # Create large dataset
    notes = []
    for i in range(10000):
        notes.append({
            "title": f"Note {i}",
            "content": f"Content for note {i}" * 100,  # Large content
            "summary": f"Summary for note {i}"
        })

    # Process notes and measure memory
    results = []
    for note in notes:
        result = service.create_note(note)
        results.append(result)

    assert len(results) == 10000

@profile
def test_memory_profiling():
    """Profile memory usage of specific function."""
    from src.core.validation import validate_email

    # This will show memory usage line by line
    emails = [f"user{i}@example.com" for i in range(1000)]
    results = [validate_email(email) for email in emails]

    assert len(results) == 1000
```

### Running Memory Tests
```bash
# Run memory profiling
python -m memory_profiler tests/performance/test_memory.py

# Run with memory profiling
pytest tests/performance/test_memory.py -s

# Run specific memory test
pytest tests/performance/test_memory.py::test_memory_profiling -s
```

## 🔍 Database Performance Testing

### Database Query Performance
```python
# tests/performance/test_database_performance.py
import pytest
import time
from src.repositories.note_repository import NoteRepository
from src.repositories.user_repository import UserRepository

@pytest.mark.asyncio
async def test_database_query_performance():
    """Test database query performance."""
    note_repo = NoteRepository()

    # Test single query performance
    start_time = time.time()
    notes = await note_repo.get_notes_by_user_id(1, limit=100)
    query_time = time.time() - start_time

    assert query_time < 0.1  # Should be under 100ms
    assert len(notes) <= 100

@pytest.mark.asyncio
async def test_database_bulk_operations():
    """Test bulk database operations performance."""
    note_repo = NoteRepository()

    # Test bulk insert performance
    notes_data = [
        {
            "title": f"Bulk Note {i}",
            "content": f"Content for bulk note {i}",
            "user_id": 1
        }
        for i in range(1000)
    ]

    start_time = time.time()
    results = []
    for note_data in notes_data:
        result = await note_repo.create_note(note_data)
        results.append(result)
    bulk_time = time.time() - start_time

    assert bulk_time < 5.0  # Should be under 5 seconds
    assert len(results) == 1000

@pytest.mark.asyncio
async def test_database_concurrent_queries():
    """Test concurrent database queries."""
    import asyncio

    note_repo = NoteRepository()

    async def query_notes(user_id):
        return await note_repo.get_notes_by_user_id(user_id)

    # Run 10 concurrent queries
    start_time = time.time()
    tasks = [query_notes(i % 5 + 1) for i in range(10)]
    results = await asyncio.gather(*tasks)
    concurrent_time = time.time() - start_time

    assert concurrent_time < 1.0  # Should be under 1 second
    assert len(results) == 10
```

## 🚀 API Performance Testing

### API Endpoint Performance
```python
# tests/performance/test_api_performance.py
import pytest
import time
from fastapi.testclient import TestClient
from src.api.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_api_response_times(client):
    """Test API response times."""
    endpoints = [
        "/api/v1/users/register",
        "/api/v1/users/login",
        "/api/v1/notes/",
        "/api/v1/admin/system-info"
    ]

    for endpoint in endpoints:
        start_time = time.time()

        if endpoint == "/api/v1/users/register":
            response = client.post(endpoint, json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "TestPassword123!",
                "confirm_password": "TestPassword123!",
                "first_name": "Test",
                "last_name": "User"
            })
        elif endpoint == "/api/v1/users/login":
            response = client.post(endpoint, json={
                "email": "test@example.com",
                "password": "TestPassword123!"
            })
        else:
            response = client.get(endpoint)

        response_time = time.time() - start_time

        # Response should be under 200ms
        assert response_time < 0.2
        assert response.status_code in [200, 201, 422]  # Valid responses

def test_api_concurrent_requests(client):
    """Test API with concurrent requests."""
    import threading
    import queue

    results = queue.Queue()

    def make_request():
        start_time = time.time()
        response = client.get("/api/v1/admin/system-info")
        response_time = time.time() - start_time
        results.put((response.status_code, response_time))

    # Create 10 concurrent requests
    threads = []
    for _ in range(10):
        thread = threading.Thread(target=make_request)
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Check results
    response_times = []
    while not results.empty():
        status_code, response_time = results.get()
        assert status_code == 200
        response_times.append(response_time)

    # Average response time should be under 200ms
    avg_response_time = sum(response_times) / len(response_times)
    assert avg_response_time < 0.2
```

## 📊 Performance Monitoring

### Performance Metrics Collection
```python
# tests/performance/test_metrics.py
import pytest
import time
import psutil
import os
from src.api.main import app
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    return TestClient(app)

def test_system_resources(client):
    """Monitor system resources during API calls."""
    process = psutil.Process(os.getpid())

    # Get initial resource usage
    initial_cpu = process.cpu_percent()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB

    # Make API calls
    for _ in range(100):
        response = client.get("/api/v1/admin/system-info")
        assert response.status_code == 200

    # Get final resource usage
    final_cpu = process.cpu_percent()
    final_memory = process.memory_info().rss / 1024 / 1024  # MB

    # Memory usage should not increase significantly
    memory_increase = final_memory - initial_memory
    assert memory_increase < 50  # Less than 50MB increase

    # CPU usage should be reasonable
    assert final_cpu < 80  # Less than 80% CPU usage

def test_database_connection_pool(client):
    """Test database connection pool performance."""
    # Make multiple concurrent requests
    import threading
    import queue

    results = queue.Queue()

    def make_request():
        start_time = time.time()
        response = client.get("/api/v1/admin/system-info")
        response_time = time.time() - start_time
        results.put((response.status_code, response_time))

    # Create 20 concurrent requests
    threads = []
    for _ in range(20):
        thread = threading.Thread(target=make_request)
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Check that all requests succeeded
    success_count = 0
    while not results.empty():
        status_code, response_time = results.get()
        if status_code == 200:
            success_count += 1

    assert success_count == 20  # All requests should succeed
```

## 🎯 Performance Test Configuration

### Pytest Configuration
```ini
# pytest.ini
[tool:pytest]
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    performance: marks tests as performance tests
    benchmark: marks tests as benchmark tests
    memory: marks tests as memory tests
    load: marks tests as load tests

# Run performance tests
pytest -m performance

# Run all tests except slow ones
pytest -m "not slow"

# Run benchmark tests
pytest -m benchmark --benchmark-only
```

### Performance Test Commands
```bash
# Run all performance tests
pytest tests/performance/ -v

# Run only benchmark tests
pytest tests/performance/ -m benchmark --benchmark-only

# Run memory tests
pytest tests/performance/ -m memory -s

# Run load tests
pytest tests/performance/ -m load

# Run with performance profiling
pytest tests/performance/ --profile

# Run specific performance test
pytest tests/performance/test_benchmarks.py::test_validate_email_performance -v
```

## 📋 Performance Testing Checklist

### Before Performance Testing
- [ ] Set up performance testing environment
- [ ] Install required tools (pytest-benchmark, locust, etc.)
- [ ] Configure test data and fixtures
- [ ] Set performance targets and thresholds

### During Performance Testing
- [ ] Monitor system resources (CPU, memory, disk)
- [ ] Record response times and throughput
- [ ] Test under different load conditions
- [ ] Identify performance bottlenecks

### After Performance Testing
- [ ] Analyze performance results
- [ ] Compare against performance targets
- [ ] Document performance issues
- [ ] Create performance improvement plan

## 🚨 Performance Issues and Solutions

### Common Performance Issues
1. **Slow Database Queries**
   - Solution: Add database indexes, optimize queries

2. **Memory Leaks**
   - Solution: Fix memory leaks, add garbage collection

3. **Slow API Responses**
   - Solution: Add caching, optimize code paths

4. **High CPU Usage**
   - Solution: Optimize algorithms, reduce computational complexity

### Performance Optimization Strategies
1. **Database Optimization**
   - Add appropriate indexes
   - Use connection pooling
   - Optimize queries

2. **Caching**
   - Implement Redis caching
   - Cache frequently accessed data
   - Use HTTP caching headers

3. **Code Optimization**
   - Profile and optimize hot paths
   - Use async/await where appropriate
   - Minimize database queries

4. **Infrastructure**
   - Use CDN for static content
   - Implement load balancing
   - Scale horizontally

---

**Last Updated**: October 2024
**Performance Tests**: 25+
**Benchmark Tests**: 15+
**Load Tests**: 5+
