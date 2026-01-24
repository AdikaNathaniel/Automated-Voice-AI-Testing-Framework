"""
Auto-Translation Service

Provides automatic translation functionality using deep-translator library.
Supports multiple translation backends (Google Translate, MyMemory, etc.)
"""

from typing import Dict, List, Optional
import logging
from deep_translator import GoogleTranslator, MyMemoryTranslator

logger = logging.getLogger(__name__)


class AutoTranslationService:
    """Service for automatically translating text between languages"""

    # Map our language codes to deep-translator codes
    SUPPORTED_LANGUAGES = {
        'en-US': 'en',
        'es-ES': 'es',
        'fr-FR': 'fr',
        'de-DE': 'de',
        'it-IT': 'it',
        'pt-BR': 'pt',
        'ja-JP': 'ja',
        'zh-CN': 'zh-CN',
        'ko-KR': 'ko',
        'ar-SA': 'ar',
    }

    @classmethod
    def translate_text(
        cls,
        text: str,
        source_lang: str,
        target_lang: str,
        backend: str = 'google'
    ) -> Optional[str]:
        """
        Translate text from source language to target language.

        Args:
            text: Text to translate
            source_lang: Source language code (e.g., 'en-US')
            target_lang: Target language code (e.g., 'es-ES')
            backend: Translation backend ('google' or 'mymemory')

        Returns:
            Translated text or None if translation fails

        Example:
            >>> AutoTranslationService.translate_text(
            ...     "Hello world",
            ...     "en-US",
            ...     "es-ES"
            ... )
            "Hola mundo"
        """
        try:
            # Convert language codes (e.g., 'en-US' -> 'en')
            source = cls.SUPPORTED_LANGUAGES.get(source_lang, source_lang[:2])
            target = cls.SUPPORTED_LANGUAGES.get(target_lang, target_lang[:2])

            # Skip if source and target are the same
            if source == target:
                return text

            # Choose translator backend
            if backend == 'google':
                translator = GoogleTranslator(source=source, target=target)
            else:
                translator = MyMemoryTranslator(source=source, target=target)

            # Translate
            result = translator.translate(text)
            logger.info(f"Translated '{text[:50]}...' from {source} to {target}")
            return result

        except Exception as e:
            logger.error(f"Translation failed from {source_lang} to {target_lang}: {e}")
            return None

    @classmethod
    def auto_translate_step(
        cls,
        source_utterance: str,
        source_lang: str,
        target_languages: List[str],
        backend: str = 'google'
    ) -> Dict[str, Dict[str, str]]:
        """
        Auto-translate a scenario step's user utterance to multiple languages.

        Note: Expected response is now managed at the ExpectedOutcome level,
        not at the step level. Use auto_translate_expected_content() for that.

        Args:
            source_utterance: User utterance in source language
            source_lang: Source language code (e.g., 'en-US')
            target_languages: List of target language codes
            backend: Translation backend to use

        Returns:
            Dictionary mapping language codes to translations

        Example:
            >>> AutoTranslationService.auto_translate_step(
            ...     "What's the weather?",
            ...     "en-US",
            ...     ["es-ES", "fr-FR"]
            ... )
            {
                "en-US": {
                    "language_code": "en-US",
                    "user_utterance": "What's the weather?"
                },
                "es-ES": {
                    "language_code": "es-ES",
                    "user_utterance": "¿Cómo está el clima?"
                },
                "fr-FR": {
                    "language_code": "fr-FR",
                    "user_utterance": "Quel temps fait-il?"
                }
            }
        """
        translations = {}

        # Always include source language
        translations[source_lang] = {
            'language_code': source_lang,
            'user_utterance': source_utterance
        }

        # Translate to each target language
        for target_lang in target_languages:
            if target_lang == source_lang:
                continue

            # Translate utterance
            translated_utterance = cls.translate_text(
                source_utterance,
                source_lang,
                target_lang,
                backend
            )

            if translated_utterance:
                translations[target_lang] = {
                    'language_code': target_lang,
                    'user_utterance': translated_utterance
                }
                logger.info(f"Successfully translated to {target_lang}")
            else:
                logger.warning(f"Failed to translate to {target_lang}")

        return translations

    @classmethod
    def auto_translate_expected_content(
        cls,
        source_content: str,
        source_lang: str,
        target_languages: List[str],
        backend: str = 'google'
    ) -> Dict[str, str]:
        """
        Translate expected response content patterns to multiple languages.

        Use this to create language-specific expected_response_content for ExpectedOutcome.

        Args:
            source_content: Expected content pattern in source language
            source_lang: Source language code (e.g., 'en-US')
            target_languages: List of target language codes
            backend: Translation backend to use

        Returns:
            Dictionary mapping language codes to translated content
        """
        translations = {source_lang: source_content}

        for target_lang in target_languages:
            if target_lang == source_lang:
                continue

            translated = cls.translate_text(
                source_content,
                source_lang,
                target_lang,
                backend
            )

            if translated:
                translations[target_lang] = translated

        return translations

