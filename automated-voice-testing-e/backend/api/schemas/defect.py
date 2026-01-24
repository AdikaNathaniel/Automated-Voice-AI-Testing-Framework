"""
Pydantic schemas for defect management API.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DefectCreate(BaseModel):
    """Payload for creating a defect."""

    script_id: Optional[UUID] = Field(default=None, description="Scenario script that produced the defect")
    execution_id: Optional[UUID] = Field(default=None, description="Multi-turn execution where defect was detected")
    suite_run_id: Optional[UUID] = None
    severity: str = Field(..., max_length=50)
    category: str = Field(..., max_length=100)
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    language_code: Optional[str] = Field(default=None, max_length=10)
    detected_at: datetime
    status: str = Field(default="open", max_length=50)


class DefectCreateFromValidation(BaseModel):
    """Payload for creating a defect from a validation result during human review."""

    validation_result_id: UUID = Field(..., description="Validation result that prompted defect creation")
    severity: str = Field(default="medium", max_length=50, description="Defect severity (low, medium, high, critical)")
    category: str = Field(default="uncategorized", max_length=100, description="Defect category")
    title: Optional[str] = Field(default=None, max_length=255, description="Custom defect title (auto-generated if not provided)")
    description: Optional[str] = Field(default=None, description="Additional context or notes about the defect")


class DefectUpdate(BaseModel):
    """Payload for updating mutable defect fields."""

    severity: Optional[str] = Field(default=None, max_length=50)
    category: Optional[str] = Field(default=None, max_length=100)
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    language_code: Optional[str] = Field(default=None, max_length=10)
    detected_at: Optional[datetime] = None
    status: Optional[str] = Field(default=None, max_length=50)
    assigned_to: Optional[UUID] = None
    resolved_at: Optional[datetime] = None


class DefectAssign(BaseModel):
    """Payload for assigning a defect to a user."""

    assigned_to: UUID


class DefectResolve(BaseModel):
    """Payload for resolving a defect."""

    resolution: str = Field(..., min_length=1)


class DefectResponse(BaseModel):
    """Response model representing a defect record."""

    id: UUID
    script_id: Optional[UUID] = None
    execution_id: Optional[UUID] = None
    suite_run_id: Optional[UUID] = None
    severity: str
    category: str
    title: str
    description: Optional[str] = None
    language_code: Optional[str] = None
    detected_at: datetime
    status: str
    assigned_to: Optional[UUID] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    jira_issue_key: Optional[str] = None
    jira_issue_url: Optional[str] = None
    jira_status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DefectListResponse(BaseModel):
    """Response when listing defects."""

    total: int
    items: List[DefectResponse]


class DefectRelatedExecution(BaseModel):
    """Execution related to a defect."""

    id: UUID
    status: str
    suite_run_id: Optional[UUID] = None
    executed_at: Optional[datetime] = None


class DefectComment(BaseModel):
    """Comment on a defect."""

    id: UUID
    author: str
    message: str
    created_at: datetime


class DefectDetailResponse(DefectResponse):
    """Extended response for defect detail view with related data."""

    related_executions: List[DefectRelatedExecution] = Field(default_factory=list)
    comments: List[DefectComment] = Field(default_factory=list)
