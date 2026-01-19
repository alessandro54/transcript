"""Internationalization (i18n) module for the bot."""

import json
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Default language
DEFAULT_LANGUAGE = "es"

# Cache for translations
_translations: Dict[str, Dict[str, str]] = {}

def load_translations() -> None:
    """Load all translation files."""
    # Get absolute path to translations directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    translations_dir = os.path.join(current_dir, "translations")

    # Ensure directory exists
    os.makedirs(translations_dir, exist_ok=True)

    # Load each language file
    for filename in os.listdir(translations_dir):
        if filename.endswith(".json"):
            lang_code = filename[:-5]  # Remove .json extension
            filepath = os.path.join(translations_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    _translations[lang_code] = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load translation file {filename}: {e}")

def get_nested_key(data: dict, key: str) -> str:
    """Get value from nested dictionary using dot notation."""
    keys = key.split('.')
    current = data

    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return None

    return current if isinstance(current, str) else None

def get_translation(key: str, language: str = DEFAULT_LANGUAGE, **kwargs) -> str:
    """
    Get a translated string.

    Args:
        key: Translation key (e.g., "commands.start.welcome")
        language: Language code (e.g., "es", "en")
        **kwargs: Variables to format into the string

    Returns:
        Translated string
    """
    # Load translations if not loaded
    if not _translations:
        load_translations()

    # Get the translation using nested key lookup
    translation = get_nested_key(_translations.get(language, {}), key)

    # Fallback to default language if not found
    if not translation and language != DEFAULT_LANGUAGE:
        translation = get_nested_key(_translations.get(DEFAULT_LANGUAGE, {}), key)

    # Fallback to key if not found
    if not translation:
        translation = key

    # Format with variables
    if kwargs:
        try:
            translation = translation.format(**kwargs)
        except (KeyError, ValueError):
            pass

    return translation

def t(key: str, language: str = DEFAULT_LANGUAGE, **kwargs) -> str:
    """Short alias for get_translation."""
    return get_translation(key, language, **kwargs)

# Load translations on import
load_translations()
