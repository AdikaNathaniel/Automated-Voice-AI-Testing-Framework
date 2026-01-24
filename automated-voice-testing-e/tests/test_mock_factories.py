"""
Test suite for mock factories in conftest.py

Verifies that all mock factories are properly implemented and usable.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestMockAsyncSession:
    """Test mock_async_session fixture"""

    def test_mock_async_session_exists(self, mock_async_session):
        """Test mock_async_session fixture is available"""
        assert mock_async_session is not None

    def test_mock_async_session_has_execute(self, mock_async_session):
        """Test mock has execute method"""
        assert hasattr(mock_async_session, 'execute')

    def test_mock_async_session_has_commit(self, mock_async_session):
        """Test mock has commit method"""
        assert hasattr(mock_async_session, 'commit')

    def test_mock_async_session_has_rollback(self, mock_async_session):
        """Test mock has rollback method"""
        assert hasattr(mock_async_session, 'rollback')

    def test_mock_async_session_has_add(self, mock_async_session):
        """Test mock has add method"""
        assert hasattr(mock_async_session, 'add')

    def test_mock_async_session_has_delete(self, mock_async_session):
        """Test mock has delete method"""
        assert hasattr(mock_async_session, 'delete')


class TestMockRedisClient:
    """Test mock_redis_client fixture"""

    def test_mock_redis_exists(self, mock_redis_client):
        """Test mock_redis_client fixture is available"""
        assert mock_redis_client is not None

    def test_mock_redis_has_get(self, mock_redis_client):
        """Test mock has get method"""
        assert hasattr(mock_redis_client, 'get')

    def test_mock_redis_has_set(self, mock_redis_client):
        """Test mock has set method"""
        assert hasattr(mock_redis_client, 'set')

    def test_mock_redis_has_delete(self, mock_redis_client):
        """Test mock has delete method"""
        assert hasattr(mock_redis_client, 'delete')

    def test_mock_redis_has_setex(self, mock_redis_client):
        """Test mock has setex method"""
        assert hasattr(mock_redis_client, 'setex')


class TestMockTwilioClient:
    """Test mock_twilio_client fixture"""

    def test_mock_twilio_exists(self, mock_twilio_client):
        """Test mock_twilio_client fixture is available"""
        assert mock_twilio_client is not None

    def test_mock_twilio_has_calls(self, mock_twilio_client):
        """Test mock has calls attribute"""
        assert hasattr(mock_twilio_client, 'calls')

    def test_mock_twilio_has_messages(self, mock_twilio_client):
        """Test mock has messages attribute"""
        assert hasattr(mock_twilio_client, 'messages')


class TestMockAWSS3Client:
    """Test mock_s3_client fixture"""

    def test_mock_s3_exists(self, mock_s3_client):
        """Test mock_s3_client fixture is available"""
        assert mock_s3_client is not None

    def test_mock_s3_has_upload_file(self, mock_s3_client):
        """Test mock has upload_file method"""
        assert hasattr(mock_s3_client, 'upload_file')

    def test_mock_s3_has_download_file(self, mock_s3_client):
        """Test mock has download_file method"""
        assert hasattr(mock_s3_client, 'download_file')

    def test_mock_s3_has_get_object(self, mock_s3_client):
        """Test mock has get_object method"""
        assert hasattr(mock_s3_client, 'get_object')

    def test_mock_s3_has_put_object(self, mock_s3_client):
        """Test mock has put_object method"""
        assert hasattr(mock_s3_client, 'put_object')

    def test_mock_s3_has_delete_object(self, mock_s3_client):
        """Test mock has delete_object method"""
        assert hasattr(mock_s3_client, 'delete_object')


class TestMockHttpClient:
    """Test mock_http_client fixture"""

    def test_mock_http_exists(self, mock_http_client):
        """Test mock_http_client fixture is available"""
        assert mock_http_client is not None

    def test_mock_http_has_get(self, mock_http_client):
        """Test mock has get method"""
        assert hasattr(mock_http_client, 'get')

    def test_mock_http_has_post(self, mock_http_client):
        """Test mock has post method"""
        assert hasattr(mock_http_client, 'post')

    def test_mock_http_has_put(self, mock_http_client):
        """Test mock has put method"""
        assert hasattr(mock_http_client, 'put')

    def test_mock_http_has_delete(self, mock_http_client):
        """Test mock has delete method"""
        assert hasattr(mock_http_client, 'delete')


class TestMockFactoryHelpers:
    """Test helper fixtures for mocking"""

    def test_sample_uuid_exists(self, sample_uuid):
        """Test sample_uuid fixture is available"""
        from uuid import UUID
        assert isinstance(sample_uuid, UUID)

    def test_test_credentials_exists(self, test_credentials):
        """Test test_credentials fixture is available"""
        assert isinstance(test_credentials, dict)
        assert 'email' in test_credentials
        assert 'password' in test_credentials

    def test_frozen_time_exists(self, frozen_time):
        """Test frozen_time fixture is available"""
        assert frozen_time is not None
        assert callable(frozen_time)

