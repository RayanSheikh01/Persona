from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from persona.api.auth import verify_persona_key
from persona.deps import get_app_deps

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"],
    dependencies=[Depends(verify_persona_key)],
)


class ConversationOut(BaseModel):
    id: str
    title: str | None
    created_at: str
    last_message_at: str | None


class MessageOut(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: str


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ConversationOut)
def create_conversation() -> ConversationOut:
    deps = get_app_deps()
    conv_id = str(uuid4())
    now = _now_iso()
    deps.conn.execute(
        "INSERT INTO conversations (id, title, created_at, last_message_at) "
        "VALUES (?, NULL, ?, ?)",
        (conv_id, now, now),
    )
    deps.conn.commit()
    return ConversationOut(id=conv_id, title=None, created_at=now, last_message_at=now)


@router.get("", response_model=list[ConversationOut])
def list_conversations() -> list[ConversationOut]:
    deps = get_app_deps()
    rows = deps.conn.execute(
        "SELECT id, title, created_at, last_message_at "
        "FROM conversations ORDER BY last_message_at DESC"
    ).fetchall()
    return [ConversationOut(**dict(r)) for r in rows]


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
def list_messages(conversation_id: str) -> list[MessageOut]:
    deps = get_app_deps()
    exists = deps.conn.execute(
        "SELECT 1 FROM conversations WHERE id = ?", (conversation_id,)
    ).fetchone()
    if not exists:
        raise HTTPException(status_code=404, detail="conversation not found")
    rows = deps.conn.execute(
        "SELECT id, conversation_id, role, content, created_at "
        "FROM messages WHERE conversation_id = ? ORDER BY created_at",
        (conversation_id,),
    ).fetchall()
    return [MessageOut(**dict(r)) for r in rows]
