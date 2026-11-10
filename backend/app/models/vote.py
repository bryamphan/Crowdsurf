from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, SmallInteger, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Vote(Base):
    # maps to the "votes" table
    __tablename__ = "votes"
    __table_args__ = (CheckConstraint("value IN (1, -1)", name="ck_votes_value"),)

    guest_id: Mapped[int] = mapped_column(
        ForeignKey("guests.id", ondelete="CASCADE"), primary_key=True
    )
    queue_item_id: Mapped[int] = mapped_column(
        ForeignKey("queue_items.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    value: Mapped[int] = mapped_column(SmallInteger)
    voted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
