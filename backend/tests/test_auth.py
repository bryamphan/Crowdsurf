"""Host signup and login, tokens, and the get_current_host / get_current_guest
dependencies."""

from datetime import timedelta

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core.security import (
    create_host_token,
    decode_host_token,
    get_current_guest,
    hash_password,
    new_guest_token,
    verify_password,
)

SIGNUP = "/api/v1/auth/signup"
LOGIN = "/api/v1/auth/login"
ME = "/api/v1/auth/me"


def bearer(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


# --- Signup -----------------------------------------------------------------------


async def test_signup_creates_host_and_logs_them_in(client):
    resp = await client.post(SIGNUP, json={"email": "dj@example.com", "password": "hunter22"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["host"]["email"] == "dj@example.com"
    assert body["token_type"] == "bearer"
    assert "password_hash" not in body["host"]

    me = await client.get(ME, headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.json()["id"] == body["host"]["id"]


async def test_signup_rejects_taken_email_ignoring_case(client):
    await client.post(SIGNUP, json={"email": "dj@example.com", "password": "hunter22"})
    resp = await client.post(SIGNUP, json={"email": "DJ@Example.com", "password": "hunter22"})
    assert resp.status_code == 409


@pytest.mark.parametrize(
    "body",
    [
        {"email": "not-an-email", "password": "hunter22"},
        {"email": "dj@example.com", "password": "short"},
        {"email": "dj@example.com", "password": "x" * 73},
    ],
)
async def test_signup_validates_input(client, body):
    resp = await client.post(SIGNUP, json=body)
    assert resp.status_code == 422


# --- Login ------------------------------------------------------------------------


async def test_login_with_correct_password(client):
    await client.post(SIGNUP, json={"email": "dj@example.com", "password": "hunter22"})
    resp = await client.post(LOGIN, json={"email": "DJ@example.com", "password": "hunter22"})
    assert resp.status_code == 200
    assert resp.json()["host"]["email"] == "dj@example.com"


@pytest.mark.parametrize(
    "email, password",
    [
        ("dj@example.com", "wrong-password"),
        ("nobody@example.com", "hunter22"),
        ("dj@example.com", "x" * 100),
    ],
)
async def test_login_rejects_bad_credentials(client, email, password):
    await client.post(SIGNUP, json={"email": "dj@example.com", "password": "hunter22"})
    resp = await client.post(LOGIN, json={"email": email, "password": password})
    assert resp.status_code == 401
    # Same message either way, so nobody can find out which emails have accounts.
    assert resp.json()["detail"] == "Incorrect email or password"


# --- get_current_host (through /auth/me) ------------------------------------------


async def test_me_with_auth_headers_fixture(client, make_host, auth_headers):
    host = await make_host()
    resp = await client.get(ME, headers=auth_headers(host))
    assert resp.status_code == 200
    assert resp.json()["email"] == host.email


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"Authorization": "Bearer garbage"},
        {"Authorization": f"Bearer {create_host_token(1, expires_in=timedelta(seconds=-1))}"},
    ],
    ids=["missing", "garbage", "expired"],
)
async def test_me_rejects_bad_tokens(client, headers):
    resp = await client.get(ME, headers=headers)
    assert resp.status_code == 401


async def test_me_rejects_token_for_deleted_host(client):
    resp = await client.get(ME, headers={"Authorization": f"Bearer {create_host_token(999999)}"})
    assert resp.status_code == 401


async def test_guest_token_is_not_a_host_token(client, make_guest, auth_headers):
    guest = await make_guest()
    resp = await client.get(ME, headers=auth_headers(guest))
    assert resp.status_code == 401


# --- get_current_guest ------------------------------------------------------------
# No endpoint uses it yet, so call the dependency directly.


async def test_current_guest_from_token(session, make_guest):
    guest = await make_guest()
    assert (await get_current_guest(bearer(guest.token), session)).id == guest.id


async def test_current_guest_rejects_unknown_token(session):
    with pytest.raises(HTTPException) as exc:
        await get_current_guest(bearer("not-a-real-token"), session)
    assert exc.value.status_code == 401


async def test_current_guest_rejects_kicked_guest(session, make_guest):
    guest = await make_guest(is_kicked=True)
    with pytest.raises(HTTPException) as exc:
        await get_current_guest(bearer(guest.token), session)
    assert exc.value.status_code == 403


# --- Helpers ----------------------------------------------------------------------


def test_password_hashing():
    hashed = hash_password("hunter22")
    assert hashed != "hunter22"
    assert verify_password("hunter22", hashed)
    assert not verify_password("hunter23", hashed)


def test_guest_tokens_are_random_and_stored_hashed():
    token1, hash1 = new_guest_token()
    token2, _ = new_guest_token()
    assert token1 != token2
    assert hash1 != token1
    assert len(hash1) == 64  # fits guests.token_hash


def test_host_token_round_trip():
    assert decode_host_token(create_host_token(42)) == 42
    assert decode_host_token("garbage") is Non
    