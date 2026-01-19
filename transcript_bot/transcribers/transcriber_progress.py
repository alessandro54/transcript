"""Enhanced transcriber with progress callback."""

import os
import tempfile
from openai import OpenAI
import noisereduce as nr
import soundfile as sf
import numpy as np
import time
import threading

# Determine which transcriber to use
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

if ENVIRONMENT == "production":
    print("🚀 Using OpenAI Whisper API for transcription")
    from .transcriber_openai import transcribe_audio as _transcribe_audio
else:
    print("🔧 Using local Whisper model for transcription")
    from .transcriber_local import transcribe_audio as _transcribe_audio


def reduce_noise(audio_path: str) -> str:
    """
    Apply noise reduction to audio file.

    Args:
        audio_path: Path to the original audio file

    Returns:
        Path to the cleaned audio file
    """
    try:
        # Load audio
        data, sample_rate = sf.read(audio_path)

        # Reduce noise
        reduced_noise = nr.reduce_noise(y=data, sr=sample_rate)

        # Save cleaned audio
        cleaned_path = audio_path.replace(".ogg", "_cleaned.ogg")
        sf.write(cleaned_path, reduced_noise, sample_rate)

        return cleaned_path
    except Exception as e:
        print(f"Noise reduction failed: {e}")
        return audio_path


def transcribe_with_progress(audio_path: str, language: str = None, progress_callback=None):
    """
    Transcribe audio with progress updates.

    Args:
        audio_path: Path to the audio file
        language: Language code
        progress_callback: Function to call with progress updates

    Returns:
        Transcribed text
    """
    # Get audio duration for realistic timing
    try:
        audio_file = MutagenFile(audio_path)
        duration = getattr(audio_file.info, 'length', 10)  # Default to 10s if unknown
    except:
        duration = 10  # Default duration

    # Calculate expected transcription time (use more conservative estimate)
    expected_time = max(3, duration * 0.6)  # Increased to 0.6x, min 3 seconds

    # For progress tracking
    progress_done = threading.Event()
    current_progress = [0]

    # Simulate progress for local Whisper
    if ENVIRONMENT == "development" and progress_callback:
        # Start progress thread that matches actual transcription time
        def update_progress():
            # Progress steps with timing based on audio duration
            progress_steps = [
                (0, 0.00),    # 0% immediately
                (5, 0.05),    # 5% after 5% of time
                (10, 0.10),   # 10% after 10% of time
                (20, 0.20),   # 20% after 20% of time
                (30, 0.30),   # 30% after 30% of time
                (40, 0.40),   # 40% after 40% of time
                (50, 0.50),   # 50% after 50% of time
                (60, 0.60),   # 60% after 60% of time
                (70, 0.70),   # 70% after 70% of time
                (80, 0.80),   # 80% after 80% of time
                (90, 0.90),   # 90% after 90% of time
                (95, 0.95),   # 95% after 95% of time
                (99, 0.98),   # 99% after 98% of time
            ]

            last_time = 0
            for percent, time_fraction in progress_steps:
                if progress_callback:
                    current_progress[0] = percent
                    progress_callback(percent)

                # Sleep based on expected transcription time
                sleep_time = (time_fraction - last_time) * expected_time
                time.sleep(max(0.1, sleep_time))  # Minimum 0.1s between updates
                last_time = time_fraction

            # Wait at 99% until transcription is actually done
            while not progress_done.is_set():
                time.sleep(0.1)

            # Finally show 100%
            if progress_callback:
                progress_callback(100)

        progress_thread = threading.Thread(target=update_progress)
        progress_thread.start()

    # Do actual transcription
    try:
        result = _transcribe_audio(audio_path, language)
    finally:
        # Signal that transcription is done
        progress_done.set()

    return result


def transcribe_audio(audio_path: str, language: str | None = None) -> str:
    """
    Transcribe audio using the configured backend.

    Args:
        audio_path: Path to the audio file
        language: Optional language code

    Returns:
        Transcribed text
    """
    # Clean audio first
    cleaned_path = reduce_noise(audio_path)

    # Transcribe
    try:
        result = transcribe_with_progress(cleaned_path, language)
        return result
    finally:
        # Clean up temporary file if created
        if cleaned_path != audio_path and os.path.exists(cleaned_path):
            os.unlink(cleaned_path)
