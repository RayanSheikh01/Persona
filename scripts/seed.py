"""Seed Persona with ~30 sample memories spanning all 5 types.

Run from repo root: `python scripts/seed.py`
First run downloads the embedder model (~400MB, cached).
"""
from __future__ import annotations

import asyncio
import os
import random
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "backend"))

from persona.db.connection import get_db_connection  # noqa: E402
from persona.db.migrations.migrations import apply_migrations  # noqa: E402
from persona.memory.schema import Memory  # noqa: E402
from persona.memory.store import MemoryStore  # noqa: E402


SEED_CONVERSATION_ID = "seed-conversation"
SEED_MESSAGE_ID = "seed-message"

SEEDS: list[tuple[str, str, int]] = [
    # profile (6)
    ("profile", "User's name is Rayan.", 5),
    ("profile", "User is a software engineer based in Toronto.", 4),
    ("profile", "User has been programming for about 7 years.", 3),
    ("profile", "User's primary languages are Python and TypeScript.", 4),
    ("profile", "User works remotely most days.", 2),
    ("profile", "User is a vegetarian.", 3),
    # preference (6)
    ("preference", "Prefers terse, direct responses without preamble.", 5),
    ("preference", "Likes dark-mode interfaces with monospace headings.", 3),
    ("preference", "Drinks black coffee, no sugar.", 2),
    ("preference", "Prefers pytest over unittest for Python testing.", 4),
    ("preference", "Avoids meetings before 10am.", 4),
    ("preference", "Likes ambient music when coding deep work sessions.", 2),
    # fact (6)
    ("fact", "User owns a small dog named Pip.", 4),
    ("fact", "User's partner is named Sam.", 5),
    ("fact", "User lives in a one-bedroom apartment near High Park.", 3),
    ("fact", "User drives a 2018 Honda Civic.", 2),
    ("fact", "User's sister works as a nurse in Vancouver.", 3),
    ("fact", "User is allergic to shellfish.", 5),
    # goal (6)
    ("goal", "Wants to launch a side project this quarter.", 5),
    ("goal", "Learning Rust in evenings; finish the book by end of summer.", 4),
    ("goal", "Run a half-marathon in October.", 4),
    ("goal", "Save 15% of income toward a house down payment.", 5),
    ("goal", "Read at least one book per month this year.", 3),
    ("goal", "Get conversational in French before next year's trip to Montreal.", 3),
    # event (6)
    ("event", "Started a new role on 2026-01-12.", 4),
    ("event", "Adopted Pip from the local shelter on 2025-03-20.", 4),
    ("event", "Moved into current apartment in autumn 2024.", 3),
    ("event", "Attended PyCon US 2025 in Pittsburgh.", 3),
    ("event", "Completed first 10k race on 2026-04-05.", 4),
    ("event", "Visited family in Lahore over the 2025 winter holidays.", 3),
]


def _ensure_seed_conversation_and_message(conn) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT OR IGNORE INTO conversations (id, title, created_at, last_message_at) "
        "VALUES (?, ?, ?, ?)",
        (SEED_CONVERSATION_ID, "Seed data", now, now),
    )
    conn.execute(
        "INSERT OR IGNORE INTO messages (id, conversation_id, role, content, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (SEED_MESSAGE_ID, SEED_CONVERSATION_ID, "user", "[seed]", now),
    )
    conn.commit()


async def main() -> None:
    from sentence_transformers import SentenceTransformer

    embed_model_id = os.environ.get(
        "HF_EMBED_MODEL", "sentence-transformers/all-mpnet-base-v2"
    )
    print(f"Loading embedder: {embed_model_id} (first run downloads ~400MB)...")
    embedder = SentenceTransformer(embed_model_id)

    conn = get_db_connection()
    try:
        await apply_migrations(conn)
        _ensure_seed_conversation_and_message(conn)

        store = MemoryStore(conn)
        rng = random.Random(42)
        now = datetime.now(timezone.utc)

        inserted = 0
        for mtype, content, importance in SEEDS:
            age_days = rng.uniform(0, 90)
            created = now - timedelta(days=age_days)
            embedding = embedder.encode(content, normalize_embeddings=True).tolist()
            store.insert(
                Memory(
                    id=str(uuid.uuid4()),
                    type=mtype,
                    content=content,
                    importance=importance,
                    created_at=created,
                    updated_at=created,
                    source_message_id=SEED_MESSAGE_ID,
                    source_conversation_id=SEED_CONVERSATION_ID,
                ),
                embedding,
            )
            inserted += 1
        conn.commit()
        print(f"Inserted {inserted} memories across 5 types.")
    finally:
        conn.close()


if __name__ == "__main__":
    asyncio.run(main())
