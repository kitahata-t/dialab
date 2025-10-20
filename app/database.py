import sqlite3
from contextlib import contextmanager
from typing import Dict, Iterator, Optional

from .config import get_settings


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Yield a SQLite connection and close it afterwards."""
    settings = get_settings()
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """Create tables if they do not exist."""
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                model TEXT,
                input_tokens INTEGER,
                output_tokens INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """
        )
        conn.commit()


def get_user_by_username(username: str) -> Optional[Dict]:
    """Return a user dictionary for a given username."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, username, password_hash, role FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    return dict(row) if row else None


def create_user(username: str, password_hash: str, role: str = "user") -> int:
    """Insert a new user and return its id."""
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role),
        )
        conn.commit()
        return int(cursor.lastrowid)


def log_chat_message(
    user_id: int,
    role: str,
    content: str,
    model: str,
    input_tokens: Optional[int],
    output_tokens: Optional[int],
) -> None:
    """Persist a chat message for auditing."""
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO chat_logs (user_id, role, content, model, input_tokens, output_tokens)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, role, content, model, input_tokens, output_tokens),
        )
        conn.commit()
