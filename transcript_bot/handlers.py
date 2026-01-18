"""Message handlers for the transcription bot."""

import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from .utils import transcribe_message, LANGUAGES, set_user_language, get_user_language

logger = logging.getLogger(__name__)

# Supported audio formats for transcription
SUPPORTED_FORMATS = {
    'audio/mpeg',      # MP3
    'audio/wav',       # WAV
    'audio/x-wav',     # WAV variant
    'audio/ogg',       # OGG (Telegram voice messages)
    'audio/x-m4a',     # M4A
    'audio/mp4',       # M4A/MP4 audio
    'audio/aac',       # AAC
    'audio/x-aac',     # AAC variant
    'audio/flac',      # FLAC
    'audio/opus',      # OPUS
    'audio/x-opus',    # OPUS variant
}

# Supported MIME types for video notes (converted to audio)
VIDEO_NOTE_FORMATS = {
    'video/mp4',       # Telegram video notes
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    user_lang = get_user_language(update.effective_user.id)
    current_lang = LANGUAGES.get(user_lang, '🇪🇸 Spanish')

    await update.message.reply_text(
        "🎙️ *Audio Transcription Bot*\n\n"
        "Send me a voice message or audio file and I'll transcribe it for you.\n\n"
        "*Supported formats:*\n"
        "• Voice messages 🎤\n"
        "• MP3, WAV, OGG, OPUS, M4A, AAC, FLAC 📁\n"
        "• Video notes (circular videos) 📹\n\n"
        "*Current language:* " + current_lang + "\n"
        "Use /setlang to change language\n\n"
        "*Limits:*⏱️\n"
        "• Maximum duration: 2 minutes\n\n"
        "*Tips for better accuracy:*\n"
        "• Speak clearly and close to the mic\n"
        "• Use voice messages when possible\n"
        "• Avoid background noise",
        parse_mode='Markdown'
    )


async def setlang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /setlang command."""
    # Create inline keyboard for language selection
    keyboard = [
        [InlineKeyboardButton("🇪🇸 Spanish", callback_data="lang_es")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🌐 *Select your language:*\n\n"
        "Choose the language for transcription:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /command command - show all available commands."""
    user_lang = get_user_language(update.effective_user.id)
    current_lang = LANGUAGES.get(user_lang, '🇪🇸 Spanish')

    await update.message.reply_text(
        "📋 *Available Commands:*\n\n"
        "🏠 /start - Show welcome message and bot info\n"
        "🌐 /setlang - Change transcription language\n"
        "📋 /command - Show this help message\n\n"
        f"*Current Settings:*\n"
        f"🗣️ Language: {current_lang}\n"
        f"⏱️ Max duration: 2 minutes\n\n"
        "*Simply send me:*\n"
        "🎤 Voice message\n"
        "📁 Audio file (MP3, WAV, OGG, etc.)\n"
        "📹 Video note\n\n"
        "_I'll transcribe it for you!_",
        parse_mode='Markdown'
    )


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle voice messages."""
    await transcribe_message(update, context, update.message.voice)


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle audio files with format validation."""
    audio = update.message.audio

    # Check if format is supported
    if audio.mime_type not in SUPPORTED_FORMATS:
        await update.message.reply_text(
            f"❌ Unsupported format: `{audio.mime_type}`\n\n"
            "*Supported formats:*\n"
            "• MP3, WAV, OGG, OPUS, M4A, AAC, FLAC\n"
            "• Voice messages and video notes\n\n"
            "Please convert your audio to one of these formats.",
            parse_mode='Markdown'
        )
        return

    await transcribe_message(update, context, audio)


async def handle_video_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle video notes (circular videos)."""
    # Video notes are always MP4, no need to check format
    await transcribe_message(update, context, update.message.video_note)
