"""
Language API routes.

Provides endpoints for retrieving supported languages and their configurations.
"""

from fastapi import APIRouter
from typing import List, Dict, Any

from api.schemas.responses import SuccessResponse
from services.language_service import get_supported_languages

router = APIRouter(prefix="/languages", tags=["languages"])


@router.get("", response_model=SuccessResponse)
async def list_languages() -> SuccessResponse:
    """
    Get list of supported languages.
    
    Returns all languages configured in the system with their:
    - Language code (e.g., 'en-US', 'es-ES')
    - Display name (e.g., 'English (United States)')
    - Native name (e.g., 'English', 'Español')
    - SoundHound model identifier
    
    This endpoint is used by the frontend to populate language selectors
    and validate language codes.
    
    Returns:
        SuccessResponse containing list of language configurations
    
    Example:
        >>> GET /api/languages
        {
            "success": true,
            "data": [
                {
                    "code": "en-US",
                    "name": "English (United States)",
                    "native_name": "English",
                    "soundhound_model": "en-US-v3.2"
                },
                {
                    "code": "es-ES",
                    "name": "Spanish (Spain)",
                    "native_name": "Español",
                    "soundhound_model": "es-ES-v2.8"
                }
            ]
        }
    """
    languages = get_supported_languages()
    return SuccessResponse(data=languages)

