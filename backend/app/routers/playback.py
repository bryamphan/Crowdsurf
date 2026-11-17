"""Playback endpoints and the live WebSocket stream."""

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.security import get_owned_room, get_room
from app.models import Room
from app.schemas.queue import QueueItemOut
from app.services.playback import RoomClosedError, advance, get_history, get_now_playing

router = APIRouter(prefix="/rooms/{room_id}", tags=["playback"])


@router.post("/next", response_model=QueueItemOut | None)
async def next_track(
    room: Room = Depends(get_owned_room), session: AsyncSession = Depends(get_session)
):
    """Finish the current song and start the highest-ranked one. Host only.

    Returns the song that's now playing, or null if the queue is empty.
    """
    try:
        return await advance(session, room)
    except RoomClosedError:
        raise HTTPException(status.HTTP_409_CONFLICT, "This room is closed") from None


@router.get("/now-playing", response_model=QueueItemOut | None)
async def now_playing(room: Room = Depends(get_room), session: AsyncSession = Depends(get_session)):
    """The song that's playing right now, or null if nothing is."""
    return await get_now_playing(session, room.id)


@router.get("/history", response_model=list[QueueItemOut])
async def history(
    room: Room = Depends(get_room),
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """Songs that have already played, most recent first."""
    return await get_history(session, room.id, limit)


@router.websocket("/stream")
async def stream(websocket: WebSocket, room_id: int):
    """Live queue and now-playing updates, fed by Redis pub/sub on room:{id}."""
    await websocket.close(code=1013, reason="Not implemented yet")
