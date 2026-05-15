from persona.memory.schema import MemoryCandidate
from persona.llm.client import LLMClient

async def extract_candidates(
    client: LLMClient,
    user_message: str,
    assistant_message: str,
    extract_prompt: str,
) -> list[MemoryCandidate]:
    conversation_history = f"User: {user_message}\nAssistant: {assistant_message}"
    prompt = extract_prompt.format(conversation_history=conversation_history)
    extraction_results = await client.extract(prompt)
    candidates = []
    for result in extraction_results:
        if result.get("type") and result.get("content"):
            candidates.append(MemoryCandidate(**result))
    return candidates


