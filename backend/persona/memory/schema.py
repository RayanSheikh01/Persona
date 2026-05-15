from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

MemoryType = Literal["profile", "preference", "fact", "goal", "event"]
MEMORY_TYPES = ["profile", "preference", "fact", "goal", "event"]


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

