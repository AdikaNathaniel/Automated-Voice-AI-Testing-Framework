# Voice AI Automated Testing Framework - Development Guide

This document provides essential information for Claude Code instances working in this repository.

## Project Overview

This is a comprehensive automated testing framework for voice AI systems, built with FastAPI (Python backend) and React (TypeScript frontend). The framework enables automated testing of voice AI agents through realistic phone call simulations, with support for various telephony providers and AI platforms.

**Key Technologies:**
- **Backend**: FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic, PostgreSQL
- **Frontend**: React 18, TypeScript, Vite, TailwindCSS
- **Infrastructure**: Docker Compose, Redis, pgAdmin
- **Testing**: pytest with TDD methodology

## Development Commands

### Testing
```bash
# Run all tests with verbose output
venv/bin/pytest tests/ -v

# Run specific test file
venv/bin/pytest tests/test_responses.py -v

# Run tests with coverage
venv/bin/pytest tests/ --cov=backend --cov-report=term-missing

# Run tests matching pattern
venv/bin/pytest tests/ -k "test_success_response" -v
```

### Python Environment
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
venv/bin/pip install -r requirements.txt

# Install specific package
venv/bin/pip install <package-name>
```

### Database Migrations (Alembic)
```bash
# Create new migration
venv/bin/alembic revision --autogenerate -m "description"

# Apply migrations
venv/bin/alembic upgrade head

# Downgrade one revision
venv/bin/alembic downgrade -1

# Check current revision
venv/bin/alembic current

# View migration history
venv/bin/alembic history
```

### Docker Services
```bash
# Start all services (PostgreSQL, Redis, pgAdmin)
docker-compose up -d

# Stop all services
docker-compose down

# View service logs
docker-compose logs -f postgres
docker-compose logs -f redis

# Restart specific service
docker-compose restart postgres
```

**Service Access:**
- PostgreSQL: `localhost:5432` (user: postgres, password: postgres, db: voiceai_testing)
- Redis: `localhost:6379`
- pgAdmin: `http://localhost:5050` (email: admin@voiceai.com, password: admin)

### Backend Server
```bash
# Run FastAPI development server
venv/bin/uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Access API documentation
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

## Architecture Overview

### Backend Structure
```
backend/
├── api/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Settings management with Pydantic BaseSettings
│   ├── dependencies.py      # FastAPI dependency injection functions
│   ├── schemas/
│   │   ├── responses.py     # Standard API response models
│   │   └── __init__.py      # Schema exports
│   └── routes/              # API endpoint routers (to be created)
├── models/                   # SQLAlchemy ORM models (to be created)
├── services/                # Business logic layer (to be created)
└── tests/                   # Test utilities for backend
```

### Database Migration Structure
```
alembic/
├── versions/                # Migration scripts (auto-generated)
├── env.py                   # Migration environment configuration
├── script.py.mako          # Migration template
└── README                   # Alembic documentation
```

### Test Structure
```
tests/
├── test_config.py          # Configuration validation tests
├── test_responses.py       # API response model tests
├── test_docker_compose.py  # Infrastructure tests
├── test_alembic.py         # Migration system tests
└── (more test files...)
```

## Development Methodology

### Test-Driven Development (TDD)
This project strictly follows TDD methodology:

1. **Red Phase**: Write failing test first
2. **Green Phase**: Write minimal code to pass test
3. **Refactor Phase**: Improve code while keeping tests green

**Example workflow:**
```bash
# 1. Write test in tests/test_feature.py
# 2. Run test - should fail
venv/bin/pytest tests/test_feature.py -v

# 3. Implement feature
# 4. Run test - should pass
venv/bin/pytest tests/test_feature.py -v

