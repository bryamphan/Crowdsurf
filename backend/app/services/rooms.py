"""Rooms: create, update, close, and check whether a room is still open."""

from datetime import UTC, datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import Host, Room
from app.services.join_codes import generate_join_code

# A collision is very unlikely (about 887 million codes), so a few tries is plenty.
MAX_CODE_ATTEMPTS = 5


class JoinCodeUnavailableError(Exception):
    """Couldn't find an unused join code after MAX_CODE_ATTEMPTS tries."""


async def create_room(session: AsyncSession, host: Host, mode: str) -> Room:
    """Create an open room for this host with a fresh, unused join code."""
    now = datetime.now(UTC)
    lifetime = timedelta(hours=get_settings().room_ttl_hours)  # ← changed

    for _ in range(MAX_CODE_ATTEMPTS):
        room = Room(
            host_id=host.id,
            join_code=generate_join_code(),
            mode=mode,
            is_locked=False,
            expires_at=now + lifetime,
        )
        try:
            async with session.begin_nested():  # savepoint: a failure undoes only this insert
                session.add(room)
        except IntegrityError:  # the join code was taken; try another
            continue
        await session.commit()
        await session.refresh(room)  # load created_at, which the database fills in
        return room

    raise JoinCodeUnavailableError
