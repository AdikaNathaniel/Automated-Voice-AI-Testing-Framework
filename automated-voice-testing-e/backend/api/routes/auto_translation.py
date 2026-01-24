"""
Auto-Translation API Routes

Provides endpoints for automatic translation of text and scenario steps.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict

from services.auto_translation_service import AutoTranslationService
from api.schemas.responses import SuccessResponse

router = APIRouter(prefix="/auto-translation", tags=["auto-translation"])


class TranslateTextRequest(BaseModel):
    """Request model for translating a single text"""
    text: str = Field(..., description="Text to translate")
    source_lang: str = Field(..., description="Source language code (e.g., 'en-US')")
    target_lang: str = Field(..., description="Target language code (e.g., 'es-ES')")
    backend: str = Field(default='google', description="Translation backend ('google' or 'mymemory')")


class AutoTranslateStepRequest(BaseModel):
    """Request model for auto-translating a scenario step"""
    user_utterance: str = Field(..., description="User utterance in source language")
    expected_response: str = Field(default="", description="Expected response in source language (optional)")
    source_lang: str = Field(..., description="Source language code (e.g., 'en-US')")
    target_languages: List[str] = Field(..., description="List of target language codes")
    backend: str = Field(default='google', description="Translation backend to use")


@router.post("/translate-text")
async def translate_text(request: TranslateTextRequest):
    """
    Translate a single text from source to target language.
    
    Args:
        request: Translation request with text and language codes
        
    Returns:
        SuccessResponse with translated text
        
    Raises:
        HTTPException: If translation fails
        
    Example:
        POST /api/v1/auto-translation/translate-text
        {
            "text": "Hello world",
            "source_lang": "en-US",
            "target_lang": "es-ES"
        }
        
        Response:
        {
            "success": true,
            "data": {
                "translated_text": "Hola mundo"
            }
        }
    """
    result = AutoTranslationService.translate_text(
        request.text,
        request.source_lang,
        request.target_lang,
        request.backend
    )
    
    if result is None:
        raise HTTPException(
            status_code=500,
            detail=f"Translation failed from {request.source_lang} to {request.target_lang}"
        )
    
    return SuccessResponse(data={"translated_text": result})


@router.post("/auto-translate-step")
async def auto_translate_step(request: AutoTranslateStepRequest):
    """
    Auto-translate a scenario step to multiple languages.
    
    Args:
        request: Auto-translation request with utterance, response, and target languages
        
    Returns:
        SuccessResponse with translations for all languages
        
    Example:
        POST /api/v1/auto-translation/auto-translate-step
        {
            "user_utterance": "What's the weather?",
            "expected_response": "It's sunny, 72 degrees",
            "source_lang": "en-US",
            "target_languages": ["es-ES", "fr-FR", "de-DE"]
        }
        
        Response:
        {
            "success": true,
            "data": {
                "translations": {
                    "en-US": {
                        "user_utterance": "What's the weather?",
                        "expected_response": "It's sunny, 72 degrees"
                    },
                    "es-ES": {
                        "user_utterance": "¿Cómo está el clima?",
                        "expected_response": "Está soleado, 72 grados"
                    },
                    "fr-FR": {
                        "user_utterance": "Quel temps fait-il?",
                        "expected_response": "Il fait beau, 22 degrés"
                    }
                }
            }
        }
    """
    translations = AutoTranslationService.auto_translate_step(
        request.user_utterance,
        request.source_lang,
        request.target_languages,
        request.backend
    )
    
    return SuccessResponse(data={"translations": translations})


@router.get("/supported-languages")
async def get_supported_languages():
    """
    Get list of supported language codes.
    
    Returns:
        SuccessResponse with list of supported language codes
        
    Example:
        GET /api/v1/auto-translation/supported-languages
        
        Response:
        {
            "success": true,
            "data": {
                "languages": ["en-US", "es-ES", "fr-FR", ...]
            }
        }
    """
    languages = list(AutoTranslationService.SUPPORTED_LANGUAGES.keys())
    return SuccessResponse(data={"languages": languages})

