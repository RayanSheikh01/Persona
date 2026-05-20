from datetime import datetime, timezone
from inspect import iscoroutinefunction

from persona.memory.retrieval import rank
from persona.settings import get_settings

settings = get_settings()
procedural_max_rules = settings.procedural_max_rules

def make_retrieve_node(*, store, client, k: int = 8, top_n: int = 20, on_retrieved=None, summary_store=None):
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
        procedural = [m for m in memories if m.type == "procedural"]
        if procedural:
            retrieved_memories = procedural
            retrieved_scores = [sim_by_id[m.id] for m in procedural]
            store.list_procedural(limit=procedural_max_rules)  # Touch procedural memories to update their recency
        else:
            pairs = [(m, sim_by_id[m.id]) for m in memories]
            ranked = rank(pairs, now=datetime.now(timezone.utc), k=k)
            retrieved_memories = [m for m, _ in ranked]
            retrieved_scores = [s for _, s in ranked]

        session_summary = None
        if on_retrieved is not None:
            result = on_retrieved(retrieved_memories)
            if iscoroutinefunction(on_retrieved) or hasattr(result, "__await__"):
                result = await result
            session_summary = result

        return {
            "retrieved_memories": retrieved_memories,
            "retrieved_scores": retrieved_scores,
            "procedural_rules": procedural,
            "session_summary": session_summary,
        }

    return retrieve
