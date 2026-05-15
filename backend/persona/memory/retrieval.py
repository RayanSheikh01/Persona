from persona.memory.schema import Memory


W_SIM, W_IMP, W_REC = 0.7, 0.2, 0.1
RECENCY_HALFLIFE_DAYS = 60.0

def recency_decay(created_at, now) -> float:
    age_days = max(0.0, (now - created_at).total_seconds() / 86400.0)
    return 0.5 ** (age_days / RECENCY_HALFLIFE_DAYS)

def _score(m, similarity, now) -> float:
    return W_SIM*similarity + W_IMP*(m.importance/5.0) + W_REC*recency_decay(m.created_at, now)

def rank(candidates: list[tuple[Memory, float]], *, now, k=8) -> list[Memory]:
    scored = [(m, _score(m, sim, now)) for m, sim in candidates]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [m for m, score in scored[:k]]

