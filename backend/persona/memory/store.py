class MemoryStore:
    def __init__(self):
        self._memory = {}

    def insert(self, embedding):
        self._memory[len(self._memory)] = embedding

    def get(self, id):
        return self._memory.get(id)

    def list_by_type(self, type):
        return [embedding for embedding in self._memory.values() if embedding['type'] == type]

    def list_all(self):
        return list(self._memory.values())

def vector_search(m, query_embedding, top_k=5):
    # Simple cosine similarity search
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
    # Simple full-text search on 'content' field
    results = []
    for embedding in m.values():
        if query.lower() in embedding['content'].lower():
            results.append(embedding)
    return results

def by_ids(m, ids):
    return [m[id] for id in ids if id in m]

def _row_to_memory(row):
    return {
        'id': row['id'],
        'type': row['type'],
        'content': row['content'],
        'embedding': row['embedding']
    }


