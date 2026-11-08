"""Guest endpoints: join a room, list who's in it, and kick someone."""

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/rooms", tags=["guests"])


def _todo() -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.post("/{code}/join", status_code=status.HTTP_201_CREATED)
async def join_room(code: str):
    """Join a room with a nickname and receive a guest token."""
    _todo()


@router.get("/{room_id}/guests")
async def list_guests(room_id: int):
    """List guests in a room."""
    _todo()


@router.delete("/{room_id}/guests/{guest_id}", status_code=status.HTTP_204_NO_CONTENT)
async def kick_guest(room_id: int, guest_id: int):
    """Kick a guest. Host only."""
    _todo()
