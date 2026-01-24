"""
Unit tests for audio upload API endpoints.

Tests the audio upload, retrieval, and deletion endpoints for scenario steps.
Covers file format validation, transcription, S3 storage, and metadata management.
Uses mocked services (S3, Whisper) to test route logic without external dependencies.
"""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, UploadFile
import io

from api.routes.scenarios import (
    upload_step_audio,
    get_step_audio,
    delete_step_audio,
    batch_upload_step_audio,
)
from api.schemas.auth import UserResponse
from api.auth.roles import Role


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_db():
    """Create mock database session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def admin_user():
    """Create admin user with mutation permissions."""
    user = MagicMock(spec=UserResponse)
    user.id = uuid4()
    user.email = "admin@example.com"
    user.username = "admin"
    user.role = Role.ORG_ADMIN.value
    user.is_active = True
    user.tenant_id = uuid4()
    return user


@pytest.fixture
def viewer_user():
    """Create viewer user without mutation permissions."""
    user = MagicMock(spec=UserResponse)
    user.id = uuid4()
    user.email = "viewer@example.com"
    user.username = "viewer"
    user.role = Role.VIEWER.value
    user.is_active = True
    user.tenant_id = uuid4()
    return user


@pytest.fixture
def sample_scenario_id():
    """Generate sample scenario UUID."""
    return uuid4()


@pytest.fixture
def sample_step_id():
    """Generate sample step UUID."""
    return uuid4()


@pytest.fixture
def mock_mp3_file():
    """Create mock MP3 upload file."""
    file = MagicMock(spec=UploadFile)
    file.filename = "test_audio.mp3"
    file.content_type = "audio/mpeg"
    # Minimal MP3 header bytes (mock)
    file.read = AsyncMock(return_value=b'\xff\xfb\x90\x00' + b'\x00' * 1000)
    return file


@pytest.fixture
def mock_wav_file():
    """Create mock WAV upload file."""
    file = MagicMock(spec=UploadFile)
    file.filename = "test_audio.wav"
    file.content_type = "audio/wav"
    # Minimal WAV header bytes (mock)
    file.read = AsyncMock(return_value=b'RIFF' + b'\x00' * 1000)
    return file


@pytest.fixture
def mock_invalid_file():
    """Create mock invalid (PDF) upload file."""
    file = MagicMock(spec=UploadFile)
    file.filename = "document.pdf"
    file.content_type = "application/pdf"
    file.read = AsyncMock(return_value=b'%PDF-1.4' + b'\x00' * 100)
    return file


@pytest.fixture
def mock_scenario():
    """Create mock scenario object."""
    scenario = MagicMock()
    scenario.id = uuid4()
    scenario.name = "Test Scenario"
    scenario.tenant_id = uuid4()
    return scenario


@pytest.fixture
def mock_step():
    """Create mock step object without audio."""
    step = MagicMock()
    step.id = uuid4()
    step.scenario_id = uuid4()
    step.step_metadata = {}
    return step


@pytest.fixture
def mock_step_with_audio():
    """Create mock step object with existing audio."""
    step = MagicMock()
    step.id = uuid4()
    step.scenario_id = uuid4()
    step.step_metadata = {
        "uploaded_audio": {
            "en-US": {
                "s3_key": "scenarios/test/steps/test/audio-en-US.mp3",
                "transcription": "Hello world",
                "duration_ms": 2500,
                "original_format": "mp3",
                "stt_confidence": 0.95,
            }
        }
    }
    return step


@pytest.fixture
def mock_transcription_result():
    """Create mock Whisper transcription result."""
    result = MagicMock()
    result.text = "Hello, this is a test transcription."
    result.language_probability = 0.98
    return result


# =============================================================================
# TestAudioUploadEndpoint
# =============================================================================

class TestAudioUploadEndpoint:
    """Tests for POST /scenarios/{id}/steps/{step_id}/audio"""

    @pytest.mark.asyncio
    async def test_upload_mp3_success(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_mp3_file, mock_scenario, mock_step, mock_transcription_result
    ):
        """Upload MP3 file and verify transcription."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('services.audio_utils.validate_audio_format', return_value=True), \
             patch('services.audio_utils.get_audio_duration', return_value=2.5), \
             patch('services.stt_service.get_stt_service') as mock_stt, \
             patch('services.storage_service.get_storage_service') as mock_storage:

            # Setup mocks
            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step)
            mock_service.update_step_audio = AsyncMock()

            mock_stt_instance = MagicMock()
            mock_stt_instance.transcribe.return_value = mock_transcription_result
            mock_stt.return_value = mock_stt_instance

            mock_storage_instance = AsyncMock()
            mock_storage_instance.upload_audio = AsyncMock()
            mock_storage.return_value = mock_storage_instance

            # Execute
            result = await upload_step_audio(
                scenario_id=sample_scenario_id,
                step_id=sample_step_id,
                file=mock_mp3_file,
                language_code="en-US",
                db=mock_db,
                current_user=admin_user
            )

            # Verify
            assert result.transcription == "Hello, this is a test transcription."
            assert result.stt_confidence == 0.98
            assert result.original_format == "mp3"
            assert result.language_code == "en-US"
            assert result.duration_ms == 2500
            mock_storage_instance.upload_audio.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_wav_success(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_wav_file, mock_scenario, mock_step, mock_transcription_result
    ):
        """Upload WAV file and verify transcription."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('services.audio_utils.validate_audio_format', return_value=True), \
             patch('services.audio_utils.get_audio_duration', return_value=3.0), \
             patch('services.stt_service.get_stt_service') as mock_stt, \
             patch('services.storage_service.get_storage_service') as mock_storage:

            # Setup mocks
            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step)
            mock_service.update_step_audio = AsyncMock()

            mock_stt_instance = MagicMock()
            mock_stt_instance.transcribe.return_value = mock_transcription_result
            mock_stt.return_value = mock_stt_instance

            mock_storage_instance = AsyncMock()
            mock_storage_instance.upload_audio = AsyncMock()
            mock_storage.return_value = mock_storage_instance

            # Execute
            result = await upload_step_audio(
                scenario_id=sample_scenario_id,
                step_id=sample_step_id,
                file=mock_wav_file,
                language_code="en-US",
                db=mock_db,
                current_user=admin_user
            )

            # Verify
            assert result.original_format == "wav"
            assert result.duration_ms == 3000

    @pytest.mark.asyncio
    async def test_upload_invalid_format_rejected(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id, mock_invalid_file
    ):
        """Reject non-audio files (e.g., PDF)."""
        with pytest.raises(HTTPException) as exc_info:
            await upload_step_audio(
                scenario_id=sample_scenario_id,
                step_id=sample_step_id,
                file=mock_invalid_file,
                language_code="en-US",
                db=mock_db,
                current_user=admin_user
            )

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Unsupported audio format" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_upload_corrupted_audio_rejected(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_mp3_file, mock_scenario, mock_step
    ):
        """Reject audio files that can't be decoded."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('services.audio_utils.validate_audio_format', return_value=False):

            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step)

            with pytest.raises(HTTPException) as exc_info:
                await upload_step_audio(
                    scenario_id=sample_scenario_id,
                    step_id=sample_step_id,
                    file=mock_mp3_file,
                    language_code="en-US",
                    db=mock_db,
                    current_user=admin_user
                )

            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "Invalid audio data" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_upload_scenario_not_found(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id, mock_mp3_file
    ):
        """Return 404 when scenario doesn't exist."""
        with patch('api.routes.scenarios.scenario_service') as mock_service:
            mock_service.get = AsyncMock(return_value=None)

            with pytest.raises(HTTPException) as exc_info:
                await upload_step_audio(
                    scenario_id=sample_scenario_id,
                    step_id=sample_step_id,
                    file=mock_mp3_file,
                    language_code="en-US",
                    db=mock_db,
                    current_user=admin_user
                )

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert "Scenario" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_upload_step_not_found(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_mp3_file, mock_scenario
    ):
        """Return 404 when step doesn't exist."""
        with patch('api.routes.scenarios.scenario_service') as mock_service:
            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=None)

            with pytest.raises(HTTPException) as exc_info:
                await upload_step_audio(
                    scenario_id=sample_scenario_id,
                    step_id=sample_step_id,
                    file=mock_mp3_file,
                    language_code="en-US",
                    db=mock_db,
                    current_user=admin_user
                )

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert "Step" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_upload_permission_denied_for_viewer(
        self, mock_db, viewer_user, sample_scenario_id, sample_step_id, mock_mp3_file
    ):
        """Viewer cannot upload audio."""
        with pytest.raises(HTTPException) as exc_info:
            await upload_step_audio(
                scenario_id=sample_scenario_id,
                step_id=sample_step_id,
                file=mock_mp3_file,
                language_code="en-US",
                db=mock_db,
                current_user=viewer_user
            )

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_upload_multi_language_support(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_mp3_file, mock_scenario, mock_step, mock_transcription_result
    ):
        """Different languages can have different audio."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('services.audio_utils.validate_audio_format', return_value=True), \
             patch('services.audio_utils.get_audio_duration', return_value=2.0), \
             patch('services.stt_service.get_stt_service') as mock_stt, \
             patch('services.storage_service.get_storage_service') as mock_storage:

            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step)
            mock_service.update_step_audio = AsyncMock()

            mock_stt_instance = MagicMock()
            mock_stt_instance.transcribe.return_value = mock_transcription_result
            mock_stt.return_value = mock_stt_instance

            mock_storage_instance = AsyncMock()
            mock_storage_instance.upload_audio = AsyncMock()
            mock_storage.return_value = mock_storage_instance

            # Upload Spanish audio
            result = await upload_step_audio(
                scenario_id=sample_scenario_id,
                step_id=sample_step_id,
                file=mock_mp3_file,
                language_code="es-ES",
                db=mock_db,
                current_user=admin_user
            )

            assert result.language_code == "es-ES"
            # Verify S3 key includes language code
            assert "es-ES" in result.s3_key

    @pytest.mark.asyncio
    async def test_transcription_returns_confidence(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_mp3_file, mock_scenario, mock_step
    ):
        """Verify STT confidence is returned."""
        mock_result = MagicMock()
        mock_result.text = "Test transcription"
        mock_result.language_probability = 0.87

        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('services.audio_utils.validate_audio_format', return_value=True), \
             patch('services.audio_utils.get_audio_duration', return_value=1.5), \
             patch('services.stt_service.get_stt_service') as mock_stt, \
             patch('services.storage_service.get_storage_service') as mock_storage:

            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step)
            mock_service.update_step_audio = AsyncMock()

            mock_stt_instance = MagicMock()
            mock_stt_instance.transcribe.return_value = mock_result
            mock_stt.return_value = mock_stt_instance

            mock_storage_instance = AsyncMock()
            mock_storage_instance.upload_audio = AsyncMock()
            mock_storage.return_value = mock_storage_instance

            result = await upload_step_audio(
                scenario_id=sample_scenario_id,
                step_id=sample_step_id,
                file=mock_mp3_file,
                language_code="en-US",
                db=mock_db,
                current_user=admin_user
            )

            assert result.stt_confidence == 0.87

    @pytest.mark.asyncio
    async def test_upload_s3_failure_returns_500(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_mp3_file, mock_scenario, mock_step, mock_transcription_result
    ):
        """S3 upload failure returns 500 error."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('services.audio_utils.validate_audio_format', return_value=True), \
             patch('services.audio_utils.get_audio_duration', return_value=2.0), \
             patch('services.stt_service.get_stt_service') as mock_stt, \
             patch('services.storage_service.get_storage_service') as mock_storage:

            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step)

            mock_stt_instance = MagicMock()
            mock_stt_instance.transcribe.return_value = mock_transcription_result
            mock_stt.return_value = mock_stt_instance

            mock_storage_instance = AsyncMock()
            mock_storage_instance.upload_audio = AsyncMock(
                side_effect=Exception("S3 connection failed")
            )
            mock_storage.return_value = mock_storage_instance

            with pytest.raises(HTTPException) as exc_info:
                await upload_step_audio(
                    scenario_id=sample_scenario_id,
                    step_id=sample_step_id,
                    file=mock_mp3_file,
                    language_code="en-US",
                    db=mock_db,
                    current_user=admin_user
                )

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to store audio" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_upload_exceeds_size_limit(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id
    ):
        """Reject files over size limit (25MB)."""
        # Create a mock file that exceeds size limit
        large_file = MagicMock(spec=UploadFile)
        large_file.filename = "large_audio.mp3"
        large_file.content_type = "audio/mpeg"
        # 30MB of data (exceeds 25MB limit)
        large_file.read = AsyncMock(return_value=b'\x00' * (30 * 1024 * 1024))

        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('services.audio_utils.validate_audio_format', return_value=True), \
             patch('services.audio_utils.get_audio_duration', side_effect=Exception("File too large")):

            mock_scenario = MagicMock()
            mock_scenario.id = sample_scenario_id
            mock_service.get = AsyncMock(return_value=mock_scenario)

            mock_step = MagicMock()
            mock_step.id = sample_step_id
            mock_step.step_metadata = {}
            mock_service.get_step = AsyncMock(return_value=mock_step)

            with pytest.raises(HTTPException) as exc_info:
                await upload_step_audio(
                    scenario_id=sample_scenario_id,
                    step_id=sample_step_id,
                    file=large_file,
                    language_code="en-US",
                    db=mock_db,
                    current_user=admin_user
                )

            # Should fail during validation/processing
            assert exc_info.value.status_code in [
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ]

    @pytest.mark.asyncio
    async def test_upload_overwrites_existing(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_mp3_file, mock_scenario, mock_step_with_audio, mock_transcription_result
    ):
        """Uploading new audio replaces existing audio for same language."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('services.audio_utils.validate_audio_format', return_value=True), \
             patch('services.audio_utils.get_audio_duration', return_value=3.5), \
             patch('services.stt_service.get_stt_service') as mock_stt, \
             patch('services.storage_service.get_storage_service') as mock_storage:

            # Step already has audio for en-US
            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step_with_audio)
            mock_service.update_step_audio = AsyncMock()

            mock_stt_instance = MagicMock()
            new_transcription = MagicMock()
            new_transcription.text = "New transcription text"
            new_transcription.language_probability = 0.99
            mock_stt_instance.transcribe.return_value = new_transcription
            mock_stt.return_value = mock_stt_instance

            mock_storage_instance = AsyncMock()
            mock_storage_instance.upload_audio = AsyncMock()
            mock_storage.return_value = mock_storage_instance

            # Upload new audio to same language
            result = await upload_step_audio(
                scenario_id=sample_scenario_id,
                step_id=sample_step_id,
                file=mock_mp3_file,
                language_code="en-US",
                db=mock_db,
                current_user=admin_user
            )

            # Should have new transcription
            assert result.transcription == "New transcription text"
            assert result.stt_confidence == 0.99
            assert result.duration_ms == 3500

            # Verify update was called (overwrites existing)
            mock_service.update_step_audio.assert_called_once()


# =============================================================================
# TestAudioRetrievalEndpoint
# =============================================================================

class TestAudioRetrievalEndpoint:
    """Tests for GET /scenarios/{id}/steps/{step_id}/audio/{lang}"""

    @pytest.mark.asyncio
    async def test_get_audio_returns_presigned_url(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id, mock_step_with_audio
    ):
        """Verify presigned URL is generated."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('services.storage_service.get_storage_service') as mock_storage:

            mock_service.get_step = AsyncMock(return_value=mock_step_with_audio)

            mock_storage_instance = AsyncMock()
            mock_storage_instance.get_presigned_url = AsyncMock(
                return_value="https://minio.example.com/bucket/audio.mp3?signature=abc123"
            )
            mock_storage.return_value = mock_storage_instance

            result = await get_step_audio(
                scenario_id=sample_scenario_id,
                step_id=sample_step_id,
                language_code="en-US",
                db=mock_db,
                current_user=admin_user
            )

            assert result.download_url is not None
            assert "https://" in result.download_url
            assert result.transcription == "Hello world"
            assert result.stt_confidence == 0.95

    @pytest.mark.asyncio
    async def test_get_audio_nonexistent_returns_404(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id, mock_step
    ):
        """Missing audio returns 404."""
        with patch('api.routes.scenarios.scenario_service') as mock_service:
            mock_service.get_step = AsyncMock(return_value=mock_step)

            with pytest.raises(HTTPException) as exc_info:
                await get_step_audio(
                    scenario_id=sample_scenario_id,
                    step_id=sample_step_id,
                    language_code="en-US",
                    db=mock_db,
                    current_user=admin_user
                )

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert "No audio found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_audio_step_not_found(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id
    ):
        """Step not found returns 404."""
        with patch('api.routes.scenarios.scenario_service') as mock_service:
            mock_service.get_step = AsyncMock(return_value=None)

            with pytest.raises(HTTPException) as exc_info:
                await get_step_audio(
                    scenario_id=sample_scenario_id,
                    step_id=sample_step_id,
                    language_code="en-US",
                    db=mock_db,
                    current_user=admin_user
                )

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert "Step" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_audio_wrong_language_returns_404(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id, mock_step_with_audio
    ):
        """Request for non-existent language returns 404."""
        with patch('api.routes.scenarios.scenario_service') as mock_service:
            mock_service.get_step = AsyncMock(return_value=mock_step_with_audio)

            with pytest.raises(HTTPException) as exc_info:
                await get_step_audio(
                    scenario_id=sample_scenario_id,
                    step_id=sample_step_id,
                    language_code="fr-FR",  # French not uploaded
                    db=mock_db,
                    current_user=admin_user
                )

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# TestAudioDeletionEndpoint
# =============================================================================

