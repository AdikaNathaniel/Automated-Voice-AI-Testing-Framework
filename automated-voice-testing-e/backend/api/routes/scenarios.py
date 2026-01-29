"""
Scenario Script API routes.

Provides endpoints for scenario script management including creation, retrieval,
updates, deletion, and step management.

Endpoints:
    GET /api/v1/scenarios - List scenarios with filters and pagination
    POST /api/v1/scenarios - Create new scenario
    GET /api/v1/scenarios/{scenario_id} - Get scenario by ID
    PUT /api/v1/scenarios/{scenario_id} - Update scenario
    DELETE /api/v1/scenarios/{scenario_id} - Delete scenario
    POST /api/v1/scenarios/{scenario_id}/steps - Add step to scenario
    GET /api/v1/scenarios/{scenario_id}/steps - Get scenario steps
    POST /api/v1/scenarios/{scenario_id}/steps/{step_id}/audio - Upload audio
    GET /api/v1/scenarios/{scenario_id}/steps/{step_id}/audio/{language_code} - Get audio
    DELETE /api/v1/scenarios/{scenario_id}/steps/{step_id}/audio/{language_code} - Remove audio
    GET /api/v1/scenarios/noise-profiles - List available noise profiles

All endpoints require authentication via JWT token.
"""

import asyncio
import logging
from typing import Annotated, Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import Response
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.dependencies import get_current_user_with_db
from api.schemas.scenario import (
    ScenarioScriptCreate,
    ScenarioScriptUpdate,
    ScenarioScriptResponse,
    ScenarioStepCreate,
    ScenarioStepResponse,
    StepAudioUploadResponse,
    StepAudioInfoResponse,
    NoiseProfileInfo,
    NoiseConfigCreate,
    NoiseAppliedInfo,
    NormalizationAppliedInfo,
    BatchAudioUploadResponse,
    BatchAudioUploadResult,
)
from api.schemas.auth import UserResponse
from services.scenario_service import scenario_service
from api.auth.roles import Role

logger = logging.getLogger(__name__)


# Create router
router = APIRouter(prefix="/scenarios", tags=["Scenarios"])

# Security scheme for Bearer token
security = HTTPBearer()
_SCENARIO_MUTATION_ROLES = {Role.SUPER_ADMIN.value, Role.ORG_ADMIN.value, Role.QA_LEAD.value}
_EXPORT_ROLES = {Role.SUPER_ADMIN.value, Role.ORG_ADMIN.value, Role.QA_LEAD.value}


def _get_effective_tenant_id(user: UserResponse) -> UUID:
    """
    Get effective tenant_id for a user.

    Uses user.tenant_id if set (user belongs to an organization),
    otherwise uses user.id (user is their own tenant).

    This ensures tenant_id is NEVER None for data isolation.
    """
    return user.tenant_id if user.tenant_id else user.id


def _ensure_can_mutate_scenario(user: UserResponse) -> None:
    """
    Verify user has permission to mutate scenarios (create, update, delete, etc).

    Args:
        user: Current authenticated user

    Raises:
        HTTPException: 403 if user lacks required role
    """
    if user.role not in _SCENARIO_MUTATION_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or QA lead role required to modify scenarios.",
        )


def _ensure_owns_resource(user: UserResponse, resource, resource_name: str = "resource") -> None:
    """
    For qa_lead users, verify they own the resource (created_by matches user.id).
    Admins (super_admin, org_admin) can modify any resource.
    """
    if user.role in {Role.SUPER_ADMIN.value, Role.ORG_ADMIN.value}:
        return
    if hasattr(resource, "created_by") and resource.created_by and str(resource.created_by) != str(user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You can only modify your own {resource_name}.",
        )


# =============================================================================
# Helper Functions
# =============================================================================

# Use centralized get_current_user_with_db from api.dependencies


# =============================================================================
# Scenario Endpoints
# =============================================================================

