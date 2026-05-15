CREATE VIRTUAL TABLE IF NOT EXISTS memories_vec USING vec0(
  memory_id TEXT PRIMARY KEY,
  embedding FLOAT[768]
);