class TestAudioDeletionEndpoint:
    """Tests for DELETE /scenarios/{id}/steps/{step_id}/audio/{lang}"""

    @pytest.mark.asyncio
    async def test_delete_audio_removes_from_s3(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id, mock_step_with_audio
    ):
        """Verify S3 deletion is called."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('services.storage_service.get_storage_service') as mock_storage:

            mock_service.get_step = AsyncMock(return_value=mock_step_with_audio)
            mock_service.remove_step_audio = AsyncMock()

            mock_storage_instance = AsyncMock()
            mock_storage_instance.delete_audio = AsyncMock()
            mock_storage.return_value = mock_storage_instance

            await delete_step_audio(
                scenario_id=sample_scenario_id,
                step_id=sample_step_id,
                language_code="en-US",
                db=mock_db,
                current_user=admin_user
            )

            mock_storage_instance.delete_audio.assert_called_once_with(
                key="scenarios/test/steps/test/audio-en-US.mp3"
            )

    @pytest.mark.asyncio
    async def test_delete_audio_updates_metadata(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id, mock_step_with_audio
    ):
        """Verify step metadata is updated."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('services.storage_service.get_storage_service') as mock_storage:

            mock_service.get_step = AsyncMock(return_value=mock_step_with_audio)
            mock_service.remove_step_audio = AsyncMock()

            mock_storage_instance = AsyncMock()
            mock_storage_instance.delete_audio = AsyncMock()
            mock_storage.return_value = mock_storage_instance

            await delete_step_audio(
                scenario_id=sample_scenario_id,
                step_id=sample_step_id,
                language_code="en-US",
                db=mock_db,
                current_user=admin_user
            )

            mock_service.remove_step_audio.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_audio_not_found(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id, mock_step
    ):
        """Deleting non-existent audio returns 404."""
        with patch('api.routes.scenarios.scenario_service') as mock_service:
            mock_service.get_step = AsyncMock(return_value=mock_step)

            with pytest.raises(HTTPException) as exc_info:
                await delete_step_audio(
                    scenario_id=sample_scenario_id,
                    step_id=sample_step_id,
                    language_code="en-US",
                    db=mock_db,
                    current_user=admin_user
                )

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_delete_permission_denied_for_viewer(
        self, mock_db, viewer_user, sample_scenario_id, sample_step_id
    ):
        """Viewer cannot delete audio."""
        with pytest.raises(HTTPException) as exc_info:
            await delete_step_audio(
                scenario_id=sample_scenario_id,
                step_id=sample_step_id,
                language_code="en-US",
                db=mock_db,
                current_user=viewer_user
            )

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_delete_step_not_found(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id
    ):
        """Deleting from non-existent step returns 404."""
        with patch('api.routes.scenarios.scenario_service') as mock_service:
            mock_service.get_step = AsyncMock(return_value=None)

            with pytest.raises(HTTPException) as exc_info:
                await delete_step_audio(
                    scenario_id=sample_scenario_id,
                    step_id=sample_step_id,
                    language_code="en-US",
                    db=mock_db,
                    current_user=admin_user
                )

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_delete_s3_failure_still_updates_metadata(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id, mock_step_with_audio
    ):
        """S3 deletion failure is logged but metadata still updated."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('services.storage_service.get_storage_service') as mock_storage:

            mock_service.get_step = AsyncMock(return_value=mock_step_with_audio)
            mock_service.remove_step_audio = AsyncMock()

            mock_storage_instance = AsyncMock()
            mock_storage_instance.delete_audio = AsyncMock(
                side_effect=Exception("S3 error")
            )
            mock_storage.return_value = mock_storage_instance

            # Should not raise - S3 errors are logged but not fatal
            await delete_step_audio(
                scenario_id=sample_scenario_id,
                step_id=sample_step_id,
                language_code="en-US",
                db=mock_db,
                current_user=admin_user
            )

            # Metadata should still be updated
            mock_service.remove_step_audio.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_reverts_to_tts(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id, mock_step_with_audio
    ):
        """After deleting audio, audio_source should revert to 'tts'."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('services.storage_service.get_storage_service') as mock_storage:

            mock_service.get_step = AsyncMock(return_value=mock_step_with_audio)

            # Track the call to remove_step_audio
            remove_call_args = []

            async def track_remove(*args, **kwargs):
                remove_call_args.append((args, kwargs))

            mock_service.remove_step_audio = AsyncMock(side_effect=track_remove)

            mock_storage_instance = AsyncMock()
            mock_storage_instance.delete_audio = AsyncMock()
            mock_storage.return_value = mock_storage_instance

            await delete_step_audio(
                scenario_id=sample_scenario_id,
                step_id=sample_step_id,
                language_code="en-US",
                db=mock_db,
                current_user=admin_user
            )

            # Verify remove_step_audio was called with correct params
            # This service method handles reverting audio_source to 'tts'
            mock_service.remove_step_audio.assert_called_once()
            call_kwargs = mock_service.remove_step_audio.call_args.kwargs
            assert call_kwargs.get('language_code') == 'en-US'
            assert call_kwargs.get('step_id') == sample_step_id


