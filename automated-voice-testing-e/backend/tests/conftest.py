"""
Pytest fixtures for backend tests (TASK-141)

This module provides shared pytest fixtures for testing the Voice AI Testing Framework.
Fixtures are automatically discovered and available to all tests in the backend/tests directory.

Key Fixtures:
- db_session: Async database session for tests
- test_user: Creates a test user in the database
- test_suite: Creates a test suite with test cases

Usage:
    def test_something(db_session, test_user):
        # db_session and test_user are automatically injected
        assert test_user.email == "test@example.com"
"""

import os
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from uuid import uuid4

# Set up test environment variables BEFORE any imports that use Settings
# This must be done first, before importing api.config or any routes
os.environ.setdefault('DATABASE_URL', 'sqlite+aiosqlite:///:memory:')
os.environ.setdefault('REDIS_URL', 'redis://localhost:6379/1')
os.environ.setdefault('JWT_SECRET_KEY', 'test_secret_key_for_testing_only')
os.environ.setdefault('JWT_ALGORITHM', 'HS256')
os.environ.setdefault('SOUNDHOUND_API_KEY', 'test_soundhound_key')
os.environ.setdefault('SOUNDHOUND_CLIENT_ID', 'test_soundhound_id')
os.environ.setdefault('AWS_ACCESS_KEY_ID', 'test_aws_key')
os.environ.setdefault('AWS_SECRET_ACCESS_KEY', 'test_aws_secret')
os.environ.setdefault('AWS_REGION', 'us-east-1')
os.environ.setdefault('ENVIRONMENT', 'development')

# Test Database Configuration
# ============================
# Use in-memory SQLite database for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
TEST_SYNC_DATABASE_URL = "sqlite:///:memory:"

# Import SQLAlchemy components
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Try to import models and Base
try:
    from models.base import Base
    from models.user import User
    from models.test_suite import TestSuite
    from models.scenario_script import ScenarioScript
    from models.test_suite_scenario import TestSuiteScenario
    from api.auth.password import hash_password
except ImportError:
    # Fallback to None if models not available
    Base = None
    User = None
    TestSuite = None
    ScenarioScript = None
    TestSuiteScenario = None
    hash_password = None


# Note: event_loop fixture is provided automatically by pytest-asyncio in auto mode
# No need to define custom event_loop fixture when asyncio_mode = auto in pytest.ini


