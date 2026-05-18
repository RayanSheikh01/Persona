from datetime import datetime, timezone
from inspect import iscoroutinefunction

from persona.memory.retrieval import rank


def make_retrieve_node(*, store, client, k: int = 8, top_n: int = 20, on_retrieved=None):
    async def retrieve(state):
        user_message = state["user_message"]
        query_embedding = await client.embed(user_message)

        try:
            hits = store.vector_search(query_embedding, k=top_n)
        except Exception:
            ids = store.fts_search(user_message, k=top_n)
            hits = [(i, 0.5) for i in ids]

        ids = [i for i, _ in hits]
        sim_by_id = {i: s for i, s in hits}
        memories = store.by_ids(ids)
        pairs = [(m, sim_by_id[m.id]) for m in memories]
        ranked = rank(pairs, now=datetime.now(timezone.utc), k=k)

        retrieved_memories = [m for m, _ in ranked]
        retrieved_scores = [s for _, s in ranked]

        if on_retrieved is not None:
            result = on_retrieved(retrieved_memories)
            if iscoroutinefunction(on_retrieved) or hasattr(result, "__await__"):
                await result

        return {
            "retrieved_memories": retrieved_memories,
            "retrieved_scores": retrieved_scores,
        }

    return retrieve
