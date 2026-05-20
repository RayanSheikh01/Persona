import pytest

from persona.memory.schema import MemoryCandidate


@pytest.mark.asyncio
async def test_memory_dedup():
    from persona.memory.dedup import drop_duplicates
    from persona.db.connection import get_db_connection

    candidates = [
        MemoryCandidate(type="fact", content="The sky is blue.", importance=3),
        MemoryCandidate(type="fact", content="The sky is very blue.", importance=2),
        MemoryCandidate(type="fact", content="Water is wet.", importance=1),
    ]
    candidate_embeddings = [
        [0.1, 0.2, 0.3],
        [0.1, 0.2, 0.31],
        [0.9, 0.1, 0.05],
    ]

    existing = [
        ("existing1", "fact", [0.1, 0.2, 0.3]),  # Similar to candidate 1 and 2
        ("existing2", "fact", [0.4, 0.5, 0.6]),  # Unrelated to all candidates
    ]

    to_keep, to_supersede = drop_duplicates(candidates, candidate_embeddings, existing, threshold=0.95, supersede_threshold=0.9)

    assert len(to_keep) == 1
    assert to_keep[0].content == "Water is wet."
    assert len(to_supersede) == 2
    assert to_supersede[0][0] == 0  # Candidate 1
    assert to_supersede[0][1] == "existing1"
    assert to_supersede[1][0] == 1  # Candidate 2
    assert to_supersede[1][1] == "existing1"

