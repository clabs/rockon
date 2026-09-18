from __future__ import annotations

from ninja import Schema


class CrewDateResponseIn(Schema):
    crew_date: str
    status: str


class CrewDateResponseOut(Schema):
    crew_date: str
    status: str
