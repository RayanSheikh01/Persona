import pytest


class FakeEmbedClient:
    def __init__(self, vector):
        self._vector = vector

    async def embed(self, text):
        return self._vector


@pytest.mark.asyncio
async def test_node_retrieve():
    from persona.memory.store import MemoryStore
    from persona.agent.nodes.retrieve import make_retrieve_node

    store = MemoryStore()
    embedding1 = {'type': 'text', 'content': 'Hello world', 'embedding': [0.1, 0.2, 0.3]}
    embedding2 = {'type': 'text', 'content': 'Goodbye world', 'embedding': [0.2, 0.3, 0.4]}
    store.insert(embedding1)
    store.insert(embedding2)

    client = FakeEmbedClient([0.1, 0.2, 0.3])
    retrieve_node = make_retrieve_node(store=store, client=client)

    state = {
        'user_message': "What is the content of the first embedding?",
        'assistant_message': "",
        'conversation_history': [],
    }
    retrieved = await retrieve_node(state)

    assert len(retrieved) > 0
    assert retrieved[0]['content'] == 'Hello world'
