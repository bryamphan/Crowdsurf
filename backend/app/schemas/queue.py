"""How a queue item looks in API responses.

Shared by playback (now-playing, history, next), the queue endpoints, and the WebSocket
events, so the frontend renders a song the same way everywhere.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TrackOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    external_id: str
    title: str
    artist: str
    album_art_url: str | None
    preview_url: str | None
    duration_ms: int | None


class AddedBy(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nickname: str


class QueueItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    score: int
    added_at: datetime
    played_at: datetime | None
    track: TrackOut
    added_by: AddedBy
