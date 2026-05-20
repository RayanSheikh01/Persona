import json
import struct
from datetime import datetime
from sqlite3 import Connection
from typing import List, Optional, Tuple

from persona.memory.schema import Memory, MemoryType

EMBED_DIM = 768


def _pack(vec: List[float]) -> bytes:
    return struct.pack(f"{len(vec)}f", *vec)


def _unpack(blob: bytes) -> List[float]:
    n = len(blob) // 4
    return list(struct.unpack(f"{n}f", blob))


def _row_to_memory(row) -> Memory:
    return Memory(
        id=row["id"],
        type=row["type"],
        content=row["content"],
        importance=row["importance"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
        source_message_id=row["source_message_id"],
        source_conversation_id=row["source_conversation_id"],
        superseded_by=row["superseded_by"],
        related_ids=json.loads(row["related_ids"] or "[]"),
    )


class MemoryStore:
    def __init__(self, conn: Connection):
        self.conn = conn

    def insert(self, m: Memory, embedding: List[float]) -> None:
        if len(embedding) != EMBED_DIM:
            raise ValueError(f"embedding must be {EMBED_DIM}-d, got {len(embedding)}")
        self.conn.execute(
            """
            INSERT INTO memories (
                id, type, content, importance, created_at, updated_at,
                source_message_id, source_conversation_id, superseded_by, related_ids
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                m.id,
                m.type,
                m.content,
                m.importance,
                m.created_at.isoformat(),
                m.updated_at.isoformat(),
                m.source_message_id,
                m.source_conversation_id,
                m.superseded_by,
                json.dumps(m.related_ids),
            ),
        )
        self.conn.execute(
            "INSERT INTO memories_vec (memory_id, embedding) VALUES (?, ?)",
            (m.id, _pack(embedding)),
        )
        self.conn.execute(
            "INSERT INTO memories_fts (memory_id, content) VALUES (?, ?)",
            (m.id, m.content),
        )

    def get(self, id: str) -> Optional[Memory]:
        row = self.conn.execute(
            "SELECT * FROM memories WHERE id = ?", (id,)
        ).fetchone()
        return _row_to_memory(row) if row else None

    def list_by_type(
        self, type: MemoryType, *, include_superseded: bool = False, limit: int = 200
    ) -> List[Memory]:
        sql = "SELECT * FROM memories WHERE type = ?"
        if not include_superseded:
            sql += " AND superseded_by IS NULL"
        sql += " ORDER BY created_at DESC LIMIT ?"
        rows = self.conn.execute(sql, (type, limit)).fetchall()
        return [_row_to_memory(r) for r in rows]

    def list_all(
        self, *, include_superseded: bool = False, limit: int = 200, offset: int = 0
    ) -> List[Memory]:
        sql = "SELECT * FROM memories"
        if not include_superseded:
            sql += " WHERE superseded_by IS NULL"
        sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        rows = self.conn.execute(sql, (limit, offset)).fetchall()
        return [_row_to_memory(r) for r in rows]

    def vector_search(
        self, query: List[float], *, k: int = 20
    ) -> List[Tuple[str, float]]:
        rows = self.conn.execute(
            """
            SELECT memory_id, distance
            FROM memories_vec
            WHERE embedding MATCH ?
            ORDER BY distance
            LIMIT ?
            """,
            (_pack(query), k),
        ).fetchall()
        out = []
        for r in rows:
            sim = max(0.0, 1.0 - r["distance"] / 2.0)
            out.append((r["memory_id"], sim))
        return out

    def fts_search(self, q: str, *, k: int = 20) -> List[str]:
        rows = self.conn.execute(
            """
            SELECT memory_id FROM memories_fts
            WHERE content MATCH ?
            LIMIT ?
            """,
            (q, k),
        ).fetchall()
        return [r["memory_id"] for r in rows]

    def by_ids(self, ids: List[str]) -> List[Memory]:
        if not ids:
            return []
        placeholders = ",".join("?" * len(ids))
        rows = self.conn.execute(
            f"SELECT * FROM memories WHERE id IN ({placeholders})", ids
        ).fetchall()
        by_id = {r["id"]: _row_to_memory(r) for r in rows}
        return [by_id[i] for i in ids if i in by_id]

    def get_embedding(self, id: str) -> Optional[List[float]]:
        row = self.conn.execute(
            "SELECT embedding FROM memories_vec WHERE memory_id = ?", (id,)
        ).fetchone()
        return _unpack(row["embedding"]) if row else None
    
    def list_procedural(self, *, limit: int = 20) -> List[Memory]:
        rows = self.conn.execute(
            "SELECT * FROM memories WHERE type = 'procedural' ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [_row_to_memory(r) for r in rows]
    
    def set_superseded_by(self, memory_id: str, superseded_by: Optional[str]) -> None:
        self.conn.execute(
            "UPDATE memories SET superseded_by = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (superseded_by, memory_id)
        )
