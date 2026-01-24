"""
Pytest configuration and fixtures for all tests

This file is automatically loaded by pytest and provides:
- Environment variable setup for testing
- Common fixtures available to all test files
- Test configuration and hooks
"""

import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pytest
import pytest_asyncio


# Set up test environment variables before any tests run
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Set up environment variables for testing.

    This fixture runs once per test session before any tests execute.
    It sets required environment variables to test values.
    """
    # Save original environment
    original_env = dict(os.environ)

    # Set test environment variables
    test_env = {
        # Database configuration
        'DATABASE_URL': 'postgresql://postgres:postgres@localhost:5432/voiceai_testing',
        'DB_POOL_SIZE': '5',
        'DB_MAX_OVERFLOW': '10',
        'DB_POOL_TIMEOUT': '30',

        # Redis configuration
        'REDIS_URL': 'redis://localhost:6379/0',
        'REDIS_MAX_CONNECTIONS': '10',
        'REDIS_SOCKET_TIMEOUT': '5',

        # Application configuration
        'ENVIRONMENT': 'development',  # Must be development, staging, or production
        'DEBUG': 'false',
        'LOG_LEVEL': 'INFO',

        # JWT configuration
        'JWT_SECRET_KEY': 'test-secret-key-for-testing-only-not-for-production',
        'JWT_ALGORITHM': 'HS256',
        'JWT_ACCESS_TOKEN_EXPIRE_MINUTES': '30',

        # SoundHound API configuration
        'SOUNDHOUND_API_KEY': 'test-soundhound-api-key',
        'SOUNDHOUND_CLIENT_ID': 'test-soundhound-client-id',
        'SOUNDHOUND_ENDPOINT': 'https://api.soundhound.com/test',

        # AWS configuration
        'AWS_ACCESS_KEY_ID': 'test-aws-access-key',
        'AWS_SECRET_ACCESS_KEY': 'test-aws-secret-key',
        'AWS_REGION': 'us-east-1',
        'AWS_S3_BUCKET': 'test-voiceai-bucket',

        # API Server configuration
        'API_HOST': '0.0.0.0',
        'API_PORT': '8000',
        'CORS_ORIGINS': 'http://localhost:3000,http://localhost:8000',

        # Testing configuration
        'TEST_TIMEOUT': '30',
        'TEST_CONCURRENCY_LIMIT': '5',
    }

    # Set test environment variables
    os.environ.update(test_env)

    # Yield to run tests
    yield

    # Restore original environment after all tests
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def clean_settings_cache():
    """
    Clear the settings cache before each test.

    The get_settings() function uses @lru_cache, so we need to clear
    it between tests to ensure fresh settings are loaded.
    """
    from api.config import get_settings
    # Clear the cache
    get_settings.cache_clear()
    yield
    # Clear again after test
    get_settings.cache_clear()


@pytest_asyncio.fixture
async def db_session():
    """
    Provide a database session for tests with automatic cleanup.

    Creates a new database session for each test, and rolls back
    all changes after the test completes to ensure test isolation.
    """
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from models.base import Base

    # Import all models to ensure SQLAlchemy can resolve relationships
    from models.user import User  # noqa: F401
    from models.test_suite import TestSuite  # noqa: F401
    from models.scenario_script import ScenarioScript, ScenarioStep  # noqa: F401
    from models.suite_run import SuiteRun  # noqa: F401
    from models.validation_result import ValidationResult  # noqa: F401
    from models.expected_outcome import ExpectedOutcome  # noqa: F401
    from models.multi_turn_execution import MultiTurnExecution  # noqa: F401
    from models.device_test_execution import DeviceTestExecution  # noqa: F401
    from models.test_execution_queue import TestExecutionQueue  # noqa: F401
    from models.configuration import Configuration  # noqa: F401
    from models.configuration_history import ConfigurationHistory  # noqa: F401

    # Create test database engine
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/voiceai_testing')
    if DATABASE_URL.startswith('postgresql://'):
        DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://', 1)

    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )

    # Drop and recreate all tables for clean test environment
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        # Rollback to clean up test data
        await session.rollback()

    # Clean up
    await engine.dispose()


@pytest_asyncio.fixture
async def async_db(db_session):
    """
    Alias for db_session to match integration test naming conventions.

    This fixture provides the same database session as db_session,
    but with a more descriptive name for async operations.
    """
    return db_session


@pytest_asyncio.fixture
async def test_user(async_db):
    """
    Create a test user for integration tests.

    Returns:
        User: A test user with valid credentials
    """
    from models.user import User
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    user = User(
        email="test@example.com",
        username="testuser",
        password_hash=pwd_context.hash("testpassword123"),
        is_active=True
    )

    async_db.add(user)
    await async_db.commit()
    await async_db.refresh(user)

    return user


@pytest_asyncio.fixture
async def test_suite(async_db, test_user):
    """
    Create a basic test suite for integration tests.

    Returns:
        TestSuite: A test suite without test cases
    """
    from models.test_suite import TestSuite

    suite = TestSuite(
        name="Test Suite for Integration Tests",
        description="A test suite used in integration tests",
        category="Integration",
        is_active=True,
        created_by=test_user.id
    )

    async_db.add(suite)
    await async_db.commit()
    await async_db.refresh(suite)

    return suite


@pytest_asyncio.fixture
async def test_suite_with_scenarios(async_db, test_user):
    """
    Create a test suite with scenarios for integration tests.

    Returns:
        TestSuite: A test suite with 3 active scenarios
    """
    from models.test_suite import TestSuite
    from models.scenario_script import ScenarioScript, ScenarioStep

    # Create suite
    suite = TestSuite(
        name="Test Suite with Scenarios",
        description="A test suite with scenarios",
        category="Integration",
        is_active=True,
        created_by=test_user.id
    )

    async_db.add(suite)
    await async_db.commit()
    await async_db.refresh(suite)

    # Create scenarios
    scenarios_data = [
        {
            "name": "Weather Scenario",
            "description": "Test weather queries",
            "version": "1.0.0",
            "script_metadata": {"category": "Weather"}
        },
        {
            "name": "Music Scenario",
            "description": "Test music queries",
            "version": "1.0.0",
            "script_metadata": {"category": "Music"}
        },
        {
            "name": "News Scenario",
            "description": "Test news queries",
            "version": "1.0.0",
            "script_metadata": {"category": "News"}
        }
    ]

    for scenario_data in scenarios_data:
        scenario = ScenarioScript(
            created_by=test_user.id,
            is_active=True,
            approval_status="approved",
            **scenario_data
        )
        async_db.add(scenario)
        await async_db.flush()

        # Add a step to each scenario
        step = ScenarioStep(
            script_id=scenario.id,
            step_order=1,
            user_utterance=f"Test utterance for {scenario_data['name']}",
            expected_response="Expected response"
        )
        async_db.add(step)

    await async_db.commit()
    await async_db.refresh(suite)

    return suite


@pytest_asyncio.fixture
async def test_run_pending(async_db, test_suite_with_scenarios, test_user):
    """
    Create a pending test run for integration tests.

    Returns:
        TestRun: A test run in pending status
    """
    from services import orchestration_service

    test_run = await orchestration_service.create_test_run(
        db=async_db,
        suite_id=test_suite_with_scenarios.id,
        languages=["en"],
        trigger_type="manual",
        created_by=test_user.id
    )

    return test_run


@pytest_asyncio.fixture
async def test_run_completed(async_db, test_suite_with_scenarios, test_user):
    """
    Create a completed test run for integration tests.

    Returns:
        TestRun: A test run in completed status with test results
    """
    from services import orchestration_service

    test_run = await orchestration_service.create_test_run(
        db=async_db,
        suite_id=test_suite_with_scenarios.id,
        languages=["en"],
        trigger_type="manual",
        created_by=test_user.id
    )

    # Mark as running then completed
    test_run.mark_as_running()
    test_run.update_test_counts(passed=2, failed=1, skipped=0)
    test_run.mark_as_completed()

    await async_db.commit()
    await async_db.refresh(test_run)

    return test_run


@pytest_asyncio.fixture
async def validation_result(async_db, test_run_completed):
    """
    Create a validation result for integration tests.

    Returns:
        ValidationResult: A validation result linked to a test run
    """
    from models.validation_result import ValidationResult

    result = ValidationResult(
        test_run_id=test_run_completed.id,
        accuracy_score=0.85,
        confidence_score=0.90,
        semantic_similarity_score=0.88,
        command_kind_match_score=0.95,
        asr_confidence_score=0.82
    )

    async_db.add(result)
    await async_db.commit()
    await async_db.refresh(result)

    return result


# ==========================================
# Consolidated Fixtures for Service Testing
# ==========================================

@pytest.fixture
def project_root():
    """
    Provide the project root directory path.

    Returns:
        str: Absolute path to project root

    Example:
        def test_something(project_root):
            config_file = os.path.join(project_root, 'backend', 'api', 'config.py')
    """
    return os.path.dirname(os.path.dirname(__file__))


@pytest.fixture
def backend_services_dir(project_root):
    """
    Provide the backend services directory path.

    Returns:
        str: Absolute path to backend/services directory
    """
    return os.path.join(project_root, 'backend', 'services')


def service_file_reader(service_name):
    """
    Factory function to read service file content.

    Args:
        service_name: Name of service file (without .py extension)

    Returns:
        str: Content of the service file

    Example:
        content = service_file_reader('text_normalization_service')
    """
    service_file = os.path.join(
        os.path.dirname(__file__),
        '..', 'backend', 'services', f'{service_name}.py'
    )
    with open(service_file, 'r') as f:
        return f.read()


@pytest.fixture
def read_service_file():
    """
    Fixture factory for reading service files.

    Returns a function that can read any service file by name.

    Example:
        def test_something(read_service_file):
            content = read_service_file('user_service')
            assert 'class UserService' in content
    """
    return service_file_reader


@pytest.fixture
def sample_uuid():
    """
    Provide a consistent UUID for testing.

    Returns:
        UUID: A test UUID
    """
    from uuid import UUID
    return UUID('12345678-1234-5678-1234-567812345678')


@pytest.fixture
def sample_audio_bytes():
    """
    Provide sample audio bytes for testing audio utilities.

    Returns:
        bytes: Minimal valid WAV audio data

    Note:
        This is a minimal WAV header with silence. For actual audio testing,
        use soundfile to generate proper test audio.
    """
    import struct

    # Minimal WAV file: 44-byte header + 0 data bytes
    sample_rate = 16000
    num_channels = 1
    bits_per_sample = 16
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8

    # Generate 0.1 seconds of silence
    num_samples = sample_rate // 10  # 0.1 seconds
    data_size = num_samples * num_channels * (bits_per_sample // 8)

    header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF',
        36 + data_size,  # file size - 8
        b'WAVE',
        b'fmt ',
        16,  # format chunk size
        1,   # audio format (PCM)
        num_channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b'data',
        data_size
    )

    # Silence data
    data = b'\x00' * data_size

    return header + data


@pytest.fixture
def mock_async_session():
    """
    Provide a mock async database session.

    Returns:
        AsyncMock: Mock async session with common methods
    """
    from unittest.mock import AsyncMock, MagicMock

    session = MagicMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    session.delete = AsyncMock()
    session.flush = AsyncMock()

    return session


@pytest.fixture
def test_credentials():
    """
    Provide standard test credentials.

    Returns:
        dict: Dictionary with test user credentials
    """
    return {
        'email': 'test@example.com',
        'username': 'testuser',
        'password': 'TestPassword123!',
        'invalid_email': 'not-an-email',
        'weak_password': '123'
    }


# ==========================================
# Time Control Fixtures
# ==========================================

@pytest.fixture
def frozen_time():
    """
    Provide freezegun time freezing for tests.

    Returns a function that can be used to freeze time at a specific moment.

    Example:
        def test_token_expiration(frozen_time):
            with frozen_time("2024-01-01 12:00:00"):
                token = create_token()

            with frozen_time("2024-01-01 13:00:00"):
                # Token should be expired
                with pytest.raises(TokenExpiredError):
                    decode_token(token)
    """
    from freezegun import freeze_time
    return freeze_time


@pytest.fixture
def mock_datetime_now():
    """
    Provide a mock for datetime.now() using freezegun.

    Returns a context manager that freezes time.

    Example:
        def test_something(mock_datetime_now):
            with mock_datetime_now("2024-01-01"):
                result = some_function_using_datetime()
                assert result.date == "2024-01-01"
    """
    from freezegun import freeze_time
    return freeze_time


# ==========================================
# External Service Mock Factories
# ==========================================

@pytest.fixture
def mock_redis_client():
    """
    Provide a mock Redis client for testing.

    Returns:
        Mock: Mock Redis client with common methods

    Example:
        async def test_cache(mock_redis_client):
            await mock_redis_client.set("key", "value")
            result = await mock_redis_client.get("key")
    """
    from unittest.mock import Mock, AsyncMock

    mock_client = Mock()
    mock_client.get = AsyncMock(return_value=None)
    mock_client.set = AsyncMock(return_value=True)
    mock_client.setex = AsyncMock(return_value=True)
    mock_client.delete = AsyncMock(return_value=1)
    mock_client.exists = AsyncMock(return_value=0)
    mock_client.expire = AsyncMock(return_value=True)
    mock_client.ttl = AsyncMock(return_value=-1)
    mock_client.incr = AsyncMock(return_value=1)
    mock_client.decr = AsyncMock(return_value=0)
    mock_client.lpush = AsyncMock(return_value=1)
    mock_client.rpush = AsyncMock(return_value=1)
    mock_client.lpop = AsyncMock(return_value=None)
    mock_client.rpop = AsyncMock(return_value=None)
    mock_client.lrange = AsyncMock(return_value=[])
    mock_client.hset = AsyncMock(return_value=1)
    mock_client.hget = AsyncMock(return_value=None)
    mock_client.hgetall = AsyncMock(return_value={})
    mock_client.publish = AsyncMock(return_value=0)

    return mock_client


@pytest.fixture
def mock_twilio_client():
    """
    Provide a mock Twilio client for testing.

    Returns:
        Mock: Mock Twilio client with calls and messages

    Example:
        def test_send_sms(mock_twilio_client):
            mock_twilio_client.messages.create.return_value = Mock(sid="SM123")
            result = send_sms("Hello")
            assert result.sid == "SM123"
    """
    from unittest.mock import Mock, MagicMock

    mock_client = Mock()

    # Mock calls
    mock_calls = MagicMock()
    mock_calls.create = Mock(return_value=Mock(
        sid="CA123",
        status="queued",
        to="+1234567890",
        from_="+0987654321"
    ))
    mock_calls.get = Mock(return_value=Mock(
        sid="CA123",
        status="completed"
    ))
    mock_client.calls = mock_calls

    # Mock messages
    mock_messages = MagicMock()
    mock_messages.create = Mock(return_value=Mock(
        sid="SM123",
        status="sent",
        to="+1234567890",
        body="Test message"
    ))
    mock_messages.get = Mock(return_value=Mock(
        sid="SM123",
        status="delivered"
    ))
    mock_client.messages = mock_messages

    # Mock account info
    mock_client.account_sid = "AC_test_account"

    return mock_client


@pytest.fixture
def mock_s3_client():
    """
    Provide a mock AWS S3 client for testing.

    Returns:
        Mock: Mock S3 client with common methods

    Example:
        def test_upload(mock_s3_client):
            mock_s3_client.upload_file("local.txt", "bucket", "remote.txt")
            mock_s3_client.upload_file.assert_called_once()
    """
    from unittest.mock import Mock, MagicMock
    import io

    mock_client = Mock()

    # File operations
    mock_client.upload_file = Mock(return_value=None)
    mock_client.download_file = Mock(return_value=None)
    mock_client.upload_fileobj = Mock(return_value=None)
    mock_client.download_fileobj = Mock(return_value=None)

    # Object operations
    mock_client.get_object = Mock(return_value={
        'Body': io.BytesIO(b'test content'),
        'ContentLength': 12,
        'ContentType': 'text/plain'
    })
    mock_client.put_object = Mock(return_value={
        'ETag': '"abc123"',
        'VersionId': 'v1'
    })
    mock_client.delete_object = Mock(return_value={
        'DeleteMarker': True,
        'VersionId': 'v1'
    })
    mock_client.head_object = Mock(return_value={
        'ContentLength': 12,
        'ContentType': 'text/plain',
        'ETag': '"abc123"'
    })
    mock_client.copy_object = Mock(return_value={
        'CopyObjectResult': {'ETag': '"abc123"'}
    })

    # Bucket operations
    mock_client.list_objects_v2 = Mock(return_value={
        'Contents': [],
        'IsTruncated': False
    })
    mock_client.list_buckets = Mock(return_value={
        'Buckets': [{'Name': 'test-bucket'}]
    })

    # Presigned URLs
    mock_client.generate_presigned_url = Mock(
        return_value='https://s3.example.com/presigned-url'
    )

    return mock_client


@pytest.fixture
def mock_http_client():
    """
    Provide a mock HTTP client for testing.

    Returns:
        Mock: Mock HTTP client with common methods

    Example:
        async def test_api_call(mock_http_client):
            mock_http_client.get.return_value.json.return_value = {"data": "value"}
            result = await fetch_data()
            assert result["data"] == "value"
    """
    from unittest.mock import Mock, AsyncMock

    mock_client = Mock()

    # Create response mock factory
    def create_response(status_code=200, json_data=None, text="", content=b""):
        response = Mock()
        response.status_code = status_code
        response.ok = 200 <= status_code < 300
        response.json = Mock(return_value=json_data or {})
        response.text = text
        response.content = content
        response.headers = {}
        response.raise_for_status = Mock()
        return response

    # HTTP methods
    mock_client.get = AsyncMock(return_value=create_response())
    mock_client.post = AsyncMock(return_value=create_response(201))
    mock_client.put = AsyncMock(return_value=create_response())
    mock_client.patch = AsyncMock(return_value=create_response())
    mock_client.delete = AsyncMock(return_value=create_response(204))
    mock_client.head = AsyncMock(return_value=create_response())
    mock_client.options = AsyncMock(return_value=create_response())

    return mock_client
