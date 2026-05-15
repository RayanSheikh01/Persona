from persona.memory.schema import Memory


W_SIM, W_IMP, W_REC = 0.7, 0.2, 0.1
RECENCY_HALFLIFE_DAYS = 60.0


def vector_search(m, query_embedding, top_k=5):
    def cosine_similarity(vec1, vec2):
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        return dot_product / (norm1 * norm2) if norm1 and norm2 else 0.0

    scored_embeddings = []
    for embedding in m.values():
        score = cosine_similarity(query_embedding, embedding['embedding'])
        scored_embeddings.append((score, embedding))

    scored_embeddings.sort(key=lambda x: x[0], reverse=True)
    return [embedding for score, embedding in scored_embeddings[:top_k]]

def fts_search(m, query):
    results = []
    for embedding in m.values():
        if query.lower() in embedding['content'].lower():
            results.append(embedding)
    return results

def by_ids(m, ids):
    return [m[id] for id in ids if id in m]

def recency_decay(created_at, now) -> float:
    age_days = max(0.0, (now - created_at).total_seconds() / 86400.0)
    return 0.5 ** (age_days / RECENCY_HALFLIFE_DAYS)

def _score(m, similarity, now) -> float:
    return W_SIM*similarity + W_IMP*(m.importance/5.0) + W_REC*recency_decay(m.created_at, now)

def rank(candidates: list[tuple[Memory, float]], *, now, k=8) -> list[Memory]:
    scored = [(m, _score(m, sim, now)) for m, sim in candidates]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [m for m, score in scored[:k]]

