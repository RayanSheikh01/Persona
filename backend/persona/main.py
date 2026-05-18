from contextlib import asynccontextmanager

from fastapi import FastAPI

from persona.agent.prompts import load_prompt
from persona.api.conversations import router as conversations_router
from persona.api.health import router as health_router
from persona.api.chat import router as chat_router
from persona.api.memories import (
    messages_router as memory_messages_router,
    router as memories_router,
)
from persona.api.stats import router as stats_router
from persona.db.connection import get_db_connection
from persona.db.migrations.migrations import apply_migrations
from persona.deps import AppDeps, set_app_deps
from persona.llm.client import HFBackend, LLMClient
from persona.memory.store import MemoryStore
from persona.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    conn = get_db_connection()
    await apply_migrations(conn)

    backend = HFBackend(
        hf_token=settings.hf_token,
        chat_model=settings.hf_chat_model,
        embed_model=settings.hf_embed_model,
    )
    client = LLMClient(backend=backend)
    store = MemoryStore(conn)

    set_app_deps(
        AppDeps(
            conn=conn,
            store=store,
            client=client,
            system_prompt=load_prompt("system"),
            extract_prompt=load_prompt("extract"),
            title_prompt=load_prompt("title"),
        )
    )
    try:
        yield
    finally:
        conn.close()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(health_router)
    app.include_router(conversations_router)
    app.include_router(chat_router)
    app.include_router(memories_router)
    app.include_router(memory_messages_router)
    app.include_router(stats_router)
    return app


app = create_app()
