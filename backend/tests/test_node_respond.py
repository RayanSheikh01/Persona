from datetime import datetime, timezone

import pytest

from persona.agent.nodes.respond import make_respond_node, render_memories
from persona.llm.client import FakeLLMBackend, LLMClient
from persona.memory.schema import Memory


def _mem(type_, content):
    now = datetime.now(timezone.utc)
    return Memory(
        id=f"id-{content}", type=type_, content=content, importance=3,
        created_at=now, updated_at=now,
        source_message_id="m", source_conversation_id="c",
    )


def test_render_memories_empty():
    assert render_memories([]) == "_(no memories retrieved for this turn)_"


def test_render_memories_grouped_by_type():
    memories = [
        _mem("goal", "run a marathon"),
        _mem("fact", "owns a dog"),
        _mem("fact", "lives in NYC"),
    ]
    rendered = render_memories(memories)
    assert "## fact" in rendered
    assert "## goal" in rendered
    assert rendered.index("## fact") < rendered.index("## goal")
    assert "- owns a dog" in rendered


@pytest.mark.asyncio
async def test_respond_collects_streamed_chunks():
    client = LLMClient(FakeLLMBackend(chat_chunks=["hello", " world"]))
    node = make_respond_node(client=client, system_prompt_template="sys {memories_block}")
    out = await node({"user_message": "hi", "retrieved_memories": [], "history": []})
    assert out["assistant_response"] == "hello world"
