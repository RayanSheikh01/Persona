import sqlite3

import pytest

from persona.agent.nodes.summarize import make_summarize_node, should_summarize
from persona.db.migrations.migrations import apply_migrations
from persona.memory.summaries import ConversationSummaryStore


def _open(path):
    conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@pytest.mark.asyncio
async def test_should_summarize_triggers_when_over_buffer_plus_stride():
    history = [{"role": "user", "content": "hi"}] * 30
    assert not should_summarize(history, buffer_turns=20, stride=10)
    history.append({"role": "user", "content": "hi"})
    assert should_summarize(history, buffer_turns=20, stride=10)


@pytest.mark.asyncio
async def test_summarize_node_writes_summary_and_last_id(tmp_path):
    conn = _open(tmp_path / "t.db")
    await apply_migrations(conn)
    store = ConversationSummaryStore(conn)

    async def fake_summarizer(prompt: str) -> str:
        return "new summary"

    node = make_summarize_node(
        store, buffer_turns=20, stride=10, summarizer=fake_summarizer
    )
    history = [
        {"id": f"a{i}", "role": "user", "content": f"message {i}"} for i in range(31)
    ]

    result = await node.run(history=history, conversation_id="conv1")

    assert result == {"summary": "new summary"}
    saved = store.get("conv1")
    assert saved is not None
    assert saved.summary == "new summary"
    assert saved.summarized_through_message_id == "a10"
    conn.close()


@pytest.mark.asyncio
async def test_summarize_node_short_history_is_noop(tmp_path):
    conn = _open(tmp_path / "t.db")
    await apply_migrations(conn)
    store = ConversationSummaryStore(conn)

    node = make_summarize_node(store, buffer_turns=20, stride=10)
    history = [
        {"id": f"a{i}", "role": "user", "content": f"message {i}"} for i in range(10)
    ]

    result = await node.run(history=history, conversation_id="conv1")

    assert result == {}
    assert store.get("conv1") is None
    conn.close()
