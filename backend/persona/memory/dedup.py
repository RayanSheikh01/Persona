from persona.memory.schema import MemoryCandidate


def drop_duplicates(
    candidates: list[MemoryCandidate],
    candidate_embeddings: list[list[float]],
    existing_same_type: list[tuple[str, list[float]]],
    *, threshold: float = 0.92,
) -> list[MemoryCandidate]:
    def cosine_similarity(vec1, vec2):
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        return dot_product / (norm1 * norm2) if norm1 and norm2 else 0.0

    filtered: list[MemoryCandidate] = []
    kept_embeddings: list[list[float]] = []
    for candidate, embedding in zip(candidates, candidate_embeddings):
        is_duplicate = any(
            cosine_similarity(embedding, existing) >= threshold
            for _, existing in existing_same_type
        ) or any(
            cosine_similarity(embedding, kept) >= threshold
            for kept in kept_embeddings
        )
        if not is_duplicate:
            filtered.append(candidate)
            kept_embeddings.append(embedding)
    return filtered

