import pytest

@pytest.mark.asyncio
async def test_auth():
    from persona.api.auth import verify_persona_key
    from persona.settings import get_settings

    settings = get_settings()
    PERSONA_KEY = settings.persona_api_key

    # Test missing header
    try:
        verify_persona_key(None)
    except Exception as e:
        assert e.status_code == 401

    # Test invalid key
    try:
        verify_persona_key("invalid_key")
    except Exception as e:
        assert e.status_code == 403

    # Test valid key
    assert verify_persona_key(PERSONA_KEY) is True