import pytest

@pytest.mark.asyncio
async def test_llm_client_initialization():
    from persona.llm.client import FakeLLMBackend

    # Test that the FakeLLMBackend can be initialized without errors
    backend = FakeLLMBackend()
    assert backend is not None
    
