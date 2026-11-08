"""Queue and voting endpoints: the core of Crowdsurf.

Owner: queue and voting.

What's left to do:
- Replace each _todo() stub with a real implementation.
- Add schemas in schemas/queue.py (e.g. QueueAdd, VoteRequest with value 1/-1/0, QueueItemOut).
- Write the ranking logic in services/ranking.py (see docs/decisions/0001):
  - Every vote is saved to Postgres first; the votes table allows one vote per guest per song.
  - Then update the room's Redis sorted set with ZINCRBY by the change in vote
    (e.g. changing +1 to -1 is ZINCRBY -2).
  - GET /queue reads the order with ZREVRANGE. If the sorted set is missing, rebuild it
    from Postgres.
- After any add, remove, or vote, publish an event with services/pubsub.py so connected
  phones update live. Agree on the event format with the real-time owner first.
- Rate-limit votes per guest (VOTE_RATE_LIMIT in core/config.py) in services/rate_limit.py.
- Guests use get_current_guest; removing a song is allowed for the host or whoever added it.
- Add tests in tests/test_queue.py, including changing a vote and voting twice.
"""

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
