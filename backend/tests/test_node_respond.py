import pytest

@pytest.mark.asyncio
async def test_node_respond():
    from persona.agent.nodes.respond import render_memories

    # Test with no memories
    assert render_memories([]) == "No relevant memories found."
    # Test with some memories
    memories = [
        {"timestamp": "2024-01-01 10:00:00", "content": "Memory 1"},
        {"timestamp": "2024-01-01 11:00:00", "content": "Memory 2"},
    ]
    expected_output = "2024-01-01 10:00:00: Memory 1\n2024-01-01 11:00:00: Memory 2"
    assert render_memories(memories) == expected_output
