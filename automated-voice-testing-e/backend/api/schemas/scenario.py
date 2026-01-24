"""
Pydantic schemas for scenario script API operations.

This module defines the request/response schemas for scripted test scenarios:
- ScenarioStepCreate/Response: Individual scenario step schemas
- ScenarioScriptCreate/Response/Update: Full scenario script schemas
- ScenarioExport: Schema for JSON/YAML export format

Example:
    >>> from api.schemas.scenario import ScenarioScriptCreate, ScenarioStepCreate
    >>>
    >>> step = ScenarioStepCreate(
    ...     step_order=1,
    ...     user_utterance="Find a coffee shop"
    ... )
    >>>
    >>> script = ScenarioScriptCreate(
    ...     name="Navigation Test",
    ...     steps=[step]
    ... )
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, model_validator


class ScenarioStepCreate(BaseModel):
    """
    Schema for creating a scenario step.

    Attributes:
        step_order: Order of this step in the scenario sequence
        user_utterance: What the user says in this step
        step_metadata: Additional metadata including language_variants
        follow_up_action: Action to take after step execution

    Example:
        >>> step = ScenarioStepCreate(
        ...     step_order=1,
        ...     user_utterance="Navigate to work"
        ... )
    """

    step_order: int = Field(
        ...,
        description="Order of this step in the scenario sequence",
        ge=1
    )
    user_utterance: str = Field(
        ...,
        description="What the user says in this step",
        min_length=1
    )
    step_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata including language_variants"
    )
    follow_up_action: Optional[str] = Field(
        default=None,
        description="Action to take after step execution"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "step_order": 1,
                "user_utterance": "Find me a coffee shop",
                "step_metadata": {"primary_language": "en-US"}
            }
        }
    )


class ScenarioStepResponse(BaseModel):
    """
    Schema for scenario step response.

    Includes all step fields plus the unique identifier.

    Attributes:
        id: Unique step identifier
        step_order: Order of this step in the scenario sequence
        user_utterance: What the user says in this step
        step_metadata: Additional step metadata including language variants
        follow_up_action: Action to take after step execution
        created_at: When the step was created
        updated_at: When the step was last updated
    """

    id: UUID = Field(..., description="Unique step identifier")
    step_order: int = Field(..., description="Order in scenario sequence")
    user_utterance: str = Field(..., description="User input for this step")
    step_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata including language_variants"
    )
    follow_up_action: Optional[str] = Field(
        default=None,
        description="Action to take after step execution"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class ScenarioScriptCreate(BaseModel):
    """
    Schema for creating a scenario script.

    Attributes:
        name: Scenario script name (required)
        description: Detailed description of the scenario
        version: Version string (e.g., "1.0.0")
        steps: List of scenario steps to create with the script

    Example:
        >>> script = ScenarioScriptCreate(
        ...     name="Weather Query Scenario",
        ...     description="Test weather-related voice commands",
        ...     version="1.0.0",
        ...     steps=[
        ...         ScenarioStepCreate(
        ...             step_order=1,
        ...             user_utterance="What's the weather?"
        ...         )
        ...     ]
        ... )
    """

    name: str = Field(
        ...,
        description="Scenario script name",
        min_length=1,
        max_length=255
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of the scenario"
    )
    version: Optional[str] = Field(
        default=None,
        description="Version string (e.g., 1.0.0)",
        max_length=50
    )
    steps: Optional[List[ScenarioStepCreate]] = Field(
        default=None,
        description="List of scenario steps"
    )
    noise_config: Optional['NoiseConfigCreate'] = Field(
        default=None,
        description="Noise injection configuration for scenario execution"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Navigation Test Scenario",
                "description": "Test voice navigation commands",
                "version": "1.0.0",
                "steps": [
                    {
                        "step_order": 1,
                        "user_utterance": "Find a coffee shop"
                    }
                ],
                "noise_config": {
                    "enabled": False,
                    "profile": "car_cabin_city",
                    "snr_db": 15.0
                }
            }
        }
    )


class ScenarioScriptResponse(BaseModel):
    """
    Schema for scenario script response.

    Includes all script fields plus identifiers and timestamps.

    Attributes:
        id: Unique script identifier
        name: Scenario script name
        description: Detailed description
        version: Version string
        is_active: Whether the scenario is active
        tenant_id: Tenant identifier for multi-tenancy
        created_by: User who created the scenario
        steps: List of scenario steps
        languages: List of language codes from step metadata
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id: UUID = Field(..., description="Unique script identifier")
    name: str = Field(..., description="Scenario script name")
    description: Optional[str] = Field(
        default=None,
        description="Detailed description"
    )
    version: Optional[str] = Field(default=None, description="Version string")
    is_active: bool = Field(
        default=True,
        description="Whether the scenario is active"
    )
    tenant_id: Optional[UUID] = Field(
        default=None,
        description="Tenant identifier"
    )
    created_by: Optional[UUID] = Field(
        default=None,
        description="Creator user ID"
    )
    steps: Optional[List[ScenarioStepResponse]] = Field(
        default=None,
        description="Scenario steps"
    )
    languages: Optional[List[str]] = Field(
        default=None,
        description="Language codes available in this scenario"
    )
    script_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata including noise_config"
    )
    noise_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Noise injection configuration (extracted from script_metadata)"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='after')
    def extract_noise_config(self) -> 'ScenarioScriptResponse':
        """Extract noise_config from script_metadata if present."""
        if self.noise_config is None and self.script_metadata:
            noise = self.script_metadata.get('noise_config')
            if noise:
                object.__setattr__(self, 'noise_config', noise)
        return self

    @model_validator(mode='after')
    def extract_languages(self) -> 'ScenarioScriptResponse':
        """Extract unique languages from step metadata."""
        if self.languages is not None:
            return self
        if not self.steps:
            return self

        languages_set = set()
        for step in self.steps:
            if step.step_metadata:
                # Check for language_variants array
                variants = step.step_metadata.get('language_variants', [])
                for variant in variants:
                    if isinstance(variant, dict) and 'language_code' in variant:
                        languages_set.add(variant['language_code'])
                # Check for primary_language
                primary = step.step_metadata.get('primary_language')
                if primary:
                    languages_set.add(primary)

        if languages_set:
            self.languages = sorted(list(languages_set))
        return self


