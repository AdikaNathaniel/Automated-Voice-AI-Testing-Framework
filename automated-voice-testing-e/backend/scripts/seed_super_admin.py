#!/usr/bin/env python3
"""
Seed script to create initial super_admin user.

This script creates the first super_admin user needed to access
the admin console. Run this after initial database setup.

Usage:
    cd backend
    python -m scripts.seed_super_admin

Environment Variables:
    SUPER_ADMIN_EMAIL - Email for super admin (default: admin@voiceai.local)
    SUPER_ADMIN_USERNAME - Username for super admin (default: superadmin)
    SUPER_ADMIN_PASSWORD - Password for super admin (default: SuperAdmin123!)
    DATABASE_URL - Database connection string
"""

from __future__ import annotations

import asyncio
import os
import sys
from uuid import uuid4

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from api.config import get_settings
from api.auth.password import hash_password
from models.user import User


# Default credentials (override with environment variables)
DEFAULT_EMAIL = "admin@voiceai.local"
DEFAULT_USERNAME = "superadmin"
DEFAULT_PASSWORD = "SuperAdmin123!"


async def create_super_admin(db: AsyncSession) -> User | None:
    """Create the super admin user if it doesn't exist."""

    email = os.getenv("SUPER_ADMIN_EMAIL", DEFAULT_EMAIL)
    username = os.getenv("SUPER_ADMIN_USERNAME", DEFAULT_USERNAME)
    password = os.getenv("SUPER_ADMIN_PASSWORD", DEFAULT_PASSWORD)

    # Check if super admin already exists
    result = await db.execute(
        select(User).where(User.role == "super_admin")
    )
    existing = result.scalar_one_or_none()

    if existing:
        print(f"Super admin already exists: {existing.email}")
        return existing

    # Also check by email/username
    result = await db.execute(
        select(User).where(
            (User.email == email) | (User.username == username)
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        print(f"User with email/username already exists: {existing.email}")
        # Update to super_admin role if needed
        if existing.role != "super_admin":
            existing.role = "super_admin"
            await db.commit()
            print(f"Updated {existing.email} to super_admin role")
        return existing

    # Create new super admin
    super_admin = User(
        id=uuid4(),
        email=email,
        username=username,
        password_hash=hash_password(password),
        full_name="Super Administrator",
        role="super_admin",
        is_active=True,
        is_organization_owner=False,
        tenant_id=None,
    )

    db.add(super_admin)
    await db.commit()
    await db.refresh(super_admin)

    print("=" * 60)
    print("Super Admin Created Successfully!")
    print("=" * 60)
    print(f"  Email:    {email}")
    print(f"  Username: {username}")
    print(f"  Password: {password}")
    print("=" * 60)
    print("\nIMPORTANT: Change the password after first login!")
    print("Access admin console at: /admin")
    print()

    return super_admin


async def main():
    """Main entry point."""
    settings = get_settings()

    # Create async engine
    database_url = settings.DATABASE_URL
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    print("Connecting to database...")

    async with async_session() as session:
        try:
            await create_super_admin(session)
        except Exception as e:
            print(f"Error creating super admin: {e}")
            await session.rollback()
            raise

    await engine.dispose()
    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
