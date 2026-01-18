"""Utility functions for the transcription bot."""

import asyncio
import logging
import os
import tempfile
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from mutagen import File as MutagenFile

from transcriber import transcribe_audio

logger = logging.getLogger(__name__)
executor = ThreadPoolExecutor(max_workers=2)

# Store failed transcriptions for retry
failed_transcriptions = {}

# Maximum duration in seconds (2 minutes)
MAX_DURATION = 120

# User language preferences (default to Spanish)
user_languages = {}

# Available languages
LANGUAGES = {
    'es': '🇪🇸 Spanish',
    'en': '🇬🇧 English',
}


def get_user_language(user_id: int) -> str:
    """Get user's preferred language, default to Spanish."""
    return user_languages.get(str(user_id), 'es')


def set_user_language(user_id: int, language: str) -> None:
    """Set user's preferred language."""
    user_languages[str(user_id)] = language


def get_audio_duration(file_path: str) -> float:
    """
    Get audio duration in seconds.

    Args:
        file_path: Path to the audio file

    Returns:
        Duration in seconds, or 0 if cannot be determined
    """
    try:
        audio = MutagenFile(file_path)
        if audio is not None and hasattr(audio, 'info'):
            return audio.info.length
    except Exception as e:
        logger.error(f"Error getting duration: {e}")
    return 0


async def transcribe_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    media,
) -> None:
    """Download and transcribe audio from a message."""
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing",
    )

    try:
        file = await context.bot.get_file(media.file_id)

        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            tmp_path = tmp.name

        await file.download_to_drive(tmp_path)

        # Check duration
        duration = get_audio_duration(tmp_path)
        if duration > MAX_DURATION:
            os.unlink(tmp_path)
            await update.message.reply_text(
                f"❌ Audio too long: {duration:.1f} seconds\n\n"
                f"Maximum allowed: {MAX_DURATION // 60} minutes\n\n"
                "Please split your audio into shorter segments."
            )
            return

        loop = asyncio.get_event_loop()
        # Get user's preferred language
        user_lang = get_user_language(update.effective_user.id)
        text = await loop.run_in_executor(
            executor, lambda: transcribe_audio(tmp_path, language=user_lang)
        )

        os.unlink(tmp_path)

        # Clean up old failed transcriptions (older than 5 minutes)
        cleanup_old_files()

        if text:
            await update.message.reply_text(text)
        else:
            await update.message.reply_text("Could not transcribe any speech from the audio.")

    except Exception as e:
        logger.error(f"Transcription error: {e}")
        # Store file for retry
        retry_id = str(uuid.uuid4())[:8]
        failed_transcriptions[retry_id] = {
            "tmp_path": tmp_path,
            "chat_id": update.effective_chat.id,
            "message_id": update.message.message_id,
            "timestamp": datetime.now()
        }

        keyboard = [[InlineKeyboardButton("🔄 Retry Transcription", callback_data=f"retry_{retry_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"❌ Error transcribing audio: {str(e)}\n\n"
            "You can retry using the button below (file kept for 5 minutes):",
            reply_markup=reply_markup
        )


def cleanup_old_files() -> None:
    """Clean up files older than 5 minutes."""
    now = datetime.now()
    expired = []

    for retry_id, data in failed_transcriptions.items():
        if now - data["timestamp"] > timedelta(minutes=5):
            expired.append(retry_id)
            try:
                os.unlink(data["tmp_path"])
            except:
                pass

    for retry_id in expired:
        del failed_transcriptions[retry_id]