class ScenarioScriptUpdate(BaseModel):
    """
    Schema for updating a scenario script.

    All fields are optional to allow partial updates.

    Attributes:
        name: New scenario name
        description: New description
        version: New version string
        is_active: Update active status
        steps: Replace all steps with new list

    Example:
        >>> update = ScenarioScriptUpdate(
        ...     name="Updated Scenario Name",
        ...     version="1.1.0"
        ... )
    """

    name: Optional[str] = Field(
        default=None,
        description="Scenario script name",
        min_length=1,
        max_length=255
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed description"
    )
    version: Optional[str] = Field(
        default=None,
        description="Version string",
        max_length=50
    )
    is_active: Optional[bool] = Field(
        default=None,
        description="Whether the scenario is active"
    )
    steps: Optional[List[ScenarioStepCreate]] = Field(
        default=None,
        description="Replace all steps"
    )
    noise_config: Optional['NoiseConfigCreate'] = Field(
        default=None,
        description="Noise injection configuration for scenario execution"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated Scenario",
                "version": "1.1.0",
                "noise_config": {
                    "enabled": True,
                    "profile": "car_cabin_highway",
                    "snr_db": 10.0
                }
            }
        }
    )


class ScenarioExport(BaseModel):
    """
    Schema for exporting scenario to JSON/YAML format.

    Designed for portable scenario definitions that can be
    imported into other systems or version controlled.

    Attributes:
        name: Scenario name
        description: Scenario description
        version: Version string
        metadata: Additional metadata (language, domain, tags)
        steps: List of scenario steps for export

    Example:
        >>> export = ScenarioExport(
        ...     name="Weather Scenario",
        ...     version="1.0.0",
        ...     steps=[...]
        ... )
    """

    name: str = Field(..., description="Scenario name")
    description: Optional[str] = Field(
        default=None,
        description="Scenario description"
    )
    version: Optional[str] = Field(default=None, description="Version string")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata"
    )
    steps: List[Dict[str, Any]] = Field(
        ...,
        description="List of scenario steps"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Navigation Scenario",
                "version": "1.0.0",
                "metadata": {"language": "en-US", "domain": "navigation"},
                "steps": [
                    {
                        "step_order": 1,
                        "user_utterance": "Find a coffee shop"
                    }
                ]
            }
        }
    )


