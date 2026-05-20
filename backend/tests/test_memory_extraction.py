import pytest

from persona.llm.client import FakeLLMBackend, LLMClient
from persona.memory.extraction import extract_candidates


@pytest.mark.asyncio
async def test_valid_candidates_pass_through():
    backend = FakeLLMBackend(
        extraction=[
            {"type": "fact", "content": "Pip is a dog", "importance": 3},
            {"type": "goal", "content": "Run a marathon", "importance": 4},
        ]
    )
    client = LLMClient(backend)
    candidates = await extract_candidates(client, "u", "a", extract_prompt="p")
    assert [c.type for c in candidates] == ["fact", "goal"]


@pytest.mark.asyncio
async def test_invalid_candidates_dropped_silently():
    extraction: list = [
        {"type": "fact", "content": "valid", "importance": 3},
        {"type": "nope", "content": "bad type", "importance": 3},
        {"type": "fact", "content": "bad imp", "importance": 99},
        "not a dict",
    ]
    backend = FakeLLMBackend(extraction=extraction)
    client = LLMClient(backend)
    candidates = await extract_candidates(client, "u", "a", extract_prompt="p")
    assert len(candidates) == 1
    assert candidates[0].content == "valid"

@pytest.mark.asyncio
async def test_procdedural_extraction():
    backend = FakeLLMBackend(
        extraction=[
            {"type": "procedural", "content": "Never suggest decaf coffee. Why: user said 'don't ever recommend decaf, I hate it'.", "importance": 4},
        ]
    )
    client = LLMClient(backend)
    candidates = await extract_candidates(client, "u", "a", extract_prompt="p")
    assert len(candidates) == 1
    assert candidates[0].type == "procedural"
    assert candidates[0].content == "Never suggest decaf coffee. Why: user said 'don't ever recommend decaf, I hate it'."
    assert candidates[0].importance == 4