@router.post(
    "/",
    response_model=ScenarioScriptResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create scenario",
    description="Create a new scenario script with optional steps"
)
async def create_scenario(
    data: ScenarioScriptCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> ScenarioScriptResponse:
    """
    Create a new scenario script.

    Args:
        data: Scenario creation data
        db: Database session
        current_user: Authenticated user

    Returns:
        Created scenario with ID and timestamps

    Raises:
        HTTPException: 403 if user lacks required role
    """
    _ensure_can_mutate_scenario(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    scenario = await scenario_service.create(
        db=db,
        data=data,
        user_id=current_user.id,
        tenant_id=tenant_id
    )

    return ScenarioScriptResponse.model_validate(scenario)


@router.get(
    "/",
    response_model=List[ScenarioScriptResponse],
    summary="List scenarios",
    description="List scenarios with optional filtering and pagination"
)
async def list_scenarios(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status")
) -> List[ScenarioScriptResponse]:
    """
    List scenarios with pagination and filtering.

    Args:
        db: Database session
        current_user: Authenticated user
        skip: Number of records to skip
        limit: Maximum records to return
        is_active: Optional filter by active status

    Returns:
        List of scenarios
    """
    tenant_id = _get_effective_tenant_id(current_user)
    scenarios = await scenario_service.list(
        db=db,
        tenant_id=tenant_id,
        skip=skip,
        limit=limit,
        is_active=is_active
    )

    return [ScenarioScriptResponse.model_validate(s) for s in scenarios]


@router.get(
    "/noise-profiles",
    response_model=List[NoiseProfileInfo],
    summary="List noise profiles",
    description="Get all available noise profiles for scenario configuration"
)
async def list_noise_profiles(
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> List[NoiseProfileInfo]:
    """
    List available noise profiles.

    Returns a list of all noise profiles that can be used for
    background noise simulation during scenario execution.

    Returns:
        List of noise profile information
    """
    try:
        from services.noise_profile_library_service import NoiseProfileLibraryService
        library = NoiseProfileLibraryService()
        profile_names = library.list_profiles()

        result = []
        for profile_key in profile_names:
            p = library.get_profile(profile_key)
            result.append(NoiseProfileInfo(
                name=profile_key,
                category=p.get("category", "general"),
                description=p.get("description"),
                default_snr_db=float(p.get("typical_snr", 15.0)),
                difficulty=p.get("asr_difficulty", "medium"),
                estimated_wer_increase=None
            ))
        return result
    except ImportError:
        logger.warning("NoiseProfileLibraryService not available")
        return []
    except Exception as e:
        logger.error(f"Failed to get noise profiles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve noise profiles"
        )


class TTSSynthesizeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Text to synthesize")
    language: str = Field(default="en", max_length=10, description="Language code (e.g. en, es, fr)")


@router.post(
    "/tts/synthesize",
    summary="Synthesize speech from text",
    description="Convert text to speech audio using TTS engine. Returns MP3 audio."
)
async def synthesize_speech(
    request: TTSSynthesizeRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> Response:
    """Synthesize text to speech audio."""
    try:
        from services.tts_service import TTSService
        tts = TTSService()
        audio_bytes = tts.text_to_speech(request.text, lang=request.language)
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=tts_output.mp3"}
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"TTS synthesis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Text-to-speech synthesis failed"
        )


@router.get(
    "/{scenario_id}",
    response_model=ScenarioScriptResponse,
    summary="Get scenario",
    description="Get a scenario by ID"
)
async def get_scenario(
    scenario_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> ScenarioScriptResponse:
    """
    Get a scenario by ID.

    Args:
        scenario_id: Scenario UUID
        db: Database session
        current_user: Authenticated user

    Returns:
        Scenario with steps

    Raises:
        HTTPException: 404 if scenario not found
    """
    tenant_id = _get_effective_tenant_id(current_user)
    scenario = await scenario_service.get(
        db=db,
        scenario_id=scenario_id,
        tenant_id=tenant_id
    )

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {scenario_id} not found"
        )

    return ScenarioScriptResponse.model_validate(scenario)


@router.put(
    "/{scenario_id}",
    response_model=ScenarioScriptResponse,
    summary="Update scenario",
    description="Update an existing scenario"
)
async def update_scenario(
    scenario_id: UUID,
    data: ScenarioScriptUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> ScenarioScriptResponse:
    """
    Update a scenario.

    Args:
        scenario_id: Scenario UUID
        data: Update data
        db: Database session
        current_user: Authenticated user

    Returns:
        Updated scenario

    Raises:
        HTTPException: 403 if user lacks required role
        HTTPException: 404 if scenario not found
    """
    _ensure_can_mutate_scenario(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    # Fetch scenario first to check ownership for qa_lead
    existing = await scenario_service.get(db=db, scenario_id=scenario_id, tenant_id=tenant_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {scenario_id} not found"
        )
    _ensure_owns_resource(current_user, existing, "scenario")

    scenario = await scenario_service.update(
        db=db,
        scenario_id=scenario_id,
        data=data,
        tenant_id=tenant_id
    )

    return ScenarioScriptResponse.model_validate(scenario)


@router.delete(
    "/{scenario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete scenario",
    description="Delete a scenario and its steps"
)
async def delete_scenario(
    scenario_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
):
    """
    Delete a scenario.

    Args:
        scenario_id: Scenario UUID
        db: Database session
        current_user: Authenticated user

    Raises:
        HTTPException: 403 if user lacks required role
        HTTPException: 404 if scenario not found
    """
    _ensure_can_mutate_scenario(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    # Fetch scenario first to check ownership for qa_lead
    existing = await scenario_service.get(db=db, scenario_id=scenario_id, tenant_id=tenant_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {scenario_id} not found"
        )
    _ensure_owns_resource(current_user, existing, "scenario")

    deleted = await scenario_service.delete(
        db=db,
        scenario_id=scenario_id,
        tenant_id=tenant_id
    )


# =============================================================================
# Scenario Steps Endpoints
# =============================================================================

@router.post(
    "/{scenario_id}/steps",
    response_model=ScenarioStepResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add step to scenario",
    description="Add a new step to an existing scenario"
)
async def add_scenario_step(
    scenario_id: UUID,
    data: ScenarioStepCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> ScenarioStepResponse:
    """
    Add a step to a scenario.

    Args:
        scenario_id: Scenario UUID
        data: Step creation data
        db: Database session
        current_user: Authenticated user

    Returns:
        Created step

    Raises:
        HTTPException: 403 if user lacks required role
        HTTPException: 404 if scenario not found
    """
    _ensure_can_mutate_scenario(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    step = await scenario_service.add_step(
        db=db,
        scenario_id=scenario_id,
        data=data,
        tenant_id=tenant_id
    )

    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {scenario_id} not found"
        )

    return ScenarioStepResponse.model_validate(step)


@router.get(
    "/{scenario_id}/steps",
    response_model=List[ScenarioStepResponse],
    summary="List scenario steps",
    description="Get all steps for a scenario"
)
async def list_scenario_steps(
    scenario_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> List[ScenarioStepResponse]:
    """
    Get all steps for a scenario.

    Args:
        scenario_id: Scenario UUID
        db: Database session
        current_user: Authenticated user

    Returns:
        List of steps ordered by step_order

    Raises:
        HTTPException: 404 if scenario not found
    """
    # Verify scenario exists
    tenant_id = _get_effective_tenant_id(current_user)
    scenario = await scenario_service.get(
        db=db,
        scenario_id=scenario_id,
        tenant_id=tenant_id
    )

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {scenario_id} not found"
        )

    steps = await scenario_service.get_steps(
        db=db,
        scenario_id=scenario_id,
        tenant_id=tenant_id
    )

    return [ScenarioStepResponse.model_validate(s) for s in steps]


# =============================================================================
# Export/Import Endpoints
# =============================================================================

@router.get(
    "/{scenario_id}/export/json",
    summary="Export scenario as JSON",
    description="Export scenario to JSON format for backup or transfer"
)
async def export_scenario_json(
    scenario_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
):
    """
    Export scenario as JSON.

    Args:
        scenario_id: Scenario UUID
        db: Database session
        current_user: Authenticated user

    Returns:
        JSON string representation of the scenario

    Raises:
        HTTPException: 403 if user lacks export permission
    """
    if current_user.role not in _EXPORT_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to export data.",
        )
    from fastapi.responses import Response

    tenant_id = _get_effective_tenant_id(current_user)
    scenario = await scenario_service.get(
        db=db,
        scenario_id=scenario_id,
        tenant_id=tenant_id
    )

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {scenario_id} not found"
        )

    json_content = scenario_service.export_to_json(scenario)

    return Response(
        content=json_content,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename={scenario.name}.json"
        }
    )


@router.get(
    "/{scenario_id}/export/yaml",
    summary="Export scenario as YAML",
    description="Export scenario to YAML format for backup or transfer"
)
async def export_scenario_yaml(
    scenario_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
):
    """
    Export scenario as YAML.

    Args:
        scenario_id: Scenario UUID
        db: Database session
        current_user: Authenticated user

    Returns:
        YAML string representation of the scenario

    Raises:
        HTTPException: 403 if user lacks export permission
    """
    if current_user.role not in _EXPORT_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to export data.",
        )
    from fastapi.responses import Response

    tenant_id = _get_effective_tenant_id(current_user)
    scenario = await scenario_service.get(
        db=db,
        scenario_id=scenario_id,
        tenant_id=tenant_id
    )

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {scenario_id} not found"
        )

    yaml_content = scenario_service.export_to_yaml(scenario)

    return Response(
        content=yaml_content,
        media_type="text/yaml",
        headers={
            "Content-Disposition": f"attachment; filename={scenario.name}.yaml"
        }
    )


@router.post(
    "/import/json",
    response_model=ScenarioScriptResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Import scenario from JSON",
    description="Import scenario from JSON format"
)
async def import_scenario_json(
    json_content: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> ScenarioScriptResponse:
    """
    Import scenario from JSON.

    Args:
        json_content: JSON string with scenario data
        db: Database session
        current_user: Authenticated user

    Returns:
        Created scenario

    Raises:
        HTTPException: 403 if user lacks required role
    """
    _ensure_can_mutate_scenario(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    try:
        scenario = await scenario_service.import_from_json(
            db=db,
            json_str=json_content,
            user_id=current_user.id,
            tenant_id=tenant_id
        )
        return ScenarioScriptResponse.model_validate(scenario)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON format: {str(e)}"
        )


@router.post(
    "/import/yaml",
    response_model=ScenarioScriptResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Import scenario from YAML",
    description="Import scenario from YAML format"
)
async def import_scenario_yaml(
    yaml_content: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> ScenarioScriptResponse:
    """
    Import scenario from YAML.

    Args:
        yaml_content: YAML string with scenario data
        db: Database session
        current_user: Authenticated user

    Returns:
        Created scenario

    Raises:
        HTTPException: 403 if user lacks required role
    """
    _ensure_can_mutate_scenario(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    try:
        scenario = await scenario_service.import_from_yaml(
            db=db,
            yaml_str=yaml_content,
            user_id=current_user.id,
            tenant_id=tenant_id
        )
        return ScenarioScriptResponse.model_validate(scenario)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid YAML format: {str(e)}"
        )


# =============================================================================
# Audio Upload Endpoints
# =============================================================================

# Supported audio formats
SUPPORTED_AUDIO_FORMATS = {"audio/mpeg", "audio/wav", "audio/ogg", "audio/flac", "audio/mp3"}
SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac"}


@router.post(
    "/{scenario_id}/steps/{step_id}/audio",
    response_model=StepAudioUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload audio for step",
    description="Upload audio file for a scenario step, transcribe with Whisper, optionally apply noise and normalization"
)
async def upload_step_audio(
    scenario_id: UUID,
    step_id: UUID,
    file: UploadFile = File(..., description="Audio file (MP3, WAV, OGG, FLAC)"),
    language_code: str = Query("en-US", description="Language code for the audio"),
    noise_profile: Optional[str] = Query(None, description="Noise profile to apply (e.g., 'car_cabin_highway')"),
    noise_snr_db: Optional[float] = Query(None, ge=-10, le=50, description="SNR in dB for noise injection"),
    normalize: bool = Query(False, description="Apply peak normalization to audio"),
    normalize_target_db: float = Query(-3.0, ge=-20, le=0, description="Target peak level in dB for normalization"),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)] = None,
) -> StepAudioUploadResponse:
    """
    Upload audio for a scenario step.

    Workflow:
    1. Validate audio format
    2. Transcribe with local Whisper (faster-whisper)
    3. Optionally apply peak normalization
    4. Optionally apply noise injection
    5. Store in S3/MinIO
    6. Update step metadata with audio info

    Args:
        scenario_id: Scenario UUID
        step_id: Step UUID
        file: Audio file upload
        language_code: Language code (e.g., "en-US", "es-ES")
        noise_profile: Optional noise profile to apply (e.g., "car_cabin_highway")
        noise_snr_db: Optional SNR in dB (-10 to 50), uses profile default if not set
        normalize: Whether to apply peak normalization (default: False)
        normalize_target_db: Target peak level in dB for normalization (default: -3.0)
        db: Database session
        current_user: Authenticated user

    Returns:
        Audio upload response with transcription, noise, and normalization info

    Raises:
        HTTPException: 400 if audio format invalid
        HTTPException: 403 if user lacks required role
        HTTPException: 404 if scenario/step not found
    """
    _ensure_can_mutate_scenario(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    # Validate content type
    if file.content_type not in SUPPORTED_AUDIO_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported audio format: {file.content_type}. "
                   f"Supported: MP3, WAV, OGG, FLAC"
        )

    # Validate file extension
    filename = file.filename or "audio.mp3"
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext and ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension: {ext}. "
                   f"Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    # Verify scenario and step exist
    scenario = await scenario_service.get(
        db=db, scenario_id=scenario_id, tenant_id=tenant_id
    )
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {scenario_id} not found"
        )

    step = await scenario_service.get_step(
        db=db, step_id=step_id, scenario_id=scenario_id, tenant_id=tenant_id
    )
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Step {step_id} not found in scenario {scenario_id}"
        )

    # Read audio data
    audio_bytes = await file.read()

    # Validate audio can be processed
    try:
        from services.audio_utils import validate_audio_format, get_audio_duration
        if not validate_audio_format(audio_bytes):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid audio data - could not decode"
            )
        duration_seconds = get_audio_duration(audio_bytes)
        duration_ms = int(duration_seconds * 1000)
    except Exception as e:
        logger.error(f"Audio validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to validate audio: {str(e)}"
        )

    # Transcribe with Whisper (run in thread pool for async compatibility)
    try:
        from services.stt_service import get_stt_service
        stt = get_stt_service()

        # Run transcription in executor (it's CPU-bound)
        loop = asyncio.get_event_loop()
        lang_short = language_code.split("-")[0]  # en-US -> en
        result = await loop.run_in_executor(
            None,
            lambda: stt.transcribe(audio_bytes, language=lang_short)
        )

        transcription = result.text
        stt_confidence = result.language_probability
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}"
        )

    # Determine format from content type or extension
    format_map = {
        "audio/mpeg": "mp3",
        "audio/mp3": "mp3",
        "audio/wav": "wav",
        "audio/ogg": "ogg",
        "audio/flac": "flac",
    }
    original_format = format_map.get(file.content_type, ext.lstrip(".") or "mp3")

    # Apply peak normalization if requested
    normalization_applied = None
    audio_to_process = audio_bytes
    if normalize:
        try:
            from services.audio_utils import normalize_audio_peak

            loop = asyncio.get_event_loop()
            audio_to_process = await loop.run_in_executor(
                None,
                lambda: normalize_audio_peak(audio_bytes, target_db=normalize_target_db)
            )

            normalization_applied = {
                "type": "peak",
                "target_db": normalize_target_db,
            }

            logger.info(f"Applied peak normalization with target {normalize_target_db} dB")
        except Exception as e:
            logger.warning(f"Peak normalization failed, using original audio: {e}")
            audio_to_process = audio_bytes

    # Apply noise injection if requested
    noise_applied = None
    audio_to_store = audio_to_process
    if noise_profile:
        try:
            from services.noise_profile_library_service import NoiseProfileLibraryService
            from services.audio_utils import audio_bytes_to_numpy, numpy_to_audio_bytes

            noise_library = NoiseProfileLibraryService()
            profile_info = noise_library.get_profile(noise_profile)

            if profile_info.get('category') == 'unknown':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unknown noise profile: {noise_profile}"
                )

            # Use provided SNR or profile's typical SNR
            snr_to_use = noise_snr_db if noise_snr_db is not None else profile_info.get('typical_snr', 20.0)

            # Convert audio bytes to numpy, apply noise, convert back
            loop = asyncio.get_event_loop()
            audio_numpy = await loop.run_in_executor(
                None,
                lambda: audio_bytes_to_numpy(audio_to_process)
            )

            noisy_audio = await loop.run_in_executor(
                None,
                lambda: noise_library.apply_noise(audio_numpy, noise_profile, snr_to_use)
            )

            audio_to_store = await loop.run_in_executor(
                None,
                lambda: numpy_to_audio_bytes(noisy_audio, original_format)
            )

            noise_applied = {
                "profile": noise_profile,
                "profile_name": profile_info.get('name', noise_profile),
                "snr_db": snr_to_use,
                "category": profile_info.get('category'),
            }

            logger.info(f"Applied noise profile '{noise_profile}' at {snr_to_use} dB SNR")
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Noise injection failed, storing original audio: {e}")
            # Continue without noise - store original audio

    # Generate S3 key
    s3_key = f"scenarios/{scenario_id}/steps/{step_id}/audio-{language_code}.{original_format}"

    # Get storage service (keep reference for potential rollback)
    from services.storage_service import get_storage_service
    storage = get_storage_service()

    # Upload to S3/MinIO
    try:
        await storage.upload_audio(
            key=s3_key,
            audio_data=audio_to_store,
            content_type=file.content_type or "audio/mpeg"
        )
        logger.info(
            f"S3 upload successful: scenario_id={scenario_id}, step_id={step_id}, "
            f"s3_key={s3_key}, size_bytes={len(audio_to_store)}"
        )
    except Exception as e:
        logger.error(
            f"S3 upload failed: scenario_id={scenario_id}, step_id={step_id}, "
            f"s3_key={s3_key}, error={str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store audio: {str(e)}"
        )

    # Update step metadata with S3 rollback on failure
    # This implements transaction-like behavior: if DB update fails, clean up S3
    uploaded_audio_info = {
        "s3_key": s3_key,
        "transcription": transcription,
        "duration_ms": duration_ms,
        "original_format": original_format,
        "stt_confidence": stt_confidence,
        "noise_applied": noise_applied,
        "normalization_applied": normalization_applied,
    }

    try:
        await scenario_service.update_step_audio(
            db=db,
            step_id=step_id,
            language_code=language_code,
            audio_info=uploaded_audio_info,
            tenant_id=tenant_id
        )
        logger.info(
            f"Database update successful: scenario_id={scenario_id}, step_id={step_id}, "
            f"language_code={language_code}"
        )
    except Exception as db_error:
        # Database update failed - rollback by deleting the uploaded S3 file
        logger.error(
            f"Database update failed, initiating S3 rollback: scenario_id={scenario_id}, "
            f"step_id={step_id}, s3_key={s3_key}, error={str(db_error)}"
        )

        # Attempt to delete the orphaned S3 file
        rollback_success = await storage.delete_by_key(key=s3_key)

        if rollback_success:
            logger.info(
                f"S3 rollback successful: scenario_id={scenario_id}, step_id={step_id}, "
                f"deleted_key={s3_key}"
            )
        else:
            # Log critical error - orphaned file exists in S3
            logger.critical(
                f"S3 ROLLBACK FAILED - ORPHANED FILE: scenario_id={scenario_id}, "
                f"step_id={step_id}, orphaned_key={s3_key}. "
                f"Manual cleanup may be required."
            )

        # Re-raise with user-friendly message
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save audio metadata. The upload was rolled back. Please try again."
        )

    # Build noise_applied response if noise was applied
    noise_applied_response = None
    if noise_applied:
        noise_applied_response = NoiseAppliedInfo(
            profile=noise_applied["profile"],
            profile_name=noise_applied["profile_name"],
            snr_db=noise_applied["snr_db"],
            category=noise_applied.get("category")
        )

    # Build normalization_applied response if normalization was applied
    normalization_applied_response = None
    if normalization_applied:
        normalization_applied_response = NormalizationAppliedInfo(
            type=normalization_applied["type"],
            target_db=normalization_applied["target_db"]
        )

    return StepAudioUploadResponse(
        s3_key=s3_key,
        transcription=transcription,
        duration_ms=duration_ms,
        original_format=original_format,
        stt_confidence=stt_confidence,
        language_code=language_code,
        noise_applied=noise_applied_response,
        normalization_applied=normalization_applied_response
    )


