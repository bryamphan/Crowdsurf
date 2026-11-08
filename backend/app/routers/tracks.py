"""Song search endpoint, backed by the iTunes Search API.

Owner: rooms, guests, and search.

What's left to do:
- Replace the stub with a real implementation.
- Write the iTunes client in services/itunes.py using httpx (already installed).
  iTunes returns title, artist, album art, duration, and a 30-second preview URL.
- Cache results in Redis, keyed by the search query, for SEARCH_CACHE_TTL seconds
  (see core/config.py), so we stay under iTunes' rate limits.
- Add a TrackOut schema in schemas/track.py so the frontend gets a consistent shape.
- Add tests in tests/test_tracks.py. Mock the iTunes call; tests shouldn't hit the internet.
"""

from fastapi import APIRouter, HTTPException, Query, status

router = APIRouter(prefix="/tracks", tags=["tracks"])


@router.get("/search")
async def search_tracks(q: str = Query(min_length=1)):
    """Search songs via the iTunes Search API. Results are cached in Redis."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")
