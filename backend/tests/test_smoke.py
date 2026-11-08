"""Smoke tests: the app starts and every planned endpoint exists.

test_api_contract_is_registered fails if someone deletes or renames an endpoint by
accident. If the team agrees to change an endpoint, update the list below in the
same PR.

What's left to do:
- Add a test file per area next to this one (test_rooms.py, test_guests.py,
  test_tracks.py, test_queue.py, test_playback.py, test_auth.py).
- Each endpoint should have at least a happy-path test and one failure test.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_api_contract_is_registered():
    """Every endpoint in the README should exist, even if it's still a stub."""
    paths = client.get("/openapi.json").json()["paths"]
    expected = {
        "/api/v1/rooms": {"post"},
        "/api/v1/rooms/{code}": {"get"},
        "/api/v1/rooms/{room_id}": {"patch", "delete"},
        "/api/v1/rooms/{code}/join": {"post"},
        "/api/v1/rooms/{room_id}/guests": {"get"},
        "/api/v1/rooms/{room_id}/guests/{guest_id}": {"delete"},
        "/api/v1/tracks/search": {"get"},
        "/api/v1/rooms/{room_id}/queue": {"get", "post"},
        "/api/v1/rooms/{room_id}/queue/{item_id}": {"delete"},
        "/api/v1/rooms/{room_id}/queue/{item_id}/vote": {"put"},
        "/api/v1/rooms/{room_id}/next": {"post"},
        "/api/v1/rooms/{room_id}/now-playing": {"get"},
        "/api/v1/rooms/{room_id}/history": {"get"},
    }
    for path, methods in expected.items():
        assert path in paths, f"missing {path}"
        assert methods <= set(paths[path]), f"{path} missing {methods - set(paths[path])}"