@router.post(
    "/{scenario_id}/steps/{step_id}/audio/batch",
    response_model=BatchAudioUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Batch upload audio for step",
    description="Upload multiple audio files for different language variants in a single request"
)
async def batch_upload_step_audio(
    scenario_id: UUID,
    step_id: UUID,
    files: List[UploadFile] = File(..., description="Audio files (each named with language code, e.g., 'en-US.mp3')"),
    normalize: bool = Query(False, description="Apply peak normalization to all audio files"),
    normalize_target_db: float = Query(-3.0, ge=-20, le=0, description="Target peak level in dB for normalization"),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)] = None,
) -> BatchAudioUploadResponse:
    """
    Batch upload multiple audio files for a scenario step.

    Each file should be named with the language code (e.g., 'en-US.mp3', 'es-ES.wav').
    The language code is extracted from the filename.

    Workflow for each file:
    1. Extract language code from filename
    2. Validate audio format
    3. Transcribe with local Whisper
    4. Optionally apply normalization
    5. Store in S3/MinIO
    6. Update step metadata

    Args:
        scenario_id: Scenario UUID
        step_id: Step UUID
        files: List of audio files to upload
        normalize: Whether to apply peak normalization to all files
        normalize_target_db: Target peak level in dB for normalization
        db: Database session
        current_user: Authenticated user

    Returns:
        Batch upload response with results for each file

    Raises:
        HTTPException: 403 if user lacks required role
        HTTPException: 404 if scenario/step not found
    """
    _ensure_can_mutate_scenario(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    # Verify scenario and step exist
    scenario = await scenario_service.get(
        db=db, scenario_id=scenario_id, tenant_id=tenant_id
    )
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {scenario_id} not found"
        )

    step = await scenario_service.get_step(
        db=db, step_id=step_id, scenario_id=scenario_id, tenant_id=tenant_id
    )
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Step {step_id} not found in scenario {scenario_id}"
        )

    results: List[BatchAudioUploadResult] = []
    successful = 0
    failed = 0

    for file in files:
        # Extract language code from filename (e.g., 'en-US.mp3' -> 'en-US')
        filename = file.filename or "unknown.mp3"
        name_without_ext = filename.rsplit(".", 1)[0] if "." in filename else filename
        language_code = name_without_ext

        try:
            # Validate content type
            if file.content_type not in SUPPORTED_AUDIO_FORMATS:
                raise ValueError(f"Unsupported format: {file.content_type}")

            # Read audio data
            audio_bytes = await file.read()

            # Validate audio
            from services.audio_utils import validate_audio_format, get_audio_duration, normalize_audio_peak
            if not validate_audio_format(audio_bytes):
                raise ValueError("Invalid audio data - could not decode")

            duration_seconds = get_audio_duration(audio_bytes)
            duration_ms = int(duration_seconds * 1000)

            # Apply normalization if requested
            normalization_applied = None
            audio_to_process = audio_bytes
            if normalize:
                try:
                    loop = asyncio.get_event_loop()
                    audio_to_process = await loop.run_in_executor(
                        None,
                        lambda ab=audio_bytes: normalize_audio_peak(ab, target_db=normalize_target_db)
                    )
                    normalization_applied = {
                        "type": "peak",
                        "target_db": normalize_target_db,
                    }
                except Exception as e:
                    logger.warning(f"Normalization failed for {filename}: {e}")
                    audio_to_process = audio_bytes

            # Transcribe with Whisper
            from services.stt_service import get_stt_service
            stt = get_stt_service()
            loop = asyncio.get_event_loop()
            lang_short = language_code.split("-")[0]
            result = await loop.run_in_executor(
                None,
                lambda: stt.transcribe(audio_to_process, language=lang_short)
            )
            transcription = result.text
            stt_confidence = result.language_probability

            # Determine format
            ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ".mp3"
            format_map = {
                "audio/mpeg": "mp3",
                "audio/mp3": "mp3",
                "audio/wav": "wav",
                "audio/ogg": "ogg",
                "audio/flac": "flac",
            }
            original_format = format_map.get(file.content_type, ext.lstrip(".") or "mp3")

            # Generate S3 key and upload
            s3_key = f"scenarios/{scenario_id}/steps/{step_id}/audio-{language_code}.{original_format}"

            from services.storage_service import get_storage_service
            storage = get_storage_service()
            await storage.upload_audio(
                key=s3_key,
                audio_data=audio_to_process,
                content_type=file.content_type or "audio/mpeg"
            )

            # Update step metadata
            uploaded_audio_info = {
                "s3_key": s3_key,
                "transcription": transcription,
                "duration_ms": duration_ms,
                "original_format": original_format,
                "stt_confidence": stt_confidence,
                "normalization_applied": normalization_applied,
            }

            await scenario_service.update_step_audio(
                db=db,
                step_id=step_id,
                language_code=language_code,
                audio_info=uploaded_audio_info,
                tenant_id=tenant_id
            )

            # Build response
            normalization_response = None
            if normalization_applied:
                normalization_response = NormalizationAppliedInfo(
                    type=normalization_applied["type"],
                    target_db=normalization_applied["target_db"]
                )

            results.append(BatchAudioUploadResult(
                language_code=language_code,
                success=True,
                data=StepAudioUploadResponse(
                    s3_key=s3_key,
                    transcription=transcription,
                    duration_ms=duration_ms,
                    original_format=original_format,
                    stt_confidence=stt_confidence,
                    language_code=language_code,
                    normalization_applied=normalization_response
                ),
                error=None
            ))
            successful += 1

        except Exception as e:
            logger.error(f"Batch upload failed for {filename}: {e}")
            results.append(BatchAudioUploadResult(
                language_code=language_code,
                success=False,
                data=None,
                error=str(e)
            ))
            failed += 1

    return BatchAudioUploadResponse(
        total=len(files),
        successful=successful,
        failed=failed,
        results=results
    )


