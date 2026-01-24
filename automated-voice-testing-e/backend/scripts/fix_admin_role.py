"""
Quick fix script to set admin role for the admin user.

Run this script to fix the missing role for admin@voiceai.com:
    python backend/scripts/fix_admin_role.py
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from models.user import User
from api.config import get_settings


def _ensure_asyncpg(url: str) -> str:
    """Convert postgresql:// URL to postgresql+asyncpg://"""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


async def fix_admin_role():
    """Set admin role for admin@voiceai.com user."""
    settings = get_settings()

    # Create async engine with asyncpg driver
    database_url = _ensure_asyncpg(settings.DATABASE_URL)
    engine = create_async_engine(database_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        try:
            # Get admin user
            result = await db.execute(
                select(User).where(User.email == "admin@voiceai.com")
            )
            user = result.scalar_one_or_none()

            if not user:
                print("❌ Admin user not found!")
                return

            print(f"Found user: {user.email}")
            print(f"Current role: {user.role}")

            if user.role == "admin":
                print("✓ User already has admin role, no changes needed.")
                return

            # Update role
            user.role = "admin"
            await db.commit()

            print("✓ Successfully updated user role to 'admin'")

        except Exception as e:
            print(f"❌ Error: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(fix_admin_role())
