"""Database module for storing user transcription history."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Database file path
DB_PATH = Path("bot.db")

def init_database() -> None:
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create transcriptions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transcriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            language TEXT,
            duration_seconds REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            audio_type TEXT
        )
    ''')

    # Create user settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id INTEGER PRIMARY KEY,
            language TEXT DEFAULT 'es',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")

def save_transcription(
    user_id: int,
    text: str,
    language: str,
    duration_seconds: float = None,
    audio_type: str = None
) -> None:
    """Save a transcription to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO transcriptions (user_id, text, language, duration_seconds, audio_type)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, text, language, duration_seconds, audio_type))

    conn.commit()
    conn.close()

def get_user_history(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """Get user's transcription history."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT text, language, duration_seconds, timestamp, audio_type
        FROM transcriptions
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (user_id, limit))

    columns = ['text', 'language', 'duration_seconds', 'timestamp', 'audio_type']
    history = [dict(zip(columns, row)) for row in cursor.fetchall()]

    conn.close()
    return history

def get_user_stats(user_id: int) -> Dict[str, Any]:
    """Get user's transcription statistics."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Total transcriptions
    cursor.execute('SELECT COUNT(*) FROM transcriptions WHERE user_id = ?', (user_id,))
    total_count = cursor.fetchone()[0]

    # Total duration
    cursor.execute(
        'SELECT SUM(duration_seconds) FROM transcriptions WHERE user_id = ? AND duration_seconds IS NOT NULL',
        (user_id,)
    )
    total_duration = cursor.fetchone()[0] or 0

    # Most used language
    cursor.execute('''
        SELECT language, COUNT(*) as count
        FROM transcriptions
        WHERE user_id = ?
        GROUP BY language
        ORDER BY count DESC
        LIMIT 1
    ''', (user_id,))
    result = cursor.fetchone()
    favorite_lang = result[0] if result else 'es'

    conn.close()

    return {
        'total_transcriptions': total_count,
        'total_duration_seconds': total_duration,
        'total_duration_minutes': round(total_duration / 60, 1),
        'favorite_language': favorite_lang
    }

def save_user_setting(user_id: int, language: str) -> None:
    """Save user's language preference."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO user_settings (user_id, language, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
    ''', (user_id, language))

    conn.commit()
    conn.close()

def get_user_setting(user_id: int) -> str:
    """Get user's language preference."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT language FROM user_settings WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    conn.close()
    return result[0] if result else 'es'

# Initialize database on import
try:
    init_database()
except Exception as e:
    print(f"⚠️ Database initialization error: {e}")
