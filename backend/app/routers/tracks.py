"""Song search endpoint, backed by the iTunes Search API."""

from fastapi import APIRouter, HTTPException, Query, status

router = APIRouter(prefix="/tracks", tags=["tracks"])


@router.get("/search")
async def search_tracks(q: str = Query(min_length=1)):
    """Search songs via the iTunes Search API. Results are cached in Redis."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")
