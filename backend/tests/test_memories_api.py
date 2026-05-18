import uuid
from datetime import datetime, timezone

from persona.memory.schema import Memory


def _make_memory(
    *,
    type: str = "fact",
    content: str = "a memory",
    importance: int = 3,
    source_conversation_id: str = "conv-1",
) -> Memory:
    now = datetime.now(timezone.utc)
    return Memory(
        id=str(uuid.uuid4()),
        type=type,  # type: ignore[arg-type]
        content=content,
        importance=importance,
        created_at=now,
        updated_at=now,
        source_message_id="seed",
        source_conversation_id=source_conversation_id,
    )


def test_list_filters_by_type(client, auth, deps):
    fact = _make_memory(type="fact", content="sky is blue")
    goal = _make_memory(type="goal", content="learn rust")
    deps.store.insert(fact, [0.1] * 768)
    deps.store.insert(goal, [0.1] * 768)

    r = client.get("/memories?type=fact", headers=auth)
    assert r.status_code == 200
    body = r.json()
    ids = [m["id"] for m in body["items"]]
    assert fact.id in ids
    assert goal.id not in ids


def test_list_returns_all_when_no_filter(client, auth, deps):
    m1 = _make_memory(content="one")
    m2 = _make_memory(content="two")
    deps.store.insert(m1, [0.1] * 768)
    deps.store.insert(m2, [0.1] * 768)

    r = client.get("/memories", headers=auth)
    assert r.status_code == 200
    ids = [m["id"] for m in r.json()["items"]]
    assert m1.id in ids and m2.id in ids


def test_list_rejects_invalid_type(client, auth):
    r = client.get("/memories?type=bogus", headers=auth)
    assert r.status_code == 400


def test_get_memory_by_id(client, auth, deps):
    m = _make_memory(content="hello world")
    deps.store.insert(m, [0.1] * 768)

    r = client.get(f"/memories/{m.id}", headers=auth)
    assert r.status_code == 200
    got = Memory(**r.json())
    assert got.id == m.id
    assert got.content == "hello world"
    assert got.type == "fact"


def test_get_nonexistent_memory_returns_404(client, auth):
    r = client.get("/memories/does-not-exist", headers=auth)
    assert r.status_code == 404


def test_retrievals_returns_memories_for_message(client, auth, deps):
    m = _make_memory(content="retrieved memory")
    deps.store.insert(m, [0.1] * 768)

    conv_id = str(uuid.uuid4())
    msg_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    deps.conn.execute(
        "INSERT INTO conversations (id, created_at, last_message_at) VALUES (?, ?, ?)",
        (conv_id, now, now),
    )
    deps.conn.execute(
        "INSERT INTO messages (id, conversation_id, role, content, created_at) "
        "VALUES (?, ?, 'user', 'hi', ?)",
        (msg_id, conv_id, now),
    )
    deps.conn.execute(
        "INSERT INTO memory_retrievals (message_id, memory_id, score, rank) "
        "VALUES (?, ?, ?, ?)",
        (msg_id, m.id, 0.95, 0),
    )
    deps.conn.commit()

    r = client.get(f"/messages/{msg_id}/retrievals", headers=auth)
    assert r.status_code == 200
    items = r.json()
    assert [it["id"] for it in items] == [m.id]


def test_retrievals_empty_when_no_rows(client, auth):
    msg_id = str(uuid.uuid4())
    r = client.get(f"/messages/{msg_id}/retrievals", headers=auth)
    assert r.status_code == 200
    assert r.json() == []


def test_memories_require_auth(client):
    assert client.get("/memories").status_code == 401
    assert client.get("/memories/some-id").status_code == 401
    assert client.get("/messages/some-id/retrievals").status_code == 401
