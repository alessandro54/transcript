"""Message handlers."""

from .voice import handle_voice
from .audio import handle_audio
from .video_note import handle_video_note

__all__ = ["handle_voice", "handle_audio", "handle_video_note"]
