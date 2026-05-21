import pytest

def test_simplemem_adapter():
    from persona.memory.simplemem_adapter import SimpleMemAdapter
    db_dir = "test_db"
    adapter = SimpleMemAdapter(db_dir, clear=True)
    assert adapter is not None
    adapter.add_turn("user", "Hello", "2024-01-01T00:00:00Z")
    adapter.add_turn("assistant", "Hi there!", "2024-01-01T00:01:00Z")
    adapter.finalize()
    response = adapter.ask("What did I say?")
    assert response == "This is a placeholder response to the query: What did I say?"
    
    