"""Language callback handlers for the transcription bot."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from utils import set_user_language, LANGUAGES

logger = logging.getLogger(__name__)


async def handle_language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle language selection button clicks."""
    query = update.callback_query
    await query.answer()

    # Extract language from callback data
    lang_code = query.data.replace("lang_", "")

    if lang_code in LANGUAGES:
        # Set user's language preference
        set_user_language(update.effective_user.id, lang_code)

        # Get language name for confirmation
        lang_name = LANGUAGES[lang_code]

        # Update the message to show confirmation
        await query.edit_message_text(
            f"✅ *Language set to: {lang_name}*\n\n"
            f"Now I will transcribe your audio messages in {lang_name.split(' ', 1)[1]}.\n\n"
            "Send me a voice message or use /setlang to change again.",
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text("❌ Invalid language selection.")
