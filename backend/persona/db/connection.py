import sqlite3
from pathlib import Path
from sqlite3 import Connection

import sqlite_vec


def get_db_connection() -> Connection:
    repo_root = Path(__file__).resolve().parents[3]
    db_path = repo_root / "data" / "persona.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row

    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)

    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
