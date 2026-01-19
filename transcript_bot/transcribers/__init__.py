"""Transcription engines."""

from .transcriber import transcribe_audio
from .transcriber_local import transcribe_audio as transcribe_local
from .transcriber_openai import transcribe_audio as transcribe_openai

__all__ = [
    "transcribe_audio",
    "transcribe_local",
    "transcribe_openai"
]
