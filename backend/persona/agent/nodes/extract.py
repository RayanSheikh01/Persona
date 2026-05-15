from persona.memory.extraction import extract_candidates

def make_extract_node(*, client, extract_prompt):
    async def extract_node(user_input):
        try:
            candidates = await extract_candidates(
                client=client,
                user_message=user_input,
                assistant_message="",  # No assistant message for extraction
                extract_prompt=extract_prompt,
            )
            return [candidate.content for candidate in candidates]
        except Exception as e:
            print(f"Error in extract_node: {e}")
            return []
    return extract_node



