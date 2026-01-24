"""
Test suite for S3 storage service (TASK-113)

Validates the storage service implementation:
- StorageService class with S3/boto3 integration
- upload_audio: Upload audio files to S3 and return URL
- download_audio: Download audio files from S3 URL
- delete_audio: Delete audio files from S3
- Support for different buckets
- Async methods for non-blocking I/O
"""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import io

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
SERVICES_DIR = BACKEND_DIR / "services"
STORAGE_SERVICE_FILE = SERVICES_DIR / "storage_service.py"


class TestStorageServiceFileStructure:
    """Test storage_service.py file structure"""

    def test_storage_service_file_exists(self):
        """Test that storage_service.py exists"""
        assert STORAGE_SERVICE_FILE.exists(), "storage_service.py should exist"
        assert STORAGE_SERVICE_FILE.is_file(), "storage_service.py should be a file"

    def test_storage_service_has_content(self):
        """Test that storage_service.py has content"""
        content = STORAGE_SERVICE_FILE.read_text()
        assert len(content) > 0, "storage_service.py should not be empty"


class TestStorageServiceImports:
    """Test necessary imports in storage_service.py"""

    @pytest.fixture
    def storage_service_content(self):
        """Load storage_service.py content"""
        return STORAGE_SERVICE_FILE.read_text()

    def test_imports_boto3(self, storage_service_content):
        """Test that boto3 is imported"""
        assert "import boto3" in storage_service_content or "from boto3 import" in storage_service_content, \
            "Should import boto3 for S3 access"

    def test_imports_asyncio_or_async(self, storage_service_content):
        """Test that async is used"""
        # Should have async methods
        assert "async def" in storage_service_content, \
            "Should have async methods"

    def test_imports_typing(self, storage_service_content):
        """Test that typing is imported"""
        assert "from typing import" in storage_service_content or "import typing" in storage_service_content, \
            "Should import typing for type hints"

    def test_imports_optional(self, storage_service_content):
        """Test that Optional is imported or used"""
        has_optional = "Optional" in storage_service_content
        assert has_optional, \
            "Should use Optional for optional parameters"


class TestStorageServiceClass:
    """Test StorageService class definition"""

    @pytest.fixture
    def storage_service_content(self):
        """Load storage_service.py content"""
        return STORAGE_SERVICE_FILE.read_text()

    def test_has_storage_service_class(self, storage_service_content):
        """Test that StorageService class exists"""
        assert "class StorageService" in storage_service_content, \
            "Should have StorageService class"

    def test_has_init_method(self, storage_service_content):
        """Test that __init__ method exists"""
        assert "def __init__" in storage_service_content, \
            "Should have __init__ method"

    def test_has_s3_client_attribute(self, storage_service_content):
        """Test that s3_client or similar attribute exists"""
        has_s3_client = "s3_client" in storage_service_content or "self.s3" in storage_service_content
        assert has_s3_client, \
            "Should have S3 client attribute"

    def test_has_docstring(self, storage_service_content):
        """Test that StorageService has docstring"""
        lines = storage_service_content.split('\n')
        in_class = False
        has_docstring = False

        for i, line in enumerate(lines):
            if 'class StorageService' in line:
                in_class = True
            elif in_class:
                if '"""' in line or "'''" in line:
                    has_docstring = True
                    break
                elif line.strip() and not line.strip().startswith('#'):
                    if not line.strip().startswith('class'):
                        break

        assert has_docstring, "StorageService should have docstring"


