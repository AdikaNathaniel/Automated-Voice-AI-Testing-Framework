"""
LLM Model Pricing Model

Database-driven pricing for LLM models. Allows dynamic updates without code changes.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.orm import Session

from models.base import Base


class LLMModelPricing(Base):
    """
    LLM model pricing configuration.

    Stores pricing information for different LLM models and providers.
    Allows runtime updates without code changes.

    Attributes:
        model_name: Name of the LLM model (e.g., "claude-sonnet-4.5")
        provider: API provider (e.g., "anthropic", "openai", "openrouter")
        prompt_price_per_1m: Price per 1M prompt tokens in USD
        completion_price_per_1m: Price per 1M completion tokens in USD
        is_active: Whether this pricing is currently active
        effective_date: When this pricing became/becomes effective
        notes: Optional notes about the pricing (e.g., "Updated per Dec 2025 pricing")
    """

    __test__ = False  # Prevent pytest auto-discovery
    __tablename__ = "llm_model_pricing"

    # Primary key
    id = sa.Column(
        sa.UUID(),
        primary_key=True,
        default=uuid4,
        server_default=sa.text("gen_random_uuid()"),
    )

    # Model identification
    model_name = sa.Column(
        sa.String(100),
        nullable=False,
        index=True,
        comment="Name of the LLM model (e.g., 'claude-sonnet-4.5')",
    )

    provider = sa.Column(
        sa.String(50),
        nullable=False,
        index=True,
        comment="API provider (e.g., 'anthropic', 'openai', 'openrouter')",
    )

    # Pricing information (USD per 1M tokens)
    prompt_price_per_1m = sa.Column(
        sa.Numeric(precision=10, scale=2),
        nullable=False,
        comment="Price per 1 million prompt tokens in USD",
    )

    completion_price_per_1m = sa.Column(
        sa.Numeric(precision=10, scale=2),
        nullable=False,
        comment="Price per 1 million completion tokens in USD",
    )

    # Activation and versioning
    is_active = sa.Column(
        sa.Boolean(),
        nullable=False,
        default=True,
        index=True,
        comment="Whether this pricing is currently active",
    )

    effective_date = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="When this pricing became/becomes effective",
    )

    # Optional metadata
    notes = sa.Column(
        sa.Text(),
        nullable=True,
        comment="Optional notes about this pricing",
    )

    # Audit fields
    created_by = sa.Column(
        sa.UUID(),
        nullable=True,
        comment="User who created this pricing entry",
    )

    updated_by = sa.Column(
        sa.UUID(),
        nullable=True,
        comment="User who last updated this pricing entry",
    )

    # Timestamps
    created_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=sa.func.now(),
    )

    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=sa.func.now(),
        onupdate=datetime.utcnow,
    )

    # Indexes for efficient lookups
    __table_args__ = (
        # Composite index for active pricing lookup
        sa.Index("ix_llm_pricing_model_active", "model_name", "is_active"),
        # Unique constraint for model + provider + effective_date
        sa.UniqueConstraint("model_name", "provider", "effective_date", name="uq_model_provider_date"),
    )

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "id": str(self.id),
            "model_name": self.model_name,
            "provider": self.provider,
            "prompt_price_per_1m": float(self.prompt_price_per_1m),
            "completion_price_per_1m": float(self.completion_price_per_1m),
            "is_active": self.is_active,
            "effective_date": self.effective_date.isoformat() if self.effective_date else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


def get_model_pricing(
    db: Session,
    model_name: str,
    provider: str = "openrouter",
    use_default: bool = True
) -> Optional[LLMModelPricing]:
    """
    Get pricing for a specific model.

    Args:
        db: Database session
        model_name: Name of the model
        provider: API provider (default: "openrouter")
        use_default: If True and no exact match, return default pricing

    Returns:
        LLMModelPricing object or None if not found
    """
    # Try exact match
    pricing = (
        db.query(LLMModelPricing)
        .filter(
            LLMModelPricing.model_name == model_name,
            LLMModelPricing.provider == provider,
            LLMModelPricing.is_active == True
        )
        .order_by(LLMModelPricing.effective_date.desc())
        .first()
    )

    if pricing:
        return pricing

    # Fall back to default if requested
    if use_default:
        pricing = (
            db.query(LLMModelPricing)
            .filter(
                LLMModelPricing.model_name == "default",
                LLMModelPricing.is_active == True
            )
            .order_by(LLMModelPricing.effective_date.desc())
            .first()
        )

    return pricing


def calculate_cost_from_db(
    db: Session,
    model_name: str,
    prompt_tokens: int,
    completion_tokens: int,
    provider: str = "openrouter"
) -> float:
    """
    Calculate cost using database pricing.

    Args:
        db: Database session
        model_name: Name of the model
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens
        provider: API provider

    Returns:
        Estimated cost in USD
    """
    pricing = get_model_pricing(db, model_name, provider)

    if not pricing:
        # Fallback to conservative estimate if no pricing found
        return ((prompt_tokens + completion_tokens) / 1_000_000) * 3.0

    prompt_cost = (prompt_tokens / 1_000_000) * float(pricing.prompt_price_per_1m)
    completion_cost = (completion_tokens / 1_000_000) * float(pricing.completion_price_per_1m)

    return prompt_cost + completion_cost
