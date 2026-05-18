import pytest

from persona.memory.schema import Memory

def test_stats_endpoint(client, auth, deps):
    # Insert some test data, created_at can't be null
    deps.conn.execute(
        "INSERT INTO conversations (id, created_at) VALUES (?, ?)",
        ("conv-1", "2024-01-01T00:00:00Z"),
    )
    deps.conn.execute(
        "INSERT INTO messages (id, conversation_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
        ("msg-1", "conv-1", "user", "Hello", "2024-01-01T00:00:00Z"),
    )
    deps.conn.execute(
        "INSERT INTO messages (id, conversation_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
        ("msg-2", "conv-1", "assistant", "Hi there!", "2024-01-01T00:01:00Z"),
    )
    deps.conn.execute(
        "INSERT INTO memories (id, type, content, importance, created_at, updated_at, source_message_id, source_conversation_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            "mem-1",
            "fact",
            "The sky is blue.",
            3,
            "2024-01-01T00:02:00Z",
            "2024-01-01T00:02:00Z",
            "msg-2",
            "conv-1",
        ),
    )
    deps.conn.commit()

    r = client.get("/stats", headers=auth)
    assert r.status_code == 200
    data = r.json()
    assert data["conversation_total"] == 1
    assert data["messages_total"] == 2
    assert data["memory_total"] == 1
    assert data["by_type"]["fact"] == 1
    assert data["last_activity"] == "2024-01-01T00:01:00Z"

def test_stats_endpoint_no_data(client, auth):
    r = client.get("/stats", headers=auth)
    assert r.status_code == 200
    data = r.json()
    assert data["conversation_total"] == 0
    assert data["messages_total"] == 0
    assert data["memory_total"] == 0
    assert data["by_type"] == {}
    assert data["last_activity"] is None

def test_stats_endpoint_requires_auth(client):
    r = client.get("/stats")
    assert r.status_code == 401


