from typing import cast

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from persona.api.auth import verify_persona_key
from persona.deps import get_app_deps
from persona.memory.schema import MEMORY_TYPES, Memory, MemoryType

router = APIRouter(
    prefix="/memories", tags=["memories"], dependencies=[Depends(verify_persona_key)]
)

messages_router = APIRouter(
    prefix="/messages", tags=["memories"], dependencies=[Depends(verify_persona_key)]
)


class MemoriesList(BaseModel):
    items: list[Memory]
    next_cursor: int | None = None


@router.get("", response_model=MemoriesList)
async def list_memories(
    type: str | None = None,
    q: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    cursor: int = Query(0, ge=0),
    include_superseded: bool = False,
):
    if type is not None and type not in MEMORY_TYPES:
        raise HTTPException(status_code=400, detail="invalid memory type")

    deps = get_app_deps()

    if q:
        query_embedding = await deps.client.embed(q)
        hits = deps.store.vector_search(query_embedding, k=limit + cursor)
        ids = [mid for mid, _ in hits][cursor : cursor + limit]
        items = deps.store.by_ids(ids)
        if type is not None:
            items = [m for m in items if m.type == type]
        if not include_superseded:
            items = [m for m in items if m.superseded_by is None]
    elif type is not None:
        items = deps.store.list_by_type(
            cast(MemoryType, type),
            include_superseded=include_superseded,
            limit=limit,
        )
    else:
        items = deps.store.list_all(
            include_superseded=include_superseded, limit=limit, offset=cursor
        )

    next_cursor = cursor + limit if len(items) == limit else None
    return MemoriesList(items=items, next_cursor=next_cursor)


@router.get("/{memory_id}", response_model=Memory)
def get_memory(memory_id: str) -> Memory:
    deps = get_app_deps()
    m = deps.store.get(memory_id)
    if m is None:
        raise HTTPException(status_code=404, detail="memory not found")
    return m


@messages_router.get("/{message_id}/retrievals", response_model=list[Memory])
def get_retrievals(message_id: str) -> list[Memory]:
    deps = get_app_deps()
    rows = deps.conn.execute(
        "SELECT memory_id FROM memory_retrievals WHERE message_id = ? ORDER BY rank",
        (message_id,),
    ).fetchall()
    ids = [r["memory_id"] for r in rows]
    return deps.store.by_ids(ids)
