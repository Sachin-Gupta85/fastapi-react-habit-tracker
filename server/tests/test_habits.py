"""API tests for the Habit tracker (in-memory mongomock), incl. streak logic."""
import mongomock
import pytest
from fastapi.testclient import TestClient

from app.db import get_db
from app.main import app, streaks


@pytest.fixture
def client():
    db = mongomock.MongoClient()["testdb"]
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_streaks_unit():
    assert streaks([]) == {"current_streak": 0, "longest_streak": 0}
    # a 3-run then a gap then a 2-run ending at the latest date
    ds = ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-10", "2026-01-11"]
    assert streaks(ds) == {"current_streak": 2, "longest_streak": 3}
    # duplicates collapse; single day
    assert streaks(["2026-02-01", "2026-02-01"]) == {"current_streak": 1, "longest_streak": 1}


def test_checkin_is_idempotent(client):
    hid = client.post("/api/habits", json={"name": "Read"}).json()["id"]
    client.post(f"/api/habits/{hid}/checkin", json={"date": "2026-03-01"})
    out = client.post(f"/api/habits/{hid}/checkin", json={"date": "2026-03-01"}).json()
    assert out["checkins"] == ["2026-03-01"] and out["current_streak"] == 1


def test_streak_grows_and_resets(client):
    hid = client.post("/api/habits", json={"name": "Gym"}).json()["id"]
    for d in ["2026-03-01", "2026-03-02", "2026-03-03"]:
        out = client.post(f"/api/habits/{hid}/checkin", json={"date": d}).json()
    assert out["current_streak"] == 3 and out["longest_streak"] == 3
    out = client.post(f"/api/habits/{hid}/checkin", json={"date": "2026-03-05"}).json()
    assert out["current_streak"] == 1 and out["longest_streak"] == 3


def test_remove_checkin(client):
    hid = client.post("/api/habits", json={"name": "Water"}).json()["id"]
    for d in ["2026-04-01", "2026-04-02"]:
        client.post(f"/api/habits/{hid}/checkin", json={"date": d})
    out = client.request("DELETE", f"/api/habits/{hid}/checkin", json={"date": "2026-04-02"}).json()
    assert out["checkins"] == ["2026-04-01"]


def test_bad_date_and_404(client):
    hid = client.post("/api/habits", json={"name": "X"}).json()["id"]
    assert client.post(f"/api/habits/{hid}/checkin", json={"date": "nope"}).status_code == 422
    assert client.delete(f"/api/habits/{hid}").status_code == 204
    assert client.get(f"/api/habits/{hid}").status_code == 404
