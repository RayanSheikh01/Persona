import pytest

from persona.agent.graph import build_graph
from persona.db.migrations.migrations import apply_migrations
from persona.llm.client import FakeLLMBackend, LLMClient
from persona.memory.store import MemoryStore
from persona.memory.summaries import ConversationSummaryStore
from persona.memory.schema import MemoryCandidate
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
    assert result["new_candidates"] == [
        MemoryCandidate(type="fact", content="Pip is a dog", importance=3)
    ]
    assert len(result["new_memory_ids"]) == 1
    conn.close()



@pytest.mark.asyncio
async def test_graph_summarization(tmp_path):
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
    summary_store = ConversationSummaryStore(conn)
    graph = build_graph(
        conn=conn,
        store=store,
        client=client,
        system_prompt="sys {memories_block}",
        extract_prompt="extract",
        summary_store=summary_store,
    )

    long_history = [
        {"id": f"a{i}", "role": "user", "content": f"message {i}"} for i in range(31)
    ]
    await graph.ainvoke(
        {"conversation_id": "c1", "user_message": "I have a dog Pip.", "history": long_history}
    )
    summary = summary_store.get("c1")
    assert summary is not None
    first_summarized_through = summary.summarized_through_message_id

    short_history = [
        {"id": f"b{i}", "role": "user", "content": f"message {i}"} for i in range(10)
    ]
    await graph.ainvoke(
        {"conversation_id": "c1", "user_message": "I have a dog Pip.", "history": short_history}
    )
    summary = summary_store.get("c1")
    assert summary is not None
    assert summary.summarized_through_message_id == first_summarized_through

    conn.close()