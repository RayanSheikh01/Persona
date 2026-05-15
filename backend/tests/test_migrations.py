import pytest
from persona.db.migrations.migrations import apply_migrations

@pytest.mark.asyncio
async def test_migrations():
    from persona.db.migrations.migrations import apply_migrations

    try:
        await apply_migrations()
    except Exception as e:
        pytest.fail(f"Applying migrations failed with error: {e}")