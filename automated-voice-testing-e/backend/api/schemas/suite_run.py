"""
Suite Run API schemas

Pydantic schemas for suite run API operations including creation,
updates, and responses for suite runs and test executions.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict



class SuiteRunCreate(BaseModel):
    """Schema for creating a new suite run"""

    suite_id: Optional[UUID] = Field(None, description="Test suite UUID to run")
    scenario_ids: Optional[List[UUID]] = Field(None, description="List of specific scenario script UUIDs to run")
    languages: Optional[List[str]] = Field(None, description="List of language codes to test")
    trigger_type: str = Field("manual", description="Trigger type (manual, scheduled, api, webhook)")
    trigger_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional trigger metadata")

    model_config = ConfigDict(from_attributes=True)


class SuiteRunUpdate(BaseModel):
    """Schema for updating an existing suite run"""

    status: Optional[str] = Field(None, description="Suite run status (pending, running, completed, failed, canceled)")
    total_tests: Optional[int] = Field(None, description="Total number of tests")
    passed_tests: Optional[int] = Field(None, description="Number of passed tests")
    failed_tests: Optional[int] = Field(None, description="Number of failed tests")
    skipped_tests: Optional[int] = Field(None, description="Number of skipped tests")

    model_config = ConfigDict(from_attributes=True)


class SuiteRunResponse(BaseModel):
    """Schema for suite run API responses"""

    id: UUID = Field(..., description="Suite run UUID")
    suite_id: Optional[UUID] = Field(None, description="Test suite UUID")
    created_by: Optional[UUID] = Field(None, description="UUID of user who created the suite run")
    status: str = Field(..., description="Suite run status")
    created_at: datetime = Field(..., description="Suite run creation timestamp")
    updated_at: datetime = Field(..., description="Suite run last update timestamp")
    started_at: Optional[datetime] = Field(None, description="Suite run start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Suite run completion timestamp")
    total_tests: Optional[int] = Field(None, description="Total number of tests")
    passed_tests: Optional[int] = Field(None, description="Number of passed tests")
    failed_tests: Optional[int] = Field(None, description="Number of failed tests")
    skipped_tests: Optional[int] = Field(None, description="Number of skipped tests")
    trigger_type: Optional[str] = Field(None, description="Trigger type")
    trigger_metadata: Optional[Dict[str, Any]] = Field(None, description="Trigger metadata")

    model_config = ConfigDict(from_attributes=True)


class StepExecutionResponse(BaseModel):
    """Schema for individual step execution within a multi-turn scenario"""

    id: UUID = Field(..., description="Step execution UUID")
    step_order: int = Field(..., description="Order of this step in the scenario")
    user_utterance: str = Field(..., description="What the user said")
    ai_response: Optional[str] = Field(None, description="AI's spoken response")
    transcription: Optional[str] = Field(None, description="Transcription of user utterance")
    command_kind: Optional[str] = Field(None, description="Houndify CommandKind")
    confidence_score: Optional[float] = Field(None, description="Recognition confidence score")
    validation_passed: Optional[bool] = Field(None, description="Whether validation passed for this step")
    validation_details: Optional[Dict[str, Any]] = Field(None, description="Detailed validation results")
    response_time_ms: Optional[int] = Field(None, description="API response time in milliseconds")
    input_audio_url: Optional[str] = Field(None, description="S3/MinIO URL for input audio")
    response_audio_url: Optional[str] = Field(None, description="S3/MinIO URL for response audio")
    executed_at: Optional[datetime] = Field(None, description="When step was executed")
    error_message: Optional[str] = Field(None, description="Error message if step failed")

    model_config = ConfigDict(from_attributes=True)


class ValidationDetailsResponse(BaseModel):
    """Schema for validation details including Houndify and LLM results"""

    houndify_passed: Optional[bool] = Field(None, description="Whether Houndify validation passed")
    houndify_result: Optional[Dict[str, Any]] = Field(None, description="Full Houndify validation result")
    llm_passed: Optional[bool] = Field(None, description="Whether LLM ensemble validation passed")
    ensemble_result: Optional[Dict[str, Any]] = Field(None, description="LLM ensemble result with scores and reasoning")
    final_decision: Optional[str] = Field(None, description="Final combined decision: pass, fail, or uncertain")
    review_status: Optional[str] = Field(None, description="auto_pass, needs_review, or auto_fail")

    model_config = ConfigDict(from_attributes=True)


class TestExecutionResponse(BaseModel):
    """Schema for test execution API responses"""

    id: UUID = Field(..., description="Test execution UUID")
    suite_run_id: UUID = Field(..., description="Suite run UUID")
    script_id: Optional[UUID] = Field(None, description="Scenario script UUID")
    script_name: Optional[str] = Field(None, description="Scenario script name")
    status: str = Field(..., description="Execution status (pending, running, passed, failed, error, skipped)")
    created_at: datetime = Field(..., description="Execution creation timestamp")
    updated_at: datetime = Field(..., description="Execution last update timestamp")
    started_at: Optional[datetime] = Field(None, description="Execution start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Execution completion timestamp")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    result: Optional[Dict[str, Any]] = Field(None, description="Execution result data")
    error_message: Optional[str] = Field(None, description="Error message if execution failed")
    language_code: Optional[str] = Field(None, description="Language code executed")
    response_summary: Optional[str] = Field(None, description="Headline response summary or transcript snippet")
    response_time_seconds: Optional[float] = Field(None, description="Computed response time in seconds")
    confidence_score: Optional[float] = Field(None, description="Confidence score reported by the voice AI")
    validation_result_id: Optional[UUID] = Field(None, description="ID of AI validation result tied to this execution")
    validation_review_status: Optional[str] = Field(None, description="auto_pass/needs_review/auto_fail status for validation result")
    validation_details: Optional[ValidationDetailsResponse] = Field(None, description="Full validation details including Houndify and LLM results")
    pending_validation_queue_id: Optional[UUID] = Field(None, description="Pending/claimed validation queue item ID if awaiting human review")
    latest_human_validation_id: Optional[UUID] = Field(None, description="Most recent human validation decision ID, if any")
    input_audio_url: Optional[str] = Field(None, description="S3/MinIO URL for input audio (TTS generated)")
    response_audio_url: Optional[str] = Field(None, description="S3/MinIO URL for response audio (if captured)")
    step_executions: Optional[List[StepExecutionResponse]] = Field(None, description="Individual step executions for multi-turn scenarios")
    total_steps: Optional[int] = Field(None, description="Total number of steps in scenario")
    completed_steps: Optional[int] = Field(None, description="Number of completed steps")

    model_config = ConfigDict(from_attributes=True)


class SuiteRunsListResponse(BaseModel):
    """Schema for paginated list of suite runs API response."""

    runs: List[Dict[str, Any]] = Field(..., description="List of suite runs")
    total: int = Field(..., description="Total number of suite runs matching filters")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum number of records returned")
