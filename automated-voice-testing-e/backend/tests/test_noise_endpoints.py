"""
Unit tests for noise injection API endpoints.

Tests the apply-noise, preview-noise, and list-noise-profiles endpoints.
Covers noise profile validation, SNR configuration, randomization, and error handling.
Uses mocked services to test route logic without external dependencies.
"""

import pytest
import base64
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from api.routes.scenarios import (
    apply_noise_to_audio,
    preview_noise_audio,
    list_noise_profiles,
)
from api.schemas.scenario import NoiseConfigCreate
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
def mock_scenario():
    """Create mock scenario object."""
    scenario = MagicMock()
    scenario.id = uuid4()
    scenario.name = "Test Scenario"
    scenario.tenant_id = uuid4()
    return scenario


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
def mock_step_without_audio():
    """Create mock step object without audio."""
    step = MagicMock()
    step.id = uuid4()
    step.scenario_id = uuid4()
    step.step_metadata = {}
    return step


@pytest.fixture
def valid_noise_config():
    """Create valid noise configuration for apply/preview."""
    return NoiseConfigCreate(
        enabled=True,
        profile="car_cabin_highway",
        snr_db=15.0,
        randomize_snr=False,
        snr_variance=3.0
    )


@pytest.fixture
def noise_config_with_randomization():
    """Create noise configuration with SNR randomization enabled."""
    return NoiseConfigCreate(
        enabled=True,
        profile="office_hvac",
        snr_db=20.0,
        randomize_snr=True,
        snr_variance=5.0
    )


@pytest.fixture
def disabled_noise_config():
    """Create disabled noise configuration."""
    return NoiseConfigCreate(
        enabled=False,
        profile="car_cabin_highway",
        snr_db=15.0,
        randomize_snr=False
    )


@pytest.fixture
def mock_noise_profile_info():
    """Mock noise profile information from library service."""
    return {
        "name": "car_cabin_highway",
        "category": "vehicle",
        "description": "Interior of a car driving on highway",
        "typical_snr": 15.0,
        "difficulty": "medium",
        "estimated_wer_increase": 12.0
    }


@pytest.fixture
def mock_audio_bytes():
    """Create mock audio bytes for testing."""
    # Minimal WAV header + some data
    return b'RIFF' + b'\x00' * 44 + b'\x00' * 1000


@pytest.fixture
def mock_noisy_audio_bytes():
    """Create mock noisy audio bytes."""
    return b'RIFF' + b'\x00' * 44 + b'\xFF' * 1000


# =============================================================================
# Apply Noise Endpoint Tests
# =============================================================================

