import json
import uuid
from datetime import datetime, timezone
from typing import Any

from persona.memory.schema import Memory


def _parse_sse(response) -> list[tuple[str, Any]]:
    """Pair each `event: NAME` line with the following `data: JSON` payload."""
    events: list[tuple[str, Any]] = []
    current_event: str | None = None
    for raw in response.iter_lines():
        line = raw if isinstance(raw, str) else raw.decode("utf-8")
        if not line:
            current_event = None
            continue
        if line.startswith("event:"):
            current_event = line[len("event:") :].strip()
        elif line.startswith("data:") and current_event is not None:
            payload = line[len("data:") :].strip()
            events.append((current_event, json.loads(payload)))
            current_event = None
    return events


def _create_conversation(client, auth) -> str:
    return client.post("/conversations", headers=auth).json()["id"]


def test_chat_stream_emits_tokens_and_done(client, auth, deps):
    deps.client.backend.chat_chunks = ["hello", " world"]
    conv_id = _create_conversation(client, auth)

    r = client.post(
        "/chat",
        headers=auth,
        json={"conversation_id": conv_id, "message": "Hi"},
    )
    assert r.status_code == 200

    events = _parse_sse(r)
    kinds = [e for e, _ in events]
    assert "token" in kinds
    assert kinds[-1] == "done"

    tokens = [data for kind, data in events if kind == "token"]
    assert tokens == ["hello", " world"]

    done_payload = events[-1][1]
    assert done_payload["user_message_id"]
    assert done_payload["assistant_message_id"]

    # The persist node actually wrote both messages.
    rows = deps.conn.execute(
        "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY created_at",
        (conv_id,),
    ).fetchall()
    assert [r["role"] for r in rows] == ["user", "assistant"]
    assert rows[0]["content"] == "Hi"
    assert rows[1]["content"] == "hello world"


def test_chat_unknown_conversation_returns_404(client, auth):
    r = client.post(
        "/chat",
        headers=auth,
        json={"conversation_id": "does-not-exist", "message": "Hello"},
    )
    assert r.status_code == 404


def test_chat_requires_auth(client):
    r = client.post(
        "/chat",
        json={"conversation_id": "some-id", "message": "Hello"},
    )
    assert r.status_code == 401


def test_chat_retrieved_event_includes_inserted_memory(client, auth, deps):
    # Pin the fake embedder to a known unit vector so the inserted memory
    # is the closest neighbor of the query embedding.
    embedding = [1.0] + [0.0] * 767
    deps.client.backend.embedding = embedding

    conv_id = _create_conversation(client, auth)
    mem_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    deps.store.insert(
        Memory(
            id=mem_id,
            type="fact",
            content="Relevant past memory",
            importance=3,
            created_at=now,
            updated_at=now,
            source_message_id="seed",
            source_conversation_id=conv_id,
        ),
        embedding,
    )
    deps.conn.commit()

    r = client.post(
        "/chat",
        headers=auth,
        json={"conversation_id": conv_id, "message": "Hello"},
    )
    assert r.status_code == 200

    events = _parse_sse(r)
    retrieved = [data for kind, data in events if kind == "retrieved"]
    assert retrieved, "expected at least one 'retrieved' event"
    assert mem_id in retrieved[0]


def test_chat_propagates_backend_failure_as_error_event(client, auth, deps):
    conv_id = _create_conversation(client, auth)

    async def boom(_text: str):
        raise RuntimeError("LLM failure")

    deps.client.backend.embed = boom  # retrieve node calls embed first

    r = client.post(
        "/chat",
        headers=auth,
        json={"conversation_id": conv_id, "message": "Hello"},
    )
    assert r.status_code == 200

    events = _parse_sse(r)
    kinds = [e for e, _ in events]
    assert "error" in kinds
    error_payload = next(d for k, d in events if k == "error")
    assert "LLM failure" in error_payload["detail"]


def test_chat_no_token_events_when_backend_yields_nothing(client, auth, deps):
    deps.client.backend.chat_chunks = []
    conv_id = _create_conversation(client, auth)

    r = client.post(
        "/chat",
        headers=auth,
        json={"conversation_id": conv_id, "message": "Hello"},
    )
    assert r.status_code == 200

    events = _parse_sse(r)
    assert not [d for k, d in events if k == "token"]
    assert events[-1][0] == "done"


def test_chat_sets_conversation_title(client, auth, deps):
    conv_id = _create_conversation(client, auth)

    # Conversation starts with no title
    r = client.get("/conversations", headers=auth)
    conv = next(c for c in r.json() if c["id"] == conv_id)
    assert conv["title"] is None

    # After first chat message, title should be set to first 5 words of that message
    r = client.post(
        "/chat",
        headers=auth,
        json={"conversation_id": conv_id, "message": "This is a test message to set the title"},
    )
    assert r.status_code == 200

    r = client.get("/conversations", headers=auth)
    conv = next(c for c in r.json() if c["id"] == conv_id)
    assert conv["title"] == "This is a test message to set the title"[:100]