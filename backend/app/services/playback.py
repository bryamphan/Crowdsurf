"""Playback: what's playing, what has played, and moving on to the next song.

A queue item's status goes queued -> playing -> played (or removed). At most one item
per room is "playing" at a time. played_at is when the song started playing.
"""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import QueueItem, Room

# QueueItem.track and .added_by aren't loaded unless you ask (lazy="raise"). Add this to
# every query whose results get returned by the API.
WITH_DETAILS = (selectinload(QueueItem.track), selectinload(QueueItem.added_by))


class RoomClosedError(Exception):
    pass


async def get_now_playing(session: AsyncSession, room_id: int) -> QueueItem | None:
    return await session.scalar(
        select(QueueItem)
        .where(QueueItem.room_id == room_id, QueueItem.status == "playing")
        .options(*WITH_DETAILS)
    )


async def get_history(session: AsyncSession, room_id: int, limit: int) -> list[QueueItem]:
    """Songs that have played, most recent first."""
    result = await session.scalars(
        select(QueueItem)
        .where(QueueItem.room_id == room_id, QueueItem.status == "played")
        .order_by(QueueItem.played_at.desc(), QueueItem.id.desc())
        .limit(limit)
        .options(*WITH_DETAILS)
    )
    return list(result)


async def advance(session: AsyncSession, room: Room) -> QueueItem | None:
    """Finish the current song and start the highest-ranked queued one.

    Returns the song that's now playing, or None if the queue was empty.
    """
    if room.closed_at is not None:
        raise RoomClosedError

    # Lock this room's row until we commit. If the host double-clicks "next", the second
    # request waits here instead of both requests picking the same song.
    await session.execute(select(Room.id).where(Room.id == room.id).with_for_update())

    current = await session.scalar(
        select(QueueItem).where(QueueItem.room_id == room.id, QueueItem.status == "playing")
    )
    if current is not None:
        current.status = "played"

    # Highest score first; ties go to whichever song was added first.
    # TODO: read the ranking from Redis once services/ranking.py exists.
    upcoming = await session.scalar(
        select(QueueItem)
        .where(QueueItem.room_id == room.id, QueueItem.status == "queued")
        .order_by(QueueItem.score.desc(), QueueItem.added_at, QueueItem.id)
        .limit(1)
    )
    if upcoming is not None:
        upcoming.status = "playing"
        upcoming.played_at = datetime.now(UTC)

    await session.commit()
    if upcoming is None:
        return None
    return await get_now_playing(session, room.id)  # reload with track and added_by
