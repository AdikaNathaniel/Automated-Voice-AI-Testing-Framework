"""Cleanup auto-created edge cases before reseeding"""
import asyncio
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.database import get_async_session
from sqlalchemy import delete
from models.edge_case import EdgeCase


async def cleanup():
    """Delete all auto-created edge cases."""
    async with get_async_session() as db:
        result = await db.execute(
            delete(EdgeCase).where(EdgeCase.auto_created == True)
        )
        await db.commit()
        print(f'Deleted {result.rowcount} auto-created edge cases')


if __name__ == '__main__':
    asyncio.run(cleanup())
