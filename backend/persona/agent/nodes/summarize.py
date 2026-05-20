from persona.memory.summarize import build_summarize_prompt


def should_summarize(history: list[dict], *, buffer_turns: int, stride: int) -> bool:
    return len(history) > buffer_turns + stride


def make_summarize_node(summary_store, *, buffer_turns: int, stride: int, summarizer=None):
    async def _default_summarizer(prompt: str) -> str:
        return "new summary"

    summarize_fn = summarizer or _default_summarizer

    class _Node:
        async def run(self, *, history: list[dict], conversation_id: str) -> dict:
            if not should_summarize(history, buffer_turns=buffer_turns, stride=stride):
                return {}
            to_summarize = history[:-buffer_turns]
            prior = summary_store.get(conversation_id)
            prior_text = prior.summary if prior else None
            prompt = build_summarize_prompt(prior_summary=prior_text, turns=to_summarize)
            summary = await summarize_fn(prompt)
            last_id = to_summarize[-1].get("id", "")
            summary_store.upsert(conversation_id, summary, last_id)
            return {"summary": summary}

        async def __call__(self, state: dict) -> dict:
            return await self.run(
                history=state.get("history", []),
                conversation_id=state["conversation_id"],
            )

    return _Node()
