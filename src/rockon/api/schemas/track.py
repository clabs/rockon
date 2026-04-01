from __future__ import annotations

from datetime import datetime
from typing import Optional

from ninja import Schema


class TrackOut(Schema):
    id: str
    name: str
    slug: Optional[str] = None
    active: bool
    created_at: datetime
    updated_at: datetime
