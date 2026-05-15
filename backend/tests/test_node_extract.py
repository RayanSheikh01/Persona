import pytest

from persona.llm.client import FakeLLMBackend

@pytest.mark.asyncio
async def test_node_extract():
    from persona.agent.nodes.extract import make_extract_node


    llm_client = FakeLLMBackend()
    llm_client.extraction = True

    with open("persona/agent/prompts/extract.md", "r") as f:
        extract_prompt = f.read()

    extract_node = make_extract_node(client=llm_client, extract_prompt=extract_prompt)

    # Test with sample user input
    user_input = "What is the weather like today?"
    candidates = await extract_node(user_input)
    assert candidates == ["Candidate 1", "Candidate 2"]