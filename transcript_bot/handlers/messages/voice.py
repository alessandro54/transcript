"""Handle voice messages."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from ...utils import transcribe_message
from ...utils.logger import log_user_action

logger = logging.getLogger(__name__)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle voice messages."""
    user = update.effective_user
    voice = update.message.voice
    log_user_action(user.id, user.username, "sent voice", f" ({voice.duration}s if available)")

    await transcribe_message(update, context, update.message.voice)
