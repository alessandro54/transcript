"""Database functionality."""

from .database import (
    init_database,
    save_transcription,
    get_user_history,
    get_user_stats,
    save_user_setting,
    get_user_setting
)

__all__ = [
    "init_database",
    "save_transcription",
    "get_user_history",
    "get_user_stats",
    "save_user_setting",
    "get_user_setting"
]
