from datetime import datetime

from persona.memory.schema import Memory

W_SIM, W_IMP, W_REC = 0.7, 0.2, 0.1
RECENCY_HALFLIFE_DAYS = 60.0


def recency_decay(created_at: datetime, now: datetime) -> float:
    age_days = max(0.0, (now - created_at).total_seconds() / 86400.0)
    return 0.5 ** (age_days / RECENCY_HALFLIFE_DAYS)


def _score(m: Memory, similarity: float, now: datetime) -> float:
    return (
        W_SIM * similarity
        + W_IMP * (m.importance / 5.0)
        + W_REC * recency_decay(m.created_at, now)
    )


def rank(
    candidates: list[tuple[Memory, float]], *, now: datetime, k: int = 8
) -> list[tuple[Memory, float]]:
    active = [(m, sim) for m, sim in candidates if m.superseded_by is None]
    scored = [(m, sim, _score(m, sim, now)) for m, sim in active]
    scored.sort(key=lambda x: (x[2], x[0].importance, x[0].created_at), reverse=True)
    return [(m, sim) for m, sim, _ in scored[:k]]
