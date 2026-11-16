"""Shared test setup. pytest loads this file automatically; never import it.

Ask for any fixture below by naming it as a test argument:

    async def test_kick_guest(client, make_room, make_guest):
        room = await make_room()
        guest = await make_guest(room=room, nickname="dj")
        resp = await client.delete(f"/api/v1/rooms/{room.id}/guests/{guest.id}")

Fixtures:
    client          httpx client that calls the app in memory (no server needed)
    session         database session; everything it writes is undone after the test
    redis           Redis client on a separate test DB, emptied after the test
    http_mock       fakes outgoing HTTP (e.g. iTunes); unmocked requests fail the test
    make_host, make_room, make_guest, make_track, make_queue_item, make_vote
                    create a valid row with sensible defaults; override any field

Tests run against a separate `crowdsurf_test` database (created automatically) and
Redis DB 15, so running pytest never touches your local dev data.
"""

import hashlib
import itertools
import os
from datetime import UTC, datetime, timedelta
from urllib.parse import urlsplit

import pytest
import respx
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import get_settings
from app.core.db import get_session
from app.core.redis import get_redis
from app.main import app
from app.models import Base, Guest, Host, QueueItem, Room, Track, Vote

settings = get_settings()

# The dev URLs with the database name / Redis DB number swapped. Override with
# TEST_DATABASE_URL or TEST_REDIS_URL if you need to point tests somewhere else.
_dev_db = make_url(settings.database_url)
TEST_DATABASE_URL = make_url(
    os.environ.get("TEST_DATABASE_URL")
    or _dev_db.set(database=f"{_dev_db.database}_test").render_as_string(hide_password=False)
)
TEST_REDIS_URL = (
    os.environ.get("TEST_REDIS_URL") or urlsplit(settings.redis_url)._replace(path="/15").geturl()
)


# --- Database ---------------------------------------------------------------------


async def _create_database_if_missing(url) -> None:
    """CREATE DATABASE can't run inside a transaction, so connect to the built-in
    `postgres` database in autocommit mode to do it."""
    admin = create_async_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    async with admin.connect() as conn:
        exists = await conn.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": url.database}
        )
        if not exists:
            await conn.execute(text(f'CREATE DATABASE "{url.database}"'))
    await admin.dispose()


@pytest.fixture(scope="session")
async def engine():
    """One engine for the whole test run. Builds every table from the models at the start
    (dropping leftovers from a crashed run first) and drops them at the end."""
    await _create_database_if_missing(TEST_DATABASE_URL)
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def session(engine):
    """A session inside a transaction that is rolled back after the test.

    join_transaction_mode="create_savepoint" means app code can still call
    session.commit() or session.rollback(): those only affect a savepoint, and the
    outer transaction (and everything in it) is thrown away when the test ends.
    """
    async with engine.connect() as conn:
        outer = await conn.begin()
        session = AsyncSession(
            bind=conn, expire_on_commit=False, join_transaction_mode="create_savepoint"
        )
        try:
            yield session
        finally:
            await session.close()
            await outer.rollback()


# --- Redis ------------------------------------------------------------------------


@pytest.fixture
async def redis():
    """Redis client on the test DB, emptied before and after each test.

    Heads-up: pub/sub channels are shared across all Redis DB numbers, so pub/sub
    tests should use room IDs that no other test uses at the same time.
    """
    client = Redis.from_url(TEST_REDIS_URL, decode_responses=True)
    await client.flushdb()
    yield client
    await client.flushdb()
    await client.aclose()


# --- HTTP -------------------------------------------------------------------------


