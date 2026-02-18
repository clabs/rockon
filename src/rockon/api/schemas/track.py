from __future__ import annotations

from datetime import datetime

from ninja import Schema


class TrackOut(Schema):
    id: str
    name: str
    slug: str | None = None
    active: bool
    created_at: datetime
    updated_at: datetime
