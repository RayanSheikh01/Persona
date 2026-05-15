import pytest

@pytest.mark.asyncio
async def test_memory_store():
    from persona.memory.store import MemoryStore, vector_search, fts_search, by_ids

    m = MemoryStore()
    embedding1 = {'type': 'text', 'content': 'Hello world', 'embedding': [0.1, 0.2, 0.3]}
    embedding2 = {'type': 'text', 'content': 'Goodbye world', 'embedding': [0.2, 0.3, 0.4]}
    embedding3 = {'type': 'image', 'content': 'An image', 'embedding': [0.3, 0.4, 0.5]}

    m.insert(embedding1)
    m.insert(embedding2)
    m.insert(embedding3)

    assert m.get(0) == embedding1
    assert m.list_by_type('text') == [embedding1, embedding2]
    assert m.list_all() == [embedding1, embedding2, embedding3]
    assert vector_search(m._memory, [0.15, 0.25, 0.35]) == [embedding2, embedding1, embedding3]
    assert fts_search(m._memory, 'world') == [embedding1, embedding2]
    assert by_ids(m._memory, [0, 2]) == [embedding1, embedding3]