# 5. Run all tests to ensure no regression
venv/bin/pytest tests/ -v
```

### Task Management
- All tasks tracked in `TODOS.md` with hierarchical structure
- Each task has completion criteria and test requirements
- Mark tasks complete only after all tests pass
- Include completion summary with test results

## Coding Conventions

**CRITICAL: All code must strictly follow these conventions. No exceptions.**

### File and Function Size Limits
- **Maximum 500 lines per file** - If a file exceeds 500 lines, split it into smaller modules
- **Maximum 50 lines per function/method** - If a function exceeds 50 lines, refactor into smaller functions
- **Ideal function size: 10-20 lines** - Strive for small, focused functions

**When to split files:**
```python
# If backend/api/routes/tests.py grows too large, split into:
backend/api/routes/tests/
├── __init__.py           # Exports all routers
├── test_runs.py          # Test run management endpoints
├── test_cases.py         # Test case endpoints
├── test_results.py       # Test result endpoints
└── test_scenarios.py     # Test scenario endpoints
```

### Core Principles

#### 1. DRY (Don't Repeat Yourself)
- Extract common logic into reusable functions/classes
- Use base classes for shared model behavior
- Create utility modules for repeated operations
- Leverage decorators for cross-cutting concerns

**Example:**
```python
# BAD: Repeated validation logic
def create_test_run(data):
    if not data.get("name"):
        raise ValueError("Name required")
    if len(data["name"]) < 3:
        raise ValueError("Name too short")
    # ... create test run

def update_test_run(data):
    if not data.get("name"):
        raise ValueError("Name required")
    if len(data["name"]) < 3:
        raise ValueError("Name too short")
    # ... update test run

# GOOD: Extract validation
def validate_test_run_name(name: str) -> None:
    """Validate test run name meets requirements"""
    if not name:
        raise ValueError("Name required")
    if len(name) < 3:
        raise ValueError("Name too short")

def create_test_run(data):
    validate_test_run_name(data.get("name"))
    # ... create test run

def update_test_run(data):
    validate_test_run_name(data.get("name"))
    # ... update test run
```

#### 2. Single Responsibility Principle (SRP)
- Each class/function does ONE thing and does it well
- If you use "and" to describe what a function does, it's doing too much
- Separate concerns: routing, validation, business logic, data access

**Layer separation:**
```python
# Routes layer - Handle HTTP requests/responses only
@router.post("/test-runs")
async def create_test_run(data: TestRunCreate, db: Session = Depends(get_db)):
    """Create new test run endpoint"""
    test_run = await test_run_service.create(db, data)
    return SuccessResponse(data=test_run)

# Service layer - Business logic only
class TestRunService:
    async def create(self, db: Session, data: TestRunCreate) -> TestRun:
        """Create test run with business logic"""
        # Validation, processing, coordination
        return await test_run_repository.create(db, test_run_data)

# Repository layer - Data access only
class TestRunRepository:
    async def create(self, db: Session, data: dict) -> TestRun:
        """Create test run in database"""
        # Database operations only
        test_run = TestRun(**data)
        db.add(test_run)
        await db.commit()
        return test_run
```

#### 3. CLEAN Code Principles
- **Meaningful names**: Variables, functions, classes should reveal intent
- **Functions do one thing**: Small, focused, single responsibility
- **Minimize side effects**: Functions should be predictable
- **Comments explain WHY, not WHAT**: Code should be self-documenting
- **Error handling**: Use exceptions, not error codes
- **Formatting consistency**: Follow PEP 8 and Black standards

### Python-Specific Conventions

#### Type Hints (REQUIRED)
All functions must have complete type hints:

```python
# REQUIRED: Type hints for all parameters and return values
def get_test_run(
    test_run_id: int,
    db: Session,
    include_results: bool = False
) -> Optional[TestRun]:
    """Get test run by ID"""
    # Implementation

# For complex types
from typing import List, Dict, Optional, Union, Any

def process_results(
    results: List[Dict[str, Any]],
    filters: Optional[Dict[str, Union[str, int]]] = None
) -> List[ProcessedResult]:
    """Process test results with optional filters"""
    # Implementation

# For async functions
async def fetch_test_data(test_id: int) -> Dict[str, Any]:
    """Fetch test data asynchronously"""
    # Implementation
