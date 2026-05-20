from persona.memory.schema import MemoryCandidate



def drop_duplicates(
    candidates: list[MemoryCandidate],
    candidate_embeddings: list[list[float]],
    existing: list[tuple[str, str, list[float]]],   # (id, type, embedding)
    *, threshold: float, supersede_threshold: float,
) -> tuple[list[MemoryCandidate], list[tuple[int, str]]]:
    """
    Returns a deduplicated list of MemoryCandidates, along with a list of indices and ids of existing memories that should be superseded.
    """
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity

    if not candidates:
        return [], []
    candidate_matrix = np.array(candidate_embeddings)
    existing_ids, existing_types, existing_embeddings = zip(*existing) if existing else ([], [], [])
    existing_matrix = np.array(existing_embeddings) if existing else np.empty((0, len(candidate_embeddings[0])))

    if existing_matrix.size > 0:
        similarity = cosine_similarity(candidate_matrix, existing_matrix)
        to_keep = []
        to_supersede = []
        for i, candidate in enumerate(candidates):
            max_sim_idx = np.argmax(similarity[i])
            max_sim_score = similarity[i][max_sim_idx]
            if max_sim_score >= threshold:
                # Near-duplicate: drop candidate, record the pairing with the existing memory.
                to_supersede.append((i, existing_ids[max_sim_idx]))
                continue
            to_keep.append(candidate)
            if max_sim_score >= supersede_threshold:
                to_supersede.append((i, existing_ids[max_sim_idx]))
        return to_keep, to_supersede
    return candidates, []


