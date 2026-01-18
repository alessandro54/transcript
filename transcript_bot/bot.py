"""Telegram bot for audio transcription."""

# Load environment variables FIRST before any other imports
from dotenv import load_dotenv
load_dotenv()

import logging
import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from .handlers import start, handle_voice, handle_audio, handle_video_note, setlang, command, history
from .callbacks import handle_retry_callback
from .language_callbacks import handle_language_callback
from .summary_callbacks import handle_summarize_callback, handle_show_full_callback, handle_transcript_full_callback, handle_disabled_callback
from .logger import setup_logging, log_user_action

# Setup enhanced logging
setup_logging()
logger = logging.getLogger(__name__)


def main() -> None:
    """Start the bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")

    application = Application.builder().token(token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setlang", setlang))
    application.add_handler(CommandHandler("command", command))
    application.add_handler(CommandHandler("history", history))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    application.add_handler(MessageHandler(filters.VIDEO_NOTE, handle_video_note))
    application.add_handler(CallbackQueryHandler(handle_retry_callback, pattern=r"^retry_"))
    application.add_handler(CallbackQueryHandler(handle_language_callback, pattern=r"^lang_"))
    application.add_handler(CallbackQueryHandler(handle_summarize_callback, pattern=r"^summarize_"))
    application.add_handler(CallbackQueryHandler(handle_transcript_full_callback, pattern=r"^transcript_full_"))
    application.add_handler(CallbackQueryHandler(handle_show_full_callback, pattern=r"^show_full_"))
    application.add_handler(CallbackQueryHandler(handle_disabled_callback, pattern=r"^sent_disabled$"))

    logger.info("Bot started")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
