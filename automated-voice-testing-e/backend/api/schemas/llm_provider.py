"""
Pydantic schemas for LLM Provider Configuration API.

These schemas define the request/response models for the LLM provider
configuration CRUD endpoints, used for managing API keys from the admin UI.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class LLMProviderConfigCreate(BaseModel):
    """Schema for creating a new LLM provider configuration."""

    provider: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="LLM provider name (openai, anthropic, google)"
    )
    display_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Human-readable display name"
    )
    api_key: str = Field(
        ...,
        min_length=1,
        description="API key (will be encrypted before storage)"
    )
    default_model: Optional[str] = Field(
        None,
        max_length=100,
        description="Default model name"
    )
    is_active: bool = Field(
        True,
        description="Whether this configuration is active"
    )
    is_default: bool = Field(
        False,
        description="Whether this is the default config for the provider"
    )
    temperature: float = Field(
        0.0,
        ge=0.0,
        le=2.0,
        description="Default temperature for API calls"
    )
    max_tokens: int = Field(
        1024,
        ge=1,
        le=100000,
        description="Default max tokens for API calls"
    )
    timeout_seconds: int = Field(
        30,
        ge=1,
        le=300,
        description="Request timeout in seconds"
    )
    config: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional configuration"
    )

    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Validate provider is one of the supported providers."""
        valid_providers = ['openai', 'anthropic', 'google']
        if v.lower() not in valid_providers:
            raise ValueError(
                f"Provider must be one of: {', '.join(valid_providers)}"
            )
        return v.lower()


class LLMProviderConfigUpdate(BaseModel):
    """Schema for updating an LLM provider configuration."""

    display_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Human-readable display name"
    )
    api_key: Optional[str] = Field(
        None,
        min_length=1,
        description="API key (will be encrypted before storage)"
    )
    default_model: Optional[str] = Field(
        None,
        max_length=100,
        description="Default model name"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Whether this configuration is active"
    )
    is_default: Optional[bool] = Field(
        None,
        description="Whether this is the default config for the provider"
    )
    temperature: Optional[float] = Field(
        None,
        ge=0.0,
        le=2.0,
        description="Default temperature for API calls"
    )
    max_tokens: Optional[int] = Field(
        None,
        ge=1,
        le=100000,
        description="Default max tokens for API calls"
    )
    timeout_seconds: Optional[int] = Field(
        None,
        ge=1,
        le=300,
        description="Request timeout in seconds"
    )
    config: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional configuration"
    )


class LLMProviderConfigResponse(BaseModel):
    """Schema for LLM provider configuration response."""

    id: UUID
    tenant_id: Optional[UUID] = None
    provider: str
    display_name: str
    default_model: Optional[str] = None
    is_active: bool
    is_default: bool
    temperature: float
    max_tokens: float
    timeout_seconds: float
    config: Optional[Dict[str, Any]] = None
    api_key_preview: Optional[str] = Field(
        None,
        description="Masked preview of API key (e.g., 'sk-...abc1')"
    )
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LLMProviderConfigListResponse(BaseModel):
    """Schema for list of LLM provider configurations."""

    total: int
    items: List[LLMProviderConfigResponse]


class LLMProviderSummary(BaseModel):
    """Summary of available LLM providers."""

    provider: str
    display_name: str
    default_model: str
    is_configured: bool = Field(
        description="Whether API key is configured for this provider"
    )
    is_active: bool = Field(
        description="Whether the provider configuration is active"
    )


class LLMProvidersSummaryResponse(BaseModel):
    """Summary of all available LLM providers."""

    providers: List[LLMProviderSummary]
    total_configured: int
    total_active: int


class TestProviderRequest(BaseModel):
    """Schema for testing a provider configuration."""

    provider: str
    api_key: Optional[str] = Field(
        None,
        description="API key to test (uses stored key if not provided)"
    )
    model: Optional[str] = Field(
        None,
        description="Model to test (uses default if not provided)"
    )


class TestProviderResponse(BaseModel):
    """Schema for provider test result."""

    success: bool
    provider: str
    model: str
    message: str
    latency_ms: Optional[int] = None
    error: Optional[str] = None
