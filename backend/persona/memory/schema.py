from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

MemoryType = Literal["profile", "preference", "fact", "goal", "event", "procedural"]
MEMORY_TYPES = ["profile", "preference", "fact", "goal", "event", "procedural"]


class MemoryCandidate(BaseModel):
    type: MemoryType
    content: str = Field(min_length=1, max_length=2000)
    importance: int = Field(ge=1, le=5)

class Memory(BaseModel):
    id: str
    type: MemoryType
    content: str
    importance: int = Field(ge=1, le=5)
    created_at: datetime
    updated_at: datetime
    source_message_id: str
    source_conversation_id: str
    superseded_by: str | None = None
    related_ids: list[str] = Field(default_factory=list)


def _row_to_memory(row):
    return {
        'id': row['id'],
        'type': row['type'],
        'content': row['content'],
        'embedding': row['embedding']
    }

