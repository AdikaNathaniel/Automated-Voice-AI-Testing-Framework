"""
LLM Usage Log Model

Tracks all LLM API calls for cost monitoring, budgeting, and analytics.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects import postgresql
from sqlalchemy import JSON

from models.base import Base

# Use JSONB for PostgreSQL, JSON for SQLite (testing)
JSONB_TYPE = JSONB().with_variant(JSON(), "sqlite")


def _serialise(val: Any) -> Any:
    """Serialize UUID and datetime objects for JSON."""
    if isinstance(val, UUID):
        return str(val)
    if isinstance(val, datetime):
        return val.isoformat()
    return val


class LLMUsageLog(Base):
    """
    Log entry for LLM API usage tracking.

    Records every LLM API call with token usage and cost estimates
    for monitoring, budgeting, and cost optimization.

    Attributes:
        tenant_id: Organization that made the call
        service_name: Which service made the call (e.g., "pattern_analysis", "validation")
        operation: Specific operation (e.g., "analyze_edge_case", "match_pattern")
        model: LLM model used (e.g., "claude-sonnet-4.5", "gpt-4")
        provider: API provider (e.g., "openrouter", "anthropic", "openai")
        prompt_tokens: Number of tokens in the prompt
        completion_tokens: Number of tokens in the completion
        total_tokens: Total tokens used (prompt + completion)
        estimated_cost_usd: Estimated cost in USD
        request_metadata: Additional context (task_id, edge_case_id, etc.)
        response_metadata: Provider response metadata
        duration_ms: API call duration in milliseconds
        success: Whether the call succeeded
        error_message: Error message if call failed
    """

    __test__ = False  # Prevent pytest auto-discovery
    __tablename__ = "llm_usage_logs"

    # Primary key
    id = sa.Column(
        sa.UUID(),
        primary_key=True,
        default=uuid4,
        server_default=sa.text("gen_random_uuid()"),
    )

    # Tenant association
    tenant_id = sa.Column(
        sa.UUID(),
        nullable=False,
        index=True,
        comment="Organization that made this LLM call",
    )

    # Service identification
    service_name = sa.Column(
        sa.String(100),
        nullable=False,
        index=True,
        comment="Service that made the call (pattern_analysis, validation, etc.)",
    )

    operation = sa.Column(
        sa.String(100),
        nullable=False,
        comment="Specific operation (analyze_edge_case, match_pattern, etc.)",
    )

    # Model information
    model = sa.Column(
        sa.String(100),
        nullable=False,
        index=True,
        comment="LLM model used (claude-sonnet-4.5, gpt-4, etc.)",
    )

    provider = sa.Column(
        sa.String(50),
        nullable=False,
        index=True,
        comment="API provider (openrouter, anthropic, openai, etc.)",
    )

    # Token usage
    prompt_tokens = sa.Column(
        sa.Integer(),
        nullable=True,
        comment="Number of tokens in the prompt",
    )

    completion_tokens = sa.Column(
        sa.Integer(),
        nullable=True,
        comment="Number of tokens in the completion",
    )

    total_tokens = sa.Column(
        sa.Integer(),
        nullable=True,
        index=True,
        comment="Total tokens used (prompt + completion)",
    )

    # Cost tracking
    estimated_cost_usd = sa.Column(
        sa.Numeric(precision=10, scale=6),
        nullable=True,
        comment="Estimated cost in USD (based on current pricing)",
    )

    # Metadata
    request_metadata = sa.Column(
        JSONB_TYPE,
        nullable=True,
        comment="Additional request context (task_id, edge_case_id, pattern_id, etc.)",
    )

    response_metadata = sa.Column(
        JSONB_TYPE,
        nullable=True,
        comment="Provider response metadata (request_id, model_version, etc.)",
    )

    # Performance tracking
    duration_ms = sa.Column(
        sa.Integer(),
        nullable=True,
        comment="API call duration in milliseconds",
    )

    # Success tracking
    success = sa.Column(
        sa.Boolean(),
        nullable=False,
        default=True,
        index=True,
        comment="Whether the API call succeeded",
    )

    error_message = sa.Column(
        sa.Text(),
        nullable=True,
        comment="Error message if call failed",
    )

    # Timestamps
    created_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=sa.func.now(),
        index=True,
        comment="When this call was made",
    )

    # Indexes for common queries
    __table_args__ = (
        sa.Index("ix_llm_usage_tenant_created", "tenant_id", "created_at"),
        sa.Index("ix_llm_usage_service_created", "service_name", "created_at"),
        sa.Index("ix_llm_usage_model_created", "model", "created_at"),
        sa.Index("ix_llm_usage_success_created", "success", "created_at"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "id": _serialise(self.id),
            "tenant_id": _serialise(self.tenant_id),
            "service_name": self.service_name,
            "operation": self.operation,
            "model": self.model,
            "provider": self.provider,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "estimated_cost_usd": float(self.estimated_cost_usd) if self.estimated_cost_usd else None,
            "request_metadata": self.request_metadata,
            "response_metadata": self.response_metadata,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error_message": self.error_message,
            "created_at": _serialise(self.created_at),
        }


# DEPRECATED: Hardcoded pricing - use database-driven pricing instead
# This dictionary is kept only as a fallback if database is unavailable
# Updated as of December 2025 - Use llm_model_pricing table for production
LLM_PRICING_FALLBACK = {
    # Anthropic Claude models
    "claude-sonnet-4.5": {
        "prompt": 3.00,
        "completion": 15.00,
    },
    "claude-opus-4.5": {
        "prompt": 15.00,
        "completion": 75.00,
    },
    "claude-3-5-sonnet-20241022": {
        "prompt": 3.00,
        "completion": 15.00,
    },
    "claude-3-opus-20240229": {
        "prompt": 15.00,
        "completion": 75.00,
    },
    "claude-3-haiku-20240307": {
        "prompt": 0.25,
        "completion": 1.25,
    },
    # OpenAI models
    "gpt-4-turbo": {
        "prompt": 10.00,
        "completion": 30.00,
    },
    "gpt-4": {
        "prompt": 30.00,
        "completion": 60.00,
    },
    "gpt-3.5-turbo": {
        "prompt": 0.50,
        "completion": 1.50,
    },
    # Google models
    "gemini-pro": {
        "prompt": 0.50,
        "completion": 1.50,
    },
    "gemini-pro-vision": {
        "prompt": 0.50,
        "completion": 1.50,
    },
    # Default fallback
    "default": {
        "prompt": 1.00,
        "completion": 3.00,
    },
}


def calculate_cost(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    db=None,
    provider: str = "openrouter"
) -> float:
    """
    Calculate estimated cost for an LLM API call.

    Prefers database-driven pricing from llm_model_pricing table.
    Falls back to hardcoded pricing if database is unavailable.

    Args:
        model: Model name
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens
        db: Database session (optional, for database-driven pricing)
        provider: API provider (default: "openrouter")

    Returns:
        Estimated cost in USD
    """
    # Try database-driven pricing first
    if db:
        try:
            from models.llm_model_pricing import calculate_cost_from_db
            return calculate_cost_from_db(db, model, prompt_tokens, completion_tokens, provider)
        except Exception:
            # Fall back to hardcoded pricing if database query fails
            pass

    # Fallback to hardcoded pricing
    pricing = LLM_PRICING_FALLBACK.get(model, LLM_PRICING_FALLBACK["default"])

    # Calculate cost (pricing is per 1M tokens)
    prompt_cost = (prompt_tokens / 1_000_000) * pricing["prompt"]
    completion_cost = (completion_tokens / 1_000_000) * pricing["completion"]

    return prompt_cost + completion_cost
