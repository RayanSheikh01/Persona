import uuid
from datetime import datetime, timezone

from persona.memory.dedup import drop_duplicates
from persona.memory.schema import Memory


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_persist_node(
    *, conn, store, client, dedup_threshold: float = 0.92, supersede_threshold: float = 0.85, simplemem=None
):
    async def persist(state):
        conversation_id = state["conversation_id"]
        user_msg_id = str(uuid.uuid4())
        assistant_msg_id = str(uuid.uuid4())
        now_iso = _iso_now()

        candidates = state.get("new_candidates", [])
        cand_embeddings: list[list[float]] = []
        for c in candidates:
            cand_embeddings.append(await client.embed(c.content))

        kept_candidates = candidates
        kept_embeddings = cand_embeddings
        to_supersede: list[tuple[int, str]] = []
        if candidates:
            same_type_existing: list[tuple[str, str, list[float]]] = []
            for t in {c.type for c in candidates}:
                for m in store.list_by_type(t, include_superseded=True):
                    emb = store.get_embedding(m.id)
                    if emb is not None:
                        same_type_existing.append((m.id, m.type, emb))
            kept_candidates, to_supersede = drop_duplicates(
                candidates,
                cand_embeddings,
                same_type_existing,
                threshold=dedup_threshold,
                supersede_threshold=supersede_threshold,
            )
            kept_set = {id(c) for c in kept_candidates}
            kept_embeddings = [
                e for c, e in zip(candidates, cand_embeddings) if id(c) in kept_set
            ]

        try:
            conn.execute(
                "INSERT INTO messages (id, conversation_id, role, content, created_at)"
                " VALUES (?, ?, 'user', ?, ?)",
                (user_msg_id, conversation_id, state["user_message"], now_iso),
            )
            conn.execute(
                "INSERT INTO messages (id, conversation_id, role, content, created_at)"
                " VALUES (?, ?, 'assistant', ?, ?)",
                (
                    assistant_msg_id,
                    conversation_id,
                    state.get("assistant_response", ""),
                    now_iso,
                ),
            )
            conn.execute(
                "UPDATE conversations SET last_message_at = ? WHERE id = ?",
                (now_iso, conversation_id),
            )
            
            if simplemem:
                simplemem.add_turn("user", state["user_message"], ts=now_iso)
                simplemem.add_turn("assistant", state.get("assistant_response", ""), ts=now_iso)
                simplemem.finalize()

            new_ids: list[str] = []
            for cand, emb in zip(kept_candidates, kept_embeddings):
                mem_id = str(uuid.uuid4())
                m = Memory(
                    id=mem_id,
                    type=cand.type,
                    content=cand.content,
                    importance=cand.importance,
                    created_at=datetime.fromisoformat(now_iso),
                    updated_at=datetime.fromisoformat(now_iso),
                    source_message_id=user_msg_id,
                    source_conversation_id=conversation_id,
                )
                store.insert(m, emb)
                new_ids.append(mem_id)

            for rank_idx, (mem, score) in enumerate(
                zip(state.get("retrieved_memories", []), state.get("retrieved_scores", []))
            ):
                conn.execute(
                    "INSERT INTO memory_retrievals (message_id, memory_id, score, rank)"
                    " VALUES (?, ?, ?, ?)",
                    (user_msg_id, mem.id, float(score), rank_idx),
                )

            conn.commit()
        except Exception:
            conn.rollback()
            raise

        return {
            "user_message_id": user_msg_id,
            "assistant_message_id": assistant_msg_id,
            "new_memory_ids": new_ids,
        }

    return persist
