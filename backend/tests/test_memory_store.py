from datetime import datetime, timezone

import pytest
import pytest_asyncio

from persona.db.migrations.migrations import apply_migrations
from persona.memory.schema import Memory
from persona.memory.store import MemoryStore


def _mem(id: str, type: str = "fact", content: str = "hello world", importance: int = 3) -> Memory:
    now = datetime.now(timezone.utc)
    return Memory(
        id=id,
        type=type,
        content=content,
        importance=importance,
        created_at=now,
        updated_at=now,
        source_message_id="msg-1",
        source_conversation_id="conv-1",
    )


@pytest_asyncio.fixture
async def store(tmp_path):
    conn = _open(tmp_path / "test.db")
    await apply_migrations(conn)
    yield MemoryStore(conn)
    conn.close()


def _open(path):
    import sqlite3, sqlite_vec
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


@pytest.mark.asyncio
async def test_insert_and_get_roundtrip(store):
    m = _mem("a", content="dogs are great")
    store.insert(m, [0.1] * 768)
    got = store.get("a")
    assert got is not None
    assert got.content == "dogs are great"


@pytest.mark.asyncio
async def test_list_by_type_filters(store):
    store.insert(_mem("a", type="fact"), [0.0] * 768)
    store.insert(_mem("b", type="goal"), [0.0] * 768)
    assert [m.id for m in store.list_by_type("fact")] == ["a"]


@pytest.mark.asyncio
async def test_vector_search_orders_by_closeness(store):
    near = [1.0] + [0.0] * 767
    far = [0.0] * 767 + [1.0]
    store.insert(_mem("near"), near)
    store.insert(_mem("far"), far)
    results = store.vector_search(near, k=2)
    assert results[0][0] == "near"


@pytest.mark.asyncio
async def test_insert_rejects_wrong_dim(store):
    with pytest.raises(ValueError):
        store.insert(_mem("a"), [0.0] * 10)



@pytest.mark.asyncio
async def test_superseding(store):
    m1 = _mem("a", content="old memory")
    m2 = _mem("b", content="new memory")
    store.insert(m1, [0.0] * 768)
    store.insert(m2, [0.0] * 768)
    store.set_superseded_by("a", "b")
    assert store.get("a").superseded_by == "b"
    assert store.get("b").superseded_by is None
    # Superseded memory should still be retrievable
    assert store.get("a").content == "old memory"
    # Superseded memory should not appear in list_by_type by default
    assert [m.id for m in store.list_by_type("fact")] == ["b"]
    # Superseded memory should appear if include_superseded=True
    assert [m.id for m in store.list_by_type("fact", include_superseded=True)] == ["b", "a"]

    
