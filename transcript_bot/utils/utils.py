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

from ..transcribers import transcribe_audio as _transcribe_audio
from ..db import save_transcription, save_user_setting
from .logger import log_transcription, log_api_call
from .summarizer import summarize_text
from ..i18n import t

logger = logging.getLogger(__name__)
executor = ThreadPoolExecutor(max_workers=2)

# Check environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

# Global processing lock
processing_lock = asyncio.Lock()
is_processing = False

# Store failed transcriptions for retry
failed_transcriptions = {}

# Store temporary transcripts for button callbacks
temp_transcripts = {}

# Maximum duration in seconds (30 minutes)
MAX_DURATION = 1800

# Supported audio formats for transcription
SUPPORTED_FORMATS = {
    'audio/mpeg',      # MP3
    'audio/wav',       # WAV
    'audio/x-wav',     # WAV variant
    'audio/ogg',       # OGG (Telegram voice messages)
    'audio/x-m4a',     # M4A
    'audio/mp4',       # M4A/MP4 audio
    'audio/aac',       # AAC
    'audio/x-aac',     # AAC variant
    'audio/flac',      # FLAC
    'audio/opus',      # OPUS
    'audio/x-opus',    # OPUS variant
}

# Supported MIME types for video notes (converted to audio)
VIDEO_NOTE_FORMATS = {
    'video/mp4',       # Telegram video notes
}

# User language preferences cache (fallback)
user_languages_cache = {}

# Available languages
LANGUAGES = {
    'es': '🇪🇸 Spanish',
    'en': '🇬🇧 English',
}


