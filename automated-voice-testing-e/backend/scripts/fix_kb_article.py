"""Fix KB article content by extracting markdown from JSON wrapper"""
import asyncio
import sys
import json
import re
sys.path.insert(0, '/app')
from api.database import get_async_session
from sqlalchemy import select
from models.knowledge_base import KnowledgeBase
from uuid import UUID

async def fix_article():
    async with get_async_session() as db:
        result = await db.execute(
            select(KnowledgeBase).where(KnowledgeBase.id == UUID('383f2e87-9f8e-47aa-99dc-7330b13af0b2'))
        )
        article = result.scalar_one_or_none()

        if not article:
            print('Article not found')
            return

        content = article.content

        # Remove markdown code block if present
        if content.startswith('```'):
            # Remove opening ```json or ```
            content = re.sub(r'^```(json)?\n', '', content)
            # Remove closing ```
            content = re.sub(r'\n```$', '', content)

        # Parse the JSON and extract article content
        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict) and 'article' in parsed:
                markdown_content = parsed['article']
                article.content = markdown_content
                await db.commit()
                print(f'✅ Fixed article content ({len(markdown_content)} chars)')
                print('Preview (first 200 chars):')
                print(markdown_content[:200])
            else:
                print('❌ Content is not in expected JSON format')
                print('Keys found:', list(parsed.keys()) if isinstance(parsed, dict) else 'not a dict')
        except json.JSONDecodeError as e:
            print(f'❌ Failed to parse JSON: {e}')
            print('Content preview after cleanup:')
            print(content[:300])

if __name__ == '__main__':
    asyncio.run(fix_article())