@router.get(
    "/{scenario_id}/steps/{step_id}/audio/{language_code}",
    response_model=StepAudioInfoResponse,
    summary="Get step audio info",
    description="Get audio information and download URL for a step"
)
async def get_step_audio(
    scenario_id: UUID,
    step_id: UUID,
    language_code: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> StepAudioInfoResponse:
    """
    Get audio info for a scenario step.

    Args:
        scenario_id: Scenario UUID
        step_id: Step UUID
        language_code: Language code (e.g., "en-US")
        db: Database session
        current_user: Authenticated user

    Returns:
        Audio info with pre-signed download URL

    Raises:
        HTTPException: 404 if scenario/step/audio not found
    """
    tenant_id = _get_effective_tenant_id(current_user)

    # Get step
    step = await scenario_service.get_step(
        db=db, step_id=step_id, scenario_id=scenario_id, tenant_id=tenant_id
    )
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Step {step_id} not found"
        )

    # Check for uploaded audio in metadata
    metadata = step.step_metadata or {}
    uploaded_audio = metadata.get("uploaded_audio", {})
    audio_info = uploaded_audio.get(language_code)

    if not audio_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No audio found for language {language_code}"
        )

    # Generate pre-signed download URL
    download_url = None
    try:
        from services.storage_service import get_storage_service
        storage = get_storage_service()
        download_url = await storage.get_presigned_url(
            key=audio_info["s3_key"],
            expires_in=3600  # 1 hour
        )
    except Exception as e:
        logger.warning(f"Failed to generate download URL: {e}")

    return StepAudioInfoResponse(
        s3_key=audio_info["s3_key"],
        transcription=audio_info["transcription"],
        duration_ms=audio_info["duration_ms"],
        original_format=audio_info["original_format"],
        stt_confidence=audio_info["stt_confidence"],
        language_code=language_code,
        download_url=download_url
    )


