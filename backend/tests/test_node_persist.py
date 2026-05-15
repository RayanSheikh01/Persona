from unittest.mock import AsyncMock

import pytest

from persona.agent.nodes.persist import make_persist_node


@pytest.mark.asyncio
async def test_node_persist_calls_persist_memory():
    conn = object()
    store = AsyncMock()
    store.retrieve_memories.return_value = []
    client = AsyncMock()
    client.get_embedding.return_value = [0.0] * 768

    persist_node = make_persist_node(conn=conn, store=store, client=client)

    user_input = "Remember that I have a meeting tomorrow."
    assistant_response = "I will remember that for you."
    await persist_node(user_input, assistant_response, store)

    store.persist_memory.assert_awaited_once()
    args, kwargs = store.persist_memory.await_args
    assert args[0] is conn
    assert user_input in kwargs["content"]
    assert assistant_response in kwargs["content"]
    assert kwargs["embedding"] == [0.0] * 768


@pytest.mark.asyncio
async def test_node_persist_skips_when_duplicate():
    conn = object()
    embedding = [0.0] * 768
    store = AsyncMock()
    store.retrieve_memories.return_value = [{"embedding": embedding}]
    client = AsyncMock()
    client.get_embedding.return_value = embedding
    client.compute_similarity.return_value = 0.99

    persist_node = make_persist_node(conn=conn, store=store, client=client)
    await persist_node("u", "a", store)

    store.persist_memory.assert_not_awaited()
