import pytest

@pytest.mark.asyncio
async def test_llm_client_initialization():
    from persona.llm.client import FakeLLMBackend