# =============================================================================
# TestErrorRecovery
# =============================================================================

class TestErrorRecovery:
    """Tests for error recovery with S3 rollback on partial failures."""

    @pytest.mark.asyncio
    async def test_db_failure_triggers_s3_rollback(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_mp3_file, mock_scenario, mock_step, mock_transcription_result
    ):
        """When DB update fails, S3 file should be deleted (rollback)."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('services.audio_utils.validate_audio_format', return_value=True), \
             patch('services.audio_utils.get_audio_duration', return_value=2.5), \
             patch('services.stt_service.get_stt_service') as mock_stt, \
             patch('services.storage_service.get_storage_service') as mock_storage:

            # Setup mocks
            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step)
            # DB update fails
            mock_service.update_step_audio = AsyncMock(
                side_effect=Exception("Database connection lost")
            )

            mock_stt_instance = MagicMock()
            mock_stt_instance.transcribe.return_value = mock_transcription_result
            mock_stt.return_value = mock_stt_instance

            mock_storage_instance = AsyncMock()
            mock_storage_instance.upload_audio = AsyncMock()  # S3 upload succeeds
            mock_storage_instance.delete_by_key = AsyncMock(return_value=True)  # Rollback succeeds
            mock_storage.return_value = mock_storage_instance

            # Execute - should raise HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await upload_step_audio(
                    scenario_id=sample_scenario_id,
                    step_id=sample_step_id,
                    file=mock_mp3_file,
                    language_code="en-US",
                    db=mock_db,
                    current_user=admin_user
                )

            # Verify error response
            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "rolled back" in str(exc_info.value.detail).lower()

            # Verify S3 rollback was triggered
            mock_storage_instance.upload_audio.assert_called_once()
            mock_storage_instance.delete_by_key.assert_called_once()

    @pytest.mark.asyncio
    async def test_db_failure_rollback_deletes_correct_key(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_mp3_file, mock_scenario, mock_step, mock_transcription_result
    ):
        """Verify rollback deletes the exact S3 key that was uploaded."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('services.audio_utils.validate_audio_format', return_value=True), \
             patch('services.audio_utils.get_audio_duration', return_value=2.5), \
             patch('services.stt_service.get_stt_service') as mock_stt, \
             patch('services.storage_service.get_storage_service') as mock_storage:

            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step)
            mock_service.update_step_audio = AsyncMock(
                side_effect=Exception("DB error")
            )

            mock_stt_instance = MagicMock()
            mock_stt_instance.transcribe.return_value = mock_transcription_result
            mock_stt.return_value = mock_stt_instance

            mock_storage_instance = AsyncMock()
            mock_storage_instance.upload_audio = AsyncMock()
            mock_storage_instance.delete_by_key = AsyncMock(return_value=True)
            mock_storage.return_value = mock_storage_instance

            with pytest.raises(HTTPException):
                await upload_step_audio(
                    scenario_id=sample_scenario_id,
                    step_id=sample_step_id,
                    file=mock_mp3_file,
                    language_code="es-ES",  # Spanish
                    db=mock_db,
                    current_user=admin_user
                )

            # Verify the correct key was deleted
            delete_call = mock_storage_instance.delete_by_key.call_args
            deleted_key = delete_call.kwargs.get('key')
            assert str(sample_scenario_id) in deleted_key
            assert str(sample_step_id) in deleted_key
            assert "es-ES" in deleted_key
            assert ".mp3" in deleted_key

    @pytest.mark.asyncio
    async def test_db_failure_with_failed_rollback_still_raises(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_mp3_file, mock_scenario, mock_step, mock_transcription_result
    ):
        """When both DB and S3 rollback fail, user still gets error message."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('services.audio_utils.validate_audio_format', return_value=True), \
             patch('services.audio_utils.get_audio_duration', return_value=2.5), \
             patch('services.stt_service.get_stt_service') as mock_stt, \
             patch('services.storage_service.get_storage_service') as mock_storage:

            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step)
            mock_service.update_step_audio = AsyncMock(
                side_effect=Exception("DB error")
            )

            mock_stt_instance = MagicMock()
            mock_stt_instance.transcribe.return_value = mock_transcription_result
            mock_stt.return_value = mock_stt_instance

            mock_storage_instance = AsyncMock()
            mock_storage_instance.upload_audio = AsyncMock()
            # Rollback fails
            mock_storage_instance.delete_by_key = AsyncMock(return_value=False)
            mock_storage.return_value = mock_storage_instance

            with pytest.raises(HTTPException) as exc_info:
                await upload_step_audio(
                    scenario_id=sample_scenario_id,
                    step_id=sample_step_id,
                    file=mock_mp3_file,
                    language_code="en-US",
                    db=mock_db,
                    current_user=admin_user
                )

            # Should still return user-friendly error
            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "rolled back" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_s3_upload_failure_no_rollback_needed(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_mp3_file, mock_scenario, mock_step, mock_transcription_result
    ):
        """When S3 upload fails, no rollback is needed (nothing to clean up)."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('services.audio_utils.validate_audio_format', return_value=True), \
             patch('services.audio_utils.get_audio_duration', return_value=2.5), \
             patch('services.stt_service.get_stt_service') as mock_stt, \
             patch('services.storage_service.get_storage_service') as mock_storage:

            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step)

            mock_stt_instance = MagicMock()
            mock_stt_instance.transcribe.return_value = mock_transcription_result
            mock_stt.return_value = mock_stt_instance

            mock_storage_instance = AsyncMock()
            # S3 upload fails
            mock_storage_instance.upload_audio = AsyncMock(
                side_effect=Exception("S3 bucket not found")
            )
            mock_storage_instance.delete_by_key = AsyncMock()
            mock_storage.return_value = mock_storage_instance

            with pytest.raises(HTTPException) as exc_info:
                await upload_step_audio(
                    scenario_id=sample_scenario_id,
                    step_id=sample_step_id,
                    file=mock_mp3_file,
                    language_code="en-US",
                    db=mock_db,
                    current_user=admin_user
                )

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to store audio" in str(exc_info.value.detail)

            # No rollback should be attempted since S3 upload failed
            mock_storage_instance.delete_by_key.assert_not_called()

    @pytest.mark.asyncio
    async def test_transcription_failure_no_partial_state(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_mp3_file, mock_scenario, mock_step
    ):
        """When transcription fails, no S3 upload or DB update should occur."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('services.audio_utils.validate_audio_format', return_value=True), \
             patch('services.audio_utils.get_audio_duration', return_value=2.5), \
             patch('services.stt_service.get_stt_service') as mock_stt, \
             patch('services.storage_service.get_storage_service') as mock_storage:

            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step)

            mock_stt_instance = MagicMock()
            # Transcription fails
            mock_stt_instance.transcribe.side_effect = Exception("Whisper model error")
            mock_stt.return_value = mock_stt_instance

            mock_storage_instance = AsyncMock()
            mock_storage.return_value = mock_storage_instance

            with pytest.raises(HTTPException) as exc_info:
                await upload_step_audio(
                    scenario_id=sample_scenario_id,
                    step_id=sample_step_id,
                    file=mock_mp3_file,
                    language_code="en-US",
                    db=mock_db,
                    current_user=admin_user
                )

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Transcription failed" in str(exc_info.value.detail)

            # Neither S3 nor DB should be called
            mock_storage_instance.upload_audio.assert_not_called()
            mock_service.update_step_audio.assert_not_called()


# =============================================================================
# TestAudioNormalization
# =============================================================================

class TestAudioNormalization:
    """Tests for audio peak normalization feature."""

    @pytest.mark.asyncio
    async def test_upload_with_normalization_enabled(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_mp3_file, mock_scenario, mock_step, mock_transcription_result
    ):
        """Upload with normalization flag applies peak normalization."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('services.audio_utils.validate_audio_format', return_value=True), \
             patch('services.audio_utils.get_audio_duration', return_value=2.5), \
             patch('services.audio_utils.normalize_audio_peak') as mock_normalize, \
             patch('services.stt_service.get_stt_service') as mock_stt, \
             patch('services.storage_service.get_storage_service') as mock_storage:

            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step)
            mock_service.update_step_audio = AsyncMock()

            # Normalization returns processed audio
            mock_normalize.return_value = b'\x00' * 500

            mock_stt_instance = MagicMock()
            mock_stt_instance.transcribe.return_value = mock_transcription_result
            mock_stt.return_value = mock_stt_instance

            mock_storage_instance = AsyncMock()
            mock_storage_instance.upload_audio = AsyncMock()
            mock_storage.return_value = mock_storage_instance

            result = await upload_step_audio(
                scenario_id=sample_scenario_id,
                step_id=sample_step_id,
                file=mock_mp3_file,
                language_code="en-US",
                normalize=True,
                normalize_target_db=-3.0,
                db=mock_db,
                current_user=admin_user
            )

            # Verify normalization was applied
            assert result.normalization_applied is not None
            assert result.normalization_applied.type == "peak"
            assert result.normalization_applied.target_db == -3.0

    @pytest.mark.asyncio
    async def test_upload_without_normalization(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_mp3_file, mock_scenario, mock_step, mock_transcription_result
    ):
        """Upload without normalization flag does not apply normalization."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('services.audio_utils.validate_audio_format', return_value=True), \
             patch('services.audio_utils.get_audio_duration', return_value=2.5), \
             patch('services.stt_service.get_stt_service') as mock_stt, \
             patch('services.storage_service.get_storage_service') as mock_storage:

            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step)
            mock_service.update_step_audio = AsyncMock()

            mock_stt_instance = MagicMock()
            mock_stt_instance.transcribe.return_value = mock_transcription_result
            mock_stt.return_value = mock_stt_instance

            mock_storage_instance = AsyncMock()
            mock_storage_instance.upload_audio = AsyncMock()
            mock_storage.return_value = mock_storage_instance

            result = await upload_step_audio(
                scenario_id=sample_scenario_id,
                step_id=sample_step_id,
                file=mock_mp3_file,
                language_code="en-US",
                normalize=False,
                db=mock_db,
                current_user=admin_user
            )

            # Normalization should not be applied
            assert result.normalization_applied is None

    @pytest.mark.asyncio
    async def test_normalization_failure_uses_original_audio(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_mp3_file, mock_scenario, mock_step, mock_transcription_result
    ):
        """When normalization fails, original audio is used."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('services.audio_utils.validate_audio_format', return_value=True), \
             patch('services.audio_utils.get_audio_duration', return_value=2.5), \
             patch('services.audio_utils.normalize_audio_peak') as mock_normalize, \
             patch('services.stt_service.get_stt_service') as mock_stt, \
             patch('services.storage_service.get_storage_service') as mock_storage:

            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step)
            mock_service.update_step_audio = AsyncMock()

            # Normalization fails
            mock_normalize.side_effect = Exception("Normalization error")

            mock_stt_instance = MagicMock()
            mock_stt_instance.transcribe.return_value = mock_transcription_result
            mock_stt.return_value = mock_stt_instance

            mock_storage_instance = AsyncMock()
            mock_storage_instance.upload_audio = AsyncMock()
            mock_storage.return_value = mock_storage_instance

            # Should still succeed with original audio
            result = await upload_step_audio(
                scenario_id=sample_scenario_id,
                step_id=sample_step_id,
                file=mock_mp3_file,
                language_code="en-US",
                normalize=True,
                db=mock_db,
                current_user=admin_user
            )

            # Normalization not applied due to failure
            assert result.normalization_applied is None
            # But upload still succeeds
            assert result.transcription is not None


