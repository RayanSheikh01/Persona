import pytest

@pytest.mark.asyncio
async def test_memory_extraction():
    from persona.memory.extraction import extract_candidates
    from persona.llm.client import FakeLLMBackend

    # Create a fake LLM client that supports extraction
    llm_client = FakeLLMBackend()
    llm_client.extraction = True

    # Define test inputs
    user_message = "What is the capital of France?"
    assistant_message = "The capital of France is Paris."
    extract_prompt = "Extract the key information from the following conversation:\n{conversation_history}"

    # Call the extraction function
    candidates = await extract_candidates(
        client=llm_client,
        user_message=user_message,
        assistant_message=assistant_message,
        extract_prompt=extract_prompt,
    )

    # Assert that candidates were extracted correctly
    assert len(candidates) == 1
    assert candidates[0].content == "example value"




