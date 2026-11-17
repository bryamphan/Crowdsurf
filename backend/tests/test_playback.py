"""Playback: now-playing, history, and next."""

from datetime import UTC, datetime, timedelta

import pytest


def url(room, path: str) -> str:
    return f"/api/v1/rooms/{room.id}/{path}"


# --- now-playing ------------------------------------------------------------------


async def test_now_playing_is_null_when_nothing_plays(client, make_room, make_queue_item):
    room = await make_room()
    await make_queue_item(room=room)  # queued, not playing
    resp = await client.get(url(room, "now-playing"))
    assert resp.status_code == 200
    assert resp.json() is None


async def test_now_playing_returns_song_with_details(
    client, make_room, make_guest, make_track, make_queue_item, make_vote
):
    room = await make_room()
    guest = await make_guest(room=room, nickname="dj")
    track = await make_track(title="Dancing Queen")
    item = await make_queue_item(room=room, track=track, added_by=guest, status="playing")
    await make_vote(item=item, value=1)
    await make_vote(item=item, value=1)

    body = (await client.get(url(room, "now-playing"))).json()
    assert body["id"] == item.id
    assert body["track"]["title"] == "Dancing Queen"
    assert body["added_by"]["nickname"] == "dj"
    assert body["score"] == 2


async def test_unknown_room_is_404(client):
    resp = await client.get("/api/v1/rooms/999999/now-playing")
    assert resp.status_code == 404


# --- history ----------------------------------------------------------------------


async def test_history_lists_played_songs_newest_first(client, make_room, make_queue_item):
    room = await make_room()
    now = datetime.now(UTC)
    older = await make_queue_item(room=room, status="played", played_at=now - timedelta(hours=1))
    newer = await make_queue_item(room=room, status="played", played_at=now)
    await make_queue_item(room=room, status="queued")
    await make_queue_item(room=room, status="playing", played_at=now)
    await make_queue_item(room=room, status="removed")
    await make_queue_item(status="played", played_at=now)  # a different room

    body = (await client.get(url(room, "history"))).json()
    assert [i["id"] for i in body] == [newer.id, older.id]


async def test_history_limit(client, make_room, make_queue_item):
    room = await make_room()
    for _ in range(3):
        await make_queue_item(room=room, status="played", played_at=datetime.now(UTC))
    assert len((await client.get(url(room, "history"), params={"limit": 2})).json()) == 2
    assert (await client.get(url(room, "history"), params={"limit": 0})).status_code == 422


# --- next: who can call it --------------------------------------------------------


async def test_next_requires_login(client, make_room):
    room = await make_room()
    assert (await client.post(url(room, "next"))).status_code == 401


async def test_next_rejects_other_hosts(client, make_room, make_host, auth_headers):
    room = await make_room()
    stranger = await make_host()
    resp = await client.post(url(room, "next"), headers=auth_headers(stranger))
    assert resp.status_code == 403


async def test_next_rejects_guests(client, make_room, make_guest, auth_headers):
    room = await make_room()
    guest = await make_guest(room=room)
    resp = await client.post(url(room, "next"), headers=auth_headers(guest))
    assert resp.status_code == 401


async def test_next_on_closed_room_is_409(client, make_host, make_room, auth_headers):
    host = await make_host()
    room = await make_room(host=host, closed_at=datetime.now(UTC))
    resp = await client.post(url(room, "next"), headers=auth_headers(host))
    assert resp.status_code == 409


async def test_next_on_unknown_room_is_404(client, make_host, auth_headers):
    host = await make_host()
    resp = await client.post("/api/v1/rooms/999999/next", headers=auth_headers(host))
    assert resp.status_code == 404


# --- next: what it does -----------------------------------------------------------


@pytest.fixture
async def host_room(make_host, make_room):
    host = await make_host()
    return host, await make_room(host=host)


async def test_next_plays_highest_score(
    client, host_room, make_queue_item, make_vote, auth_headers
):
    host, room = host_room
    low = await make_queue_item(room=room)
    high = await make_queue_item(room=room)
    disliked = await make_queue_item(room=room)
    await make_vote(item=high, value=1)
    await make_vote(item=disliked, value=-1)

    resp = await client.post(url(room, "next"), headers=auth_headers(host))
    assert resp.status_code == 200
    assert resp.json()["id"] == high.id
    assert resp.json()["status"] == "playing"

    resp = await client.post(url(room, "next"), headers=auth_headers(host))
    assert resp.json()["id"] == low.id  # score 0 beats score -1


async def test_next_breaks_ties_by_who_was_added_first(
    client, host_room, make_queue_item, auth_headers
):
    host, room = host_room
    now = datetime.now(UTC)
    # Both have score 0. Created in this order on purpose: the earlier added_at should
    # win even though it has the higher id.
    await make_queue_item(room=room, added_at=now)
    first = await make_queue_item(room=room, added_at=now - timedelta(minutes=5))

    resp = await client.post(url(room, "next"), headers=auth_headers(host))
    assert resp.json()["id"] == first.id


async def test_next_moves_current_song_to_history(client, host_room, make_queue_item, auth_headers):
    host, room = host_room
    playing = await make_queue_item(room=room, status="playing", played_at=datetime.now(UTC))
    queued = await make_queue_item(room=room)

    await client.post(url(room, "next"), headers=auth_headers(host))

    now_playing = (await client.get(url(room, "now-playing"))).json()
    history = (await client.get(url(room, "history"))).json()
    assert now_playing["id"] == queued.id
    assert [i["id"] for i in history] == [playing.id]


async def test_next_with_empty_queue_stops_playback(
    client, host_room, make_queue_item, auth_headers
):
    host, room = host_room
    playing = await make_queue_item(room=room, status="playing", played_at=datetime.now(UTC))

    resp = await client.post(url(room, "next"), headers=auth_headers(host))
    assert resp.status_code == 200
    assert resp.json() is None
    assert (await client.get(url(room, "now-playing"))).json() is None
    assert (await client.get(url(room, "history"))).json()[0]["id"] == playing.id


async def test_next_ignores_removed_songs_and_other_rooms(
    client, host_room, make_queue_item, make_vote, auth_headers
):
    host, room = host_room
    removed = await make_queue_item(room=room, status="removed")
    elsewhere = await make_queue_item()
    await make_vote(item=removed, value=1)
    await make_vote(item=elsewhere, value=1)

    resp = await client.post(url(room, "next"), headers=auth_headers(host))
    assert resp.json() is None
