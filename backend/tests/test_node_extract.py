import pytest

from persona.agent.nodes.extract import make_extract_node
from persona.llm.client import FakeLLMBackend, LLMClient


@pytest.mark.asyncio
async def test_extract_node_returns_candidates_on_happy_path():
    extraction = [{"type": "fact", "content": "x", "importance": 3}]
    client = LLMClient(FakeLLMBackend(extraction=extraction))
    node = make_extract_node(client=client, extract_prompt="p")
    out = await node({"user_message": "hi", "assistant_response": "hello"})
    assert len(out["new_candidates"]) == 1
    assert out["new_candidates"][0].content == "x"


class _RaisingBackend:
    async def chat_stream(self, system, messages):
        if False:
            yield ""

    async def embed(self, text):
        return [0.0] * 768

    async def extract(self, prompt):
        raise RuntimeError("rate limited")


@pytest.mark.asyncio
async def test_extract_node_swallows_errors():
    client = LLMClient(_RaisingBackend())
    node = make_extract_node(client=client, extract_prompt="p")
    out = await node({"user_message": "hi", "assistant_response": "hello"})
    assert out == {"new_candidates": []}
