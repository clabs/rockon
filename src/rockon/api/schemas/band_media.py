from __future__ import annotations

from datetime import datetime

from ninja import Schema


class BandMediaIn(Schema):
    band: str
    media_type: str = 'unknown'
    url: str | None = None


class BandMediaOut(Schema):
    id: str
    band: str
    media_type: str
    url: str | None = None
    file: str | None = None
    encoded_file: str | None = None
    file_name_original: str | None = None
    thumbnail: str | None = None
    created_at: datetime
    updated_at: datetime
