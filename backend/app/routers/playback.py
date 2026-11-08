"""Playback endpoints and the live WebSocket stream.

Owner: real-time and playback.

What's left to do:
- Replace each _todo() stub with a real implementation.
- POST /next (host only): mark the current song "played", take the top song from the
  Redis sorted set, mark it "playing", remove it from the set, and publish an event.
- GET /now-playing and GET /history read queue_items by status. Add schemas in
  schemas/playback.py.
- WebSocket /stream: accept the connection, subscribe to the room:{id} channel with
  services/pubsub.py, and forward every event to the client until it disconnects.
  Because events go through Redis, this works even with several API servers running.
- Room expiry: rooms expire after ROOM_TTL_HOURS (core/config.py). Write a background job
  (e.g. services/expiry.py) and start it from main.py.
- Add tests in tests/test_playback.py.
"""

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
