import pytest

@pytest.mark.asyncio
async def test_open_connection_enables_wal_and_vec():
    from persona.db.connection import get_db_connection

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode")
    journal_mode = cursor.fetchone()[0]
    assert journal_mode == "wal"

    cursor.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    busy, _log_pages, _checkpointed = cursor.fetchone()
    assert busy == 0

@pytest.mark.asyncio
async def test_busy_timeout_set():
    from persona.db.connection import get_db_connection

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA busy_timeout")
    timeout_value = cursor.fetchone()[0]
    assert timeout_value == 5000
