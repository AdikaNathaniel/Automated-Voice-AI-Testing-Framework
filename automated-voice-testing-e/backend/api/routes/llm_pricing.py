"""
LLM Pricing Management API

Endpoints for managing LLM model pricing and viewing audit trails.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user_with_db, require_role
from api.schemas.auth import UserResponse
from api.schemas.llm_pricing import (
    LLMPricingCreate,
    LLMPricingUpdate,
    LLMPricingResponse,
    LLMPricingListResponse,
    AuditTrailResponse,
    AuditTrailListResponse,
)
from models.llm_model_pricing import LLMModelPricing
from models.audit_trail import AuditTrail, log_audit_trail

router = APIRouter(
    prefix="/llm-pricing",
    tags=["LLM Pricing"],
)


@router.get("", response_model=LLMPricingListResponse)
async def list_pricing(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    model_name: Optional[str] = Query(None, description="Filter by model name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> LLMPricingListResponse:
    """
    List all LLM pricing configurations.

    Requires: Super Admin role
    """
    # Build query filters
    filters = []
    if is_active is not None:
        filters.append(LLMModelPricing.is_active == is_active)
    if provider:
        filters.append(LLMModelPricing.provider == provider)
    if model_name:
        filters.append(LLMModelPricing.model_name.ilike(f"%{model_name}%"))

    # Get total count
    count_query = select(func.count(LLMModelPricing.id))
    if filters:
        count_query = count_query.where(and_(*filters))

    result = await db.execute(count_query)
    total = result.scalar_one()

    # Get pricing entries
    query = select(LLMModelPricing)
    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(LLMModelPricing.model_name, LLMModelPricing.effective_date.desc())
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    pricing_entries = result.scalars().all()

    return LLMPricingListResponse(
        pricing=[LLMPricingResponse.model_validate(p) for p in pricing_entries],
        total=total
    )


@router.get("/{pricing_id}", response_model=LLMPricingResponse)
async def get_pricing(
    pricing_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> LLMPricingResponse:
    """
    Get a specific LLM pricing configuration.

    Requires: Super Admin role
    """
    query = select(LLMModelPricing).where(LLMModelPricing.id == pricing_id)
    result = await db.execute(query)
    pricing = result.scalar_one_or_none()

    if not pricing:
        raise HTTPException(status_code=404, detail="Pricing configuration not found")

    return LLMPricingResponse.model_validate(pricing)


@router.post("", response_model=LLMPricingResponse)
async def create_pricing(
    pricing_data: LLMPricingCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(require_role(["super_admin"])),
) -> LLMPricingResponse:
    """
    Create a new LLM pricing configuration.

    Requires: Super Admin role

    Creates an audit trail entry for this action.
    """
    # Check for duplicate
    query = select(LLMModelPricing).where(
        and_(
            LLMModelPricing.model_name == pricing_data.model_name,
            LLMModelPricing.provider == pricing_data.provider,
            LLMModelPricing.effective_date == (pricing_data.effective_date or datetime.utcnow())
        )
    )
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Pricing already exists for {pricing_data.model_name} ({pricing_data.provider}) on this date"
        )

    # Create pricing entry
    pricing = LLMModelPricing(
        model_name=pricing_data.model_name,
        provider=pricing_data.provider,
        prompt_price_per_1m=pricing_data.prompt_price_per_1m,
        completion_price_per_1m=pricing_data.completion_price_per_1m,
        is_active=pricing_data.is_active,
        effective_date=pricing_data.effective_date or datetime.utcnow(),
        notes=pricing_data.notes,
        created_by=current_user.id,
        updated_by=current_user.id,
    )

    db.add(pricing)
    await db.flush()

    # Create audit trail
    await log_audit_trail(
        db=db,
        action_type="create",
        resource_type="llm_pricing",
        resource_id=str(pricing.id),
        user_id=current_user.id,
        new_values=pricing_data.model_dump(),
        changes_summary=f"Created pricing for {pricing_data.model_name} ({pricing_data.provider}): ${pricing_data.prompt_price_per_1m}/${pricing_data.completion_price_per_1m} per 1M tokens",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    await db.commit()
    await db.refresh(pricing)

    return LLMPricingResponse.model_validate(pricing)


@router.patch("/{pricing_id}", response_model=LLMPricingResponse)
async def update_pricing(
    pricing_id: UUID,
    pricing_data: LLMPricingUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(require_role(["super_admin"])),
) -> LLMPricingResponse:
    """
    Update an LLM pricing configuration.

    Requires: Super Admin role

    Creates an audit trail entry for this action.
    """
    # Get existing pricing
    query = select(LLMModelPricing).where(LLMModelPricing.id == pricing_id)
    result = await db.execute(query)
    pricing = result.scalar_one_or_none()

    if not pricing:
        raise HTTPException(status_code=404, detail="Pricing configuration not found")

    # Store old values for audit
    old_values = pricing.to_dict()

    # Update fields
    update_data = pricing_data.model_dump(exclude_unset=True)
    changes = []

    for field, value in update_data.items():
        if hasattr(pricing, field):
            old_value = getattr(pricing, field)
            if old_value != value:
                setattr(pricing, field, value)
                changes.append(f"{field}: {old_value} → {value}")

    if not changes:
        raise HTTPException(status_code=400, detail="No changes detected")

    # Update audit fields
    pricing.updated_by = current_user.id
    pricing.updated_at = datetime.utcnow()

    await db.flush()

    # Create audit trail
    await log_audit_trail(
        db=db,
        action_type="update",
        resource_type="llm_pricing",
        resource_id=str(pricing.id),
        user_id=current_user.id,
        old_values=old_values,
        new_values=update_data,
        changes_summary=f"Updated {pricing.model_name} pricing: {'; '.join(changes)}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    await db.commit()
    await db.refresh(pricing)

    return LLMPricingResponse.model_validate(pricing)


@router.delete("/{pricing_id}")
async def deactivate_pricing(
    pricing_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(require_role(["super_admin"])),
) -> dict:
    """
    Deactivate an LLM pricing configuration.

    Requires: Super Admin role

    Note: We don't actually delete pricing entries, just deactivate them
    to preserve historical cost calculations and audit trail.

    Creates an audit trail entry for this action.
    """
    # Get existing pricing
    query = select(LLMModelPricing).where(LLMModelPricing.id == pricing_id)
    result = await db.execute(query)
    pricing = result.scalar_one_or_none()

    if not pricing:
        raise HTTPException(status_code=404, detail="Pricing configuration not found")

    if not pricing.is_active:
        raise HTTPException(status_code=400, detail="Pricing is already deactivated")

    # Store old values for audit
    old_values = pricing.to_dict()

    # Deactivate
    pricing.is_active = False
    pricing.updated_by = current_user.id
    pricing.updated_at = datetime.utcnow()

    await db.flush()

    # Create audit trail
    await log_audit_trail(
        db=db,
        action_type="deactivate",
        resource_type="llm_pricing",
        resource_id=str(pricing.id),
        user_id=current_user.id,
        old_values=old_values,
        new_values={"is_active": False},
        changes_summary=f"Deactivated pricing for {pricing.model_name} ({pricing.provider})",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    await db.commit()

    return {"success": True, "message": "Pricing deactivated successfully"}


@router.get("/{pricing_id}/audit-trail", response_model=AuditTrailListResponse)
async def get_pricing_audit_trail(
    pricing_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
) -> AuditTrailListResponse:
    """
    Get audit trail for a specific pricing configuration.

    Requires: Super Admin role
    """
    # Verify pricing exists
    pricing_query = select(LLMModelPricing).where(LLMModelPricing.id == pricing_id)
    pricing_result = await db.execute(pricing_query)
    pricing = pricing_result.scalar_one_or_none()

    if not pricing:
        raise HTTPException(status_code=404, detail="Pricing configuration not found")

    # Get total count
    count_query = select(func.count(AuditTrail.id)).where(
        and_(
            AuditTrail.resource_type == "llm_pricing",
            AuditTrail.resource_id == str(pricing_id)
        )
    )
    result = await db.execute(count_query)
    total = result.scalar_one()

    # Get audit entries
    query = select(AuditTrail).where(
        and_(
            AuditTrail.resource_type == "llm_pricing",
            AuditTrail.resource_id == str(pricing_id)
        )
    ).order_by(AuditTrail.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    audits = result.scalars().all()

    return AuditTrailListResponse(
        audits=[AuditTrailResponse.model_validate(a) for a in audits],
        total=total
    )
