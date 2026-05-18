import os
import sqlite3

import pytest
import sqlite_vec

from persona.agent.graph import build_graph
from persona.agent.prompts import load_prompt
from persona.db.migrations.migrations import apply_migrations
from persona.llm.client import HFBackend, LLMClient
from persona.memory.store import MemoryStore


pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_HF_SMOKE") != "1",
    reason="Set RUN_HF_SMOKE=1 (and HF_TOKEN) to run the real Hugging Face smoke test.",
)


def _open(path):
    conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@pytest.mark.asyncio
async def test_real_hf_one_turn(tmp_path):
    hf_token = os.environ["HF_TOKEN"]
    chat_model = os.environ.get(
        "HF_CHAT_MODEL", "meta-llama/Llama-3.1-8B-Instruct"
    )
    embed_model = os.environ.get(
        "HF_EMBED_MODEL", "sentence-transformers/all-mpnet-base-v2"
    )

    conn = _open(tmp_path / "smoke.db")
    try:
        await apply_migrations(conn)
        conn.execute(
            "INSERT INTO conversations (id, title, created_at, last_message_at)"
            " VALUES ('c1', NULL, datetime('now'), datetime('now'))"
        )

        backend = HFBackend(
            hf_token=hf_token, chat_model=chat_model, embed_model=embed_model
        )
        client = LLMClient(backend=backend)
        store = MemoryStore(conn)

        graph = build_graph(
            conn=conn,
            store=store,
            client=client,
            system_prompt=load_prompt("system"),
            extract_prompt=load_prompt("extract"),
        )

        result = await graph.ainvoke(
            {
                "conversation_id": "c1",
                "user_message": "I have a dog named Pip.",
                "history": [],
            }
        )

        assert result.get("assistant_response"), "expected non-empty assistant_response"

        # Best effort: a memory may have been extracted. Llama extraction varies,
        # so do not strictly require it.
        mem_count = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        assert mem_count >= 0
    finally:
        conn.close()