# =============================================================================
# TestBatchUpload
# =============================================================================

class TestBatchUpload:
    """Tests for batch audio upload endpoint."""

    @pytest.fixture
    def mock_batch_files(self):
        """Create mock batch upload files."""
        files = []
        for lang in ["en-US", "es-ES", "fr-FR"]:
            file = MagicMock(spec=UploadFile)
            file.filename = f"{lang}.mp3"
            file.content_type = "audio/mpeg"
            file.read = AsyncMock(return_value=b'\xff\xfb\x90\x00' + b'\x00' * 1000)
            files.append(file)
        return files

    @pytest.mark.asyncio
    async def test_batch_upload_all_success(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_batch_files, mock_scenario, mock_step, mock_transcription_result
    ):
        """Batch upload with all files succeeding."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('services.audio_utils.validate_audio_format', return_value=True), \
             patch('services.audio_utils.get_audio_duration', return_value=2.0), \
             patch('services.stt_service.get_stt_service') as mock_stt, \
             patch('services.storage_service.get_storage_service') as mock_storage:

            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step)
            mock_service.update_step_audio = AsyncMock()

            mock_stt_instance = MagicMock()
            mock_stt_instance.transcribe.return_value = mock_transcription_result
            mock_stt.return_value = mock_stt_instance

            mock_storage_instance = AsyncMock()
            mock_storage_instance.upload_audio = AsyncMock()
            mock_storage.return_value = mock_storage_instance

            result = await batch_upload_step_audio(
                scenario_id=sample_scenario_id,
                step_id=sample_step_id,
                files=mock_batch_files,
                normalize=False,
                db=mock_db,
                current_user=admin_user
            )

            assert result.total == 3
            assert result.successful == 3
            assert result.failed == 0
            assert len(result.results) == 3

            # Verify language codes extracted from filenames
            langs = [r.language_code for r in result.results]
            assert "en-US" in langs
            assert "es-ES" in langs
            assert "fr-FR" in langs

    @pytest.mark.asyncio
    async def test_batch_upload_partial_failure(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_scenario, mock_step, mock_transcription_result
    ):
        """Batch upload with some files failing."""
        # Create files with one invalid
        files = []
        for i, lang in enumerate(["en-US", "es-ES"]):
            file = MagicMock(spec=UploadFile)
            file.filename = f"{lang}.mp3"
            file.content_type = "audio/mpeg"
            file.read = AsyncMock(return_value=b'\xff\xfb\x90\x00' + b'\x00' * 1000)
            files.append(file)

        # Add invalid file
        invalid_file = MagicMock(spec=UploadFile)
        invalid_file.filename = "fr-FR.pdf"
        invalid_file.content_type = "application/pdf"  # Invalid type
        invalid_file.read = AsyncMock(return_value=b'%PDF-1.4')
        files.append(invalid_file)

        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('services.audio_utils.validate_audio_format', return_value=True), \
             patch('services.audio_utils.get_audio_duration', return_value=2.0), \
             patch('services.stt_service.get_stt_service') as mock_stt, \
             patch('services.storage_service.get_storage_service') as mock_storage:

            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step)
            mock_service.update_step_audio = AsyncMock()

            mock_stt_instance = MagicMock()
            mock_stt_instance.transcribe.return_value = mock_transcription_result
            mock_stt.return_value = mock_stt_instance

            mock_storage_instance = AsyncMock()
            mock_storage_instance.upload_audio = AsyncMock()
            mock_storage.return_value = mock_storage_instance

            result = await batch_upload_step_audio(
                scenario_id=sample_scenario_id,
                step_id=sample_step_id,
                files=files,
                normalize=False,
                db=mock_db,
                current_user=admin_user
            )

            assert result.total == 3
            assert result.successful == 2
            assert result.failed == 1

            # Find the failed result
            failed_results = [r for r in result.results if not r.success]
            assert len(failed_results) == 1
            assert failed_results[0].language_code == "fr-FR"
            assert failed_results[0].error is not None

    @pytest.mark.asyncio
    async def test_batch_upload_with_normalization(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_batch_files, mock_scenario, mock_step, mock_transcription_result
    ):
        """Batch upload with normalization enabled."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('services.audio_utils.validate_audio_format', return_value=True), \
             patch('services.audio_utils.get_audio_duration', return_value=2.0), \
             patch('services.audio_utils.normalize_audio_peak') as mock_normalize, \
             patch('services.stt_service.get_stt_service') as mock_stt, \
             patch('services.storage_service.get_storage_service') as mock_storage:

            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step)
            mock_service.update_step_audio = AsyncMock()

            mock_normalize.return_value = b'\x00' * 500

            mock_stt_instance = MagicMock()
            mock_stt_instance.transcribe.return_value = mock_transcription_result
            mock_stt.return_value = mock_stt_instance

            mock_storage_instance = AsyncMock()
            mock_storage_instance.upload_audio = AsyncMock()
            mock_storage.return_value = mock_storage_instance

            result = await batch_upload_step_audio(
                scenario_id=sample_scenario_id,
                step_id=sample_step_id,
                files=mock_batch_files,
                normalize=True,
                normalize_target_db=-3.0,
                db=mock_db,
                current_user=admin_user
            )

            # All results should have normalization applied
            for r in result.results:
                if r.success:
                    assert r.data.normalization_applied is not None
                    assert r.data.normalization_applied.target_db == -3.0

    @pytest.mark.asyncio
    async def test_batch_upload_scenario_not_found(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id, mock_batch_files
    ):
        """Batch upload returns 404 when scenario not found."""
        with patch('api.routes.scenarios.scenario_service') as mock_service:
            mock_service.get = AsyncMock(return_value=None)

            with pytest.raises(HTTPException) as exc_info:
                await batch_upload_step_audio(
                    scenario_id=sample_scenario_id,
                    step_id=sample_step_id,
                    files=mock_batch_files,
                    db=mock_db,
                    current_user=admin_user
                )

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_batch_upload_permission_denied(
        self, mock_db, viewer_user, sample_scenario_id, sample_step_id, mock_batch_files
    ):
        """Viewer cannot batch upload audio."""
        with pytest.raises(HTTPException) as exc_info:
            await batch_upload_step_audio(
                scenario_id=sample_scenario_id,
                step_id=sample_step_id,
                files=mock_batch_files,
                db=mock_db,
                current_user=viewer_user
            )

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    @pytest.fixture
    def mock_batch_files(self):
        """Create mock batch upload files."""
        files = []
        for lang in ["en-US", "es-ES", "fr-FR"]:
            file = MagicMock(spec=UploadFile)
            file.filename = f"{lang}.mp3"
            file.content_type = "audio/mpeg"
            file.read = AsyncMock(return_value=b'\xff\xfb\x90\x00' + b'\x00' * 1000)
            files.append(file)
        return files
