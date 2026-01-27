"""Handle full transcript callback."""

import logging
import os
import tempfile
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from ...utils import get_user_language, temp_transcripts
from ...i18n import t

logger = logging.getLogger(__name__)


async def handle_transcript_full_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle full transcript button - creates and sends text file."""
    query = update.callback_query
    await query.answer()

    # Extract transcript ID from callback
    parts = query.data.split("_", 2)
    transcript_id = parts[2] if len(parts) > 2 else None

    if not transcript_id:
        await query.edit_message_text(t("commands.messages.invalid_id", "es"))
        return

    # Get transcript from temporary storage
    if transcript_id not in temp_transcripts:
        await query.edit_message_text(t("commands.messages.expired", "es"))
        return

    transcript_data = temp_transcripts[transcript_id]
    text = transcript_data["text"]
    user_lang = transcript_data["language"]

    # Get current message text to preserve it
    current_text = query.message.text

    # Create text file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(f"Transcription - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Language: {user_lang}\n\n")
        f.write("FULL TRANSCRIPT:\n\n")
        f.write(text)
        temp_path = f.name

    # Send file
    with open(temp_path, 'rb') as f:
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=f,
            filename="transcription.txt",
            caption=t("commands.messages.file_caption", user_lang)
        )

    # Clean up
    os.unlink(temp_path)

    # Update button to show it was sent, but keep the summary
    keyboard = [[InlineKeyboardButton(
        t("commands.transcription.sent_button", user_lang),
        callback_data="sent_disabled"
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        current_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
