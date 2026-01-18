"""Local Whisper transcription module for development."""

import os
from faster_whisper import WhisperModel

# Global transcriber instance
_transcriber = None


def get_transcriber():
    """Get or create the local Whisper transcriber."""
    global _transcriber
    if _transcriber is None:
        model_size = os.getenv("WHISPER_MODEL", "base")
        device = os.getenv("WHISPER_DEVICE", "auto")

        if device == "auto":
            compute_type = "int8"
        elif device == "cuda":
            compute_type = "float16"
        else:
            compute_type = "int8"

        print(f"Loading local Whisper model: {model_size} on {device}")
        _transcriber = WhisperModel(
            model_size,
            device=device if device != "auto" else "cpu",
            compute_type=compute_type,
        )
        print("Local Whisper model loaded successfully!")

    return _transcriber


def transcribe_audio(audio_path: str, language: str | None = None) -> str:
    """
    Transcribe audio using local Whisper model.

    Args:
        audio_path: Path to the audio file
        language: Language code (e.g., 'es')

    Returns:
        Transcribed text
    """
    transcriber = get_transcriber()

    segments, info = transcriber.transcribe(
        audio_path,
        language=language,
        beam_size=5,
    )

    text_parts = [segment.text for segment in segments]
    return "".join(text_parts).strip()
