from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class QueueItem(Base):
    # maps to the "queue_items" table
    __tablename__ = "queue_items"
    __table_args__ = (Index("ix_queue_items_room_id_status", "room_id", "status"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"))
    track_id: Mapped[int] = mapped_column(ForeignKey("tracks.id", ondelete="RESTRICT"))
    added_by_guest_id: Mapped[int] = mapped_column(ForeignKey("guests.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(20), default="queued")
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    played_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
