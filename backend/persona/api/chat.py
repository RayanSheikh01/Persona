import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from persona.agent.graph import build_graph
from persona.api.auth import verify_persona_key
from persona.deps import get_app_deps

router = APIRouter(
    prefix="/chat", tags=["chat"], dependencies=[Depends(verify_persona_key)]
)


class ChatIn(BaseModel):
    conversation_id: str
    message: str


def _sse(event: str, data) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@router.post("")
async def chat(body: ChatIn):
    deps = get_app_deps()

    exists = deps.conn.execute(
        "SELECT 1 FROM conversations WHERE id = ?", (body.conversation_id,)
    ).fetchone()
    if not exists:
        raise HTTPException(status_code=404, detail="conversation not found")

    rows = deps.conn.execute(
        "SELECT role, content FROM messages WHERE conversation_id = ? "
        "ORDER BY created_at",
        (body.conversation_id,),
    ).fetchall()
    history = [{"role": r["role"], "content": r["content"]} for r in rows]

    events: asyncio.Queue = asyncio.Queue()

    async def on_token(chunk: str) -> None:
        await events.put(("token", chunk))

    async def on_retrieved(memories) -> None:
        await events.put(("retrieved", [m.id for m in memories]))

    graph = build_graph(
        conn=deps.conn,
        store=deps.store,
        client=deps.client,
        system_prompt=deps.system_prompt,
        extract_prompt=deps.extract_prompt,
        on_token=on_token,
        on_retrieved=on_retrieved,
    )

    async def run() -> None:
        try:
            result = await graph.ainvoke(
                {
                    "conversation_id": body.conversation_id,
                    "history": history,
                    "user_message": body.message,
                }
            )
            await events.put(
                (
                    "done",
                    {
                        "user_message_id": result.get("user_message_id"),
                        "assistant_message_id": result.get("assistant_message_id"),
                        "new_memory_ids": result.get("new_memory_ids", []),
                    },
                )
            )
        except Exception as e:
            await events.put(("error", {"detail": str(e)}))
        finally:
            await events.put((None, None))

    async def stream():
        task = asyncio.create_task(run())
        try:
            while True:
                kind, data = await events.get()
                if kind is None:
                    break
                yield _sse(kind, data)
        finally:
            await task
            # if conversation has 2 messages and title is null, set title to first 5 words of first message
            deps.conn.execute(
                "UPDATE conversations SET title = substr(?, 1, 100) "
                "WHERE id = ? AND title IS NULL AND "
                "(SELECT COUNT(*) FROM messages WHERE conversation_id = ?) = 2",
                (body.message[:100], body.conversation_id, body.conversation_id),
            )
            deps.conn.commit()

    return StreamingResponse(stream(), media_type="text/event-stream")
