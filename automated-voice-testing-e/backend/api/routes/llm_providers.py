"""
LLM Provider Configuration API routes.

These endpoints allow admins to manage LLM provider configurations,
including API keys, from the UI instead of environment variables.

Security: Only admin and QA lead roles can access these endpoints.
API keys are encrypted before storage and masked in responses.
"""

from __future__ import annotations

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.schemas.auth import UserResponse
from api.auth.roles import Role
from api.dependencies import get_current_user_with_db
from api.schemas.llm_provider import (
    LLMProviderConfigCreate,
    LLMProviderConfigUpdate,
    LLMProviderConfigResponse,
    LLMProviderConfigListResponse,
    LLMProvidersSummaryResponse,
    LLMProviderSummary,
    TestProviderRequest,
    TestProviderResponse,
)
from models.audit_trail import log_audit_trail
from services.llm_provider_config_service import LLMProviderConfigService

router = APIRouter(prefix="/llm-providers", tags=["LLM Providers"])

_ADMIN_ROLES = {Role.SUPER_ADMIN.value, Role.ORG_ADMIN.value}


def _get_effective_tenant_id(user: UserResponse) -> UUID:
    """
    Get effective tenant_id for a user.

    Uses user.tenant_id if set (user belongs to an organization),
    otherwise uses user.id (user is their own tenant).

    This ensures tenant_id is NEVER None for data isolation.
    """
    return user.tenant_id if user.tenant_id else user.id


def _ensure_admin_user(user: UserResponse) -> None:
    """Ensure user has admin or QA lead role."""
    if user.role not in _ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or QA lead role required for LLM provider management.",
        )


async def _run_in_sync(
    db: AsyncSession,
    func,
    *args,
    **kwargs,
):
    """Run a sync service function within async context."""
    def _inner(sync_session):
        service = LLMProviderConfigService(sync_session)
        return func(service, *args, **kwargs)

    return await db.run_sync(_inner)


def _to_response(config, include_key_preview: bool = True) -> LLMProviderConfigResponse:
    """Convert model to response schema."""
    data = config.to_dict(include_key=include_key_preview)
    return LLMProviderConfigResponse.model_validate(data)


