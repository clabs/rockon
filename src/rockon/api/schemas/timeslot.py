from __future__ import annotations

from datetime import datetime
from typing import Optional

from ninja import Schema


class TimeSlotOut(Schema):
    id: str
    stage_id: str
    stage_name: str
    day: str
    day_label: str
    start: str
    end: str
    band_id: Optional[str] = None
    band_name: Optional[str] = None
    band_guid: Optional[str] = None
    band_genre: Optional[str] = None
    band_track: Optional[str] = None
    band_bid_status: Optional[str] = None


class TimeSlotPatchIn(Schema):
    band_id: Optional[str] = None


class TimeSlotPatchOut(Schema):
    id: str
    band_id: Optional[str] = None
    band_name: Optional[str] = None
    band_guid: Optional[str] = None
    band_genre: Optional[str] = None
    band_track: Optional[str] = None
    band_bid_status: Optional[str] = None
    updated_at: datetime
