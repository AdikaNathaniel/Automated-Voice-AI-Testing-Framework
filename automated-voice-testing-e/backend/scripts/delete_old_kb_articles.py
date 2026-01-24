"""Delete old KB articles with JSON-wrapped content"""
import asyncio
import sys
sys.path.insert(0, '/app')
from api.database import get_async_session
from sqlalchemy import select, delete
from models.knowledge_base import KnowledgeBase

async def delete_old_articles():
    async with get_async_session() as db:
        # Get all articles
        result = await db.execute(select(KnowledgeBase))
        articles = result.scalars().all()

        deleted_count = 0
        for article in articles:
            content = article.content.strip()

            # Check if content starts with ```json or {
            is_json_wrapped = (
                content.startswith('```json') or
                content.startswith('```') or
                content.startswith('{')
            )

            if is_json_wrapped:
                print(f'Deleting article: {article.title} (ID: {article.id})')
                await db.delete(article)
                deleted_count += 1

        if deleted_count > 0:
            await db.commit()
            print(f'\n✅ Deleted {deleted_count} old KB articles with JSON wrapper')
        else:
            print('No old articles found to delete')

if __name__ == '__main__':
    asyncio.run(delete_old_articles())