class TestUploadAudioMethod:
    """Test upload_audio method"""

    @pytest.fixture
    def storage_service_content(self):
        """Load storage_service.py content"""
        return STORAGE_SERVICE_FILE.read_text()

    def test_has_upload_audio_method(self, storage_service_content):
        """Test that upload_audio method exists"""
        assert "def upload_audio" in storage_service_content, \
            "Should have upload_audio method"

    def test_upload_audio_is_async(self, storage_service_content):
        """Test that upload_audio is async"""
        assert "async def upload_audio" in storage_service_content, \
            "upload_audio should be async"

    def test_upload_audio_has_file_data_param(self, storage_service_content):
        """Test that upload_audio has file_data parameter"""
        lines = storage_service_content.split('\n')
        for i, line in enumerate(lines):
            if 'async def upload_audio' in line:
                func_def = ''.join(lines[i:min(i+10, len(lines))])
                assert 'file_data' in func_def, \
                    "upload_audio should have file_data parameter"
                break

    def test_upload_audio_has_file_name_param(self, storage_service_content):
        """Test that upload_audio has file_name parameter"""
        lines = storage_service_content.split('\n')
        for i, line in enumerate(lines):
            if 'async def upload_audio' in line:
                func_def = ''.join(lines[i:min(i+10, len(lines))])
                assert 'file_name' in func_def, \
                    "upload_audio should have file_name parameter"
                break

    def test_upload_audio_has_bucket_param(self, storage_service_content):
        """Test that upload_audio has bucket parameter"""
        lines = storage_service_content.split('\n')
        for i, line in enumerate(lines):
            if 'async def upload_audio' in line:
                func_def = ''.join(lines[i:min(i+10, len(lines))])
                assert 'bucket' in func_def, \
                    "upload_audio should have bucket parameter"
                break

    def test_upload_audio_returns_str(self, storage_service_content):
        """Test that upload_audio return type is str"""
        assert "-> str" in storage_service_content, \
            "upload_audio should return str (S3 URL)"

    def test_upload_audio_has_docstring(self, storage_service_content):
        """Test that upload_audio has docstring"""
        lines = storage_service_content.split('\n')
        in_method = False
        has_docstring = False
        lines_checked = 0

        for i, line in enumerate(lines):
            if 'async def upload_audio' in line:
                in_method = True
            elif in_method:
                lines_checked += 1
                if '"""' in line or "'''" in line:
                    has_docstring = True
                    break
                elif lines_checked > 10:
                    break

        assert has_docstring, "upload_audio should have docstring"


class TestDownloadAudioMethod:
    """Test download_audio method"""

    @pytest.fixture
    def storage_service_content(self):
        """Load storage_service.py content"""
        return STORAGE_SERVICE_FILE.read_text()

    def test_has_download_audio_method(self, storage_service_content):
        """Test that download_audio method exists"""
        assert "def download_audio" in storage_service_content, \
            "Should have download_audio method"

    def test_download_audio_is_async(self, storage_service_content):
        """Test that download_audio is async"""
        assert "async def download_audio" in storage_service_content, \
            "download_audio should be async"

    def test_download_audio_has_s3_url_param(self, storage_service_content):
        """Test that download_audio has s3_url parameter"""
        lines = storage_service_content.split('\n')
        for i, line in enumerate(lines):
            if 'async def download_audio' in line:
                func_def = ''.join(lines[i:min(i+10, len(lines))])
                assert 's3_url' in func_def or 'url' in func_def, \
                    "download_audio should have s3_url parameter"
                break

    def test_download_audio_returns_bytes(self, storage_service_content):
        """Test that download_audio return type is bytes"""
        assert "-> bytes" in storage_service_content, \
            "download_audio should return bytes"

    def test_download_audio_has_docstring(self, storage_service_content):
        """Test that download_audio has docstring"""
        lines = storage_service_content.split('\n')
        in_method = False
        has_docstring = False
        lines_checked = 0

        for i, line in enumerate(lines):
            if 'async def download_audio' in line:
                in_method = True
            elif in_method:
                lines_checked += 1
                if '"""' in line or "'''" in line:
                    has_docstring = True
                    break
                elif lines_checked > 10:
                    break

        assert has_docstring, "download_audio should have docstring"


