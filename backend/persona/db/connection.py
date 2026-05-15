import sqlite3
from sqlite3 import Connection
from pathlib import Path


def get_db_connection() -> Connection:
    # Locate repository root and use data/persona.db so tests target the workspace data folder
    repo_root = Path(__file__).resolve().parents[3]
    db_path = repo_root / "data" / "persona.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    # Enable WAL journal mode and set busy timeout to match tests' expectations
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn
