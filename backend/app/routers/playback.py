"""Playback endpoints and the live WebSocket stream."""

from fastapi import APIRouter, HTTPException, WebSocket, status

router = APIRouter(prefix="/rooms/{room_id}", tags=["playback"])


def _todo() -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.post("/next")
async def next_track(room_id: int):
    """Advance to the next song. Host only."""
    _todo()


@router.get("/now-playing")
async def now_playing(room_id: int):
    """The song that's playing right now."""
    _todo()


@router.get("/history")
async def history(room_id: int):
    """Songs that have already played."""
    _todo()


@router.websocket("/stream")
async def stream(websocket: WebSocket, room_id: int):
    """Live queue and now-playing updates, fed by Redis pub/sub on room:{id}."""
    await websocket.close(code=1013, reason="Not implemented yet")
