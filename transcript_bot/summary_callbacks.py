"""Callback handlers for summarization feature."""

import logging
import tempfile
import os
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from .summarizer import summarize_text

logger = logging.getLogger(__name__)


async def handle_summarize_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle summarize button clicks."""
    query = update.callback_query
    await query.answer()

    # Extract transcript ID from callback
    parts = query.data.split("_", 2)
    transcript_id = parts[2] if len(parts) > 2 else None

    if not transcript_id:
        await query.edit_message_text("❌ Error: Invalid transcript ID")
        return

    # Get transcript from temporary storage
    from .utils import temp_transcripts
    if transcript_id not in temp_transcripts:
        await query.edit_message_text("❌ Error: Transcript expired. Please send the audio again.")
        return

    transcript_data = temp_transcripts[transcript_id]
    text = transcript_data["text"]
    user_lang = transcript_data["language"]

    # Show summary immediately
    await query.edit_message_text("📝 **Generating summary...**")

    # Generate summary
    summary = summarize_text(text, user_lang)

    if summary:
        # Create keyboard for full transcript
        keyboard = [[InlineKeyboardButton("📄 Full Transcript", callback_data=f"transcript_full_{transcript_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"📝 **Summary:**\n\n{summary}",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text("❌ Failed to generate summary.")


async def handle_transcript_full_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle full transcript button - creates and sends text file."""
    query = update.callback_query
    await query.answer()

    # Extract transcript ID from callback
    parts = query.data.split("_", 2)
    transcript_id = parts[2] if len(parts) > 2 else None

    if not transcript_id:
        await query.edit_message_text("❌ Error: Invalid transcript ID")
        return

    # Get transcript from temporary storage
    from .utils import temp_transcripts
    if transcript_id not in temp_transcripts:
        await query.edit_message_text("❌ Error: Transcript expired. Please send the audio again.")
        return

    transcript_data = temp_transcripts[transcript_id]
    text = transcript_data["text"]
    user_lang = transcript_data["language"]

    # Get current message text to preserve it
    current_text = query.message.text

    # Create text file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(f"Transcription - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Language: {user_lang}\n\n")
        f.write("FULL TRANSCRIPT:\n\n")
        f.write(text)
        temp_path = f.name

    # Send file
    with open(temp_path, 'rb') as f:
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=f,
            filename="transcription.txt",
            caption="📄 Full transcription"
        )

    # Clean up
    os.unlink(temp_path)

    # Update button to show it was sent, but keep the summary
    keyboard = [[InlineKeyboardButton("✅ Transcript Sent", callback_data="sent_disabled")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        current_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def handle_show_full_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle show full transcript button (legacy)."""
    # Redirect to transcript full handler
    await handle_transcript_full_callback(update, context)


async def handle_disabled_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle disabled button clicks."""
    query = update.callback_query
    await query.answer("Transcript already sent!", show_alert=True)
