from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Guest(Base):
    # maps to the "guests" table
    __tablename__ = "guests"
    __table_args__ = (UniqueConstraint("room_id", "nickname"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    nickname: Mapped[str] = mapped_column(String(30))
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_kicked: Mapped[bool] = mapped_column(Boolean, default=False)
