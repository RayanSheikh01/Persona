import asyncio
import sqlite3

import pytest
from fastapi.testclient import TestClient

from persona.db.migrations.migrations import apply_migrations
from persona.deps import AppDeps, set_app_deps
from persona.llm.client import FakeLLMBackend, LLMClient
from persona.main import create_app
from persona.memory.store import MemoryStore


@pytest.fixture
def deps(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("HF_TOKEN", "test-token")
    monkeypatch.setenv("PERSONA_API_KEY", "test-key")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys=ON")

    asyncio.run(apply_migrations(conn))

    backend = FakeLLMBackend(
        chat_chunks=["hello"],
        embedding=[0.0] * 768,
        extraction=[],
    )
    app_deps = AppDeps(
        conn=conn,
        store=MemoryStore(conn),
        client=LLMClient(backend=backend),
        system_prompt="",
        extract_prompt="",
        title_prompt="",
    )
    set_app_deps(app_deps)
    yield app_deps
    conn.close()


@pytest.fixture
def client(deps):
    # No `with` block: skip the lifespan so HFBackend / real DB are never built.
    return TestClient(create_app())


@pytest.fixture
def auth():
    return {"X-Persona-Key": "test-key"}
