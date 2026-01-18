"""Callback handlers for the transcription bot."""

import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor

from telegram import Update
from telegram.ext import ContextTypes

from .transcriber import transcribe_audio
from .utils import failed_transcriptions

logger = logging.getLogger(__name__)
executor = ThreadPoolExecutor(max_workers=2)


async def handle_retry_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle retry button clicks."""

    query = update.callback_query
    await query.answer()

    retry_id = query.data.replace("retry_", "")

    if retry_id not in failed_transcriptions:
        await query.edit_message_text("❌ Retry expired. Please send the audio again.")
        return

    retry_data = failed_transcriptions[retry_id]
    tmp_path = retry_data["tmp_path"]

    try:
        await context.bot.send_chat_action(
            chat_id=retry_data["chat_id"],
            action="typing",
        )

        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(
            executor, lambda: transcribe_audio(tmp_path, language="es")
        )

        # Clean up
        os.unlink(tmp_path)
        del failed_transcriptions[retry_id]

        if text:
            await query.edit_message_text(f"✅ Transcription successful:\n\n{text}")
        else:
            await query.edit_message_text("❌ Could not transcribe any speech from the audio.")

    except Exception as e:
        logger.error(f"Retry transcription error: {e}")
        await query.edit_message_text(
            f"❌ Retry failed: {str(e)}\n\n"
            "Please send the audio again."
        )
        # Clean up on final failure
        os.unlink(tmp_path)
        del failed_transcriptions[retry_id]
