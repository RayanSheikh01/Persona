import pytest

from persona.memory.schema import Memory
from datetime import datetime

@pytest.mark.asyncio
async def test_memory():
    

    memory = Memory(
        id="test_id",
        type="profile",
        content="Test content",
        importance=3,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        source_message_id="test_message_id",
        source_conversation_id="test_conversation_id",
        related_ids=["related_id_1", "related_id_2"]
    )

    assert memory.id == "test_id"
    assert memory.type == "profile"
    assert memory.content == "Test content"
    assert memory.importance == 3
    assert memory.source_message_id == "test_message_id"
    assert memory.source_conversation_id == "test_conversation_id"