```

#### Docstrings (REQUIRED)
Use Google-style docstrings for all public functions, classes, and methods:

```python
def create_test_scenario(
    name: str,
    test_cases: List[TestCase],
    config: Dict[str, Any]
) -> TestScenario:
    """Create a new test scenario with specified configuration.

    Args:
        name: Unique name for the test scenario
        test_cases: List of test cases to include in scenario
        config: Configuration dictionary with scenario settings

    Returns:
        TestScenario: Created test scenario instance

    Raises:
        ValueError: If name is empty or test_cases is empty
        ConfigurationError: If config is invalid

    Example:
        >>> scenario = create_test_scenario(
        ...     name="Login Flow",
        ...     test_cases=[test1, test2],
        ...     config={"timeout": 30}
        ... )
    """
    # Implementation
```

#### Line Length
- **Maximum 88 characters per line** (Black formatter standard)
- Break long lines logically:

```python
# Good line breaks
result = some_long_function_name(
    parameter1=value1,
    parameter2=value2,
    parameter3=value3,
)

# Chain methods with line breaks
query = (
    db.query(TestRun)
    .filter(TestRun.status == "completed")
    .filter(TestRun.created_at >= start_date)
    .order_by(TestRun.created_at.desc())
    .limit(100)
)
```

#### Import Organization
Organize imports in three groups with blank line between:

```python
# 1. Standard library imports
import os
import sys
from datetime import datetime
from typing import List, Optional

# 2. Third-party imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

# 3. Local application imports
from api.config import get_settings
from api.dependencies import get_db
from models.test_run import TestRun
from services.test_service import TestService
```

#### Naming Conventions (PEP 8)
```python
# Constants: ALL_CAPS with underscores
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT = 30
DATABASE_URL = "postgresql://..."

# Classes: PascalCase
class TestRunService:
    pass

class AIProviderConfig:
    pass

# Functions and variables: snake_case
def get_test_results():
    pass

test_run_id = 123
user_data = {"name": "Test"}

# Private attributes/methods: leading underscore
class TestService:
    def __init__(self):
        self._cache = {}

    def _internal_helper(self):
        pass

