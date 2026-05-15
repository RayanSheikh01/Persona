CREATE TABLE IF NOT EXISTS memories (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL CHECK (type IN ('profile','preference','fact','goal','event')),
  content TEXT NOT NULL,
  importance INTEGER NOT NULL CHECK (importance BETWEEN 1 AND 5),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  source_message_id TEXT NOT NULL,
  source_conversation_id TEXT NOT NULL,
  superseded_by TEXT REFERENCES memories(id),
  related_ids TEXT NOT NULL DEFAULT '[]'
);

CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type);
CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at);
CREATE INDEX IF NOT EXISTS idx_memories_superseded ON memories(superseded_by);
