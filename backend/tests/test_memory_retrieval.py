import pytest

@pytest.mark.asyncio
async def test_recency_decay():
    from datetime import datetime, timedelta
    from persona.memory.retrieval import recency_decay, RECENCY_HALFLIFE_DAYS

    now = datetime.now()
    assert recency_decay(now, now) == 1.0
    past = now - timedelta(days=RECENCY_HALFLIFE_DAYS)
    assert abs(recency_decay(past, now) - 0.5) < 0.01
    future = now + timedelta(days=10)
    assert recency_decay(future, now) == 1.0
