"""
Fix categories in existing scenario_scripts to match the new standardized categories.

This script updates all scenarios with old category names to use the new
lowercase, standardized category names.
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from api.config import get_settings

# Category mapping from old to new
CATEGORY_MAPPING = {
    'Weather': 'weather',
    'SmartHome': 'smart_home',
    'Reservation': 'reservation',
    'Music': 'media',
    'Validation Test': 'other',
    'Multi-Language Test': 'other',
    'Regex Test': 'other',
    'LLM Test': 'other',
    'Hybrid Test': 'other',
}


def fix_categories():
    """Update scenario categories to use standardized names."""
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        print("Checking current categories...")

        # Get current categories
        result = conn.execute(text("""
            SELECT DISTINCT script_metadata->>'category' as category, COUNT(*) as count
            FROM scenario_scripts
            WHERE script_metadata->>'category' IS NOT NULL
            GROUP BY script_metadata->>'category'
            ORDER BY category
        """))

        current_categories = list(result)
        print(f"\nFound {len(current_categories)} unique categories:")
        for cat, count in current_categories:
            print(f"  - {cat}: {count} scenarios")

        print("\n" + "="*60)
        print("Starting category updates...")
        print("="*60 + "\n")

        total_updated = 0

        # Update each category
        for old_cat, new_cat in CATEGORY_MAPPING.items():
            result = conn.execute(text("""
                UPDATE scenario_scripts
                SET script_metadata = jsonb_set(
                    script_metadata,
                    '{category}',
                    (:new_category)::jsonb
                )
                WHERE script_metadata->>'category' = :old_category
            """), {"old_category": old_cat, "new_category": f'"{new_cat}"'})

            count = result.rowcount
            if count > 0:
                print(f"  ✅ Updated '{old_cat}' → '{new_cat}': {count} scenarios")
                total_updated += count

        conn.commit()

        print("\n" + "="*60)
        print(f"✨ Category update complete! Updated {total_updated} scenarios")
        print("="*60 + "\n")

        # Show final state
        result = conn.execute(text("""
            SELECT DISTINCT script_metadata->>'category' as category, COUNT(*) as count
            FROM scenario_scripts
            WHERE script_metadata->>'category' IS NOT NULL
            GROUP BY script_metadata->>'category'
            ORDER BY category
        """))

        print("Final categories in database:")
        for cat, count in result:
            print(f"  - {cat}: {count} scenarios")


if __name__ == "__main__":
    fix_categories()
