"""Audio transcription module using OpenAI Whisper API with noise reduction."""

import os
import tempfile
from openai import OpenAI
import noisereduce as nr
import soundfile as sf
import numpy as np
import av

# Global OpenAI client
_client: OpenAI | None = None


def convert_to_wav(input_path: str) -> str:
    """
    Convert audio file to WAV format using PyAV.

    Args:
        input_path: Path to the input audio file

    Returns:
        Path to the converted WAV file
    """
    output_path = tempfile.mktemp(suffix=".wav")

    input_container = av.open(input_path)
    output_container = av.open(output_path, mode='w')

    # Get audio stream
    input_stream = input_container.streams.audio[0]

    # Create output stream (16kHz mono WAV - optimal for Whisper)
    output_stream = output_container.add_stream('pcm_s16le', rate=16000)
    output_stream.layout = 'mono'

    # Create resampler
    resampler = av.AudioResampler(
        format='s16',
        layout='mono',
        rate=16000,
    )

    for frame in input_container.decode(audio=0):
        # Resample frame
        resampled_frames = resampler.resample(frame)
        for resampled_frame in resampled_frames:
            for packet in output_stream.encode(resampled_frame):
                output_container.mux(packet)

    # Flush encoder
    for packet in output_stream.encode():
        output_container.mux(packet)

    output_container.close()
    input_container.close()

    return output_path


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

    # Save cleaned audio to temporary WAV file
    cleaned_path = tempfile.mktemp(suffix="_cleaned.wav")
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
    wav_path = None
    cleaned_path = None

    try:
        # Convert to WAV first (handles OGG Opus and other formats)
        wav_path = convert_to_wav(audio_path)
        use_path = wav_path

        # Apply noise reduction
        try:
            cleaned_path = reduce_noise(wav_path)
            use_path = cleaned_path
        except Exception as e:
            print(f"Noise reduction failed, using converted file: {e}")

        # Transcribe
        with open(use_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,  # Optional, auto-detect if None
                response_format="text"
            )

        return transcript.strip() if transcript else ""

    finally:
        # Clean up temporary files
        if wav_path and os.path.exists(wav_path):
            os.unlink(wav_path)
        if cleaned_path and os.path.exists(cleaned_path):
            os.unlink(cleaned_path)
