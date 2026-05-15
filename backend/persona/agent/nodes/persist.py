def make_persist_node(*, conn, store, client, dedup_threshold=0.92):
    async def persist_node(user_input, assistant_response, memories):
        try:
            # Combine user input and assistant response for embedding
            combined_text = f"User: {user_input}\nAssistant: {assistant_response}"
            embedding = await client.get_embedding(combined_text)

            # Check for duplicates
            existing_memories = await store.retrieve_memories(conn, embedding, top_k=5)
            for mem in existing_memories:
                similarity = await client.compute_similarity(embedding, mem['embedding'])
                if similarity > dedup_threshold:
                    print(f"Duplicate memory found with similarity {similarity:.2f}. Skipping persist.")
                    return

            # Persist new memory
            await store.persist_memory(conn, content=combined_text, embedding=embedding)
        except Exception as e:
            print(f"Error in persist_node: {e}")
    return persist_node