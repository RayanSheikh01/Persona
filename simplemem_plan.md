# SimpleMem Integration Plan

Add [SimpleMem](https://github.com/aiming-lab/SimpleMem) as an alternative long-term memory backend, switchable via `MEMORY_BACKEND`.

**Strategy:** thin adapter around `SimpleMemSystem` (`add_dialogue → finalize → ask`); branch the existing `retrieve` and `persist` nodes on the backend setting so graph wiring is unchanged.

---

## File Map

`[C]` create, `[M]` modify.

```text
backend/
├── pyproject.toml                              [M]  + simplemem dep
├── persona/
│   ├── settings.py                             [M]  + memory_backend, simplemem_db_dir
│   ├── memory/simplemem_adapter.py             [C]  SimpleMemAdapter
│   ├── agent/nodes/retrieve.py                 [M]  branch on backend
│   ├── agent/nodes/persist.py                  [M]  branch on backend
│   ├── agent/graph.py                          [M]  forward simplemem kwarg
│   ├── deps.py                                 [M]  carry adapter
│   └── main.py                                 [M]  build adapter in lifespan
└── tests/
    ├── test_simplemem_adapter.py               [C]
    ├── test_node_retrieve_simplemem.py         [C]
    └── test_simplemem_e2e.py                   [C]  env-gated
```

---

## Task 1 — dep + settings ✅

- [x] Add `simplemem` to `backend/pyproject.toml`.
- [x] `settings.py`: `memory_backend: Literal["sqlite","simplemem"]`, `simplemem_db_dir`.
- [x] Append `MEMORY_BACKEND` + `SIMPLEMEM_DB_DIR` to `.env.example`.
- [x] `pip install simplemem`.

## Task 2 — adapter

- [ ] `memory/simplemem_adapter.py`: `SimpleMemAdapter(db_dir, clear=False)` wrapping `SimpleMemSystem` with `add_turn(speaker, content, ts)`, `finalize()`, `ask(query)`.
- [ ] Test: tmp_path init + add two dialogues + finalize + ask returns non-empty (env-gated `RUN_SIMPLEMEM=1`).
- [ ] Commit: `feat(memory): SimpleMemAdapter`.

## Task 3 — retrieve node branch

- [ ] `make_retrieve_node(..., simplemem=None)`: if set, call `simplemem.ask(user_message)`, stash result in `state["session_summary"]`, return empty `retrieved_memories`/`retrieved_scores`.
- [ ] Test with stub adapter.
- [ ] Commit: `feat(agent): retrieve via SimpleMem`.

## Task 4 — persist node branch

- [ ] `make_persist_node(..., simplemem=None)`: after writing messages rows, call `add_turn` x2 + `finalize()`; skip embed/dedup/memories insert block.
- [ ] Test with stub adapter.
- [ ] Commit: `feat(agent): persist into SimpleMem`.

## Task 5 — wire through deps + graph

- [ ] `AppDeps.simplemem: SimpleMemAdapter | None`.
- [ ] `build_graph(..., simplemem=None)` forwards kwarg to retrieve + persist factories.
- [ ] `main.lifespan`: if `settings.memory_backend == "simplemem"`, construct adapter and pass through.
- [ ] Commit: `feat(app): wire SimpleMem through lifespan + graph`.

## Task 6 — e2e smoke

- [ ] `tests/test_simplemem_e2e.py`, `skipif RUN_SIMPLEMEM != "1"`: one chat round-trip with `MEMORY_BACKEND=simplemem`; assert non-empty response + adapter db dir populated.
- [ ] Commit: `test: env-gated SimpleMem e2e`.

---

## Notes / Risks

- SimpleMem brings its own LLM + embedder config (`config.py`); document required env in README.
- `/memories` inspector is empty under SimpleMem (no typed rows); accept for v1.
- Procedural rules + working summary are bypassed in SimpleMem branch — `ask()` occupies the `{session_summary}` slot.
- First `finalize()` is slow; consider moving to a background task after SSE `done` if it hurts UX.