class TestDeleteAudioMethod:
    """Test delete_audio method"""

    @pytest.fixture
    def storage_service_content(self):
        """Load storage_service.py content"""
        return STORAGE_SERVICE_FILE.read_text()

    def test_has_delete_audio_method(self, storage_service_content):
        """Test that delete_audio method exists"""
        assert "def delete_audio" in storage_service_content, \
            "Should have delete_audio method"

    def test_delete_audio_is_async(self, storage_service_content):
        """Test that delete_audio is async"""
        assert "async def delete_audio" in storage_service_content, \
            "delete_audio should be async"

    def test_delete_audio_has_s3_url_param(self, storage_service_content):
        """Test that delete_audio has s3_url parameter"""
        lines = storage_service_content.split('\n')
        for i, line in enumerate(lines):
            if 'async def delete_audio' in line:
                func_def = ''.join(lines[i:min(i+10, len(lines))])
                assert 's3_url' in func_def or 'url' in func_def, \
                    "delete_audio should have s3_url parameter"
                break

    def test_delete_audio_returns_bool(self, storage_service_content):
        """Test that delete_audio return type is bool"""
        assert "-> bool" in storage_service_content, \
            "delete_audio should return bool"

    def test_delete_audio_has_docstring(self, storage_service_content):
        """Test that delete_audio has docstring"""
        lines = storage_service_content.split('\n')
        in_method = False
        has_docstring = False
        lines_checked = 0

        for i, line in enumerate(lines):
            if 'async def delete_audio' in line:
                in_method = True
            elif in_method:
                lines_checked += 1
                if '"""' in line or "'''" in line:
                    has_docstring = True
                    break
                elif lines_checked > 10:
                    break

        assert has_docstring, "delete_audio should have docstring"


class TestStorageServiceImportability:
    """Test that storage service can be imported"""

    def test_can_import_storage_service_module(self):
        """Test that storage_service module can be imported"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from services import storage_service
            assert storage_service is not None, \
                "storage_service module should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import storage_service: {e}")

    def test_can_import_storage_service_class(self):
        """Test that StorageService class can be imported"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from services.storage_service import StorageService
            assert StorageService is not None, \
                "StorageService class should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import StorageService: {e}")

    def test_can_instantiate_storage_service(self):
        """Test that StorageService can be instantiated"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from services.storage_service import StorageService
            service = StorageService()
            assert service is not None, \
                "Should be able to instantiate StorageService"
        except Exception as e:
            pytest.fail(f"Cannot instantiate StorageService: {e}")


class TestUploadAudioFunctionality:
    """Test upload_audio functionality with mocked S3"""

    @pytest.mark.asyncio
    async def test_upload_audio_returns_str(self):
        """Test that upload_audio returns a string URL"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from services.storage_service import StorageService

        with patch('boto3.client') as mock_boto3_client:
            # Mock S3 client
            mock_s3 = MagicMock()
            mock_boto3_client.return_value = mock_s3

            service = StorageService()

            # Mock the upload
            test_data = b"test audio data"
            result = await service.upload_audio(test_data, "test.mp3")

            assert isinstance(result, str), "Should return string URL"
            assert len(result) > 0, "URL should not be empty"

    @pytest.mark.asyncio
    async def test_upload_audio_calls_s3_put_object(self):
        """Test that upload_audio calls S3 put_object"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from services.storage_service import StorageService

        with patch('boto3.client') as mock_boto3_client:
            mock_s3 = MagicMock()
            mock_boto3_client.return_value = mock_s3

            service = StorageService()

            test_data = b"test audio data"
            await service.upload_audio(test_data, "test.mp3", bucket="test-bucket")

            # Verify put_object was called
            mock_s3.put_object.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_audio_with_custom_bucket(self):
        """Test that upload_audio works with custom bucket"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from services.storage_service import StorageService

        with patch('boto3.client') as mock_boto3_client:
            mock_s3 = MagicMock()
            mock_boto3_client.return_value = mock_s3

            service = StorageService()

            test_data = b"test audio data"
            result = await service.upload_audio(test_data, "test.mp3", bucket="custom-bucket")

            assert isinstance(result, str), "Should return string URL"
            # Verify the custom bucket was used
            call_args = mock_s3.put_object.call_args
            if call_args:
                assert call_args[1]['Bucket'] == 'custom-bucket' or call_args[0][0] == 'custom-bucket'


