"""Queue and voting endpoints: the core of Crowdsurf."""

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/rooms/{room_id}/queue", tags=["queue"])


def _todo() -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.get("")
async def get_queue(room_id: int):
    """Ranked queue, highest score first (served from the Redis sorted set)."""
    _todo()


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_to_queue(room_id: int):
    """Add a song to the queue."""
    _todo()


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_queue(room_id: int, item_id: int):
    """Remove a song from the queue."""
    _todo()


@router.put("/{item_id}/vote")
async def vote(room_id: int, item_id: int):
    """Cast or change a vote: 1, -1, or 0 to clear. Idempotent."""
    _todo()
