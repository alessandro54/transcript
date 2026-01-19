"""Handle video notes (circular videos)."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from ...utils import transcribe_message
from ...utils.logger import log_user_action

logger = logging.getLogger(__name__)


async def handle_video_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle video notes (circular videos)."""
    user = update.effective_user
    video_note = update.message.video_note
    log_user_action(user.id, user.username, "sent video note", f" ({video_note.duration}s if available)")

    # Video notes are always MP4, no need to check format
    await transcribe_message(update, context, update.message.video_note)
