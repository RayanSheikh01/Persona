

from datetime import datetime
from persona.db.connection import get_db_connection

conn = get_db_connection()



class ConversationSummary():
    conversation_id: str
    summary: str
    summarized_through_message_id: str
    updated_at: datetime

    def __init__(self, conversation_id: str, summary: str, summarized_through_message_id: str, updated_at: datetime):
        self.conversation_id = conversation_id
        self.summary = summary
        self.summarized_through_message_id = summarized_through_message_id
        self.updated_at = updated_at

class ConversationSummaryStore():

    def __init__(self, connection):
        self.conn = connection

    def get(self, conversation_id: str) -> ConversationSummary | None:
        row = self.conn.execute(
            "SELECT conversation_id, summary, summarized_through_message_id, updated_at "
            "FROM conversation_summaries WHERE conversation_id = ?",
            (conversation_id,)
        ).fetchone()
        if row is None:
            return None
        return ConversationSummary(
            conversation_id=row['conversation_id'],
            summary=row['summary'],
            summarized_through_message_id=row['summarized_through_message_id'],
            updated_at=datetime.fromisoformat(row['updated_at'])
        )
    
    def upsert(self, conversation_id: str, summary: str, summarized_through_message_id: str) -> None:
        self.conn.execute(
            "INSERT INTO conversations (id, created_at) VALUES (?, CURRENT_TIMESTAMP) ON CONFLICT(id) DO NOTHING",
            (conversation_id,)
        )

        self.conn.execute(
            "INSERT INTO conversation_summaries (conversation_id, summary, summarized_through_message_id, updated_at) "
            "VALUES (?, ?, ?, CURRENT_TIMESTAMP) "

            
            "ON CONFLICT(conversation_id) DO UPDATE SET " 
            "summary = excluded.summary, "
            "summarized_through_message_id = excluded.summarized_through_message_id, "
            "updated_at = CURRENT_TIMESTAMP",
            (conversation_id, summary, summarized_through_message_id)
        )

