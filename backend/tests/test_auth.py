import pytest
from fastapi import HTTPException

from persona.api.auth import verify_persona_key
from persona.settings import get_settings


def test_missing_header_returns_401():
    with pytest.raises(HTTPException) as exc:
        verify_persona_key(None)
    assert exc.value.status_code == 401


def test_wrong_key_returns_401():
    with pytest.raises(HTTPException) as exc:
        verify_persona_key("invalid_key")
    assert exc.value.status_code == 401


def test_correct_key_returns_true():
    assert verify_persona_key(get_settings().persona_api_key) is True
