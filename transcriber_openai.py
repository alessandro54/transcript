"""Audio transcription module using OpenAI Whisper API with noise reduction."""

import os
import tempfile
from openai import OpenAI
import noisereduce as nr
import soundfile as sf
import numpy as np

# Global OpenAI client
_client: OpenAI | None = None


def get_client() -> OpenAI:
    """Get or create the OpenAI client."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        _client = OpenAI(api_key=api_key)
    return _client


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
    # Note: For voice messages, we assume the first 0.5 seconds is noise
    # This works well for Telegram voice messages
    if len(data) > rate * 0.5:  # If audio is longer than 0.5 seconds
        noise_sample = data[:int(rate * 0.5)]
        reduced_noise = nr.reduce_noise(y=data, sr=rate, y_noise=noise_sample)
    else:
        # For very short audio, just apply basic reduction
        reduced_noise = nr.reduce_noise(y=data, sr=rate)

    # Save cleaned audio to temporary file
    cleaned_path = audio_path.replace('.ogg', '_cleaned.ogg')
    sf.write(cleaned_path, reduced_noise, rate)

    return cleaned_path


def transcribe_audio(audio_path: str, language: str | None = None) -> str:
    """
    Transcribe an audio file using OpenAI Whisper API with noise reduction.

    Args:
        audio_path: Path to the audio file
        language: Optional language code (e.g., 'en', 'it'). Auto-detected if None.

    Returns:
        Transcribed text
    """
    client = get_client()

    # Apply noise reduction
    try:
        cleaned_path = reduce_noise(audio_path)
        use_path = cleaned_path
    except Exception as e:
        print(f"Noise reduction failed, using original: {e}")
        use_path = audio_path

    # Transcribe
    with open(use_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=language,  # Optional, auto-detect if None
            response_format="text"
        )

    # Clean up temporary file if created
    if use_path != audio_path and os.path.exists(use_path):
        os.unlink(use_path)

    return transcript.strip() if transcript else ""
