import pytest

@pytest.mark.asyncio
async def test_memory_summaries():
    from persona.memory.summaries import ConversationSummaryStore
    from persona.db.connection import get_db_connection

    conn = get_db_connection()
    store = ConversationSummaryStore(conn)

    conversation_id = "test_conversation"
    summary = "This is a test summary."
    message_id = "test_message"

    # Test upsert
    store.upsert(conversation_id, summary, message_id)
    retrieved = store.get(conversation_id)
    assert retrieved is not None
    assert retrieved.conversation_id == conversation_id
    assert retrieved.summary == summary
    assert retrieved.summarized_through_message_id == message_id


    new_summary = "This is an updated summary."
    store.upsert(conversation_id, new_summary, message_id)
    updated = store.get(conversation_id)
    assert updated is not None
    assert updated.conversation_id == conversation_id
    assert updated.summary == new_summary
    assert updated.summarized_through_message_id == message_id



@pytest.mark.asyncio
async def test_memory_summaries_no_prior():
    from persona.memory.summaries import ConversationSummaryStore
    from persona.db.connection import get_db_connection

    conn = get_db_connection()
    store = ConversationSummaryStore(conn)

    conversation_id = "new_conversation"
    retrieved = store.get(conversation_id)
    assert retrieved is None