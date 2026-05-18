import pytest

from persona.llm.client import FakeLLMBackend, LLMClient


@pytest.mark.asyncio
async def test_chat_stream_yields_chunks():
    backend = FakeLLMBackend(chat_chunks=["hello ", "world"])
    client = LLMClient(backend)
    out = []
    async for chunk in client.chat_stream("sys", [{"role": "user", "content": "hi"}]):
        out.append(chunk)
    assert out == ["hello ", "world"]


@pytest.mark.asyncio
async def test_embed_returns_768_dim_vector():
    backend = FakeLLMBackend(embedding=[0.1] * 768)
    client = LLMClient(backend)
    vec = await client.embed("text")
    assert len(vec) == 768


@pytest.mark.asyncio
async def test_extract_memories_returns_candidates():
    extraction = [{"type": "fact", "content": "x", "importance": 3}]
    backend = FakeLLMBackend(extraction=extraction)
    client = LLMClient(backend)
    result = await client.extract_memories("u", "a", extract_prompt="prompt")
    assert result == extraction
