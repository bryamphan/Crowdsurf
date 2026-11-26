"""Request and response shapes for rooms."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

# The only mode currently (only voting mode)
RoomMode = Literal["vote"]


class RoomCreate(BaseModel):
    mode: RoomMode = "vote"


class RoomUpdate(BaseModel):
    # Send only the fields you want to change; anything left out stays the same.
    is_locked: bool | None = None
    mode: RoomMode | None = None


class RoomOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # lets us return a Room model directly

    id: int
    join_code: str
    mode: str
    is_locked: bool
    created_at: datetime
    expires_at: datetime
    closed_at: datetime | None