@router.delete(
    "/{scenario_id}/steps/{step_id}/audio/{language_code}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete step audio",
    description="Remove uploaded audio for a step language"
)
async def delete_step_audio(
    scenario_id: UUID,
    step_id: UUID,
    language_code: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
):
    """
    Delete audio for a scenario step.

    Args:
        scenario_id: Scenario UUID
        step_id: Step UUID
        language_code: Language code (e.g., "en-US")
        db: Database session
        current_user: Authenticated user

    Raises:
        HTTPException: 403 if user lacks required role
        HTTPException: 404 if scenario/step/audio not found
    """
    _ensure_can_mutate_scenario(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    # qa_lead can only delete audio from their own scenarios
    scenario = await scenario_service.get(db=db, scenario_id=scenario_id, tenant_id=tenant_id)
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {scenario_id} not found"
        )
    _ensure_owns_resource(current_user, scenario, "audio file")

    # Get step
    step = await scenario_service.get_step(
        db=db, step_id=step_id, scenario_id=scenario_id, tenant_id=tenant_id
    )
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Step {step_id} not found"
        )

    # Check for uploaded audio
    metadata = step.step_metadata or {}
    uploaded_audio = metadata.get("uploaded_audio", {})
    audio_info = uploaded_audio.get(language_code)

    if not audio_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No audio found for language {language_code}"
        )

    # Delete from S3
    try:
        from services.storage_service import get_storage_service
        storage = get_storage_service()
        await storage.delete_audio(key=audio_info["s3_key"])
    except Exception as e:
        logger.warning(f"Failed to delete from S3: {e}")

    # Remove from step metadata
    await scenario_service.remove_step_audio(
        db=db,
        step_id=step_id,
        language_code=language_code,
        tenant_id=tenant_id
    )


