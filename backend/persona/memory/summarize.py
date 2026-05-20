def build_summarize_prompt(*, prior_summary: str | None, turns: list[dict]) -> str:
    turn_texts = []
    for t in turns:
        role = t["role"]
        content = t["content"]
        turn_texts.append(f"{role.capitalize()}: {content}")
    turns_block = "\n".join(turn_texts)
    if prior_summary is not None:
        prior_block = f"Prior summary:\n{prior_summary}\n\n"
    else:
        prior_block = ""
    prompt = (
        f"{prior_block}"
        "Here are the new conversation turns since the last summary:\n"
        f"{turns_block}\n\n"
        "Please write an updated summary of the conversation so far, incorporating any new information from these turns. "
        "The summary should be concise but comprehensive, and should reflect the most current state of the conversation."
    )
    return prompt

