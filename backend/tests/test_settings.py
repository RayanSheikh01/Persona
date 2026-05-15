import pytest

@pytest.mark.asyncio
async def test_settings():
    from persona.settings import get_settings
    settings = get_settings()
    assert settings.hf_token == "hf_replace_me"
    assert settings.hf_chat_model == "meta-llama/Llama-3.1-8B-Instruct"
    assert settings.hf_embed_model == "sentence-transformers/all-mpnet-base-v2"
    assert settings.persona_api_key == "local-dev-shared-secret"
    assert settings.database_url == "sqlite:///data/persona.db"
    assert settings.persona_log_level == "INFO"

