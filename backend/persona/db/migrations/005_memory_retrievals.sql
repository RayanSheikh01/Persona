CREATE TABLE IF NOT EXISTS memory_retrievals (
  message_id TEXT NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
  memory_id TEXT NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
  score REAL NOT NULL,
  rank INTEGER NOT NULL,
  PRIMARY KEY (message_id, memory_id)
);

CREATE INDEX IF NOT EXISTS idx_memory_retrievals_message ON memory_retrievals(message_id);
CREATE INDEX IF NOT EXISTS idx_memory_retrievals_memory ON memory_retrievals(memory_id);
