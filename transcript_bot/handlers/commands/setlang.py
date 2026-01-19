"""Handle the /setlang command."""

import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from ...utils import LANGUAGES, set_user_language, get_user_language
from ...utils.logger import log_user_action
from ...i18n import t

logger = logging.getLogger(__name__)


async def setlang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /setlang command."""
    user = update.effective_user
    log_user_action(user.id, user.username, "requested language change")

    user_lang = get_user_language(user.id)

    # Create inline keyboard for language selection
    keyboard = [
        [InlineKeyboardButton("🇪🇸 Spanish", callback_data="lang_es")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await update.message.reply_text(
            t("commands.setlang.select", user_lang),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Failed to send language selection: {e}")
        await update.message.reply_text(t("commands.setlang.error", user_lang))
