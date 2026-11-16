"""Tests for the shared test setup in conftest.py.

If one of these fails, the problem is in the fixtures, not in your feature.
"""

import httpx
import pytest
from respx.models import AllMockedAssertionError
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.models import Guest, Host, QueueItem


async def test_client_uses_test_database_and_redis(client):
    resp = await client.get("/health/ready")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "db": "ok", "redis": "ok"}


# Each of these runs twice. If anything leaked from the first run, the second would
# hit the unique email constraint or find the Redis key already set.
@pytest.mark.parametrize("run", [1, 2])
async def test_database_is_rolled_back_between_tests(session, make_host, run):
    await make_host(email="same@example.com")
    await session.commit()  # even a commit is undone after the test
    count = await session.scalar(select(func.count()).select_from(Host))
    assert count == 1


@pytest.mark.parametrize("run", [1, 2])
async def test_redis_is_emptied_between_tests(redis, run):
    assert await redis.get("leftover") is None
    await redis.set("leftover", "x")


async def test_make_vote_builds_a_consistent_chain(session, make_vote):
    vote = await make_vote(value=-1)
    guest = await session.get(Guest, vote.guest_id)
    queue_item = await session.get(QueueItem, vote.queue_item_id)
    assert vote.value == -1
    assert guest.room_id == queue_item.room_id  # voter and song are in the same room


async def test_model_constraints_are_enforced(make_room, make_guest):
    room = await make_room()
    await make_guest(room=room, nickname="dj")
    with pytest.raises(IntegrityError):
        await make_guest(room=room, nickname="dj")


async def test_real_http_is_blocked():
    async with httpx.AsyncClient() as c:
        with pytest.raises(AllMockedAssertionError):
            await c.get("https://itunes.apple.com/search?term=x")


async def test_http_mock_fakes_responses(http_mock):
    http_mock.get("https://itunes.apple.com/search").respond(json={"resultCount": 0})
    async with httpx.AsyncClient() as c:
        resp = await c.get("https://itunes.apple.com/search", params={"term": "x"})
    assert resp.json() == {"resultCount": 0}
