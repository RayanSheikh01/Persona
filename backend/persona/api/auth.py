from fastapi import Header, HTTPException
from persona.settings import get_settings


def verify_persona_key(x_persona_key: str | None = Header(default=None)):
    if x_persona_key is None:
        raise HTTPException(status_code=401, detail="Missing X-Persona-Key header")
    if x_persona_key != get_settings().persona_api_key:
        raise HTTPException(status_code=401, detail="Invalid X-Persona-Key")
    return True