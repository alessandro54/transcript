"""Handle the /history command."""

import logging
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from ...utils import LANGUAGES, get_user_language
from ...db import get_user_history, get_user_stats
from ...utils.logger import log_user_action
from ...i18n import t

logger = logging.getLogger(__name__)


async def history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /history command."""
    user = update.effective_user
    log_user_action(user.id, user.username, "requested history")

    user_lang = get_user_language(user.id)

    try:
        # Get user's transcription history
        history = get_user_history(user.id, limit=10)
        stats = get_user_stats(user.id)

        if not history:
            await update.message.reply_text(
                t("commands.history.empty", user_lang),
                parse_mode='Markdown'
            )
            return

        # Format history message
        message = t("commands.history.title", user_lang)

        # Add statistics
        message += t("commands.history.stats", user_lang,
                    total=stats.get('total_transcriptions', 0),
                    duration=stats.get('total_duration', 0),
                    fav_lang=LANGUAGES.get(stats.get('favorite_language', 'es'), 'Spanish'))

        # Add recent transcriptions
        message += t("commands.history.recent", user_lang)

        for i, item in enumerate(history[:5], 1):
            date = datetime.fromisoformat(item['timestamp']).strftime('%Y-%m-%d %H:%M')
            message += f"{i}. {date} - {item['text'][:50]}...\n"

        await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Failed to send history: {e}")
        await update.message.reply_text(t("commands.history.error", user_lang))
