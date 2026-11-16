"""Host accounts: sign up and check a login."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models import Host

# Checked against when the email doesn't exist, so a login for an unknown email takes
# as long as a wrong password. Otherwise response time reveals which emails have accounts.
_DUMMY_HASH = hash_password("not-a-real-password")


class EmailTakenError(Exception):
    pass


async def register_host(session: AsyncSession, email: str, password: str) -> Host:
    host = Host(email=email, password_hash=hash_password(password))
    session.add(host)
    try:
        await session.commit()
    except IntegrityError as e:  # the unique constraint on hosts.email
        await session.rollback()
        raise EmailTakenError from e
    await session.refresh(host)  # load created_at, which the database fills in
    return host


async def authenticate_host(session: AsyncSession, email: str, password: str) -> Host | None:
    """The host if the email and password match, otherwise None."""
    host = await session.scalar(select(Host).where(Host.email == email))
    if host is None:
        verify_password(password, _DUMMY_HASH)
        return None
    if not verify_password(password, host.password_hash):
        return None
    return host
