"""Audio transcription module that switches between local and OpenAI based on environment."""

import os

# Determine which transcriber to use
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

if ENVIRONMENT == "production":
    print("🚀 Using OpenAI Whisper API for transcription")
    from .transcriber_openai import transcribe_audio as _transcribe_audio
else:
    print("🔧 Using local Whisper model for transcription")
    from .transcriber_local import transcribe_audio as _transcribe_audio


def transcribe_audio(audio_path: str, language: str | None = None) -> str:
    """
    Transcribe an audio file using the appropriate transcription service.

    Args:
        audio_path: Path to the audio file
        language: Language code (e.g., 'es')

    Returns:
        Transcribed text
    """
    # Both transcribers handle conversion and noise reduction internally
    return _transcribe_audio(audio_path, language)
