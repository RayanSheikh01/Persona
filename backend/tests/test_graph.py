import pytest

from persona.agent.graph import build_graph
from persona.db.migrations.migrations import apply_migrations
from persona.llm.client import FakeLLMBackend, LLMClient
from persona.memory.store import MemoryStore
from tests.test_memory_store import _open


@pytest.mark.asyncio
async def test_graph_end_to_end_with_fake_backend(tmp_path):
    conn = _open(tmp_path / "g.db")
    await apply_migrations(conn)
    store = MemoryStore(conn)
    conn.execute(
        "INSERT INTO conversations (id, title, created_at, last_message_at)"
        " VALUES ('c1', NULL, datetime('now'), datetime('now'))"
    )

    client = LLMClient(
        FakeLLMBackend(
            chat_chunks=["hello"],
            embedding=[0.1] * 768,
            extraction=[{"type": "fact", "content": "Pip is a dog", "importance": 3}],
        )
    )
    graph = build_graph(
        conn=conn,
        store=store,
        client=client,
        system_prompt="sys {memories_block}",
        extract_prompt="extract",
    )

    result = await graph.ainvoke(
        {"conversation_id": "c1", "user_message": "I have a dog Pip.", "history": []}
    )
    assert result["assistant_response"] == "hello"
    mem_count = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
    assert mem_count >= 1
    conn.close()