@router.get(
    "/summary",
    response_model=LLMProvidersSummaryResponse,
    summary="Get providers summary",
    description="Get summary of all LLM providers and their configuration status.",
)
async def get_providers_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> LLMProvidersSummaryResponse:
    """Get summary of all LLM providers."""
    _ensure_admin_user(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    summary = await _run_in_sync(
        db,
        LLMProviderConfigService.get_providers_summary,
        tenant_id=tenant_id,
    )

    return LLMProvidersSummaryResponse(
        providers=[LLMProviderSummary(**p) for p in summary['providers']],
        total_configured=summary['total_configured'],
        total_active=summary['total_active'],
    )


@router.get(
    "",
    response_model=LLMProviderConfigListResponse,
    summary="List provider configs",
    description="List all LLM provider configurations.",
)
async def list_provider_configs(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
    provider: Optional[str] = Query(
        None,
        description="Filter by provider (openai, anthropic, google)"
    ),
    is_active: Optional[bool] = Query(
        None,
        description="Filter by active status"
    ),
) -> LLMProviderConfigListResponse:
    """List all LLM provider configurations."""
    _ensure_admin_user(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    configs = await _run_in_sync(
        db,
        LLMProviderConfigService.list_configs,
        tenant_id=tenant_id,
        provider=provider,
        is_active=is_active,
    )

    items = [_to_response(c) for c in configs]
    return LLMProviderConfigListResponse(total=len(items), items=items)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=LLMProviderConfigResponse,
    summary="Create provider config",
    description="Create a new LLM provider configuration with encrypted API key.",
)
async def create_provider_config(
    payload: LLMProviderConfigCreate,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> LLMProviderConfigResponse:
    """Create a new LLM provider configuration."""
    _ensure_admin_user(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    try:
        config = await _run_in_sync(
            db,
            LLMProviderConfigService.create_config,
            provider=payload.provider,
            display_name=payload.display_name,
            api_key=payload.api_key,
            tenant_id=tenant_id,
            default_model=payload.default_model,
            is_active=payload.is_active,
            is_default=payload.is_default,
            temperature=payload.temperature,
            max_tokens=payload.max_tokens,
            timeout_seconds=payload.timeout_seconds,
            config=payload.config,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        ) from exc

    # Log audit trail - NEVER log api_key
    await log_audit_trail(
        db=db,
        action_type="create",
        resource_type="llm_provider_config",
        resource_id=str(config.id),
        tenant_id=tenant_id,
        user_id=current_user.id,
        new_values={
            "provider": config.provider,
            "display_name": config.display_name,
            "default_model": config.default_model,
            "is_active": config.is_active,
            "is_default": config.is_default,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
        },
        changes_summary=f"LLM provider {config.provider} ({config.display_name}) created by {current_user.email}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True,
    )

    return _to_response(config)


@router.get(
    "/{config_id}",
    response_model=LLMProviderConfigResponse,
    summary="Get provider config",
    description="Get a specific LLM provider configuration by ID.",
)
async def get_provider_config(
    config_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> LLMProviderConfigResponse:
    """Get a specific LLM provider configuration."""
    _ensure_admin_user(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    config = await _run_in_sync(
        db,
        LLMProviderConfigService.get_config,
        config_id=config_id,
        tenant_id=tenant_id,
    )

    if config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider configuration not found"
        )

    return _to_response(config)


@router.patch(
    "/{config_id}",
    response_model=LLMProviderConfigResponse,
    summary="Update provider config",
    description="Update an LLM provider configuration.",
)
async def update_provider_config(
    config_id: UUID,
    payload: LLMProviderConfigUpdate,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> LLMProviderConfigResponse:
    """Update an LLM provider configuration."""
    _ensure_admin_user(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    # Get old config for audit logging
    old_config = await _run_in_sync(
        db,
        LLMProviderConfigService.get_config,
        config_id=config_id,
        tenant_id=tenant_id,
    )

    if old_config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider configuration not found"
        )

    # Capture old values (NEVER log api_key)
    old_values = {
        "provider": old_config.provider,
        "display_name": old_config.display_name,
        "default_model": old_config.default_model,
        "is_active": old_config.is_active,
        "is_default": old_config.is_default,
        "temperature": old_config.temperature,
        "max_tokens": old_config.max_tokens,
    }

    update_data = payload.model_dump(exclude_unset=True)
    api_key_changed = "api_key" in update_data

    try:
        config = await _run_in_sync(
            db,
            LLMProviderConfigService.update_config,
            config_id=config_id,
            tenant_id=tenant_id,
            **update_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        ) from exc

    if config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider configuration not found"
        )

    # Capture new values (NEVER log api_key)
    new_values = {
        "provider": config.provider,
        "display_name": config.display_name,
        "default_model": config.default_model,
        "is_active": config.is_active,
        "is_default": config.is_default,
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
    }

    # Add indicator if API key was changed
    if api_key_changed:
        new_values["api_key_updated"] = True

    # Build summary
    summary_parts = [f"LLM provider {config.provider} ({config.display_name}) updated by {current_user.email}"]
    if api_key_changed:
        summary_parts.append("API key updated")
    if old_values.get("is_default") != new_values.get("is_default") and new_values.get("is_default"):
        summary_parts.append("set as default")

    # Log audit trail
    await log_audit_trail(
        db=db,
        action_type="update",
        resource_type="llm_provider_config",
        resource_id=str(config.id),
        tenant_id=tenant_id,
        user_id=current_user.id,
        old_values=old_values,
        new_values=new_values,
        changes_summary=" - ".join(summary_parts),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True,
    )

    return _to_response(config)


@router.delete(
    "/{config_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete provider config",
    description="Delete an LLM provider configuration.",
)
async def delete_provider_config(
    config_id: UUID,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
):
    """Delete an LLM provider configuration."""
    _ensure_admin_user(current_user)
    tenant_id = _get_effective_tenant_id(current_user)

    # Get config for audit logging before deletion
    old_config = await _run_in_sync(
        db,
        LLMProviderConfigService.get_config,
        config_id=config_id,
        tenant_id=tenant_id,
    )

    if old_config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider configuration not found"
        )

    # Capture old values (NEVER log api_key)
    old_values = {
        "provider": old_config.provider,
        "display_name": old_config.display_name,
        "default_model": old_config.default_model,
        "is_active": old_config.is_active,
        "is_default": old_config.is_default,
    }

    deleted = await _run_in_sync(
        db,
        LLMProviderConfigService.delete_config,
        config_id=config_id,
        tenant_id=tenant_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider configuration not found"
        )

    # Log audit trail
    await log_audit_trail(
        db=db,
        action_type="delete",
        resource_type="llm_provider_config",
        resource_id=str(config_id),
        tenant_id=tenant_id,
        user_id=current_user.id,
        old_values=old_values,
        changes_summary=f"LLM provider {old_config.provider} ({old_config.display_name}) deleted by {current_user.email}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True,
    )


@router.post(
    "/test",
    response_model=TestProviderResponse,
    summary="Test provider",
    description="Test an LLM provider configuration by making a simple API call.",
)
async def test_provider(
    payload: TestProviderRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(get_current_user_with_db)],
) -> TestProviderResponse:
    """Test an LLM provider configuration."""
    _ensure_admin_user(current_user)

    import time

    provider = payload.provider.lower()
    api_key = payload.api_key
    model = payload.model

    # If no API key provided, try to get from stored config
    tenant_id = _get_effective_tenant_id(current_user)
    if not api_key:
        config = await _run_in_sync(
            db,
            LLMProviderConfigService.get_active_config,
            provider=provider,
            tenant_id=tenant_id,
        )
        if config:
            api_key = config.get_api_key()
            if not model:
                model = config.default_model

    if not api_key:
        return TestProviderResponse(
            success=False,
            provider=provider,
            model=model or "unknown",
            message="No API key provided or configured",
            error="API_KEY_MISSING",
        )

    # Set default model if not provided
    if not model:
        from models.llm_provider_config import LLMProviderConfig
        model = LLMProviderConfig.get_default_models().get(provider, "unknown")

    # Test the provider
    start_time = time.time()

    try:
        if provider == "openai":
            success, message, error = await _test_openai(api_key, model)
        elif provider == "anthropic":
            success, message, error = await _test_anthropic(api_key, model)
        elif provider == "google":
            success, message, error = await _test_google(api_key, model)
        else:
            return TestProviderResponse(
                success=False,
                provider=provider,
                model=model,
                message=f"Unknown provider: {provider}",
                error="UNKNOWN_PROVIDER",
            )

        latency_ms = int((time.time() - start_time) * 1000)

        return TestProviderResponse(
            success=success,
            provider=provider,
            model=model,
            message=message,
            latency_ms=latency_ms,
            error=error,
        )

    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        return TestProviderResponse(
            success=False,
            provider=provider,
            model=model,
            message=f"Test failed: {str(e)}",
            latency_ms=latency_ms,
            error=str(e),
        )


async def _test_openai(api_key: str, model: str) -> tuple[bool, str, Optional[str]]:
    """Test OpenAI API connection."""
    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=api_key, timeout=10.0)
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say 'OK'"}],
            max_tokens=5,
        )

        if response.choices and response.choices[0].message.content:
            return True, "OpenAI connection successful", None
        return False, "Empty response from OpenAI", "EMPTY_RESPONSE"

    except ImportError:
        return False, "openai package not installed", "PACKAGE_NOT_INSTALLED"
    except Exception as e:
        return False, str(e), "API_ERROR"


