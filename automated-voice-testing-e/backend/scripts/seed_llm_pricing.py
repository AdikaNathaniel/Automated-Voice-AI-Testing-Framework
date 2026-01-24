#!/usr/bin/env python3
"""
Seed LLM Model Pricing

Populates the llm_model_pricing table with initial pricing data
for common LLM models.

Usage:
    python backend/scripts/seed_llm_pricing.py
"""

import asyncio
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from datetime import datetime
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from api.config import get_settings
from models.llm_model_pricing import LLMModelPricing
from models.base import Base


# Pricing data as of December 2025
# Source: Official provider pricing pages
PRICING_DATA = [
    # Anthropic Claude models
    {
        "model_name": "claude-sonnet-4.5",
        "provider": "anthropic",
        "prompt_price_per_1m": 3.00,
        "completion_price_per_1m": 15.00,
        "notes": "Claude Sonnet 4.5 - December 2025 pricing",
    },
    {
        "model_name": "claude-sonnet-4.5",
        "provider": "openrouter",
        "prompt_price_per_1m": 3.00,
        "completion_price_per_1m": 15.00,
        "notes": "Claude Sonnet 4.5 via OpenRouter - December 2025 pricing",
    },
    {
        "model_name": "claude-opus-4.5",
        "provider": "anthropic",
        "prompt_price_per_1m": 15.00,
        "completion_price_per_1m": 75.00,
        "notes": "Claude Opus 4.5 - December 2025 pricing",
    },
    {
        "model_name": "claude-opus-4.5",
        "provider": "openrouter",
        "prompt_price_per_1m": 15.00,
        "completion_price_per_1m": 75.00,
        "notes": "Claude Opus 4.5 via OpenRouter - December 2025 pricing",
    },
    {
        "model_name": "claude-3-5-sonnet-20241022",
        "provider": "anthropic",
        "prompt_price_per_1m": 3.00,
        "completion_price_per_1m": 15.00,
        "notes": "Claude 3.5 Sonnet - December 2025 pricing",
    },
    {
        "model_name": "claude-3-opus-20240229",
        "provider": "anthropic",
        "prompt_price_per_1m": 15.00,
        "completion_price_per_1m": 75.00,
        "notes": "Claude 3 Opus - December 2025 pricing",
    },
    {
        "model_name": "claude-3-haiku-20240307",
        "provider": "anthropic",
        "prompt_price_per_1m": 0.25,
        "completion_price_per_1m": 1.25,
        "notes": "Claude 3 Haiku - December 2025 pricing",
    },
    # OpenAI models
    {
        "model_name": "gpt-4-turbo",
        "provider": "openai",
        "prompt_price_per_1m": 10.00,
        "completion_price_per_1m": 30.00,
        "notes": "GPT-4 Turbo - December 2025 pricing",
    },
    {
        "model_name": "gpt-4",
        "provider": "openai",
        "prompt_price_per_1m": 30.00,
        "completion_price_per_1m": 60.00,
        "notes": "GPT-4 - December 2025 pricing",
    },
    {
        "model_name": "gpt-3.5-turbo",
        "provider": "openai",
        "prompt_price_per_1m": 0.50,
        "completion_price_per_1m": 1.50,
        "notes": "GPT-3.5 Turbo - December 2025 pricing",
    },
    # Google models
    {
        "model_name": "gemini-pro",
        "provider": "google",
        "prompt_price_per_1m": 0.50,
        "completion_price_per_1m": 1.50,
        "notes": "Gemini Pro - December 2025 pricing",
    },
    {
        "model_name": "gemini-pro-vision",
        "provider": "google",
        "prompt_price_per_1m": 0.50,
        "completion_price_per_1m": 1.50,
        "notes": "Gemini Pro Vision - December 2025 pricing",
    },
    # Default fallback
    {
        "model_name": "default",
        "provider": "default",
        "prompt_price_per_1m": 1.00,
        "completion_price_per_1m": 3.00,
        "notes": "Default fallback pricing for unknown models",
    },
]


def seed_pricing(session: Session) -> None:
    """Seed LLM pricing data."""
    print("🌱 Seeding LLM model pricing...")

    effective_date = datetime.utcnow()
    created_count = 0
    skipped_count = 0

    for pricing_data in PRICING_DATA:
        # Check if pricing already exists
        query = select(LLMModelPricing).where(
            LLMModelPricing.model_name == pricing_data["model_name"],
            LLMModelPricing.provider == pricing_data["provider"],
        )
        existing = session.execute(query).scalar_one_or_none()

        if existing:
            print(f"  ⏭️  Skipping {pricing_data['model_name']} ({pricing_data['provider']}) - already exists")
            skipped_count += 1
            continue

        # Create pricing entry
        pricing = LLMModelPricing(
            model_name=pricing_data["model_name"],
            provider=pricing_data["provider"],
            prompt_price_per_1m=pricing_data["prompt_price_per_1m"],
            completion_price_per_1m=pricing_data["completion_price_per_1m"],
            is_active=True,
            effective_date=effective_date,
            notes=pricing_data["notes"],
        )

        session.add(pricing)
        created_count += 1
        print(
            f"  ✅ Created pricing for {pricing_data['model_name']} ({pricing_data['provider']}): "
            f"${pricing_data['prompt_price_per_1m']}/${pricing_data['completion_price_per_1m']} per 1M tokens"
        )

    session.commit()

    print(f"\n✅ Seeding complete!")
    print(f"  📊 Created: {created_count} pricing entries")
    print(f"  ⏭️  Skipped: {skipped_count} pricing entries (already exist)")


def main():
    """Main entry point."""
    settings = get_settings()

    # Create engine
    engine = create_engine(settings.DATABASE_URL.replace("+asyncpg", ""))

    # Create tables if they don't exist
    Base.metadata.create_all(engine)

    # Seed data
    with Session(engine) as session:
        try:
            seed_pricing(session)
        except Exception as e:
            print(f"❌ Error seeding pricing: {e}")
            session.rollback()
            sys.exit(1)

    print("\n🎉 All done! LLM pricing data seeded successfully.")


if __name__ == "__main__":
    main()
