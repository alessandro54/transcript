"""Handle the /command command."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from ...utils import get_user_language
from ...utils.logger import log_user_action
from ...i18n import t

logger = logging.getLogger(__name__)


async def command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /command command."""
    user = update.effective_user
    log_user_action(user.id, user.username, "requested commands")

    user_lang = get_user_language(user.id)

    try:
        await update.message.reply_text(
            t("commands.command.list", user_lang),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Failed to send command list: {e}")
        await update.message.reply_text(t("commands.command.error", user_lang))
