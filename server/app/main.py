"""Habit tracker API — FastAPI + MongoDB.

Track habits and daily check-ins, with current and longest streaks computed
server-side.

Endpoints:
    GET    /api/health
    GET    /api/habits                      list with streaks
    POST   /api/habits                      {name}
    GET    /api/habits/{id}
    POST   /api/habits/{id}/checkin         {date: "YYYY-MM-DD"}  (idempotent)
    DELETE /api/habits/{id}/checkin         {date: "YYYY-MM-DD"}
    DELETE /api/habits/{id}
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import List

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from .db import get_db

app = FastAPI(title="Habit Tracker API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class HabitIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class CheckIn(BaseModel):
    date: str

    @field_validator("date")
    @classmethod
    def _valid(cls, v: str) -> str:
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError("date must be YYYY-MM-DD")
        return v


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def streaks(dates: List[str]) -> dict:
    """Longest consecutive run, and the run ending at the most recent check-in."""
    days = sorted({date.fromisoformat(d) for d in dates})
    if not days:
        return {"current_streak": 0, "longest_streak": 0}
    longest = run = 1
    for prev, cur in zip(days, days[1:]):
        run = run + 1 if cur - prev == timedelta(days=1) else 1
        longest = max(longest, run)
    # current = run ending at the last (max) date
    current = 1
    for i in range(len(days) - 1, 0, -1):
        if days[i] - days[i - 1] == timedelta(days=1):
            current += 1
        else:
            break
    return {"current_streak": current, "longest_streak": longest}


def _ser(doc: dict) -> dict:
    doc = dict(doc)
    doc["id"] = str(doc.pop("_id"))
    doc["checkins"] = sorted(doc.get("checkins", []))
    doc.update(streaks(doc["checkins"]))
    return doc


def _oid(hid: str) -> ObjectId:
    try:
        return ObjectId(hid)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="habit not found")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/habits")
def list_habits(db=Depends(get_db)):
    return [_ser(d) for d in db.habits.find().sort("created_at", -1)]


@app.post("/api/habits", status_code=201)
def create_habit(h: HabitIn, db=Depends(get_db)):
    doc = {"name": h.name, "checkins": [], "created_at": _now()}
    doc["_id"] = db.habits.insert_one(doc).inserted_id
    return _ser(doc)


@app.get("/api/habits/{hid}")
def get_habit(hid: str, db=Depends(get_db)):
    doc = db.habits.find_one({"_id": _oid(hid)})
    if not doc:
        raise HTTPException(status_code=404, detail="habit not found")
    return _ser(doc)


@app.post("/api/habits/{hid}/checkin")
def check_in(hid: str, c: CheckIn, db=Depends(get_db)):
    doc = db.habits.find_one_and_update(
        {"_id": _oid(hid)}, {"$addToSet": {"checkins": c.date}}, return_document=True)
    if not doc:
        raise HTTPException(status_code=404, detail="habit not found")
    return _ser(doc)


@app.delete("/api/habits/{hid}/checkin")
def remove_checkin(hid: str, c: CheckIn, db=Depends(get_db)):
    doc = db.habits.find_one_and_update(
        {"_id": _oid(hid)}, {"$pull": {"checkins": c.date}}, return_document=True)
    if not doc:
        raise HTTPException(status_code=404, detail="habit not found")
    return _ser(doc)


@app.delete("/api/habits/{hid}", status_code=204)
def delete_habit(hid: str, db=Depends(get_db)):
    if db.habits.delete_one({"_id": _oid(hid)}).deleted_count == 0:
        raise HTTPException(status_code=404, detail="habit not found")
    return None
