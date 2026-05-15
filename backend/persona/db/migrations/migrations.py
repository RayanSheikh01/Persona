import sqlite3
from pathlib import Path

import sqlite_vec

from persona.db.connection import get_db_connection

MIGRATIONS_DIR = Path(__file__).resolve().parent


def _load_vec(conn: sqlite3.Connection) -> None:
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)


def _apply(conn: sqlite3.Connection) -> None:
    _load_vec(conn)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations ("
        "name TEXT PRIMARY KEY, "
        "applied_at TEXT NOT NULL DEFAULT (datetime('now'))"
        ")"
    )
    applied = {row[0] for row in conn.execute("SELECT name FROM schema_migrations")}

    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        if path.name in applied:
            continue
        sql = path.read_text(encoding="utf-8")
        try:
            conn.executescript(sql)
            conn.execute("INSERT INTO schema_migrations(name) VALUES (?)", (path.name,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"Failed to apply migration {path.name}: {e}") from e


async def apply_migrations(conn: sqlite3.Connection | None = None) -> None:
    try:
        if conn is not None:
            _apply(conn)
            return
        c = get_db_connection()
        try:
            _apply(c)
        finally:
            c.close()
    except Exception as e:
        raise RuntimeError(f"Failed to apply migrations: {e}") from e
