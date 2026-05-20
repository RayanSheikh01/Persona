from inspect import iscoroutinefunction

from persona.memory.schema import Memory

HISTORY_TURNS = 20
_TYPE_ORDER = ("profile", "preference", "fact", "goal", "event")


def render_memories(memories: list[Memory]) -> str:
    if not memories:
        return "_(no memories retrieved for this turn)_"
    by_type: dict[str, list[Memory]] = {t: [] for t in _TYPE_ORDER}
    for m in memories:
        by_type.setdefault(m.type, []).append(m)
    lines: list[str] = []
    for t in _TYPE_ORDER:
        if not by_type[t]:
            continue
        lines.append(f"## {t}")
        for m in by_type[t]:
            lines.append(f"- {m.content}")
    return "\n".join(lines)


def make_respond_node(*, client, system_prompt_template: str, on_token=None):
    async def respond(state):
        memories = state.get("retrieved_memories", [])
        rules = state.get("procedural_rules", [])
        summary = state.get("session_summary")
        system = system_prompt_template.format(
            memories_block=render_memories(memories),
            rules_block=render_rules(rules),
            session_summary=render_summary(summary),
        )
        history = state.get("history", [])[-HISTORY_TURNS * 2:]
        messages = list(history) + [
            {"role": "user", "content": state["user_message"]}
        ]
        chunks: list[str] = []
        async for chunk in client.chat_stream(system, messages):
            chunks.append(chunk)
            if on_token is not None:
                result = on_token(chunk)
                if iscoroutinefunction(on_token) or hasattr(result, "__await__"):
                    await result
        return {"assistant_response": "".join(chunks)}

    return respond


def render_rules(rules) -> str:
    if not rules:
        return "_(no procedural rules retrieved for this turn)_"
    lines = ["## Procedural Rules"] + [f"- {r.content}" for r in rules]
    return "\n".join(lines)

def render_summary(summary) -> str:
    if not summary:
        return "_(no session summary for this turn)_"
    return f"## Session Summary\n{summary}"

def render_memories(memories: list[Memory]) -> str:
    # filter out procedural memories since they get their own section
    memories = [m for m in memories if m.type != "procedural"]
    if not memories:
        return "_(no memories retrieved for this turn)_"
    by_type: dict[str, list[Memory]] = {t: [] for t in _TYPE_ORDER}
    for m in memories:
        by_type.setdefault(m.type, []).append(m)
    lines: list[str] = []
    for t in _TYPE_ORDER:
        if not by_type[t]:
            continue
        lines.append(f"## {t}")
        for m in by_type[t]:
            lines.append(f"- {m.content}")
    return "\n".join(lines)

