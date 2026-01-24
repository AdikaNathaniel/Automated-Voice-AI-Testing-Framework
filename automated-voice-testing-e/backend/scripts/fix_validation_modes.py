"""
Fix validation_mode for all scenarios to use 'hybrid'.

Run this script to update all scenarios to use hybrid validation:
    python backend/scripts/fix_validation_modes.py
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from models.scenario_script import ScenarioScript
from api.config import get_settings


def _ensure_asyncpg(url: str) -> str:
    """Convert postgresql:// URL to postgresql+asyncpg://"""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


async def fix_validation_modes():
    """Update all scenarios to use hybrid validation mode."""
    settings = get_settings()

    # Create async engine with asyncpg driver
    database_url = _ensure_asyncpg(settings.DATABASE_URL)
    engine = create_async_engine(database_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        try:
            # First, get count of scenarios by validation_mode
            result = await db.execute(select(ScenarioScript))
            scenarios = result.scalars().all()

            print(f"Found {len(scenarios)} total scenarios")

            # Count by mode
            modes = {}
            for s in scenarios:
                mode = s.validation_mode or 'NULL'
                modes[mode] = modes.get(mode, 0) + 1

            print("\nCurrent validation modes:")
            for mode, count in sorted(modes.items()):
                print(f"  - {mode}: {count}")

            # Update all non-hybrid scenarios to hybrid
            non_hybrid = [s for s in scenarios if s.validation_mode != 'hybrid']

            if not non_hybrid:
                print("\n✓ All scenarios already use 'hybrid' validation mode.")
                return

            print(f"\nUpdating {len(non_hybrid)} scenarios to 'hybrid'...")

            for scenario in non_hybrid:
                old_mode = scenario.validation_mode
                scenario.validation_mode = 'hybrid'
                print(f"  - {scenario.name}: {old_mode} → hybrid")

            await db.commit()

            print(f"\n✓ Successfully updated {len(non_hybrid)} scenarios to 'hybrid' validation mode.")

        except Exception as e:
            print(f"❌ Error: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(fix_validation_modes())
