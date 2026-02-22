from __future__ import annotations

from datetime import datetime

from ninja import Schema


class TimeSlotOut(Schema):
    id: str
    stage_id: str
    stage_name: str
    day: str
    day_label: str
    start: str
    end: str
    band_id: str | None = None
    band_name: str | None = None
    band_guid: str | None = None
    band_genre: str | None = None
    band_track: str | None = None


class TimeSlotPatchIn(Schema):
    band_id: str | None = None


class TimeSlotPatchOut(Schema):
    id: str
    band_id: str | None = None
    band_name: str | None = None
    band_guid: str | None = None
    band_genre: str | None = None
    band_track: str | None = None
    updated_at: datetime