class TestDownloadAudioFunctionality:
    """Test download_audio functionality with mocked S3"""

    @pytest.mark.asyncio
    async def test_download_audio_returns_bytes(self):
        """Test that download_audio returns bytes"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from services.storage_service import StorageService

        with patch('boto3.client') as mock_boto3_client:
            mock_s3 = MagicMock()
            mock_boto3_client.return_value = mock_s3

            # Mock the download response
            mock_response = {
                'Body': io.BytesIO(b"downloaded audio data")
            }
            mock_s3.get_object.return_value = mock_response

            service = StorageService()

            result = await service.download_audio("s3://test-bucket/test.mp3")

            assert isinstance(result, bytes), "Should return bytes"
            assert len(result) > 0, "Should return non-empty bytes"

    @pytest.mark.asyncio
    async def test_download_audio_calls_s3_get_object(self):
        """Test that download_audio calls S3 get_object"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from services.storage_service import StorageService

        with patch('boto3.client') as mock_boto3_client:
            mock_s3 = MagicMock()
            mock_boto3_client.return_value = mock_s3

            mock_response = {
                'Body': io.BytesIO(b"test data")
            }
            mock_s3.get_object.return_value = mock_response

            service = StorageService()

            await service.download_audio("s3://test-bucket/test.mp3")

            # Verify get_object was called
            mock_s3.get_object.assert_called_once()


class TestDeleteAudioFunctionality:
    """Test delete_audio functionality with mocked S3"""

    @pytest.mark.asyncio
    async def test_delete_audio_returns_bool(self):
        """Test that delete_audio returns a boolean"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from services.storage_service import StorageService

        with patch('boto3.client') as mock_boto3_client:
            mock_s3 = MagicMock()
            mock_boto3_client.return_value = mock_s3

            service = StorageService()

            result = await service.delete_audio("s3://test-bucket/test.mp3")

            assert isinstance(result, bool), "Should return boolean"

    @pytest.mark.asyncio
    async def test_delete_audio_calls_s3_delete_object(self):
        """Test that delete_audio calls S3 delete_object"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from services.storage_service import StorageService

        with patch('boto3.client') as mock_boto3_client:
            mock_s3 = MagicMock()
            mock_boto3_client.return_value = mock_s3

            service = StorageService()

            await service.delete_audio("s3://test-bucket/test.mp3")

            # Verify delete_object was called
            mock_s3.delete_object.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_audio_returns_true_on_success(self):
        """Test that delete_audio returns True on successful deletion"""
        import sys
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        from services.storage_service import StorageService

        with patch('boto3.client') as mock_boto3_client:
            mock_s3 = MagicMock()
            mock_boto3_client.return_value = mock_s3

            service = StorageService()

            result = await service.delete_audio("s3://test-bucket/test.mp3")

            assert result is True, "Should return True on successful deletion"


class TestTaskRequirements:
    """Test TASK-113 specific requirements"""

    def test_task_113_storage_service_class(self):
        """Test TASK-113 requirement: StorageService class exists"""
        content = STORAGE_SERVICE_FILE.read_text()
        assert "class StorageService" in content, \
            "TASK-113 requirement: Must have StorageService class"

    def test_task_113_upload_audio_method(self):
        """Test TASK-113 requirement: upload_audio method exists"""
        content = STORAGE_SERVICE_FILE.read_text()
        assert "async def upload_audio" in content, \
            "TASK-113 requirement: Must have async upload_audio method"

    def test_task_113_download_audio_method(self):
        """Test TASK-113 requirement: download_audio method exists"""
        content = STORAGE_SERVICE_FILE.read_text()
        assert "async def download_audio" in content, \
            "TASK-113 requirement: Must have async download_audio method"

    def test_task_113_delete_audio_method(self):
        """Test TASK-113 requirement: delete_audio method exists"""
        content = STORAGE_SERVICE_FILE.read_text()
        assert "async def delete_audio" in content, \
            "TASK-113 requirement: Must have async delete_audio method"

    def test_task_113_boto3_integration(self):
        """Test TASK-113 requirement: Uses boto3 for S3"""
        content = STORAGE_SERVICE_FILE.read_text()
        assert "boto3" in content, \
            "TASK-113 requirement: Must use boto3 for S3 access"

    def test_task_113_async_methods(self):
        """Test TASK-113 requirement: All methods are async"""
        content = STORAGE_SERVICE_FILE.read_text()
        assert "async def upload_audio" in content, "upload_audio must be async"
        assert "async def download_audio" in content, "download_audio must be async"
        assert "async def delete_audio" in content, "delete_audio must be async"
