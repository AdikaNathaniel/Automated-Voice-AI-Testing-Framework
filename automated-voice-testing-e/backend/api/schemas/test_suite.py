"""
Test Suite API schemas

Pydantic schemas for test suite API operations including creation,
updates, responses, and scenario management.
"""

from typing import List, Optional, Dict, Any, Literal
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class LanguageConfig(BaseModel):
    """Schema for suite language execution configuration"""

    mode: Literal["primary", "specific", "all"] = Field(
        "primary",
        description="Language execution mode: primary (only primary language), specific (selected languages), all (all available)"
    )
    languages: Optional[List[str]] = Field(
        None,
        description="List of language codes to execute when mode is 'specific'"
    )
    fallback_behavior: Literal["smart", "skip", "fail"] = Field(
        "smart",
        description="Behavior when requested language not available: smart (fallback to primary), skip (skip scenario), fail (mark as failed)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "mode": "specific",
                "languages": ["en-US", "es-ES"],
                "fallback_behavior": "smart"
            }
        }
    )


class TestSuiteCreate(BaseModel):
    """Schema for creating a new test suite"""

    name: str = Field(..., min_length=1, max_length=255, description="Test suite name")
    description: Optional[str] = Field(None, description="Test suite description")
    category: Optional[str] = Field(None, max_length=100, description="Test suite category")
    is_active: Optional[bool] = Field(True, description="Whether test suite is active")
    language_config: Optional[LanguageConfig] = Field(
        None,
        description="Language execution configuration (mode, languages, fallback_behavior)"
    )
    scenario_ids: Optional[List[UUID]] = Field(
        None,
        description="List of scenario IDs to include in the suite (optional on create)"
    )

    model_config = ConfigDict(from_attributes=True)


class TestSuiteUpdate(BaseModel):
    """Schema for updating an existing test suite"""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Test suite name")
    description: Optional[str] = Field(None, description="Test suite description")
    category: Optional[str] = Field(None, max_length=100, description="Test suite category")
    is_active: Optional[bool] = Field(None, description="Whether test suite is active")
    language_config: Optional[LanguageConfig] = Field(
        None,
        description="Language execution configuration (mode, languages, fallback_behavior)"
    )

    model_config = ConfigDict(from_attributes=True)


class TestSuiteResponse(BaseModel):
    """Schema for test suite API responses"""

    id: UUID = Field(..., description="Test suite UUID")
    name: str = Field(..., description="Test suite name")
    description: Optional[str] = Field(None, description="Test suite description")
    category: Optional[str] = Field(None, description="Test suite category")
    is_active: bool = Field(..., description="Whether test suite is active")
    language_config: Optional[Dict[str, Any]] = Field(
        None,
        description="Language execution configuration (mode, languages, fallback_behavior)"
    )
    created_by: Optional[UUID] = Field(None, description="UUID of user who created the test suite")
    created_at: datetime = Field(..., description="Test suite creation timestamp")
    updated_at: datetime = Field(..., description="Test suite last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class TestSuitesListResponse(BaseModel):
    """Schema for paginated list of test suites API response."""

    test_suites: List[TestSuiteResponse] = Field(..., description="List of test suites")
    total: int = Field(..., description="Total number of test suites matching filters")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum number of records returned")


# =============================================================================
# Suite-Scenario Management Schemas
# =============================================================================


class SuiteScenarioInfo(BaseModel):
    """Schema for scenario information within a suite"""

    scenario_id: UUID = Field(..., description="Scenario script UUID")
    name: str = Field(..., description="Scenario name")
    description: Optional[str] = Field(None, description="Scenario description")
    version: Optional[str] = Field(None, description="Scenario version")
    is_active: bool = Field(True, description="Whether the scenario is active")
    order: int = Field(..., description="Order of scenario in the suite")
    languages: Optional[List[str]] = Field(None, description="Languages available in scenario")

    model_config = ConfigDict(from_attributes=True)


class TestSuiteWithScenariosResponse(BaseModel):
    """Schema for test suite response including scenarios"""

    id: UUID = Field(..., description="Test suite UUID")
    name: str = Field(..., description="Test suite name")
    description: Optional[str] = Field(None, description="Test suite description")
    category: Optional[str] = Field(None, description="Test suite category")
    is_active: bool = Field(..., description="Whether test suite is active")
    language_config: Optional[Dict[str, Any]] = Field(
        None,
        description="Language execution configuration (mode, languages, fallback_behavior)"
    )
    created_by: Optional[UUID] = Field(None, description="UUID of user who created the test suite")
    scenarios: List[SuiteScenarioInfo] = Field(
        default_factory=list,
        description="List of scenarios in the suite with order"
    )
    scenario_count: int = Field(0, description="Number of scenarios in the suite")
    created_at: datetime = Field(..., description="Test suite creation timestamp")
    updated_at: datetime = Field(..., description="Test suite last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class AddScenariosToSuiteRequest(BaseModel):
    """Schema for adding scenarios to a suite"""

    scenario_ids: List[UUID] = Field(
        ...,
        min_length=1,
        description="List of scenario IDs to add to the suite"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "scenario_ids": [
                    "123e4567-e89b-12d3-a456-426614174001",
                    "123e4567-e89b-12d3-a456-426614174002"
                ]
            }
        }
    )


class RemoveScenariosFromSuiteRequest(BaseModel):
    """Schema for removing scenarios from a suite"""

    scenario_ids: List[UUID] = Field(
        ...,
        min_length=1,
        description="List of scenario IDs to remove from the suite"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "scenario_ids": [
                    "123e4567-e89b-12d3-a456-426614174001"
                ]
            }
        }
    )


class ReorderSuiteScenariosRequest(BaseModel):
    """Schema for reordering scenarios in a suite"""

    scenario_order: List[UUID] = Field(
        ...,
        min_length=1,
        description="List of scenario IDs in the desired order"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "scenario_order": [
                    "123e4567-e89b-12d3-a456-426614174002",
                    "123e4567-e89b-12d3-a456-426614174001"
                ]
            }
        }
    )


class RunSuiteRequest(BaseModel):
    """Schema for running a suite"""

    language_code: Optional[str] = Field(
        "en-US",
        description="Language code to use for running scenarios"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "language_code": "en-US"
            }
        }
    )


class SuiteExecutionScenarioResult(BaseModel):
    """Schema for individual scenario execution result in a suite run"""

    scenario_id: UUID = Field(..., description="Scenario script UUID")
    scenario_name: str = Field(..., description="Scenario name")
    execution_id: Optional[UUID] = Field(None, description="Multi-turn execution ID")
    status: str = Field(..., description="Execution status (pending, completed, failed)")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class RunSuiteResponse(BaseModel):
    """Schema for suite execution response"""

    suite_id: UUID = Field(..., description="Test suite UUID")
    suite_name: str = Field(..., description="Test suite name")
    suite_run_id: UUID = Field(..., description="Suite run ID for this suite execution")
    total_scenarios: int = Field(..., description="Total number of scenarios to run")
    status: str = Field(..., description="Overall status (pending, in_progress, completed, failed)")
    scenario_results: List[SuiteExecutionScenarioResult] = Field(
        default_factory=list,
        description="Results for each scenario execution"
    )
    started_at: Optional[datetime] = Field(None, description="When suite execution started")
    completed_at: Optional[datetime] = Field(None, description="When suite execution completed")