def get_user_language(user_id: int) -> str:
    """Get user's preferred language, default to Spanish."""
    # Check cache first
    if str(user_id) in user_languages_cache:
        return user_languages_cache[str(user_id)]

    # Try to get from database
    try:
        import sqlite3
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        cursor.execute('SELECT language FROM user_settings WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            lang = result[0]
            user_languages_cache[str(user_id)] = lang
            return lang
    except Exception as e:
        logger.error(f"Failed to get language from DB: {e}")

    # Default to Spanish
    return 'es'


def set_user_language(user_id: int, language: str) -> None:
    """Set user's preferred language."""
    try:
        save_user_setting(user_id, language)
        # Update cache
        user_languages_cache[str(user_id)] = language
    except Exception as e:
        logger.error(f"Failed to save language setting: {e}")


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
    global is_processing

    # Check if already processing
    if is_processing:
        user_lang = get_user_language(update.effective_user.id)
        await update.message.reply_text(
            t("commands.transcription.busy", user_lang),
            reply_to_message_id=update.message.message_id
        )
        return

    # Acquire lock
    async with processing_lock:
        is_processing = True
        tmp_path = None
        try:
            user = update.effective_user
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action="typing",
            )

            file = await context.bot.get_file(media.file_id)
            filename = f"{media.file_id}.ogg"

            with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
                tmp_path = tmp.name

            await file.download_to_drive(tmp_path)

            # Check duration
            duration = get_audio_duration(tmp_path)
            user_lang = get_user_language(update.effective_user.id)

            if duration > MAX_DURATION:
                os.unlink(tmp_path)
                log_transcription(user.id, user.username, filename, duration, "unknown", "error: too long")
                await update.message.reply_text(
                    t("commands.transcription.too_long", user_lang,
                      duration=duration,
                      max_duration=MAX_DURATION // 60),
                    reply_to_message_id=update.message.message_id
                )
                return

            # Send processing message
            processing_message = await update.message.reply_text(
                t("commands.transcription.processing", user_lang),
                reply_to_message_id=update.message.message_id
            )

            # Log transcription start
            log_transcription(user.id, user.username, filename, duration, user_lang, "processing")

            # Track transcription time
            start_time = datetime.now()

            # Run transcription
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(
                executor, lambda: _transcribe_audio(tmp_path, language=user_lang)
            )

            os.unlink(tmp_path)

            # Calculate duration
            transcription_time = (datetime.now() - start_time).total_seconds()

            # Clean up old failed transcriptions (older than 5 minutes)
            cleanup_old_files()

            if text:
                # Save to database
                try:
                    audio_type = None
                    if hasattr(media, 'mime_type'):
                        audio_type = media.mime_type
                    elif hasattr(media, 'voice'):
                        audio_type = 'voice/ogg'
                    elif hasattr(media, 'video_note'):
                        audio_type = 'video_note/mp4'

                    save_transcription(
                        user_id=update.effective_user.id,
                        text=text,
                        language=user_lang,
                        duration_seconds=duration,
                        audio_type=audio_type
                    )
                except Exception as e:
                    logger.error(f"Failed to save to database: {e}")

                # Log success
                log_transcription(user.id, user.username, filename, duration, user_lang, "success")
                log_api_call("whisper", "transcribe", "success", transcription_time)

                # Handle summarization based on duration
                if duration >= 180:  # 3+ minutes - auto summarize
                    await processing_message.edit_text(t("commands.transcription.generating_summary", user_lang))

                    summary = summarize_text(text, user_lang)
                    if summary:
                        # Store transcript temporarily with unique ID
                        transcript_id = str(uuid.uuid4())[:8]
                        temp_transcripts[transcript_id] = {
                            "text": text,
                            "language": user_lang,
                            "timestamp": datetime.now()
                        }

                        # Show summary with buttons
                        keyboard = []

                        # Add button for full transcript
                        keyboard.append([InlineKeyboardButton(
                            t("commands.transcription.full_transcript_button", user_lang),
                            callback_data=f"transcript_full_{transcript_id}"
                        )])

                        reply_markup = InlineKeyboardMarkup(keyboard)

                        message = f"📝 **Summary:**\n\n{summary}"
                        await processing_message.edit_text(message, reply_markup=reply_markup, parse_mode='Markdown')
                    else:
                        # If summary fails, offer full transcript
                        transcript_id = str(uuid.uuid4())[:8]
                        temp_transcripts[transcript_id] = {
                            "text": text,
                            "language": user_lang,
                            "timestamp": datetime.now()
                        }

                        keyboard = [[InlineKeyboardButton(
                            t("commands.transcription.full_transcript_button", user_lang),
                            callback_data=f"transcript_full_{transcript_id}"
                        )]]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await processing_message.edit_text(
                            t("commands.transcription.no_speech", user_lang),
                            reply_markup=reply_markup
                        )

                elif duration >= 60:  # 1-3 minutes - offer summarize button
                    # Store transcript temporarily
                    transcript_id = str(uuid.uuid4())[:8]
                    temp_transcripts[transcript_id] = {
                        "text": text,
                        "language": user_lang,
                        "timestamp": datetime.now()
                    }

                    keyboard = [[InlineKeyboardButton(
                        t("commands.transcription.summarize_button", user_lang),
                        callback_data=f"summarize_short_{transcript_id}"
                    )]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await processing_message.edit_text(text, reply_markup=reply_markup)

                else:  # Less than 1 minute - just transcript
                    await processing_message.edit_text(text)
            else:
                log_transcription(user.id, user.username, filename, duration, user_lang, "error: no speech")
                await processing_message.edit_text(t("commands.transcription.no_speech", user_lang))

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            log_transcription(user.id, user.username, filename, duration if 'duration' in locals() else 0, user_lang if 'user_lang' in locals() else "unknown", "error")

            # Store file for retry
            retry_id = str(uuid.uuid4())[:8]
            retry_data = {
                "chat_id": update.effective_chat.id,
                "message_id": update.message.message_id,
                "timestamp": datetime.now()
            }

            # Only add tmp_path if it exists
            if tmp_path and os.path.exists(tmp_path):
                retry_data["tmp_path"] = tmp_path

            failed_transcriptions[retry_id] = retry_data

            keyboard = [[InlineKeyboardButton(
                t("commands.transcription.retry_button", user_lang),
                callback_data=f"retry_{retry_id}"
            )]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            error_msg = t("commands.transcription.error", user_lang, error=str(e))

            if 'processing_message' in locals():
                await processing_message.edit_text(
                    error_msg,
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(
                    error_msg,
                    reply_markup=reply_markup,
                    reply_to_message_id=update.message.message_id
                )

        finally:
            # Always release the lock
            is_processing = False


def cleanup_old_files() -> None:
    """Clean up files older than 5 minutes."""
    now = datetime.now()
    expired = []

    for retry_id, data in failed_transcriptions.items():
        if now - data["timestamp"] > timedelta(minutes=5):
            expired.append(retry_id)
            # Only try to unlink if tmp_path exists
            if "tmp_path" in data and os.path.exists(data["tmp_path"]):
                try:
                    os.unlink(data["tmp_path"])
                except:
                    pass

    for retry_id in expired:
        del failed_transcriptions[retry_id]

    # Also clean up old temporary transcripts (older than 30 minutes)
    expired_transcripts = []
    for transcript_id, data in temp_transcripts.items():
        if now - data["timestamp"] > timedelta(minutes=30):
            expired_transcripts.append(transcript_id)

    for transcript_id in expired_transcripts:
        del temp_transcripts[transcript_id]
