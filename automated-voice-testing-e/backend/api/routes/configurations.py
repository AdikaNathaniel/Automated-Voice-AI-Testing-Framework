"""
Configuration management API routes.
"""

from __future__ import annotations

from typing import Annotated, Optional, Dict, Any, List
from uuid import UUID
import hashlib
import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.schemas.auth import UserResponse
from api.auth.roles import Role
from api.dependencies import get_current_user_with_db
from api.schemas.configuration import (
    ConfigurationCreate,
    ConfigurationUpdate,
    ConfigurationResponse,
    ConfigurationListResponse,
    ConfigurationHistoryListResponse,
    ConfigurationHistoryEntry,
)
from services.configuration_service import ConfigurationService
from api.redis_client import get_redis
from api.config import get_settings

router = APIRouter(prefix="/configurations", tags=["Configurations"])

_CONFIG_CACHE_PREFIX = "api:configurations:list"
_settings = get_settings()
_PRIVILEGED_ROLES = {Role.ORG_ADMIN.value, Role.ORG_ADMIN.value, Role.QA_LEAD.value}


def _get_effective_tenant_id(user: UserResponse) -> UUID:
    """
    Get effective tenant_id for a user.

    Uses user.tenant_id if set (user belongs to an organization),
    otherwise uses user.id (user is their own tenant).

    This ensures tenant_id is NEVER None for data isolation.
    """
    return user.tenant_id if user.tenant_id else user.id


def _ensure_privileged_user(user: UserResponse) -> None:
    if user.role not in _PRIVILEGED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or QA lead role required for configuration changes.",
        )


def _service_factory(session: AsyncSession) -> ConfigurationService:
    def _build(sync_session):
        return ConfigurationService(sync_session)

    return session.run_sync(_build)  # type: ignore[return-value]


async def _run_in_sync(
    db: AsyncSession, func, *args, **kwargs
):  # type: ignore[no-untyped-def]
    def _inner(sync_session):
        service = ConfigurationService(sync_session)
        return func(service, *args, **kwargs)

    return await db.run_sync(_inner)


def _build_configuration_cache_key(filters: Dict[str, Any], fields: Optional[List[str]] = None) -> str:
    normalized = {
        key: filters.get(key)
        for key in sorted(filters.keys())
    }
    normalized["fields"] = fields or []
    raw = json.dumps(normalized, sort_keys=True, default=str)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]
    return f"{_CONFIG_CACHE_PREFIX}:{digest}"


async def _load_cached_configuration_list(cache_key: str) -> Optional[ConfigurationListResponse]:
    redis_gen = get_redis()
    redis = await redis_gen.__anext__()
    try:
        cached = await redis.get(cache_key)
        if cached is None:
            return None
        data = json.loads(cached)
        return ConfigurationListResponse.model_validate(data)
    finally:
        try:
            await redis_gen.aclose()
        except StopAsyncIteration:  # pragma: no cover - defensive
            pass


async def _store_cached_configuration_list(cache_key: str, payload: ConfigurationListResponse) -> None:
    redis_gen = get_redis()
    redis = await redis_gen.__anext__()
    try:
        serialized = json.dumps(payload.model_dump(mode="json"), default=str)
        await redis.set(cache_key, serialized, ttl=_settings.CACHE_TTL)
    finally:
        try:
            await redis_gen.aclose()
        except StopAsyncIteration:  # pragma: no cover - defensive
            pass


async def _invalidate_configuration_cache() -> None:
    redis_gen = get_redis()
    redis = await redis_gen.__anext__()
    try:
        if redis.client is None:
            await redis.connect()
        keys = await redis.client.keys(f"{_CONFIG_CACHE_PREFIX}:*")
        if keys:
            await redis.client.delete(*keys)
    finally:
        try:
            await redis_gen.aclose()
        except StopAsyncIteration:  # pragma: no cover - defensive
            pass


