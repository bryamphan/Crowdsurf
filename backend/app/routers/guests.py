"""Guest endpoints: join a room, list who's in it, and kick someone.

Owner: rooms, guests, and search.

What's left to do:
- Replace each _todo() stub with a real implementation.
- Add schemas in schemas/guest.py (e.g. JoinRequest with a nickname, JoinResponse with
  the guest token, GuestOut).
- Joining creates a guest row and returns a token from core/security.py. Store only a
  hash of the token, never the raw value.
- Reject joins to rooms that are locked, closed, or expired.
- Kicking is host only (get_current_host). A kicked guest's token must stop working.
- Add tests in tests/test_guests.py.
"""

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
