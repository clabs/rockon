from __future__ import annotations

from datetime import datetime

from ninja import Schema


class CommentUserOut(Schema):
    first_name: str
    last_name: str


class CommentOut(Schema):
    id: str
    band: str
    user: CommentUserOut
    text: str
    reason: str | None = None
    mood: str | None = None
    created_at: datetime
    updated_at: datetime


class CommentIn(Schema):
    band: str
    text: str
    reason: str | None = None
    mood: str | None = None
