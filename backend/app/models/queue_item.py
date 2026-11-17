from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func, select
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship

from app.models.base import Base
from app.models.guest import Guest
from app.models.track import Track
from app.models.vote import Vote


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

    # not columns, so no migration needed. they're filled in from other tables when you
    # query a QueueItem.

    # the song and the guest who added it. lazy="raise" makes forgetting to load them an
    # immediate, clear error (see WITH_DETAILS in services/playback.py).
    track: Mapped[Track] = relationship(lazy="raise")
    added_by: Mapped[Guest] = relationship(lazy="raise")

    # upvotes minus downvotes, calculated by the database in the same query.
    score: Mapped[int] = column_property(
        select(func.coalesce(func.sum(Vote.value), 0))
        .where(Vote.queue_item_id == id)
        .correlate_except(Vote)
        .scalar_subquery()
    )
