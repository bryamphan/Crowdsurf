"""Host accounts: sign up, log in, and check who you're logged in as."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.security import create_host_token, get_current_host
from app.models import Host
from app.schemas.auth import AuthResponse, HostLogin, HostOut, HostSignup
from app.services.auth import EmailTakenError, authenticate_host, register_host

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=AuthResponse)
async def signup(body: HostSignup, session: AsyncSession = Depends(get_session)):
    """Create a host account. Returns a token, so the host is logged in right away."""
    try:
        host = await register_host(session, body.email, body.password)
    except EmailTakenError:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "An account with that email already exists"
        ) from None
    return AuthResponse(access_token=create_host_token(host.id), host=host)


@router.post("/login", response_model=AuthResponse)
async def login(body: HostLogin, session: AsyncSession = Depends(get_session)):
    """Log in with email and password. Returns a token to send as `Authorization: Bearer`."""
    host = await authenticate_host(session, body.email, body.password)
    if host is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")
    return AuthResponse(access_token=create_host_token(host.id), host=host)


@router.get("/me", response_model=HostOut)
async def me(host: Host = Depends(get_current_host)):
    """The host the token belongs to."""
    return host