# =============================================================================
# Audio Upload Schemas
# =============================================================================


class NoiseAppliedInfo(BaseModel):
    """
    Information about noise that was applied to audio.

    Attributes:
        profile: Noise profile identifier
        profile_name: Human-readable profile name
        snr_db: SNR in decibels used for injection
        category: Noise category (vehicle, environmental, industrial)
    """

    profile: str = Field(..., description="Noise profile identifier")
    profile_name: str = Field(..., description="Human-readable profile name")
    snr_db: float = Field(..., description="SNR in decibels")
    category: Optional[str] = Field(default=None, description="Noise category")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "profile": "car_cabin_highway",
                "profile_name": "Car Cabin - Highway",
                "snr_db": 10.0,
                "category": "vehicle"
            }
        }
    )


class NormalizationAppliedInfo(BaseModel):
    """
    Information about audio normalization that was applied.

    Attributes:
        type: Type of normalization (peak)
        target_db: Target dB level used for normalization
    """

    type: str = Field(default="peak", description="Normalization type (peak)")
    target_db: float = Field(..., description="Target dB level used")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "peak",
                "target_db": -3.0
            }
        }
    )


class StepAudioUploadResponse(BaseModel):
    """
    Response schema for uploading audio to a scenario step.

    Returned after successfully uploading and transcribing audio.

    Attributes:
        s3_key: S3 storage key for the uploaded audio
        transcription: Text transcribed from the audio using Whisper
        duration_ms: Audio duration in milliseconds
        original_format: Original file format (mp3, wav, etc.)
        stt_confidence: Speech-to-text confidence score (0-1)
        language_code: Language code the audio was uploaded for
        noise_applied: Information about noise injection (if applied)
        normalization_applied: Information about audio normalization (if applied)
    """

    s3_key: str = Field(..., description="S3 storage key for the audio file")
    transcription: str = Field(..., description="Transcribed text from audio")
    duration_ms: int = Field(..., description="Audio duration in milliseconds")
    original_format: str = Field(..., description="Original audio file format")
    stt_confidence: float = Field(
        ...,
        description="Speech-to-text confidence score",
        ge=0.0,
        le=1.0
    )
    language_code: str = Field(..., description="Language code (e.g., en-US)")
    noise_applied: Optional[NoiseAppliedInfo] = Field(
        default=None,
        description="Information about noise injection (if applied)"
    )
    normalization_applied: Optional[NormalizationAppliedInfo] = Field(
        default=None,
        description="Information about audio normalization (if applied)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "s3_key": "scenarios/abc123/steps/1/audio-en-US.mp3",
                "transcription": "What's the weather like today?",
                "duration_ms": 2340,
                "original_format": "mp3",
                "stt_confidence": 0.95,
                "language_code": "en-US",
                "noise_applied": {
                    "profile": "car_cabin_highway",
                    "profile_name": "Car Cabin - Highway",
                    "snr_db": 10.0,
                    "category": "vehicle"
                },
                "normalization_applied": {
                    "type": "peak",
                    "target_db": -3.0
                }
            }
        }
    )


class StepAudioInfoResponse(BaseModel):
    """
    Response schema for getting audio info for a scenario step.

    Attributes:
        s3_key: S3 storage key
        transcription: Transcribed text
        duration_ms: Duration in milliseconds
        original_format: Original file format
        stt_confidence: Confidence score
        language_code: Language code
        download_url: Pre-signed download URL (temporary)
    """

    s3_key: str = Field(..., description="S3 storage key")
    transcription: str = Field(..., description="Transcribed text")
    duration_ms: int = Field(..., description="Duration in milliseconds")
    original_format: str = Field(..., description="Original format")
    stt_confidence: float = Field(..., description="Confidence score")
    language_code: str = Field(..., description="Language code")
    download_url: Optional[str] = Field(
        default=None,
        description="Pre-signed download URL (expires in 1 hour)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "s3_key": "scenarios/abc123/steps/1/audio-en-US.mp3",
                "transcription": "What's the weather like today?",
                "duration_ms": 2340,
                "original_format": "mp3",
                "stt_confidence": 0.95,
                "language_code": "en-US",
                "download_url": "https://minio.example.com/..."
            }
        }
    )


