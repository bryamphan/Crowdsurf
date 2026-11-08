"""Room endpoints: create, look up, update, and close a party room.

Owner: rooms, guests, and search.

What's left to do:
- Replace each _todo() stub with a real implementation.
- Add request/response schemas in schemas/room.py (e.g. RoomCreate, RoomUpdate, RoomOut).
- Put the logic in services/ (e.g. join code generation in services/join_codes.py),
  and keep these functions short: parse the request, call a service, return a schema.
- Protect create/update/close with the get_current_host dependency from core/security.py,
  and make sure a host can only change their own rooms.
- Look up by join code (GET /rooms/{code}) is public, since guests use it from the QR code.
- Add tests in tests/test_rooms.py.
"""

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/rooms", tags=["rooms"])


def _todo() -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_room():
    """Create a room. Host only."""
    _todo()


@router.get("/{code}")
async def get_room_by_code(code: str):
    """Look up a room by its join code."""
    _todo()


@router.patch("/{room_id}")
async def update_room(room_id: int):
    """Change room settings (lock, mode). Host only."""
    _todo()


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def close_room(room_id: int):
    """Close a room. Host only."""
    _todo()
