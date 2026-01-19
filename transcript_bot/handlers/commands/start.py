"""Handle the /start command."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from ...utils import LANGUAGES, get_user_language
from ...utils.logger import log_user_action
from ...i18n import t

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    user = update.effective_user
    log_user_action(user.id, user.username, "started bot", f" ({user.first_name})")

    user_lang = get_user_language(update.effective_user.id)
    current_lang = LANGUAGES.get(user_lang, '🇪🇸 Spanish')

    try:
        await update.message.reply_text(
            t("commands.start.welcome", user_lang, current_lang=current_lang),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Failed to send start message: {e}")
        await update.message.reply_text(t("commands.start.error", user_lang))
