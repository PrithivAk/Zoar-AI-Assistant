"""
Shared SQLite store: mood logs + full chat history (memory across agents).
"""
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "zoar.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS mood_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            mood_score INTEGER NOT NULL,
            note TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            role TEXT NOT NULL,        -- 'user' or 'assistant'
            agent TEXT,                -- which agent handled it (wellness/shopping/interview/general)
            content TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def log_mood(mood_score: int, note: str = ""):
    conn = get_conn()
    conn.execute(
        "INSERT INTO mood_logs (date, mood_score, note) VALUES (?, ?, ?)",
        (datetime.now().isoformat(), mood_score, note),
    )
    conn.commit()
    conn.close()


def get_recent_moods(limit: int = 7):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM mood_logs ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return list(reversed(rows))  # chronological order


def log_message(role: str, content: str, agent: str = "general"):
    conn = get_conn()
    conn.execute(
        "INSERT INTO chat_history (timestamp, role, agent, content) VALUES (?, ?, ?, ?)",
        (datetime.now().isoformat(), role, agent, content),
    )
    conn.commit()
    conn.close()


def get_chat_history(limit: int = 20):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM chat_history ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return list(reversed(rows))