async def _test_anthropic(api_key: str, model: str) -> tuple[bool, str, Optional[str]]:
    """Test Anthropic API connection."""
    try:
        from anthropic import AsyncAnthropic

        client = AsyncAnthropic(api_key=api_key, timeout=10.0)
        response = await client.messages.create(
            model=model,
            messages=[{"role": "user", "content": "Say 'OK'"}],
            max_tokens=5,
        )

        if response.content:
            return True, "Anthropic connection successful", None
        return False, "Empty response from Anthropic", "EMPTY_RESPONSE"

    except ImportError:
        return False, "anthropic package not installed", "PACKAGE_NOT_INSTALLED"
    except Exception as e:
        return False, str(e), "API_ERROR"


async def _test_google(api_key: str, model: str) -> tuple[bool, str, Optional[str]]:
    """Test Google API connection."""
    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        gen_model = genai.GenerativeModel(model_name=model)
        response = await gen_model.generate_content_async(
            "Say 'OK'",
            request_options={"timeout": 10}
        )

        if response.text:
            return True, "Google connection successful", None
        return False, "Empty response from Google", "EMPTY_RESPONSE"

    except ImportError:
        return False, "google-generativeai package not installed", "PACKAGE_NOT_INSTALLED"
    except Exception as e:
        return False, str(e), "API_ERROR"
