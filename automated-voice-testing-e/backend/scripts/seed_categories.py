"""
Seed default categories for scenario organization.

This script creates the standard set of categories that are available
in the ScenarioForm dropdown. These are system categories that cannot
be deleted and are available to all tenants.

Categories match the dropdown options in:
frontend/src/pages/Scenarios/ScenarioForm.tsx (lines 208-214)
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.config import get_settings
from models.category import Category
import uuid


# Default categories with display names, descriptions, and colors
DEFAULT_CATEGORIES = [
    {
        "name": "navigation",
        "display_name": "Navigation",
        "description": "Route finding, directions, and location-based queries",
        "color": "#3B82F6",  # Blue
        "icon": "navigation",
    },
    {
        "name": "media",
        "display_name": "Media Control",
        "description": "Music playback, audio control, and media management",
        "color": "#8B5CF6",  # Purple
        "icon": "music",
    },
    {
        "name": "weather",
        "display_name": "Weather",
        "description": "Weather queries, forecasts, and climate information",
        "color": "#06B6D4",  # Cyan
        "icon": "cloud",
    },
    {
        "name": "reservation",
        "display_name": "Reservation",
        "description": "Booking, scheduling, and reservation management",
        "color": "#10B981",  # Green
        "icon": "calendar",
    },
    {
        "name": "smart_home",
        "display_name": "Smart Home",
        "description": "Home automation, device control, and IoT interactions",
        "color": "#F59E0B",  # Amber
        "icon": "home",
    },
    {
        "name": "general",
        "display_name": "General",
        "description": "General purpose scenarios and miscellaneous queries",
        "color": "#6B7280",  # Gray
        "icon": "star",
    },
    {
        "name": "other",
        "display_name": "Other",
        "description": "Uncategorized or special-purpose scenarios",
        "color": "#9CA3AF",  # Gray
        "icon": "more",
    },
]


def seed_categories():
    """Seed default categories into the database."""
    settings = get_settings()

    # Create database engine and session
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        print("Starting category seeding...")
        created_count = 0
        skipped_count = 0

        for cat_data in DEFAULT_CATEGORIES:
            # Check if category already exists (tenant_id=None for system categories)
            existing = db.query(Category).filter(
                Category.name == cat_data["name"],
                Category.tenant_id == None  # noqa: E711
            ).first()

            if existing:
                print(f"  ⏭️  Category '{cat_data['name']}' already exists, skipping")
                skipped_count += 1
                continue

            # Create new system category
            category = Category(
                id=uuid.uuid4(),
                name=cat_data["name"],
                display_name=cat_data["display_name"],
                description=cat_data["description"],
                color=cat_data["color"],
                icon=cat_data["icon"],
                is_active=True,
                is_system=True,  # System categories cannot be deleted
                tenant_id=None,  # System categories are available to all tenants
            )

            db.add(category)
            print(f"  ✅ Created system category: {cat_data['display_name']} ({cat_data['name']})")
            created_count += 1

        db.commit()

        print(f"\n✨ Category seeding complete!")
        print(f"   Created: {created_count}")
        print(f"   Skipped: {skipped_count}")
        print(f"   Total: {len(DEFAULT_CATEGORIES)}")

    except Exception as e:
        print(f"\n❌ Error seeding categories: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_categories()
