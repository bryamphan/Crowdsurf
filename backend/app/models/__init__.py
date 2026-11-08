"""Database models: one SQLAlchemy class per Postgres table.

What's left to do:
- Create one file per table, each class inheriting from Base (models/base.py):
    host.py, room.py, guest.py, track.py, queue_item.py, vote.py
  The README's "Data model" section lists the fields and constraints.
- Import every model here. If a model isn't imported here, Alembic can't see it and
  won't generate a migration for it.
- After changing a model, generate a migration (see CONTRIBUTING.md).
"""

from app.models.base import Base

__all__ = ["Base"]
