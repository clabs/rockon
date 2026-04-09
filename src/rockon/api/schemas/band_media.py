from __future__ import annotations

from datetime import datetime
from typing import Optional

from ninja import Schema


class BandMediaIn(Schema):
    band: str
    media_type: str = 'unknown'
    url: Optional[str] = None


class BandMediaOut(Schema):
    id: str
    band: str
    media_type: str
    url: Optional[str] = None
    file: Optional[str] = None
    encoded_file: Optional[str] = None
    file_name_original: Optional[str] = None
    thumbnail: Optional[str] = None
    created_at: datetime
    updated_at: datetime