@router.post(
    "/{scenario_id}/steps/{step_id}/audio/{language_code}/apply-noise",
    response_model=StepAudioUploadResponse,
    summary="Apply noise to existing audio",
    description="Apply a noise profile to already-uploaded audio for a step"
)
async def apply_noise_to_audio(
    scenario_id: UUID,
    step_id: UUID,
    language_code: str,
    noise_config: NoiseConfigCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
) -> StepAudioUploadResponse:
    """
    Apply noise to existing uploaded audio.

    Downloads the current audio from S3, applies the specified noise profile,
    and re-uploads the noisy audio. Updates step metadata with noise info.

    Args:
        scenario_id: Scenario UUID
        step_id: Step UUID
        language_code: Language code (e.g., "en-US")
        noise_config: Noise configuration to apply
        db: Database session
        current_user: Authenticated user

    Returns:
        Updated audio info with noise details

    Raises:
        HTTPException: 400 if noise profile invalid
        HTTPException: 403 if user lacks required role
        HTTPException: 404 if scenario/step/audio not found
    """
    _ensure_can_mutate_scenario(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    # Get step
    step = await scenario_service.get_step(
        db=db, step_id=step_id, scenario_id=scenario_id, tenant_id=tenant_id
    )
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Step {step_id} not found"
        )

    # Check for uploaded audio
    metadata = step.step_metadata or {}
    uploaded_audio = metadata.get("uploaded_audio", {})
    audio_info = uploaded_audio.get(language_code)

    if not audio_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No audio found for language {language_code}"
        )

    # Validate noise config
    if not noise_config.enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Noise config must have enabled=true to apply noise"
        )

    # Get noise profile
    try:
        from services.noise_profile_library_service import NoiseProfileLibraryService
        noise_library = NoiseProfileLibraryService()
        profile_info = noise_library.get_profile(noise_config.profile)

        if profile_info.get('category') == 'unknown':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown noise profile: {noise_config.profile}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get noise profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get noise profile: {str(e)}"
        )

    # Download existing audio from S3
    try:
        from services.storage_service import get_storage_service
        storage = get_storage_service()
        audio_bytes = await storage.download_audio(key=audio_info["s3_key"])
    except Exception as e:
        logger.error(f"Failed to download audio from S3: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download audio: {str(e)}"
        )

    # Determine SNR to use
    snr_to_use = noise_config.snr_db if noise_config.snr_db is not None else profile_info.get('typical_snr', 20.0)

    # Randomize SNR if requested
    if noise_config.randomize_snr:
        import random
        variance = noise_config.snr_variance
        snr_to_use = snr_to_use + random.uniform(-variance, variance)
        snr_to_use = max(-10.0, min(50.0, snr_to_use))  # Clamp to valid range

    # Apply noise
    try:
        from services.audio_utils import audio_bytes_to_numpy, numpy_to_audio_bytes

        loop = asyncio.get_event_loop()
        audio_numpy = await loop.run_in_executor(
            None,
            lambda: audio_bytes_to_numpy(audio_bytes)
        )

        noisy_audio = await loop.run_in_executor(
            None,
            lambda: noise_library.apply_noise(audio_numpy, noise_config.profile, snr_to_use)
        )

        original_format = audio_info.get("original_format", "wav")
        audio_to_store = await loop.run_in_executor(
            None,
            lambda: numpy_to_audio_bytes(noisy_audio, original_format)
        )

        logger.info(f"Applied noise profile '{noise_config.profile}' at {snr_to_use:.1f} dB SNR")
    except Exception as e:
        logger.error(f"Noise injection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply noise: {str(e)}"
        )

    # Re-upload to S3
    try:
        content_type_map = {
            "mp3": "audio/mpeg",
            "wav": "audio/wav",
            "ogg": "audio/ogg",
            "flac": "audio/flac",
        }
        content_type = content_type_map.get(original_format, "audio/mpeg")

        await storage.upload_audio(
            key=audio_info["s3_key"],
            audio_data=audio_to_store,
            content_type=content_type
        )
    except Exception as e:
        logger.error(f"S3 upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store noisy audio: {str(e)}"
        )

    # Update step metadata with noise info
    noise_applied = {
        "profile": noise_config.profile,
        "profile_name": profile_info.get('name', noise_config.profile),
        "snr_db": snr_to_use,
        "category": profile_info.get('category'),
    }

    updated_audio_info = {
        **audio_info,
        "noise_applied": noise_applied,
    }

    try:
        await scenario_service.update_step_audio(
            db=db,
            step_id=step_id,
            language_code=language_code,
            audio_info=updated_audio_info,
            tenant_id=tenant_id
        )
    except Exception as e:
        logger.error(f"Failed to update step metadata: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update step: {str(e)}"
        )

    return StepAudioUploadResponse(
        s3_key=audio_info["s3_key"],
        transcription=audio_info.get("transcription", ""),
        duration_ms=audio_info.get("duration_ms", 0),
        original_format=original_format,
        stt_confidence=audio_info.get("stt_confidence", 0.0),
        language_code=language_code,
        noise_applied=NoiseAppliedInfo(
            profile=noise_config.profile,
            profile_name=profile_info.get('name', noise_config.profile),
            snr_db=snr_to_use,
            category=profile_info.get('category')
        )
    )