# =============================================================================
# Noise Configuration Schemas
# =============================================================================


class NoiseConfigCreate(BaseModel):
    """
    Schema for configuring noise injection at scenario level.

    Attributes:
        enabled: Whether noise injection is enabled
        profile: Noise profile name from noise_profile_library
        snr_db: Signal-to-noise ratio in decibels (optional override)
        randomize_snr: Whether to randomize SNR within variance range
        snr_variance: Variance in dB when randomizing (±value)
    """

    enabled: bool = Field(
        default=False,
        description="Whether noise injection is enabled"
    )
    profile: str = Field(
        default="car_cabin_city",
        description="Noise profile name from library"
    )
    snr_db: Optional[float] = Field(
        default=None,
        description="SNR override in dB (uses profile default if not set)",
        ge=-10.0,
        le=50.0
    )
    randomize_snr: bool = Field(
        default=False,
        description="Whether to randomize SNR"
    )
    snr_variance: float = Field(
        default=3.0,
        description="SNR variance in dB when randomizing",
        ge=0.0,
        le=10.0
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "enabled": True,
                "profile": "car_cabin_highway",
                "snr_db": 15.0,
                "randomize_snr": True,
                "snr_variance": 3.0
            }
        }
    )


class NoiseProfileInfo(BaseModel):
    """
    Schema for noise profile information.

    Attributes:
        name: Profile name (e.g., "car_cabin_highway")
        category: Profile category (e.g., "vehicle", "environmental")
        description: Human-readable description
        default_snr_db: Default SNR in decibels
        difficulty: Difficulty level (easy, medium, hard, very_hard, extreme)
        estimated_wer_increase: Estimated WER increase percentage
    """

    name: str = Field(..., description="Profile name")
    category: str = Field(..., description="Profile category")
    description: Optional[str] = Field(default=None, description="Description")
    default_snr_db: float = Field(..., description="Default SNR in dB")
    difficulty: str = Field(..., description="Difficulty level")
    estimated_wer_increase: Optional[float] = Field(
        default=None,
        description="Estimated WER increase (%)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "car_cabin_highway",
                "category": "vehicle",
                "description": "Highway driving with road noise",
                "default_snr_db": 5.0,
                "difficulty": "hard",
                "estimated_wer_increase": 15.0
            }
        }
    )


# =============================================================================
# Batch Upload Schemas
# =============================================================================


class BatchAudioUploadResult(BaseModel):
    """
    Result for a single file in a batch upload.

    Attributes:
        language_code: Language code for the uploaded audio
        success: Whether the upload was successful
        data: Upload response data (if successful)
        error: Error message (if failed)
    """

    language_code: str = Field(..., description="Language code for the audio")
    success: bool = Field(..., description="Whether upload succeeded")
    data: Optional[StepAudioUploadResponse] = Field(
        default=None,
        description="Upload response data (if successful)"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message (if failed)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "language_code": "en-US",
                "success": True,
                "data": {
                    "s3_key": "scenarios/abc123/steps/1/audio-en-US.mp3",
                    "transcription": "Hello world",
                    "duration_ms": 1500,
                    "original_format": "mp3",
                    "stt_confidence": 0.95,
                    "language_code": "en-US"
                },
                "error": None
            }
        }
    )


class BatchAudioUploadResponse(BaseModel):
    """
    Response schema for batch audio upload.

    Attributes:
        total: Total number of files processed
        successful: Number of successful uploads
        failed: Number of failed uploads
        results: Individual results for each file
    """

    total: int = Field(..., description="Total files processed")
    successful: int = Field(..., description="Successful uploads")
    failed: int = Field(..., description="Failed uploads")
    results: List[BatchAudioUploadResult] = Field(
        ...,
        description="Individual results for each file"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 3,
                "successful": 2,
                "failed": 1,
                "results": [
                    {"language_code": "en-US", "success": True, "data": {}, "error": None},
                    {"language_code": "es-ES", "success": True, "data": {}, "error": None},
                    {"language_code": "fr-FR", "success": False, "data": None, "error": "Invalid format"}
                ]
            }
        }
    )


# Rebuild models with forward references to resolve NoiseConfigCreate
ScenarioScriptCreate.model_rebuild()
ScenarioScriptUpdate.model_rebuild()
