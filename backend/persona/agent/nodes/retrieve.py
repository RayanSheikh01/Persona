
from persona.agent import state
from persona.memory.store import vector_search


def make_retrieve_node(*, store, client, k=8, top_n=20, on_retrieved=None):

    async def retrieve(state):
        user_message = state['user_message']

        query_embedding = await client.embed(user_message)
        retrieved = vector_search(store._memory, query_embedding, top_k=k)

        # Optionally call a callback with the retrieved results
        if on_retrieved:
            on_retrieved(retrieved)

        return retrieved
    return retrieve