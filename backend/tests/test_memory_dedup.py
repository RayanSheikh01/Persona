import pytest


@pytest.mark.asyncio
async def test_dedup():
    from persona.memory.dedup import drop_duplicates

    candidates = [
        {'type': 'text', 'content': 'Hello world'},
        {'type': 'text', 'content': 'Hello world!'},
        {'type': 'text', 'content': 'Goodbye world'},
    ]
    candidate_embeddings = [
        [0.1, 0.2, 0.3],
        [0.1, 0.2, 0.3],
        [0.9, -0.2, 0.1],
    ]
    existing_same_type = [
        ('text', [0.1, 0.2, 0.3]),
    ]

    filtered = drop_duplicates(candidates, candidate_embeddings, existing_same_type, threshold=0.95)
    assert len(filtered) == 1
    