# Boolean variables: use is_, has_, can_ prefixes
is_valid = True
has_permission = False
can_execute = True
```

### FastAPI-Specific Conventions

#### Async/Await Usage
Use async/await consistently for I/O operations:

```python
# GOOD: Async for database and external API calls
@router.get("/test-runs/{test_run_id}")
async def get_test_run(
    test_run_id: int,
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """Get test run by ID"""
    test_run = await test_run_service.get(db, test_run_id)
    if not test_run:
        raise HTTPException(status_code=404, detail="Test run not found")
    return SuccessResponse(data=test_run)

# Use sync for CPU-bound operations
def calculate_statistics(results: List[TestResult]) -> Dict[str, float]:
    """Calculate statistics from test results"""
    # CPU-bound calculation
    return stats
```

#### Dependency Injection
Use FastAPI dependencies consistently:

```python
# Common dependencies
def get_db() -> Generator[Session, None, None]:
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current authenticated user"""
    # Token validation logic
    return user

# Use in routes
@router.post("/test-runs")
async def create_test_run(
    data: TestRunCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create test run endpoint"""
    # Implementation
```

### Database Conventions

#### Session Management
Always use context managers or FastAPI dependencies for sessions:

```python
# GOOD: Using FastAPI dependency
@router.get("/test-runs")
async def list_test_runs(db: Session = Depends(get_db)):
    """List test runs"""
    return await test_run_repository.list(db)

# GOOD: Using context manager in service layer
async def cleanup_old_data():
    """Cleanup old test data"""
    async with SessionLocal() as db:
        await test_run_repository.delete_old(db, days=90)
        await db.commit()
```

#### Transaction Handling
Explicit transaction management for complex operations:

```python
async def create_test_run_with_cases(
    db: Session,
    test_run_data: TestRunCreate,
    test_cases: List[TestCaseCreate]
) -> TestRun:
    """Create test run with test cases in single transaction"""
    try:
        # Create test run
        test_run = TestRun(**test_run_data.dict())
        db.add(test_run)
        await db.flush()  # Get ID without committing

        # Create test cases
        for case_data in test_cases:
            test_case = TestCase(**case_data.dict(), test_run_id=test_run.id)
            db.add(test_case)

        await db.commit()
        await db.refresh(test_run)
        return test_run

    except Exception as e:
        await db.rollback()
        raise DatabaseError(f"Failed to create test run: {str(e)}")
```

### Error Handling

#### Use Specific Exceptions
```python
# Define custom exceptions
class TestRunError(Exception):
    """Base exception for test run errors"""
    pass

class TestRunNotFoundError(TestRunError):
    """Test run not found"""
    pass

class TestRunValidationError(TestRunError):
    """Test run validation failed"""
    pass

# Use in code
def get_test_run(test_run_id: int) -> TestRun:
    """Get test run by ID"""
    test_run = db.query(TestRun).get(test_run_id)
    if not test_run:
        raise TestRunNotFoundError(f"Test run {test_run_id} not found")
    return test_run

# Handle in FastAPI routes
@router.get("/test-runs/{test_run_id}")
async def get_test_run_endpoint(test_run_id: int):
    """Get test run endpoint"""
    try:
        test_run = get_test_run(test_run_id)
        return SuccessResponse(data=test_run)
    except TestRunNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TestRunError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

#### Logging Instead of Print
```python
import logging

logger = logging.getLogger(__name__)

# GOOD: Use logging
logger.info(f"Creating test run: {name}")
logger.warning(f"Test run {id} exceeded timeout")
logger.error(f"Failed to connect to telephony provider: {error}")

# BAD: Never use print in production code
# print("Creating test run")  # Don't do this
```

### Testing Conventions

#### Test Structure
```python
class TestTestRunService:
    """Test suite for TestRunService"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        return TestRunService()

    @pytest.fixture
    def sample_test_run_data(self):
        """Provide sample test run data"""
        return {
            "name": "Test Run 1",
            "status": "pending",
            "config": {}
        }

    def test_create_test_run_success(self, service, sample_test_run_data):
        """Test successful test run creation"""
        # Arrange - Done in fixtures

        # Act
        result = service.create(sample_test_run_data)

        # Assert
        assert result.name == sample_test_run_data["name"]
        assert result.status == "pending"
        assert result.id is not None

    def test_create_test_run_invalid_name_raises_error(self, service):
        """Test that invalid name raises ValidationError"""
        # Arrange
        invalid_data = {"name": "", "status": "pending"}

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            service.create(invalid_data)

        assert "name" in str(exc_info.value)
```

### Code Review Checklist

Before marking any task complete, verify:

- [ ] No file exceeds 500 lines
- [ ] No function exceeds 50 lines
- [ ] All functions have type hints
- [ ] All public functions have docstrings
- [ ] No repeated code (DRY principle)
- [ ] Each function has single responsibility
- [ ] Imports are organized correctly
- [ ] Naming follows PEP 8 conventions
- [ ] Line length under 88 characters
- [ ] Async/await used for I/O operations
- [ ] Database sessions properly managed
- [ ] Specific exceptions used, not generic Exception
- [ ] Logging used instead of print statements
- [ ] All tests pass
- [ ] Test coverage meets requirements (90%+)

## Key Design Patterns

### API Response Models (backend/api/schemas/responses.py)
All API endpoints use standardized response structures:

```python
# Success response
SuccessResponse(
    success=True,
    data={"result": "value"},
    message="Optional message",
    request_id="optional-request-id"
)

# Error response
ErrorResponse(
    success=False,
    error={
        "code": "ERROR_CODE",
        "message": "Error description",
        "details": {}
    },
    request_id="optional-request-id"
)

# Paginated response
PaginatedResponse(
    data=[item1, item2, ...],
    pagination={
        "page": 1,
        "page_size": 10,
        "total_items": 100,
        "total_pages": 10
    }
)
```

### Configuration Management (backend/api/config.py)
Settings use Pydantic BaseSettings with environment variable support:

```python
from api.config import get_settings

settings = get_settings()
database_url = settings.DATABASE_URL
```

**Environment Variables:**
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `ENVIRONMENT`: dev/staging/production
- `SECRET_KEY`: JWT signing key
- `DEBUG`: Enable debug mode

### Database Models (Pattern for TASK-015+)
SQLAlchemy models will follow this pattern:

```python
from models.base import Base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

class ModelName(Base):
    __tablename__ = "table_name"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### Alembic Migration Integration
The migration system is configured to:
- Read DATABASE_URL from api.config.Settings (not alembic.ini)
- Import all models automatically for autogenerate
- Support both online and offline migration modes

When models are created, update `alembic/env.py`:
```python
# Uncomment and update:
from models.base import Base
target_metadata = Base.metadata
```

## Testing Strategy

### Test Organization
- One test file per module/feature
- Use pytest fixtures for common setup
- Group related tests in classes
- Descriptive test names: `test_<feature>_<scenario>_<expected_result>`

### Test Coverage Requirements
- All new code must have tests
- Aim for 90%+ coverage on business logic
- 100% coverage on API response models and schemas
- Integration tests for database operations

### Fixture Patterns
```python
import pytest

@pytest.fixture
def project_root():
    """Get project root directory"""
    return os.path.dirname(os.path.dirname(__file__))

@pytest.fixture
def sample_data():
    """Provide test data"""
    return {"key": "value"}
```

## Important Implementation Notes

### Database Connection
- Local development uses Docker Compose PostgreSQL
- Connection pooling configured in SQLAlchemy engine
- Alembic migrations read from application settings, not alembic.ini

### Response Model Usage
- All API endpoints must return SuccessResponse or ErrorResponse
- Use PaginatedResponse for list endpoints with pagination
- request_id is optional but recommended for tracing

### File Imports
Backend code uses absolute imports from project root:
```python
from api.config import get_settings
from api.schemas.responses import SuccessResponse
from models.base import Base  # (when created)
```

Test code adds backend to path:
```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
```

### Migration Workflow
1. Create/modify SQLAlchemy models
2. Update `alembic/env.py` to import models
3. Generate migration: `alembic revision --autogenerate -m "description"`
4. Review generated migration in `alembic/versions/`
5. Apply migration: `alembic upgrade head`
6. Test with `alembic downgrade -1` and `alembic upgrade head`

## Project Goals

This framework aims to:
1. Automate end-to-end testing of voice AI systems via realistic phone calls
2. Support multiple telephony providers (Twilio, Vonage, Bandwidth)
3. Enable testing of various AI platforms (OpenAI, Anthropic, custom models)
4. Provide comprehensive test reporting and analytics
5. Allow configuration-driven test scenarios
6. Scale to handle concurrent test execution

## Current Development Status

**Completed Tasks:**
- ✅ TASK-001 to TASK-011: Project setup, configuration, dependencies
- ✅ TASK-012: API response models (SuccessResponse, ErrorResponse, PaginatedResponse)
- ✅ TASK-013: Docker Compose setup (PostgreSQL, Redis, pgAdmin)
- ✅ TASK-014: Alembic initialization and configuration

**Next Tasks:**
- TASK-015: Create base SQLAlchemy model with common fields
- TASK-016: Design and implement database schema
- TASK-017+: API routes, business logic, telephony integration

**Test Status:** 348/348 tests passing

## Working with This Codebase

1. **Always run tests** before and after changes
2. **Follow TDD**: Write tests first, then implementation
3. **Check TODOS.md** for current task priorities
4. **Use Docker Compose** for local development (PostgreSQL, Redis)
5. **Update migrations** after any model changes
6. **Maintain test coverage** - all new code needs tests
7. **Use standard response models** for all API endpoints
8. **Document completion** with test results when marking tasks done

## Quick Start for New Tasks

1. Read task description in TODOS.md
2. Start Docker services: `docker-compose up -d`
3. Create test file: `tests/test_<feature>.py`
4. Write failing tests (Red phase)
5. Run tests: `venv/bin/pytest tests/test_<feature>.py -v`
6. Implement feature (Green phase)
7. Run tests until passing
8. Run all tests: `venv/bin/pytest tests/ -v`
9. Mark task complete in TODOS.md with test results
