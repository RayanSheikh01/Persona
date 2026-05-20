CREATE TABLE IF NOT EXISTS conversation_summaries (
  conversation_id TEXT PRIMARY KEY REFERENCES conversations(id) ON DELETE CASCADE,
  summary TEXT NOT NULL,
  summarized_through_message_id TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
