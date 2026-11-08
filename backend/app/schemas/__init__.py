"""Pydantic schemas: the shape of request bodies and responses.

FastAPI uses these to validate input (bad input gets a 422 automatically) and to
generate the /docs page. Keep them separate from the database models, so changing a
table doesn't accidentally change what the API returns.

What's left to do:
- Create one file per resource, e.g. room.py, guest.py, track.py, queue.py,
  playback.py, auth.py.
- A common pattern is XCreate for input and XOut for output (e.g. RoomCreate, RoomOut).
"""
