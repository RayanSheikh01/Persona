import pytest
from sqlalchemy import func

from persona.agent.state import ChatState

@pytest.mark.asyncio
async def test_graph():
    from persona.agent.graph import StateGraph
    
    graph = StateGraph(ChatState)
    graph.add_node("state1", func=lambda x: x)
    graph.add_node("state2", func=lambda x: x)
    graph.add_edge("state1", "state2")
    assert "state1" in graph.nodes
    assert "state2" in graph.nodes
    assert graph.edges["state1"] == ["state2"]
    graph.set_entry_point("state1")
    assert graph.entry_point == "state1"