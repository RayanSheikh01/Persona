import pytest

@pytest.mark.asyncio
async def test_memory_store():
    from persona.memory.store import MemoryStore, insert, get, list_by_type, list_all, vector_search, fts_search, by_ids

    m = MemoryStore()
    embedding1 = {'type': 'text', 'content': 'Hello world', 'embedding': [0.1, 0.2, 0.3]}
    embedding2 = {'type': 'text', 'content': 'Goodbye world', 'embedding': [0.2, 0.3, 0.4]}
    embedding3 = {'type': 'image', 'content': 'An image', 'embedding': [0.3, 0.4, 0.5]}

    insert(m, embedding1)
    insert(m, embedding2)
    insert(m, embedding3)

    assert get(0, m) == embedding1
    assert list_by_type(m, 'text') == [embedding1, embedding2]
    assert list_all(m) == [embedding1, embedding2, embedding3]
    assert vector_search(m, [0.15, 0.25, 0.35]) == [embedding2, embedding1, embedding3]
    assert fts_search(m, 'world') == [embedding1, embedding2]
    assert by_ids(m, [0, 2]) == [embedding1, embedding3]