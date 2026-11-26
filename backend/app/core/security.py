"""Passwords, tokens, and the auth dependencies every endpoint uses.

Protect an endpoint by taking the logged-in host or guest as a dependency:

    @router.post("")
    async def create_room(host: Host = Depends(get_current_host)): ...

    @router.put("/{item_id}/vote")
    async def vote(guest: Guest = Depends(get_current_guest)): ...

Both read the `Authorization: Bearer <token>` header and return 401 if it's missing or
invalid, so the endpoint only runs for a real, logged-in user.
"""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_session
from app.models import Guest, Host, Room

JWT_ALGORITHM = "HS256"
BCRYPT_MAX_BYTES = 72  # bcrypt can't hash passwords longer than this

# Reads "Authorization: Bearer <token>". auto_error=False so we can return our own 401.
# It also adds the "Authorize" button to /docs, where you paste a token to test endpoints.
bearer = HTTPBearer(auto_error=False)


# --- Passwords (hosts) ------------------------------------------------------------


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    if len(password.encode()) > BCRYPT_MAX_BYTES:
        return False  # bcrypt would raise; no stored password can be this long anyway
    return bcrypt.checkpw(password.encode(), password_hash.encode())


# --- Host tokens (JWT) ------------------------------------------------------------
# A signed token that says "this is host 5, valid until <time>". We can check it
# without a database lookup because only the server knows JWT_SECRET.


def create_host_token(host_id: int, expires_in: timedelta | None = None) -> str:
    settings = get_settings()
    expires_in = expires_in or timedelta(hours=settings.host_token_ttl_hours)
    payload = {"sub": str(host_id), "type": "host", "exp": datetime.now(UTC) + expires_in}
    return jwt.encode(payload, settings.jwt_secret, algorithm=JWT_ALGORITHM)


def decode_host_token(token: str) -> int | None:
    """Returns the host id, or None if the token is invalid, expired, or not a host token."""
    try:
        payload = jwt.decode(token, get_settings().jwt_secret, algorithms=[JWT_ALGORITHM])
    except jwt.InvalidTokenError:
        return None
    if payload.get("type") != "host":
        return None
    return int(payload["sub"])


# --- Guest tokens -----------------------------------------------------------------
# A random string handed to the guest once when they join. We store only its SHA-256
# hash (64 hex chars, matching guests.token_hash), so a database leak doesn't leak
# working tokens. No bcrypt needed: the token is long and random, not a weak password.


def new_guest_token() -> tuple[str, str]:
    """Returns (token to give the guest, hash to store in guests.token_hash)."""
    token = secrets.token_urlsafe(32)
    return token, hash_guest_token(token)


def hash_guest_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


# --- Dependencies -----------------------------------------------------------------


def _unauthorized(detail: str = "Not authenticated") -> HTTPException:
    return HTTPException(
        status.HTTP_401_UNAUTHORIZED, detail, headers={"WWW-Authenticate": "Bearer"}
    )


async def get_current_host(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    session: AsyncSession = Depends(get_session),
) -> Host:
    """The logged-in host. 401 if the token is missing, invalid, or expired."""
    if creds is None:
        raise _unauthorized()
    host_id = decode_host_token(creds.credentials)
    host = await session.get(Host, host_id) if host_id is not None else None
    if host is None:
        raise _unauthorized("Invalid or expired token")
    return host


async def get_current_guest(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    session: AsyncSession = Depends(get_session),
) -> Guest:
    """The guest making the request. 401 if the token is unknown, 403 if they were kicked.

    This doesn't check that the guest belongs to the room in the URL; endpoints that
    take a room_id should compare it with guest.room_id themselves.
    """
    if creds is None:
        raise _unauthorized()
    guest = await session.scalar(
        select(Guest).where(Guest.token_hash == hash_guest_token(creds.credentials))
    )
    if guest is None:
        raise _unauthorized("Invalid guest token")
    if guest.is_kicked:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You were removed from this room")
    return guest


# --- Room access ------------------------------------------------------------------
# For endpoints under /rooms/{room_id}. Take the room as a dependency instead of the id:
#
#     async def close_room(room: Room = Depends(get_owned_room)): ...


async def get_room(room_id: int, session: AsyncSession = Depends(get_session)) -> Room:
    """The room in the URL. 404 if it doesn't exist."""
    room = await session.get(Room, room_id)
    if room is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Room not found")
    return room


async def get_owned_room(
    host: Host = Depends(get_current_host), room: Room = Depends(get_room)
) -> Room:
    """The room in the URL, if the logged-in host owns it. 401 if not logged in, 404 if
    the room doesn't exist, 403 if it belongs to another host."""
    if room.host_id != host.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the room's host can do this")
    return room


def ensure_room_open(room: Room) -> Room:
    """Return the room if it's still usable. 410 if it was closed or has expired.

    Use this directly when you already have the room (e.g. looked up by join code),
    or use get_open_room below for endpoints with {room_id} in the URL.
    """
    if room.closed_at is not None:
        raise HTTPException(status.HTTP_410_GONE, "This room is closed")
    if room.expires_at <= datetime.now(UTC):
        raise HTTPException(status.HTTP_410_GONE, "This room has expired")
    return room


async def get_open_room(room: Room = Depends(get_room)) -> Room:
    """The room in the URL, if it's still open. 404 if it doesn't exist, 410 if it's
    closed or expired. Use for join, add song, vote, and next."""
    return ensure_room_open(room)
