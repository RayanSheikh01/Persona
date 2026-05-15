from fastapi import Header, HTTPException
from persona.settings import get_settings

settings = get_settings()
PERSONA_KEY = settings.persona_api_key

def verify_persona_key(x_persona_key: str | None = Header(default=None)):
    if x_persona_key is None:
        raise HTTPException(status_code=401, detail="Missing X-Persona-Key header")
    if x_persona_key != PERSONA_KEY:
        raise HTTPException(status_code=403, detail="Invalid X-Persona-Key")
    if x_persona_key == PERSONA_KEY:
        return True