"""
Pydantic schemas for pattern group API.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PatternGroupCreate(BaseModel):
    """Payload for creating a new pattern group."""

    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    pattern_type: Optional[str] = Field(default=None, max_length=100)
    severity: Optional[str] = Field(default="medium", max_length=50)
    status: Optional[str] = Field(default="active", max_length=50)
    suggested_actions: List[str] = Field(default_factory=list)
    pattern_metadata: Dict[str, Any] = Field(default_factory=dict)


class PatternGroupUpdate(BaseModel):
    """Payload for updating existing pattern group fields."""

    name: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = None
    pattern_type: Optional[str] = Field(default=None, max_length=100)
    severity: Optional[str] = Field(default=None, max_length=50)
    status: Optional[str] = Field(default=None, max_length=50)
    suggested_actions: Optional[List[str]] = None
    pattern_metadata: Optional[Dict[str, Any]] = None


class PatternGroupResponse(BaseModel):
    """Response model representing a pattern group record."""

    id: UUID
    name: str
    description: Optional[str] = None
    pattern_type: Optional[str] = None
    severity: str
    first_seen: datetime
    last_seen: datetime
    occurrence_count: int
    status: str
    suggested_actions: List[str]
    pattern_metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PatternGroupListResponse(BaseModel):
    """Response envelope when returning a collection of pattern groups."""

    total: int
    items: List[PatternGroupResponse]


class EdgeCasePatternLinkResponse(BaseModel):
    """Response model for edge case to pattern group link."""

    id: UUID
    edge_case_id: UUID
    pattern_group_id: UUID
    similarity_score: Optional[float] = None
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PatternGroupDetailResponse(BaseModel):
    """Detailed pattern group response with linked edge cases."""

    pattern: PatternGroupResponse
    edge_cases: List[Dict[str, Any]]
    total_edge_cases: int
