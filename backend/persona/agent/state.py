from typing import TypedDict

from persona.memory.schema import Memory, MemoryCandidate

class ChatState(TypedDict, total=False):
    conversation_id: str
    history: list[dict]
    user_message: str
    user_message_id: str
    assistant_message_id: str
    retrieved_memories: list[Memory]
    retrieved_scores: list[float]
    assistant_response: str
    new_candidates: list[MemoryCandidate]
    new_memory_ids: list[str]