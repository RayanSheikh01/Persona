from datetime import datetime, timezone

import pytest

from persona.agent.nodes.persist import make_persist_node
from persona.db.migrations.migrations import apply_migrations
from persona.llm.client import FakeLLMBackend, LLMClient
from persona.memory.schema import Memory, MemoryCandidate
from persona.memory.store import MemoryStore
from tests.test_memory_store import _open


def _mem(id, type_="fact", content="seed"):
    now = datetime.now(timezone.utc)
    return Memory(
        id=id, type=type_, content=content, importance=3,
        created_at=now, updated_at=now,
        source_message_id="m", source_conversation_id="c1",
    )


@pytest.mark.asyncio
async def test_persist_writes_messages_memories_and_retrievals(tmp_path):
    conn = _open(tmp_path / "p.db")
    await apply_migrations(conn)
    store = MemoryStore(conn)

    conn.execute(
        "INSERT INTO conversations (id, title, created_at, last_message_at)"
        " VALUES ('c1', NULL, datetime('now'), datetime('now'))"
    )
    retrieved = _mem("ret-1", content="prior fact")
    store.insert(retrieved, [1.0] + [0.0] * 767)

    client = LLMClient(FakeLLMBackend(embedding=[0.0] * 767 + [1.0]))
    node = make_persist_node(conn=conn, store=store, client=client)

    state = {
        "conversation_id": "c1",
        "user_message": "hello",
        "assistant_response": "hi",
        "retrieved_memories": [retrieved],
        "retrieved_scores": [0.8],
        "new_candidates": [MemoryCandidate(type="fact", content="new", importance=3)],
    }
    out = await node(state)

    assert len(out["new_memory_ids"]) == 1
    msg_count = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    assert msg_count == 2
    mem_count = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
    assert mem_count == 2  # seed + new
    retr_count = conn.execute("SELECT COUNT(*) FROM memory_retrievals").fetchone()[0]
    assert retr_count == 1
    conn.close()

@pytest.mark.asyncio
async def test_persist_works_with_simplemem(tmp_path):
    from persona.memory.simplemem_adapter import SimpleMemAdapter

    conn = _open(tmp_path / "p_simplemem.db")
    await apply_migrations(conn)
    store = MemoryStore(conn)

    simplemem = SimpleMemAdapter(str(tmp_path / "simplemem_db"), clear=True)

    conn.execute(
        "INSERT INTO conversations (id, title, created_at, last_message_at)"
        " VALUES ('c1', NULL, datetime('now'), datetime('now'))"
    )

    client = LLMClient(FakeLLMBackend(embedding=[0.0] * 768))
    node = make_persist_node(conn=conn, store=store, client=client, simplemem=simplemem)

    state = {
        "conversation_id": "c1",
        "user_message": "hello",
        "assistant_response": "hi",
        "retrieved_memories": [],
        "retrieved_scores": [],
        "new_candidates": [MemoryCandidate(type="fact", content="new", importance=3)],
    }
    out = await node(state)

    assert len(out["new_memory_ids"]) == 1
    msg_count = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    assert msg_count == 2
    mem_count = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
    assert mem_count == 1  # new
    
    conn.close()