class TestApplyNoiseToAudio:
    """Tests for the apply-noise endpoint."""

    @pytest.mark.asyncio
    async def test_apply_noise_success(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_scenario, mock_step_with_audio, valid_noise_config,
        mock_noise_profile_info, mock_audio_bytes, mock_noisy_audio_bytes
    ):
        """Successfully apply noise to existing audio."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('api.routes.scenarios.NoiseProfileLibraryService') as mock_noise_lib, \
             patch('services.storage_service.get_storage_service') as mock_storage, \
             patch('services.audio_utils.audio_bytes_to_numpy') as mock_to_numpy, \
             patch('services.audio_utils.numpy_to_audio_bytes') as mock_to_bytes:

            # Setup mocks
            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step_with_audio)
            mock_service.update_step_audio = AsyncMock(return_value=mock_step_with_audio)

            noise_lib_instance = MagicMock()
            noise_lib_instance.get_profile.return_value = mock_noise_profile_info
            noise_lib_instance.apply_noise.return_value = [0.1, 0.2, 0.3]  # numpy array
            mock_noise_lib.return_value = noise_lib_instance

            storage_instance = AsyncMock()
            storage_instance.download_audio = AsyncMock(return_value=mock_audio_bytes)
            storage_instance.upload_audio = AsyncMock(return_value="scenarios/test/audio.mp3")
            mock_storage.return_value = storage_instance

            mock_to_numpy.return_value = [0.1, 0.2, 0.3]
            mock_to_bytes.return_value = mock_noisy_audio_bytes

            # Execute
            result = await apply_noise_to_audio(
                scenario_id=sample_scenario_id,
                step_id=sample_step_id,
                language_code="en-US",
                noise_config=valid_noise_config,
                db=mock_db,
                current_user=admin_user
            )

            # Verify
            assert result is not None
            assert result.noise_applied is not None
            assert result.noise_applied.profile == "car_cabin_highway"
            noise_lib_instance.apply_noise.assert_called_once()
            storage_instance.upload_audio.assert_called_once()

    @pytest.mark.asyncio
    async def test_apply_noise_invalid_profile_rejected(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_scenario, mock_step_with_audio, valid_noise_config
    ):
        """Reject noise application with invalid profile."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('api.routes.scenarios.NoiseProfileLibraryService') as mock_noise_lib:

            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step_with_audio)

            noise_lib_instance = MagicMock()
            noise_lib_instance.get_profile.return_value = {"category": "unknown"}
            mock_noise_lib.return_value = noise_lib_instance

            with pytest.raises(HTTPException) as exc_info:
                await apply_noise_to_audio(
                    scenario_id=sample_scenario_id,
                    step_id=sample_step_id,
                    language_code="en-US",
                    noise_config=valid_noise_config,
                    db=mock_db,
                    current_user=admin_user
                )

            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "Unknown noise profile" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_apply_noise_disabled_config_rejected(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_scenario, mock_step_with_audio, disabled_noise_config
    ):
        """Reject noise application when config has enabled=false."""
        with patch('api.routes.scenarios.scenario_service') as mock_service:

            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step_with_audio)

            with pytest.raises(HTTPException) as exc_info:
                await apply_noise_to_audio(
                    scenario_id=sample_scenario_id,
                    step_id=sample_step_id,
                    language_code="en-US",
                    noise_config=disabled_noise_config,
                    db=mock_db,
                    current_user=admin_user
                )

            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "enabled=true" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_apply_noise_audio_not_found(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_scenario, mock_step_without_audio, valid_noise_config
    ):
        """Return 404 when step has no audio to apply noise to."""
        with patch('api.routes.scenarios.scenario_service') as mock_service:

            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step_without_audio)

            with pytest.raises(HTTPException) as exc_info:
                await apply_noise_to_audio(
                    scenario_id=sample_scenario_id,
                    step_id=sample_step_id,
                    language_code="en-US",
                    noise_config=valid_noise_config,
                    db=mock_db,
                    current_user=admin_user
                )

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_apply_noise_with_snr_randomization(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_scenario, mock_step_with_audio, noise_config_with_randomization,
        mock_noise_profile_info, mock_audio_bytes, mock_noisy_audio_bytes
    ):
        """SNR randomization applies variance within bounds."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('api.routes.scenarios.NoiseProfileLibraryService') as mock_noise_lib, \
             patch('services.storage_service.get_storage_service') as mock_storage, \
             patch('services.audio_utils.audio_bytes_to_numpy') as mock_to_numpy, \
             patch('services.audio_utils.numpy_to_audio_bytes') as mock_to_bytes, \
             patch('api.routes.scenarios.random.uniform') as mock_random:

            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step_with_audio)
            mock_service.update_step_audio = AsyncMock(return_value=mock_step_with_audio)

            noise_lib_instance = MagicMock()
            noise_lib_instance.get_profile.return_value = mock_noise_profile_info
            noise_lib_instance.apply_noise.return_value = [0.1, 0.2, 0.3]
            mock_noise_lib.return_value = noise_lib_instance

            storage_instance = AsyncMock()
            storage_instance.download_audio = AsyncMock(return_value=mock_audio_bytes)
            storage_instance.upload_audio = AsyncMock(return_value="scenarios/test/audio.mp3")
            mock_storage.return_value = storage_instance

            mock_to_numpy.return_value = [0.1, 0.2, 0.3]
            mock_to_bytes.return_value = mock_noisy_audio_bytes

            # Mock random to return specific variance
            mock_random.return_value = 3.0  # +3 dB

            result = await apply_noise_to_audio(
                scenario_id=sample_scenario_id,
                step_id=sample_step_id,
                language_code="en-US",
                noise_config=noise_config_with_randomization,
                db=mock_db,
                current_user=admin_user
            )

            # Verify randomization was applied
            mock_random.assert_called_once()
            assert result.noise_applied.snr_db == pytest.approx(23.0, abs=0.1)

    @pytest.mark.asyncio
    async def test_apply_noise_snr_clamped_to_valid_range(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_scenario, mock_step_with_audio, mock_noise_profile_info,
        mock_audio_bytes, mock_noisy_audio_bytes
    ):
        """SNR is clamped to valid range (-10 to 50 dB)."""
        # Create config with high SNR that would exceed bounds with randomization
        extreme_config = NoiseConfigCreate(
            enabled=True,
            profile="car_cabin_highway",
            snr_db=48.0,
            randomize_snr=True,
            snr_variance=10.0  # Could push to 58 dB
        )

        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('api.routes.scenarios.NoiseProfileLibraryService') as mock_noise_lib, \
             patch('services.storage_service.get_storage_service') as mock_storage, \
             patch('services.audio_utils.audio_bytes_to_numpy') as mock_to_numpy, \
             patch('services.audio_utils.numpy_to_audio_bytes') as mock_to_bytes, \
             patch('api.routes.scenarios.random.uniform') as mock_random:

            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step_with_audio)
            mock_service.update_step_audio = AsyncMock(return_value=mock_step_with_audio)

            noise_lib_instance = MagicMock()
            noise_lib_instance.get_profile.return_value = mock_noise_profile_info
            noise_lib_instance.apply_noise.return_value = [0.1, 0.2, 0.3]
            mock_noise_lib.return_value = noise_lib_instance

            storage_instance = AsyncMock()
            storage_instance.download_audio = AsyncMock(return_value=mock_audio_bytes)
            storage_instance.upload_audio = AsyncMock(return_value="scenarios/test/audio.mp3")
            mock_storage.return_value = storage_instance

            mock_to_numpy.return_value = [0.1, 0.2, 0.3]
            mock_to_bytes.return_value = mock_noisy_audio_bytes
            mock_random.return_value = 10.0  # Would give 58 dB, should clamp to 50

            result = await apply_noise_to_audio(
                scenario_id=sample_scenario_id,
                step_id=sample_step_id,
                language_code="en-US",
                noise_config=extreme_config,
                db=mock_db,
                current_user=admin_user
            )

            # SNR should be clamped to max 50 dB
            assert result.noise_applied.snr_db <= 50.0

    @pytest.mark.asyncio
    async def test_apply_noise_uses_profile_default_snr(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_scenario, mock_step_with_audio, mock_noise_profile_info,
        mock_audio_bytes, mock_noisy_audio_bytes
    ):
        """When no SNR specified, use profile's typical SNR."""
        config_without_snr = NoiseConfigCreate(
            enabled=True,
            profile="car_cabin_highway",
            snr_db=None,  # No SNR specified
            randomize_snr=False
        )

        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('api.routes.scenarios.NoiseProfileLibraryService') as mock_noise_lib, \
             patch('services.storage_service.get_storage_service') as mock_storage, \
             patch('services.audio_utils.audio_bytes_to_numpy') as mock_to_numpy, \
             patch('services.audio_utils.numpy_to_audio_bytes') as mock_to_bytes:

            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step_with_audio)
            mock_service.update_step_audio = AsyncMock(return_value=mock_step_with_audio)

            noise_lib_instance = MagicMock()
            noise_lib_instance.get_profile.return_value = mock_noise_profile_info
            noise_lib_instance.apply_noise.return_value = [0.1, 0.2, 0.3]
            mock_noise_lib.return_value = noise_lib_instance

            storage_instance = AsyncMock()
            storage_instance.download_audio = AsyncMock(return_value=mock_audio_bytes)
            storage_instance.upload_audio = AsyncMock(return_value="scenarios/test/audio.mp3")
            mock_storage.return_value = storage_instance

            mock_to_numpy.return_value = [0.1, 0.2, 0.3]
            mock_to_bytes.return_value = mock_noisy_audio_bytes

            result = await apply_noise_to_audio(
                scenario_id=sample_scenario_id,
                step_id=sample_step_id,
                language_code="en-US",
                noise_config=config_without_snr,
                db=mock_db,
                current_user=admin_user
            )

            # Should use profile's typical_snr (15.0)
            assert result.noise_applied.snr_db == pytest.approx(15.0)


