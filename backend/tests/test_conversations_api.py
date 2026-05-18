def test_create_conversation(client, auth):
    r = client.post("/conversations", headers=auth)
    assert r.status_code == 201
    body = r.json()
    assert "id" in body
    assert body["title"] is None
    assert body["created_at"]
    assert body["last_message_at"]


def test_list_conversations(client, auth):
    r = client.post("/conversations", headers=auth)
    created_id = r.json()["id"]

    r = client.get("/conversations", headers=auth)
    assert r.status_code == 200
    items = r.json()
    assert any(c["id"] == created_id for c in items)


def test_list_messages_empty(client, auth):
    conv_id = client.post("/conversations", headers=auth).json()["id"]
    r = client.get(f"/conversations/{conv_id}/messages", headers=auth)
    assert r.status_code == 200
    assert r.json() == []


def test_list_messages_unknown_conversation(client, auth):
    r = client.get("/conversations/does-not-exist/messages", headers=auth)
    assert r.status_code == 404


def test_auth_required(client):
    assert client.post("/conversations").status_code == 401
