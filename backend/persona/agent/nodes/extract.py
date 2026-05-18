import logging

from persona.memory.extraction import extract_candidates

log = logging.getLogger(__name__)


def make_extract_node(*, client, extract_prompt: str):
    async def extract(state):
        try:
            candidates = await extract_candidates(
                client,
                state["user_message"],
                state.get("assistant_response", ""),
                extract_prompt=extract_prompt,
            )
        except Exception as e:
            log.warning("extract node failed: %s", e)
            return {"new_candidates": []}
        return {"new_candidates": candidates}

    return extract
