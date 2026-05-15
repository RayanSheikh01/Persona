CREATE TABLE IF NOT EXISTS conversations (
  id TEXT PRIMARY KEY,
  title TEXT,
  created_at TEXT NOT NULL,
  last_message_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_conversations_last_message_at
  ON conversations(last_message_at DESC);
