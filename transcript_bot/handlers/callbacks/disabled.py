"""Handle disabled callback."""

from telegram import Update
from telegram.ext import ContextTypes

from ...utils import get_user_language
from ...i18n import t


async def handle_disabled_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle disabled button clicks."""
    query = update.callback_query
    user_lang = get_user_language(update.effective_user.id)
    await query.answer(t("messages.already_sent", user_lang), show_alert=True)


async def handle_show_full_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle show full transcript button (legacy)."""
    # Redirect to transcript full handler
    from .transcript import handle_transcript_full_callback
    await handle_transcript_full_callback(update, context)
