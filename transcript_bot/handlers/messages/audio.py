"""Handle audio files with format validation."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from ...utils import transcribe_message, get_user_language, SUPPORTED_FORMATS
from ...utils.logger import log_user_action
from ...i18n import t

logger = logging.getLogger(__name__)


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle audio files with format validation."""
    user = update.effective_user
    audio = update.message.audio
    user_lang = get_user_language(user.id)

    # Check if format is supported
    if audio.mime_type not in SUPPORTED_FORMATS:
        log_user_action(user.id, user.username, "sent unsupported audio", f" ({audio.mime_type})")
        await update.message.reply_text(
            t("commands.transcription.unsupported_format", user_lang, mime_type=audio.mime_type),
            parse_mode='Markdown'
        )
        return

    log_user_action(user.id, user.username, "sent audio", f" ({audio.mime_type}, {audio.file_name})")
    await transcribe_message(update, context, audio)
