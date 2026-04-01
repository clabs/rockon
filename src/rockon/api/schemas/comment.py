from __future__ import annotations

from datetime import datetime
from typing import Optional

from ninja import Schema


class CommentUserOut(Schema):
    first_name: str
    last_name: str


class CommentOut(Schema):
    id: str
    band: str
    user: CommentUserOut
    text: str
    reason: Optional[str] = None
    mood: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class CommentIn(Schema):
    band: str
    text: str
    reason: str | None = None
    mood: str | None = None