@router.get(
    "",
    response_model=ConfigurationListResponse,
    summary="List configurations",
    description="Return configurations filtered by active status.",
)
async def list_configurations(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    is_active: Optional[bool] = Query(
        None, description="Filter by active status when include_inactive is false."
    ),
    include_inactive: bool = Query(
        False, description="Include inactive configurations in the response."
    ),
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of records to return"),
    fields: Optional[str] = Query(None, description="Comma-separated list of fields to include"),
) -> ConfigurationListResponse:
    tenant_id = _get_effective_tenant_id(current_user)

    cache_filters = {
        "tenant_id": str(tenant_id),
        "is_active": None if include_inactive else is_active,
        "include_inactive": include_inactive,
        "cursor": cursor,
        "limit": limit,
    }
    field_list: Optional[List[str]] = None
    if fields:
        field_list = [part.strip() for part in fields.split(",") if part.strip()]

    # CACHING DISABLED - Causes issues during development and with frequently changing data
    # cache_key = _build_configuration_cache_key(cache_filters, field_list)
    # cached = await _load_cached_configuration_list(cache_key)
    # if cached is not None:
    #     return cached

    result = await _run_in_sync(
        db,
        ConfigurationService.list_configurations,
        tenant_id,
        is_active=None if include_inactive else is_active,
        cursor=cursor,
        limit=limit,
        fields=field_list,
    )
    items, metadata = result
    formatted_items: List[Dict[str, Any]] = []
    for cfg in items:
        schema = ConfigurationResponse.model_validate(cfg)
        data = schema.model_dump(mode="json")
        if field_list:
            data = {key: data[key] for key in field_list if key in data}
        formatted_items.append(data)

    response = ConfigurationListResponse(
        total=metadata.get("total", len(formatted_items)),
        items=formatted_items,
        next_cursor=metadata.get("next_cursor"),
        limit=metadata.get("limit", limit),
        fields=field_list or None,
    )
    # CACHING DISABLED
    # await _store_cached_configuration_list(cache_key, response)
    return response


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ConfigurationResponse,
    summary="Create configuration",
)
async def create_configuration(
    payload: ConfigurationCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> ConfigurationResponse:
    _ensure_privileged_user(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    try:
        config = await _run_in_sync(
            db,
            ConfigurationService.create_configuration,
            tenant_id=tenant_id,
            config_key=payload.config_key,
            config_data=payload.config_data,
            description=payload.description,
            is_active=payload.is_active,
            changed_by=current_user.id,
            change_reason="Created via API",
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    await _invalidate_configuration_cache()
    return ConfigurationResponse.model_validate(config)


@router.get(
    "/{configuration_id}",
    response_model=ConfigurationResponse,
    summary="Get configuration",
)
async def get_configuration(
    configuration_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    include_inactive: bool = Query(False, description="Allow retrieval of inactive configurations."),
) -> ConfigurationResponse:
    tenant_id = _get_effective_tenant_id(current_user)

    config = await _run_in_sync(
        db,
        ConfigurationService.get_configuration,
        tenant_id,
        configuration_id,
        include_inactive=include_inactive,
    )
    if config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuration not found")
    return ConfigurationResponse.model_validate(config)


@router.patch(
    "/{configuration_id}",
    response_model=ConfigurationResponse,
    summary="Update configuration",
)
async def update_configuration(
    configuration_id: UUID,
    payload: ConfigurationUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> ConfigurationResponse:
    _ensure_privileged_user(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    update_kwargs = payload.model_dump(exclude_unset=True)
    change_reason = update_kwargs.pop("change_reason", None)

    try:
        config = await _run_in_sync(
            db,
            ConfigurationService.update_configuration,
            tenant_id=tenant_id,
            configuration_id=configuration_id,
            changed_by=current_user.id,
            change_reason=change_reason,
            **update_kwargs,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    await _invalidate_configuration_cache()
    return ConfigurationResponse.model_validate(config)


@router.delete(
    "/{configuration_id}",
    response_model=ConfigurationResponse,
    summary="Delete configuration",
)
async def delete_configuration(
    configuration_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    reason: str = Query("Deleted via API", description="Reason recorded in history."),
) -> ConfigurationResponse:
    _ensure_privileged_user(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    config = await _run_in_sync(
        db,
        ConfigurationService.delete_configuration,
        tenant_id,
        configuration_id,
        changed_by=current_user.id,
        change_reason=reason,
    )
    await _invalidate_configuration_cache()
    return ConfigurationResponse.model_validate(config)


@router.get(
    "/{configuration_id}/history",
    response_model=ConfigurationHistoryListResponse,
    summary="Configuration history",
)
async def get_configuration_history(
    configuration_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> ConfigurationHistoryListResponse:
    tenant_id = _get_effective_tenant_id(current_user)

    history = await _run_in_sync(
        db,
        ConfigurationService.list_history,
        tenant_id,
        configuration_id,
    )
    entries = [ConfigurationHistoryEntry.model_validate(entry) for entry in history]
    return ConfigurationHistoryListResponse(total=len(entries), items=entries)
