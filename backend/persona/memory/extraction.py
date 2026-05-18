from pydantic import ValidationError

from persona.llm.client import LLMClient
from persona.memory.schema import MemoryCandidate


async def extract_candidates(
    client: LLMClient,
    user_message: str,
    assistant_message: str,
    *,
    extract_prompt: str,
) -> list[MemoryCandidate]:
    raw = await client.extract_memories(
        user_message, assistant_message, extract_prompt=extract_prompt
    )
    candidates: list[MemoryCandidate] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        try:
            candidates.append(MemoryCandidate(**item))
        except ValidationError:
            continue
    return candidates
