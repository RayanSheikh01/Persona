PRAGMA foreign_keys=OFF;

CREATE TABLE memories_new (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL CHECK (type IN ('profile','preference','fact','goal','event','procedural')),
  content TEXT NOT NULL,
  importance INTEGER NOT NULL CHECK (importance BETWEEN 1 AND 5),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  source_message_id TEXT NOT NULL,
  source_conversation_id TEXT NOT NULL,
  superseded_by TEXT REFERENCES memories(id),
  related_ids TEXT NOT NULL DEFAULT '[]'
);

INSERT INTO memories_new SELECT * FROM memories;

DROP TABLE memories;
ALTER TABLE memories_new RENAME TO memories;

CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type);
CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at);
CREATE INDEX IF NOT EXISTS idx_memories_superseded ON memories(superseded_by);

PRAGMA foreign_keys=ON;
