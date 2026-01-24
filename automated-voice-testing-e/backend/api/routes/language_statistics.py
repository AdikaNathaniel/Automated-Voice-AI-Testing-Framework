"""
Language statistics API endpoints.
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.database import get_db
from services.language_statistics_service import LanguageStatisticsService

router = APIRouter(prefix="/languages", tags=["Languages"])


@router.get(
    "/stats",
    summary="Get language validation statistics",
    response_model=Dict[str, Any],
)
def get_language_statistics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Retrieve aggregated validation metrics for each supported language.

    Returns:
        JSON payload containing total languages and detailed statistics list.
    """
    try:
        service = LanguageStatisticsService(db)
        stats = service.get_language_statistics()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    return {
        "total_languages": len(stats),
        "languages": stats,
    }