# =============================================================================
# Preview Noise Endpoint Tests
# =============================================================================

class TestPreviewNoiseAudio:
    """Tests for the preview-noise endpoint."""

    @pytest.mark.asyncio
    async def test_preview_noise_returns_base64(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_scenario, mock_step_with_audio, valid_noise_config,
        mock_noise_profile_info, mock_audio_bytes, mock_noisy_audio_bytes
    ):
        """Preview returns base64-encoded audio without saving."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('api.routes.scenarios.NoiseProfileLibraryService') as mock_noise_lib, \
             patch('services.storage_service.get_storage_service') as mock_storage, \
             patch('services.audio_utils.audio_bytes_to_numpy') as mock_to_numpy, \
             patch('services.audio_utils.numpy_to_audio_bytes') as mock_to_bytes:

            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step_with_audio)

            noise_lib_instance = MagicMock()
            noise_lib_instance.get_profile.return_value = mock_noise_profile_info
            noise_lib_instance.apply_noise.return_value = [0.1, 0.2, 0.3]
            mock_noise_lib.return_value = noise_lib_instance

            storage_instance = AsyncMock()
            storage_instance.download_audio = AsyncMock(return_value=mock_audio_bytes)
            mock_storage.return_value = storage_instance

            mock_to_numpy.return_value = [0.1, 0.2, 0.3]
            mock_to_bytes.return_value = mock_noisy_audio_bytes

            result = await preview_noise_audio(
                scenario_id=sample_scenario_id,
                step_id=sample_step_id,
                language_code="en-US",
                noise_config=valid_noise_config,
                db=mock_db,
                current_user=admin_user
            )

            # Verify base64 data is returned
            assert result is not None
            assert "data" in result
            preview_data = result["data"]
            assert "audio_base64" in preview_data
            assert "content_type" in preview_data

            # Verify it's valid base64
            decoded = base64.b64decode(preview_data["audio_base64"])
            assert decoded == mock_noisy_audio_bytes

            # Verify NO save occurred
            storage_instance.upload_audio.assert_not_called()
            mock_service.update_step_audio.assert_not_called()

    @pytest.mark.asyncio
    async def test_preview_noise_invalid_profile_rejected(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_scenario, mock_step_with_audio, valid_noise_config
    ):
        """Preview rejects invalid noise profile."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('api.routes.scenarios.NoiseProfileLibraryService') as mock_noise_lib:

            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step_with_audio)

            noise_lib_instance = MagicMock()
            noise_lib_instance.get_profile.return_value = {"category": "unknown"}
            mock_noise_lib.return_value = noise_lib_instance

            with pytest.raises(HTTPException) as exc_info:
                await preview_noise_audio(
                    scenario_id=sample_scenario_id,
                    step_id=sample_step_id,
                    language_code="en-US",
                    noise_config=valid_noise_config,
                    db=mock_db,
                    current_user=admin_user
                )

            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "Unknown noise profile" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_preview_noise_disabled_config_rejected(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_scenario, mock_step_with_audio, disabled_noise_config
    ):
        """Preview rejects disabled noise config."""
        with patch('api.routes.scenarios.scenario_service') as mock_service:

            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step_with_audio)

            with pytest.raises(HTTPException) as exc_info:
                await preview_noise_audio(
                    scenario_id=sample_scenario_id,
                    step_id=sample_step_id,
                    language_code="en-US",
                    noise_config=disabled_noise_config,
                    db=mock_db,
                    current_user=admin_user
                )

            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "enabled=true" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_preview_noise_includes_metadata(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_scenario, mock_step_with_audio, valid_noise_config,
        mock_noise_profile_info, mock_audio_bytes, mock_noisy_audio_bytes
    ):
        """Preview response includes noise metadata."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('api.routes.scenarios.NoiseProfileLibraryService') as mock_noise_lib, \
             patch('services.storage_service.get_storage_service') as mock_storage, \
             patch('services.audio_utils.audio_bytes_to_numpy') as mock_to_numpy, \
             patch('services.audio_utils.numpy_to_audio_bytes') as mock_to_bytes:

            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step_with_audio)

            noise_lib_instance = MagicMock()
            noise_lib_instance.get_profile.return_value = mock_noise_profile_info
            noise_lib_instance.apply_noise.return_value = [0.1, 0.2, 0.3]
            mock_noise_lib.return_value = noise_lib_instance

            storage_instance = AsyncMock()
            storage_instance.download_audio = AsyncMock(return_value=mock_audio_bytes)
            mock_storage.return_value = storage_instance

            mock_to_numpy.return_value = [0.1, 0.2, 0.3]
            mock_to_bytes.return_value = mock_noisy_audio_bytes

            result = await preview_noise_audio(
                scenario_id=sample_scenario_id,
                step_id=sample_step_id,
                language_code="en-US",
                noise_config=valid_noise_config,
                db=mock_db,
                current_user=admin_user
            )

            preview_data = result["data"]
            assert preview_data["snr_db"] == pytest.approx(15.0)
            assert preview_data["profile"] == "car_cabin_highway"
            assert preview_data["profile_name"] == "car_cabin_highway"


# =============================================================================
# List Noise Profiles Endpoint Tests
# =============================================================================

class TestListNoiseProfiles:
    """Tests for the list-noise-profiles endpoint."""

    @pytest.mark.asyncio
    async def test_list_noise_profiles_success(self, admin_user):
        """Successfully list all noise profiles."""
        mock_profiles = [
            {
                "name": "car_cabin_highway",
                "category": "vehicle",
                "description": "Car interior on highway",
                "typical_snr": 15.0,
                "difficulty": "medium",
                "estimated_wer_increase": 12.0
            },
            {
                "name": "office_hvac",
                "category": "environmental",
                "description": "Office with HVAC noise",
                "typical_snr": 25.0,
                "difficulty": "easy",
                "estimated_wer_increase": 5.0
            },
            {
                "name": "factory_machinery",
                "category": "industrial",
                "description": "Factory floor with machinery",
                "typical_snr": 5.0,
                "difficulty": "hard",
                "estimated_wer_increase": 25.0
            }
        ]

        with patch('api.routes.scenarios.NoiseProfileLibrary') as mock_library_class:
            mock_library = MagicMock()
            mock_library.get_all_profiles.return_value = mock_profiles
            mock_library_class.return_value = mock_library

            result = await list_noise_profiles(current_user=admin_user)

            assert len(result) == 3
            assert result[0].name == "car_cabin_highway"
            assert result[0].category == "vehicle"
            assert result[0].difficulty == "medium"
            assert result[1].name == "office_hvac"
            assert result[2].name == "factory_machinery"

    @pytest.mark.asyncio
    async def test_list_noise_profiles_empty_library(self, admin_user):
        """Return empty list when no profiles available."""
        with patch('api.routes.scenarios.NoiseProfileLibrary') as mock_library_class:
            mock_library = MagicMock()
            mock_library.get_all_profiles.return_value = []
            mock_library_class.return_value = mock_library

            result = await list_noise_profiles(current_user=admin_user)

            assert result == []

    @pytest.mark.asyncio
    async def test_list_noise_profiles_library_not_available(self, admin_user):
        """Return empty list when library module not available."""
        with patch('api.routes.scenarios.NoiseProfileLibrary', side_effect=ImportError):
            result = await list_noise_profiles(current_user=admin_user)

            assert result == []

    @pytest.mark.asyncio
    async def test_list_noise_profiles_includes_all_fields(self, admin_user):
        """Profile info includes all expected fields."""
        mock_profiles = [{
            "name": "car_cabin_highway",
            "category": "vehicle",
            "description": "Car interior on highway",
            "typical_snr": 15.0,
            "difficulty": "medium",
            "estimated_wer_increase": 12.0
        }]

        with patch('api.routes.scenarios.NoiseProfileLibrary') as mock_library_class:
            mock_library = MagicMock()
            mock_library.get_all_profiles.return_value = mock_profiles
            mock_library_class.return_value = mock_library

            result = await list_noise_profiles(current_user=admin_user)

            profile = result[0]
            assert profile.name == "car_cabin_highway"
            assert profile.category == "vehicle"
            assert profile.description == "Car interior on highway"
            assert profile.default_snr_db == pytest.approx(15.0)
            assert profile.difficulty == "medium"
            assert profile.estimated_wer_increase == pytest.approx(12.0)


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestNoiseEndpointErrorHandling:
    """Tests for error handling in noise endpoints."""

    @pytest.mark.asyncio
    async def test_apply_noise_s3_download_failure(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_scenario, mock_step_with_audio, valid_noise_config,
        mock_noise_profile_info
    ):
        """Handle S3 download failure gracefully."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('api.routes.scenarios.NoiseProfileLibraryService') as mock_noise_lib, \
             patch('services.storage_service.get_storage_service') as mock_storage:

            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step_with_audio)

            noise_lib_instance = MagicMock()
            noise_lib_instance.get_profile.return_value = mock_noise_profile_info
            mock_noise_lib.return_value = noise_lib_instance

            storage_instance = AsyncMock()
            storage_instance.download_audio = AsyncMock(
                side_effect=Exception("S3 connection timeout")
            )
            mock_storage.return_value = storage_instance

            with pytest.raises(HTTPException) as exc_info:
                await apply_noise_to_audio(
                    scenario_id=sample_scenario_id,
                    step_id=sample_step_id,
                    language_code="en-US",
                    noise_config=valid_noise_config,
                    db=mock_db,
                    current_user=admin_user
                )

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "download" in str(exc_info.value.detail).lower() or "Failed" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_apply_noise_injection_failure(
        self, mock_db, admin_user, sample_scenario_id, sample_step_id,
        mock_scenario, mock_step_with_audio, valid_noise_config,
        mock_noise_profile_info, mock_audio_bytes
    ):
        """Handle noise injection processing failure."""
        with patch('api.routes.scenarios.scenario_service') as mock_service, \
             patch('api.routes.scenarios.NoiseProfileLibraryService') as mock_noise_lib, \
             patch('services.storage_service.get_storage_service') as mock_storage, \
             patch('services.audio_utils.audio_bytes_to_numpy') as mock_to_numpy:

            mock_service.get = AsyncMock(return_value=mock_scenario)
            mock_service.get_step = AsyncMock(return_value=mock_step_with_audio)

            noise_lib_instance = MagicMock()
            noise_lib_instance.get_profile.return_value = mock_noise_profile_info
            noise_lib_instance.apply_noise.side_effect = Exception("Audio processing error")
            mock_noise_lib.return_value = noise_lib_instance

            storage_instance = AsyncMock()
            storage_instance.download_audio = AsyncMock(return_value=mock_audio_bytes)
            mock_storage.return_value = storage_instance

            mock_to_numpy.return_value = [0.1, 0.2, 0.3]

            with pytest.raises(HTTPException) as exc_info:
                await apply_noise_to_audio(
                    scenario_id=sample_scenario_id,
                    step_id=sample_step_id,
                    language_code="en-US",
                    noise_config=valid_noise_config,
                    db=mock_db,
                    current_user=admin_user
                )

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "noise" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_list_profiles_service_error(self, admin_user):
        """Handle profile listing service error."""
        with patch('api.routes.scenarios.NoiseProfileLibrary') as mock_library_class:
            mock_library = MagicMock()
            mock_library.get_all_profiles.side_effect = Exception("Database error")
            mock_library_class.return_value = mock_library

            with pytest.raises(HTTPException) as exc_info:
                await list_noise_profiles(current_user=admin_user)

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "profiles" in str(exc_info.value.detail).lower()