# =============================================================================
# Noise Profile Endpoints
# =============================================================================

@router.post(
    "/{scenario_id}/steps/{step_id}/audio/{language_code}/preview-noise",
    summary="Preview audio with noise",
    description="Generate a preview of audio with noise applied (not saved)"
)
async def preview_noise_audio(
    scenario_id: UUID,
    step_id: UUID,
    language_code: str,
    noise_config: NoiseConfigCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)]
):
    """
    Preview audio with noise applied without saving.

    Downloads the current audio from S3, applies the specified noise profile,
    and returns the noisy audio as a base64-encoded string for playback.
    Does NOT save the result.

    Args:
        scenario_id: Scenario UUID
        step_id: Step UUID
        language_code: Language code (e.g., "en-US")
        noise_config: Noise configuration to preview
        db: Database session
        current_user: Authenticated user

    Returns:
        Base64-encoded audio data with content type

    Raises:
        HTTPException: 400 if noise profile invalid
        HTTPException: 404 if scenario/step/audio not found
    """
    import base64
    from fastapi.responses import JSONResponse

    tenant_id = _get_effective_tenant_id(current_user)

    # Get step
    step = await scenario_service.get_step(
        db=db, step_id=step_id, scenario_id=scenario_id, tenant_id=tenant_id
    )
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Step {step_id} not found"
        )

    # Check for uploaded audio
    metadata = step.step_metadata or {}
    uploaded_audio = metadata.get("uploaded_audio", {})
    audio_info = uploaded_audio.get(language_code)

    if not audio_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No audio found for language {language_code}"
        )

    # Validate noise config
    if not noise_config.enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Noise config must have enabled=true to preview noise"
        )

    # Get noise profile
    try:
        from services.noise_profile_library_service import NoiseProfileLibraryService
        noise_library = NoiseProfileLibraryService()
        profile_info = noise_library.get_profile(noise_config.profile)

        if profile_info.get('category') == 'unknown':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown noise profile: {noise_config.profile}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get noise profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get noise profile: {str(e)}"
        )

    # Download existing audio from S3
    try:
        from services.storage_service import get_storage_service
        storage = get_storage_service()
        audio_bytes = await storage.download_audio(key=audio_info["s3_key"])
    except Exception as e:
        logger.error(f"Failed to download audio from S3: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download audio: {str(e)}"
        )

    # Determine SNR to use
    snr_to_use = noise_config.snr_db if noise_config.snr_db is not None else profile_info.get('typical_snr', 20.0)

    # Randomize SNR if requested
    if noise_config.randomize_snr:
        import random
        variance = noise_config.snr_variance
        snr_to_use = snr_to_use + random.uniform(-variance, variance)
        snr_to_use = max(-10.0, min(50.0, snr_to_use))  # Clamp to valid range

    # Apply noise
    try:
        from services.audio_utils import audio_bytes_to_numpy, numpy_to_audio_bytes

        loop = asyncio.get_event_loop()
        audio_numpy = await loop.run_in_executor(
            None,
            lambda: audio_bytes_to_numpy(audio_bytes)
        )

        noisy_audio = await loop.run_in_executor(
            None,
            lambda: noise_library.apply_noise(audio_numpy, noise_config.profile, snr_to_use)
        )

        original_format = audio_info.get("original_format", "wav")
        noisy_audio_bytes = await loop.run_in_executor(
            None,
            lambda: numpy_to_audio_bytes(noisy_audio, original_format)
        )

        logger.info(f"Generated noise preview with profile '{noise_config.profile}' at {snr_to_use:.1f} dB SNR")
    except Exception as e:
        logger.error(f"Noise preview generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate noise preview: {str(e)}"
        )

    # Encode audio as base64
    content_type_map = {
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "ogg": "audio/ogg",
        "flac": "audio/flac",
    }
    content_type = content_type_map.get(original_format, "audio/wav")
    audio_base64 = base64.b64encode(noisy_audio_bytes).decode('utf-8')

    return JSONResponse(content={
        "success": True,
        "data": {
            "audio_base64": audio_base64,
            "content_type": content_type,
            "format": original_format,
            "snr_db": snr_to_use,
            "profile": noise_config.profile,
            "profile_name": profile_info.get('name', noise_config.profile),
        }
    })


