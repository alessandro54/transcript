"""Callback handlers for the transcription bot."""

import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from .transcriber import transcribe_audio
from .utils import failed_transcriptions, get_user_language
from .logger import log_user_action, log_transcription, log_api_call

logger = logging.getLogger(__name__)
executor = ThreadPoolExecutor(max_workers=2)


async def handle_retry_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle retry button clicks."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    log_user_action(user.id, user.username, "requested retry transcription")

    retry_id = query.data.replace("retry_", "")

    if retry_id not in failed_transcriptions:
        await query.edit_message_text("❌ Retry expired. Please send the audio again.")
        return

    retry_data = failed_transcriptions[retry_id]
    tmp_path = retry_data["tmp_path"]

    try:
        # Show processing status
        await query.edit_message_text("🔄 Retrying transcription...")

        # Get user language
        user_lang = get_user_language(user.id)

        # Retry transcription
        start_time = datetime.now()
        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(
            executor, lambda: transcribe_audio(tmp_path, language=user_lang)
        )

        # Calculate duration
        transcription_time = (datetime.now() - start_time).total_seconds()

        if text:
            # Log success
            log_transcription(user.id, user.username, "retry_" + retry_id, None, user_lang, "success")
            log_api_call("whisper", "retry_transcribe", "success", transcription_time)

            await query.edit_message_text(f"✅ Transcription successful:\n\n{text}")
        else:
            log_transcription(user.id, user.username, "retry_" + retry_id, None, user_lang, "error: no speech")
            await query.edit_message_text("❌ Could not transcribe any speech from the audio.")

    except Exception as e:
        logger.error(f"Retry transcription error: {e}")
        log_transcription(user.id, user.username, "retry_" + retry_id, None, user_lang, "error")
        await query.edit_message_text(f"❌ Error during retry: {str(e)}")

    finally:
        # Clean up retry data
        if retry_id in failed_transcriptions:
            del failed_transcriptions[retry_id]
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except:
                pass
