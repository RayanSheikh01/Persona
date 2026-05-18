from dataclasses import dataclass
from sqlite3 import Connection
from typing import Optional

from persona.llm.client import LLMClient
from persona.memory.store import MemoryStore


@dataclass
class AppDeps:
    conn: Connection
    store: MemoryStore
    client: LLMClient
    system_prompt: str
    extract_prompt: str
    title_prompt: str


_deps: Optional[AppDeps] = None


def set_app_deps(deps: AppDeps) -> None:
    global _deps
    _deps = deps


def get_app_deps() -> AppDeps:
    if _deps is None:
        raise RuntimeError("AppDeps not initialized")
    return _deps
