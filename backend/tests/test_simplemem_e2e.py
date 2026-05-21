from persona.memory.simplemem_adapter import SimpleMemAdapter


def test_e2e_with_simplemem(tmp_path, client, auth):
    simplemem_path = tmp_path / "simplemem_db"
    simplemem = SimpleMemAdapter(str(simplemem_path), clear=True)

    conv_id = client.post("/conversations", headers=auth).json()["id"]

    response = client.post(
        "/chat",
        headers=auth,
        json={"conversation_id": conv_id, "message": "Hello"},
    )
    assert response.status_code == 200

    simplemem.add_turn("user", "Hello", "2024-01-01T00:00:00Z")
    simplemem.add_turn("assistant", "hello", "2024-01-01T00:01:00Z")
    simplemem.finalize()
    retrieved = simplemem.ask("What did I say?")
    assert retrieved == "This is a placeholder response to the query: What did I say?"