@pytest.fixture
async def client(session, redis):
    """Calls the app in memory, using the test database session and test Redis.

    Data made with the make_* fixtures is visible to the endpoints, because both use
    the same session.
    """
    app.dependency_overrides[get_session] = lambda: session
    app.dependency_overrides[get_redis] = lambda: redis
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            yield c
    finally:
        app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def http_mock():
    """Blocks real outgoing HTTP in every test. Fake a response like this:

        http_mock.get("https://itunes.apple.com/search").respond(json={"results": []})

    A request that matches no fake route fails the test. Calls to the app through
    `client` aren't affected.
    """
    with respx.mock(assert_all_called=False) as mock:
        yield mock


# --- Factories --------------------------------------------------------------------
# Each one adds a row, flushes it (so it gets an id), and returns the model object.
# Pass any column as a keyword to override the default. Parent rows are created for
# you when you don't pass them, e.g. make_vote() also makes a queue item, room, etc.

_counter = itertools.count(1)  # keeps unique columns (email, join_code, ...) unique


async def _save(session: AsyncSession, obj):
    session.add(obj)
    await session.flush()
    return obj


@pytest.fixture
def make_host(session):
    async def _make(**fields) -> Host:
        n = next(_counter)
        fields.setdefault("email", f"host{n}@example.com")
        fields.setdefault("password_hash", "not-a-real-hash")
        return await _save(session, Host(**fields))

    return _make


@pytest.fixture
def make_room(session, make_host):
    async def _make(host: Host | None = None, **fields) -> Room:
        if "host_id" not in fields:
            fields["host_id"] = (host or await make_host()).id
        fields.setdefault("join_code", f"T{next(_counter):05d}")
        fields.setdefault("mode", "vote")
        fields.setdefault("is_locked", False)
        fields.setdefault(
            "expires_at", datetime.now(UTC) + timedelta(hours=settings.room_ttl_hours)
        )
        return await _save(session, Room(**fields))

    return _make


@pytest.fixture
def make_guest(session, make_room):
    async def _make(room: Room | None = None, **fields) -> Guest:
        n = next(_counter)
        if "room_id" not in fields:
            fields["room_id"] = (room or await make_room()).id
        fields.setdefault("nickname", f"guest{n}")
        fields.setdefault("token_hash", hashlib.sha256(f"test-token-{n}".encode()).hexdigest())
        fields.setdefault("is_kicked", False)
        return await _save(session, Guest(**fields))

    return _make


@pytest.fixture
def make_track(session):
    async def _make(**fields) -> Track:
        n = next(_counter)
        fields.setdefault("external_id", str(1_000_000 + n))
        fields.setdefault("title", f"Song {n}")
        fields.setdefault("artist", f"Artist {n}")
        fields.setdefault("duration_ms", 30_000)
        return await _save(session, Track(**fields))

    return _make


@pytest.fixture
def make_queue_item(session, make_room, make_guest, make_track):
    async def _make(
        room: Room | None = None,
        track: Track | None = None,
        added_by: Guest | None = None,
        **fields,
    ) -> QueueItem:
        if "room_id" not in fields:
            if room is None and added_by is not None:
                fields["room_id"] = added_by.room_id
            else:
                fields["room_id"] = (room or await make_room()).id
        if "added_by_guest_id" not in fields:
            fields["added_by_guest_id"] = (
                added_by or await make_guest(room_id=fields["room_id"])
            ).id
        if "track_id" not in fields:
            fields["track_id"] = (track or await make_track()).id
        fields.setdefault("status", "queued")
        return await _save(session, QueueItem(**fields))

    return _make


@pytest.fixture
def make_vote(session, make_guest, make_queue_item):
    async def _make(
        guest: Guest | None = None, item: QueueItem | None = None, value: int = 1, **fields
    ) -> Vote:
        if "queue_item_id" not in fields:
            if item is None:
                item = await make_queue_item(**({"room_id": guest.room_id} if guest else {}))
            fields["queue_item_id"] = item.id
        if "guest_id" not in fields:
            if guest is None:
                guest = await make_guest(**({"room_id": item.room_id} if item else {}))
            fields["guest_id"] = guest.id
        return await _save(session, Vote(value=value, **fields))

    return _make
