HISTORY_TURNS = 20

def render_memories(memories) -> str:
    if not memories:
        return "No relevant memories found."
    rendered = []
    for mem in memories[-HISTORY_TURNS:]:  # Limit to last N turns
        rendered.append(f"{mem['timestamp']}: {mem['content']}")
    return "\n".join(rendered)

