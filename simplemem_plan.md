# SimpleMem Integration Plan

> Add [SimpleMem](https://github.com/aiming-lab/SimpleMem) as an alternative long-term memory backend alongside the existing typed SQLite store.

**Goal:** Replace (or run in parallel with) the current `retrieve → respond → extract → persist` memory path with SimpleMem's three-stage pipeline: `add_dialogue → finalize → ask`.

**Why:** Higher F1 on long-context recall, ~98% token reduction, atomic-fact entries with resolved coreferences & absolute timestamps.

**Strategy:** Wrap `SimpleMemSystem` behind a thin adapter that matches the existing `MemoryStore` retrieval surface so the LangGraph nodes stay unchanged. Gate via a `MEMORY_BACKEND=simplemem|sqlite` setting.

---

## File Map

`[C]` create, `[M]` modify.

```text
backend/
├── pyproject.toml                              [M]  add `simplemem` dep
├── persona/
│   ├── settings.py                             [M]  + MEMORY_BACKEND, SIMPLEMEM_DB_DIR
│   ├── memory/
│   │   └── simplemem_adapter.py                [C]  SimpleMemAdapter wrapping SimpleMemSystem
│   ├── agent/
│   │   └── nodes/
│   │       ├── retrieve.py                     [M]  branch on backend
│   │       └── persist.py                      [M]  branch on backend (add_dialogue + finalize)
│   ├── deps.py                                 [M]  build adapter when backend=simplemem
│   └── main.py                                 [M]  lifespan picks backend
└── tests/
    ├── test_simplemem_adapter.py               [C]  add_dialogue/ask roundtrip
    └── test_node_retrieve_simplemem.py         [C]  retrieve node uses adapter
```

---

## Task 1: Dependency + settings

- [ ] Add `simplemem` to `backend/pyproject.toml` deps.
- [ ] `pip install -e .` in venv.
- [ ] In `persona/settings.py` add:
  - `memory_backend: Literal["sqlite", "simplemem"] = "sqlite"` (alias `MEMORY_BACKEND`)
  - `simplemem_db_dir: str = "data/simplemem"` (alias `SIMPLEMEM_DB_DIR`)
- [ ] Append to `.env.example`.
- [ ] Commit: `feat(settings): MEMORY_BACKEND switch + simplemem dir`.

---

## Task 2: SimpleMem adapter

**File:** `persona/memory/simplemem_adapter.py`

Wrap `SimpleMemSystem` behind a minimal surface used by the graph nodes:

```python
class SimpleMemAdapter:
    def __init__(self, db_dir: str, *, clear: bool = False):
        from simplemem import SimpleMemSystem
        self._sys = SimpleMemSystem(db_dir=db_dir, clear_db=clear)

    def add_turn(self, *, speaker: str, content: str, ts: str) -> None:
        self._sys.add_dialogue(speaker, content, ts)

    def finalize(self) -> None:
        self._sys.finalize()

    def ask(self, query: str) -> str:
        return self._sys.ask(query)
```

- [ ] Failing test: instantiate with `tmp_path`, add two dialogues, `finalize`, `ask` returns non-empty string (mock the LLM via SimpleMem's config or skip-mark behind `RUN_SIMPLEMEM=1`).
- [ ] Implement.
- [ ] Commit: `feat(memory): SimpleMemAdapter`.

---

## Task 3: Branch retrieve node

**File:** `persona/agent/nodes/retrieve.py`

- [ ] Accept optional `simplemem=None` kwarg in `make_retrieve_node`.
- [ ] When set, skip vector + FTS path. Call `simplemem.ask(user_message)` and stash the returned context string in `state["session_summary"]` (reuses the existing `{session_summary}` slot in `system.md`). Set `retrieved_memories=[]`, `retrieved_scores=[]`.
- [ ] Test: with a stubbed adapter returning `"FACT"`, node yields `session_summary == "FACT"` and empty memories list.
- [ ] Commit: `feat(agent): retrieve via SimpleMem when configured`.

---

## Task 4: Branch persist node

**File:** `persona/agent/nodes/persist.py`

- [ ] Accept optional `simplemem=None`.
- [ ] When set, after writing the user+assistant `messages` rows, call:
  - `simplemem.add_turn(speaker="user", content=user_msg, ts=created_at_iso)`
  - `simplemem.add_turn(speaker="assistant", content=assistant_msg, ts=created_at_iso)`
  - `simplemem.finalize()`
- [ ] Skip the existing embed → dedup → memories insert block in this branch.
- [ ] Test: with adapter stub, assert `add_turn` called twice and `finalize` called once; no rows in `memories`.
- [ ] Commit: `feat(agent): persist into SimpleMem when configured`.

---

## Task 5: Wire into deps + lifespan

**Files:** `persona/deps.py`, `persona/main.py`, `persona/agent/graph.py`

- [ ] Add `simplemem: SimpleMemAdapter | None = None` to `AppDeps`.
- [ ] In `main.lifespan`, if `settings.memory_backend == "simplemem"`, construct adapter (`db_dir=settings.simplemem_db_dir`) and pass through to `build_graph`.
- [ ] `build_graph(..., simplemem=None)`: forward kwarg to retrieve + persist node factories.
- [ ] Commit: `feat(app): wire SimpleMem through lifespan + graph`.

---

## Task 6: Smoke test (env-gated)

**File:** `tests/test_simplemem_e2e.py`

- [ ] `pytestmark = skipif(os.environ.get("RUN_SIMPLEMEM") != "1", ...)`.
- [ ] Spin app with `MEMORY_BACKEND=simplemem`, one chat round-trip, assert assistant_response non-empty and adapter DB dir contains files.
- [ ] Commit: `test: env-gated SimpleMem end-to-end smoke`.

---

## Notes / Risks

- **SimpleMem owns its own LLM + embedder config** (`config.py`). Either reuse the project's `HF_TOKEN` env or document a separate `OPENAI_API_KEY`/Qwen embedder setup. Capture in README quickstart.
- **No typed memory inspector** when running on SimpleMem — `/memories` page will be empty. Acceptable for v1; follow-up could mirror SimpleMem entries into a read-only view.
- **Procedural rules + working-memory summary** (memory_imp_plan.md) are bypassed in the SimpleMem branch; the `ask()` result occupies the same prompt slot. Revisit if both backends need rules.
- **First `finalize()` is slow** (consolidation pass). If latency hurts UX, push it to a background task after the SSE `done` event.
