from datetime import datetime, timezone

import pytest

from persona.agent.nodes.retrieve import make_retrieve_node
from persona.db.migrations.migrations import apply_migrations
from persona.memory.schema import Memory
from persona.memory.store import MemoryStore
from tests.test_memory_store import _open  # reuse helper


class _Client:
    def __init__(self, vec):
        self._vec = vec

    async def embed(self, text):
        return self._vec


def _mem(id, content="x"):
    now = datetime.now(timezone.utc)
    return Memory(
        id=id, type="fact", content=content, importance=3,
        created_at=now, updated_at=now,
        source_message_id="m", source_conversation_id="c",
    )


@pytest.mark.asyncio
async def test_retrieve_returns_nearest_first(tmp_path):
    conn = _open(tmp_path / "t.db")
    await apply_migrations(conn)
    store = MemoryStore(conn)

    near = [1.0] + [0.0] * 767
    far = [0.0] * 767 + [1.0]
    store.insert(_mem("near", "hello"), near)
    store.insert(_mem("far", "goodbye"), far)

    node = make_retrieve_node(store=store, client=_Client(near))
    out = await node({"user_message": "hi"})
    assert out["retrieved_memories"][0].id == "near"
    conn.close()


@pytest.mark.asyncio
async def test_retrieve_calls_on_retrieved(tmp_path):
    conn = _open(tmp_path / "t.db")
    await apply_migrations(conn)
    store = MemoryStore(conn)

    proc = _mem("proc", "Keep it short. Why: user said 'stop summarizing every response'.")
    proc.type = "procedural"
    store.insert(proc, [0.0] * 768)

    node = make_retrieve_node(store=store, client=_Client([0.0] * 768), on_retrieved=lambda mems: mems[0].content)
    out = await node({"user_message": "hi"})
    assert out["procedural_rules"][0].id == "proc"
    assert out["session_summary"] == "Keep it short. Why: user said 'stop summarizing every response'."
    conn.close()

@pytest.mark.asyncio
async def test_retrieve_on_retrieved_can_be_async(tmp_path):
    conn = _open(tmp_path / "t.db")
    await apply_migrations(conn)
    store = MemoryStore(conn)

    proc = _mem("proc", "Keep it short. Why: user said 'stop summarizing every response'.")
    proc.type = "procedural"
    store.insert(proc, [0.0] * 768)

    async def on_retrieved(mems):
        assert mems[0].id == "proc"

    node = make_retrieve_node(store=store, client=_Client([0.0] * 768), on_retrieved=on_retrieved)
    await node({"user_message": "hi"})
    conn.close()
