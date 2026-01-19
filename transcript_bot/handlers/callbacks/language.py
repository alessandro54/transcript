"""Handle language selection callback."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from ...utils import set_user_language, LANGUAGES, get_user_language
from ...i18n import t

logger = logging.getLogger(__name__)


async def handle_language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle language selection from inline keyboard."""
    query = update.callback_query
    await query.answer()

    # Extract language code from callback data
    lang_code = query.data.split("_")[1]

    if lang_code in LANGUAGES:
        # Update user's language preference
        user_id = update.effective_user.id
        set_user_language(user_id, lang_code)
        lang_name = LANGUAGES[lang_code]

        try:
            await query.edit_message_text(
                t("commands.setlang.changed", lang_code, lang_name=lang_name),
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Failed to update language confirmation: {e}")
            await query.edit_message_text(t("commands.setlang.error", lang_code))
    else:
        logger.error(f"Invalid language code: {lang_code}")
        await query.edit_message_text(t("commands.setlang.error", "es"))
