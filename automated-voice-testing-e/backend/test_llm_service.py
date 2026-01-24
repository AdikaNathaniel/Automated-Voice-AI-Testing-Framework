"""Test script to verify LLM service initialization"""
import asyncio
from api.database import get_async_session
from services.edge_case_similarity_service import EdgeCaseSimilarityService


async def test():
    """Test EdgeCaseSimilarityService with LLM enabled."""
    async with get_async_session() as db:
        svc = EdgeCaseSimilarityService(db, use_llm=True)
        print(f'EdgeCase Service LLM enabled: {svc.use_llm}')
        print(f'LLM service initialized: {svc.llm_service is not None}')
        if svc.llm_service:
            print(f'LLM model: {svc.llm_service.model}')
            print(f'LLM enabled: {svc.llm_service.enabled}')


if __name__ == '__main__':
    asyncio.run(test())
