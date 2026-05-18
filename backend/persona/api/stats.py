from fastapi import APIRouter, Depends

from persona.api.auth import verify_persona_key
from persona.deps import get_app_deps

router = APIRouter(prefix="/stats", tags=["stats"], dependencies=[Depends(verify_persona_key)])

@router.get("")
async def get_stats():
    memory_total = 0
    conversation_total = 0
    messages_total = 0

    # get memory total
    deps = get_app_deps()
    row = deps.conn.execute("SELECT COUNT(*) AS total FROM memories").fetchone()
    if row:
        memory_total = row["total"]

    # get conversation total
    row = deps.conn.execute("SELECT COUNT(*) AS total FROM conversations").fetchone()
    if row:
        conversation_total = row["total"]

    # get messages total
    row = deps.conn.execute("SELECT COUNT(*) AS total FROM messages").fetchone()
    if row:
        messages_total = row["total"]

    by_type = {}
    for t in deps.conn.execute("SELECT type, COUNT(*) AS total FROM memories GROUP BY type"):
        by_type[t["type"]] = t["total"]

    last_activity = deps.conn.execute(
        "SELECT created_at FROM messages ORDER BY created_at DESC LIMIT 1"
    ).fetchone()

    return {
        "memory_total": memory_total,
        "conversation_total": conversation_total,
        "messages_total": messages_total,
        "by_type": by_type,
        "last_activity": last_activity["created_at"] if last_activity else None
    }