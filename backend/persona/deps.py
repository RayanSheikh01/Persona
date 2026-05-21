from dataclasses import dataclass
from sqlite3 import Connection
from typing import Optional

from persona.llm.client import LLMClient
from persona.memory.store import MemoryStore
from persona.memory.simplemem_adapter import SimpleMemAdapter


@dataclass
class AppDeps:
    conn: Connection
    store: MemoryStore
    client: LLMClient
    system_prompt: str
    extract_prompt: str
    title_prompt: str
    simplemem: SimpleMemAdapter | None


_deps: Optional[AppDeps] = None


def set_app_deps(deps: AppDeps) -> None:
    global _deps
    _deps = deps


def get_app_deps() -> AppDeps:
    if _deps is None:
        raise RuntimeError("AppDeps not initialized")
    return _deps

def get_summary_store():
    deps = get_app_deps()
    from persona.memory.summaries import ConversationSummaryStore

    return ConversationSummaryStore(deps.conn)