@pytest.fixture(autouse=True)
def reset_global_redis_client():
    """
    Reset the global Redis client before each test.

    This prevents "Event loop is closed" errors when the Redis client
    from a previous test's event loop is reused in a new test.
    """
    # Reset before test
    try:
        import api.redis_client as redis_module
        redis_module._redis_client = None
    except ImportError:
        pass

    yield

    # Reset after test (cleanup)
    try:
        import api.redis_client as redis_module
        redis_module._redis_client = None
    except ImportError:
        pass


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session (async).

    This fixture provides an async SQLAlchemy session for database operations
    in tests. The session is automatically created before each test and cleaned
    up afterwards. Uses an in-memory SQLite database for isolation.

    Yields:
        AsyncSession: Async SQLAlchemy database session

    Example:
        @pytest.mark.asyncio
        async def test_create_user(db_session):
            user = User(email="test@example.com", username="testuser")
            db_session.add(user)
            await db_session.commit()
            assert user.id is not None
    """
    # Create async engine
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
    )

    # Create tables
    if Base is not None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    async_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    # Create and yield session
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            # Cleanup: rollback any uncommitted changes
            await session.rollback()
            await session.close()

    # Drop tables and dispose engine
    if Base is not None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """
    Create a test user in the database.

    This fixture creates a test user with default credentials for use in tests.
    The user is automatically added to the database and committed.

    Args:
        db_session: Database session fixture (auto-injected)

    Returns:
        User: Created test user instance

    Example:
        @pytest.mark.asyncio
        async def test_user_authentication(test_user, db_session):
            # test_user is already created and committed
            assert test_user.email == "test@example.com"
            assert test_user.username == "testuser"

            # Fetch user from database
            result = await db_session.execute(
                select(User).where(User.email == "test@example.com")
            )
            user = result.scalar_one()
            assert user.id == test_user.id
    """
    if User is None:
        # Models not available, return mock
        class MockUser:
            id = uuid4()
            email = "test@example.com"
            username = "testuser"
            password_hash = "hashed_password_123"

        return MockUser()

    # Create test user with properly hashed password
    # Explicitly set id to avoid SQLAlchemy mapper isolation issues
    user = User(
        id=uuid4(),
        email="test@example.com",
        username="testuser",
        password_hash=hash_password("password123") if hash_password else "hashed_password_123"
    )

    # Add to session and commit
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest_asyncio.fixture
async def test_suite(db_session: AsyncSession, test_user):
    """
    Create a test suite with test cases.

    This fixture creates a test suite owned by the test_user, with a few
    sample test cases. Useful for testing suite-related functionality.

    Args:
        db_session: Database session fixture (auto-injected)
        test_user: Test user fixture (auto-injected)

    Returns:
        TestSuite: Created test suite with scenarios

    Example:
        @pytest.mark.asyncio
        async def test_suite_execution(test_suite, db_session):
            # test_suite is already created with scenarios
            assert test_suite.name == "Test Suite"
            assert len(test_suite.scenario_associations) >= 2

            # Execute test suite
            result = await execute_test_suite(test_suite.id)
            assert result.status == "completed"
    """
    if TestSuite is None or ScenarioScript is None:
        # Models not available, return mock
        class MockScenario:
            id = uuid4()
            name = "Weather Query"
            description = "Test weather queries"

        class MockTestSuite:
            id = uuid4()
            name = "Test Suite"
            description = "Sample test suite for testing"
            created_by_id = test_user.id if hasattr(test_user, 'id') else uuid4()
            scenario_associations = [MockScenario(), MockScenario()]

        return MockTestSuite()

    # Create test suite - explicitly set id to avoid mapper isolation issues
    suite = TestSuite(
        id=uuid4(),
        name="Test Suite",
        description="Sample test suite for testing",
        created_by_id=test_user.id
    )

    # Add to session and commit
    db_session.add(suite)
    await db_session.commit()
    await db_session.refresh(suite)

    # Create sample scenario scripts - explicitly set id to avoid mapper isolation issues
    scenario_1 = ScenarioScript(
        id=uuid4(),
        name="Weather Query",
        description="Test weather-related queries",
        created_by=test_user.id
    )

    scenario_2 = ScenarioScript(
        id=uuid4(),
        name="Alarm Command",
        description="Test alarm-related commands",
        created_by=test_user.id
    )

    # Add scenarios and commit
    db_session.add(scenario_1)
    db_session.add(scenario_2)
    await db_session.commit()

    # Link scenarios to suite via TestSuiteScenario
    if TestSuiteScenario is not None:
        association_1 = TestSuiteScenario(
            suite_id=suite.id,
            scenario_id=scenario_1.id
        )
        association_2 = TestSuiteScenario(
            suite_id=suite.id,
            scenario_id=scenario_2.id
        )
        db_session.add(association_1)
        db_session.add(association_2)
        await db_session.commit()

    # Refresh to get relationships
    await db_session.refresh(suite)

    return suite


# Additional utility fixtures
# ============================

@pytest.fixture
def sample_test_data():
    """
    Provide sample test data for use in tests.

    Returns:
        dict: Dictionary of sample test data

    Example:
        def test_validation(sample_test_data):
            assert sample_test_data["valid_email"] == "user@example.com"
    """
    return {
        "valid_email": "user@example.com",
        "invalid_email": "not-an-email",
        "valid_password": "SecurePass123!",
        "weak_password": "123",
        "sample_query": "What is the weather in New York?",
        "sample_response": {
            "intent": "weather_query",
            "entities": {
                "location": "New York"
            },
            "confidence": 0.95
        }
    }


@pytest.fixture
def mock_redis_client():
    """
    Provide a mock Redis client for testing.

    Returns:
        Mock: Mock Redis client with common methods

    Example:
        def test_cache(mock_redis_client):
            mock_redis_client.set("key", "value")
            assert mock_redis_client.get("key") == "value"
    """
    from unittest.mock import Mock, AsyncMock

    mock_client = Mock()
    mock_client.get = AsyncMock(return_value=None)
    mock_client.set = AsyncMock(return_value=True)
    mock_client.setex = AsyncMock(return_value=True)
    mock_client.delete = AsyncMock(return_value=1)

    return mock_client
