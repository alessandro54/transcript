"""Audio transcription module that switches between local and OpenAI based on environment."""

import os
import tempfile
from openai import OpenAI
import noisereduce as nr
import soundfile as sf
import numpy as np

# Determine which transcriber to use
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

if ENVIRONMENT == "production":
    print("🚀 Using OpenAI Whisper API for transcription")
    from transcriber_openai import transcribe_audio as _transcribe_audio
else:
    print("🔧 Using local Whisper model for transcription")
    from transcriber_local import transcribe_audio as _transcribe_audio


def reduce_noise(audio_path: str) -> str:
    """
    Apply noise reduction to audio file.

    Args:
        audio_path: Path to the original audio file

    Returns:
        Path to the cleaned audio file
    """
    # Load audio
    data, rate = sf.read(audio_path)

    # Apply noise reduction
    if len(data) > rate * 0.5:  # If audio is longer than 0.5 seconds
        noise_sample = data[:int(rate * 0.5)]
        reduced_noise = nr.reduce_noise(y=data, sr=rate, y_noise=noise_sample)
    else:
        reduced_noise = nr.reduce_noise(y=data, sr=rate)

    # Save cleaned audio to temporary file
    cleaned_path = audio_path.replace('.ogg', '_cleaned.ogg')
    sf.write(cleaned_path, reduced_noise, rate)

    return cleaned_path


def transcribe_audio(audio_path: str, language: str | None = None) -> str:
    """
    Transcribe an audio file using the appropriate transcription service.

    Args:
        audio_path: Path to the audio file
        language: Language code (e.g., 'es')

    Returns:
        Transcribed text
    """
    # Apply noise reduction for OpenAI (local Whisper handles it well)
    if ENVIRONMENT == "production":
        try:
            cleaned_path = reduce_noise(audio_path)
            use_path = cleaned_path
        except Exception as e:
            print(f"Noise reduction failed, using original: {e}")
            use_path = audio_path

        # Transcribe with OpenAI
        result = _transcribe_audio(use_path, language)

        # Clean up temporary file if created
        if use_path != audio_path and os.path.exists(use_path):
            os.unlink(use_path)

        return result
    else:
        # Use local Whisper directly (noise reduction is optional)
        return _transcribe_audio(audio_path, language)
