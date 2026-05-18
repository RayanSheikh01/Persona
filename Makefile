.PHONY: install dev backend frontend seed reset test fmt

install:
	cd backend && python -m venv .venv && .venv/bin/pip install -e ".[dev]"
	cd frontend && npm install

backend:
	cd backend && .venv/bin/uvicorn persona.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

dev:
	@echo "Run 'make backend' and 'make frontend' in two terminals (Windows)."
	@echo "On Unix: backend & frontend started in parallel."
	$(MAKE) -j2 backend frontend

seed:
	cd backend && .venv/bin/python ../scripts/seed.py

reset:
	rm -f data/persona.db data/persona.db-shm data/persona.db-wal

test:
	cd backend && .venv/bin/pytest -q

fmt:
	cd backend && .venv/bin/ruff format .
	cd frontend && npx prettier --write .
