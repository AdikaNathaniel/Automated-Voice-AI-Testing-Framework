"""
CI/CD routes for managing continuous integration and deployment pipelines.

Handles:
- CI/CD pipeline runs listing and detail
- Build status and logs
- Deployment tracking
"""

import logging
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user_with_db
from api.schemas.responses import SuccessResponse
from api.schemas.auth import UserResponse
from models.cicd_run import CICDRun

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cicd", tags=["cicd"])


def _get_effective_tenant_id(user: UserResponse) -> UUID:
    """
    Get effective tenant_id for a user.

    Uses user.tenant_id if set (user belongs to an organization),
    otherwise uses user.id (user is their own tenant).
    """
    return user.tenant_id if user.tenant_id else user.id


class CICDRunResponse(BaseModel):
    """Response schema for CI/CD run."""
    id: str
    pipelineName: str = Field(alias="pipeline_name")
    status: str
    branch: str
    commitSha: str = Field(alias="commit_sha")
    commitUrl: str = Field(alias="commit_url")
    triggeredBy: str = Field(alias="triggered_by")
    startedAt: Optional[str] = Field(alias="started_at")
    completedAt: Optional[str] = Field(alias="completed_at")
    totalTests: int = Field(alias="total_tests")
    passedTests: int = Field(alias="passed_tests")
    failedTests: int = Field(alias="failed_tests")

    class Config:
        populate_by_name = True


@router.get("/runs")
async def get_cicd_runs(
    status: Optional[str] = Query(None, description="Filter by run status"),
    provider: Optional[str] = Query(None, description="Filter by provider (github, gitlab, jenkins)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> SuccessResponse:
    """Get CI/CD pipeline runs for the current tenant."""
    tenant_id = _get_effective_tenant_id(current_user)
    logger.info(
        f"[CICD] Getting runs - tenant={tenant_id}, status={status}, "
        f"provider={provider}, skip={skip}, limit={limit}"
    )

    # Build query
    query = select(CICDRun).where(CICDRun.tenant_id == tenant_id)

    if status:
        query = query.where(CICDRun.status == status)

    if provider:
        query = query.where(CICDRun.provider == provider)

    # Order by most recent first
    query = query.order_by(desc(CICDRun.created_at))

    # Get total count
    count_query = select(CICDRun).where(CICDRun.tenant_id == tenant_id)
    if status:
        count_query = count_query.where(CICDRun.status == status)
    if provider:
        count_query = count_query.where(CICDRun.provider == provider)

    result = await db.execute(count_query)
    total = len(result.scalars().all())

    # Apply pagination
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    runs = result.scalars().all()

    # Convert to response format (matching frontend CICDRunRecord interface)
    items = [run.to_dict() for run in runs]

    return SuccessResponse(
        data={
            "runs": items,  # Frontend expects "runs" key
            "items": items,  # Also include "items" for consistency
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    )


@router.get("/runs/{run_id}")
async def get_cicd_run(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> SuccessResponse:
    """Get a specific CI/CD run by ID."""
    tenant_id = _get_effective_tenant_id(current_user)
    logger.info(f"[CICD] Getting run {run_id} for tenant {tenant_id}")

    result = await db.execute(
        select(CICDRun).where(
            CICDRun.id == run_id,
            CICDRun.tenant_id == tenant_id,
        )
    )
    run = result.scalar_one_or_none()

    if not run:
        raise HTTPException(status_code=404, detail="CI/CD run not found")

    return SuccessResponse(data=run.to_dict())


@router.get("/stats")
async def get_cicd_stats(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> SuccessResponse:
    """Get CI/CD statistics for the current tenant."""
    tenant_id = _get_effective_tenant_id(current_user)
    logger.info(f"[CICD] Getting stats for tenant {tenant_id}")

    # Get all runs for this tenant
    result = await db.execute(
        select(CICDRun).where(CICDRun.tenant_id == tenant_id)
    )
    runs = result.scalars().all()

    # Calculate stats
    total = len(runs)
    by_status = {}
    by_provider = {}

    for run in runs:
        by_status[run.status] = by_status.get(run.status, 0) + 1
        by_provider[run.provider] = by_provider.get(run.provider, 0) + 1

    return SuccessResponse(
        data={
            "total": total,
            "by_status": by_status,
            "by_provider": by_provider,
        }
    )
