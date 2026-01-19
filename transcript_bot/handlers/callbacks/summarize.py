"""Handle summarize callback."""

import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from ...utils import get_user_language, temp_transcripts
from ...utils.summarizer import summarize_text
from ...i18n import t

logger = logging.getLogger(__name__)


async def handle_summarize_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle summarize button clicks."""
    query = update.callback_query
    await query.answer()

    # Extract transcript ID from callback
    parts = query.data.split("_", 2)
    transcript_id = parts[2] if len(parts) > 2 else None

    if not transcript_id:
        await query.edit_message_text(t("messages.invalid_id", "es"))
        return

    # Get transcript from temporary storage
    if transcript_id not in temp_transcripts:
        await query.edit_message_text(t("messages.expired", "es"))
        return

    transcript_data = temp_transcripts[transcript_id]
    text = transcript_data["text"]
    user_lang = transcript_data["language"]

    # Show summary immediately
    await query.edit_message_text(t("transcription.generating_summary", user_lang))

    # Generate summary
    summary = summarize_text(text, user_lang)

    if summary:
        # Create keyboard for full transcript
        keyboard = [[InlineKeyboardButton(
            t("transcription.full_transcript_button", user_lang),
            callback_data=f"transcript_full_{transcript_id}"
        )]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"📝 **Summary:**\n\n{summary}",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text(t("transcription.no_speech", user_lang))
