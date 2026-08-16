from __future__ import annotations

from datetime import datetime

from ninja import Schema


class BandMediaFileOut(Schema):
    file: str | None = None
    encoded_file: str | None = None


class BandMediaOut(Schema):
    id: str
    media_type: str
    url: str | None = None
    file: str | None = None
    encoded_file: str | None = None
    file_name_original: str | None = None
    thumbnail: str | None = None
    band: str


class UserOut(Schema):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str


class BandListOut(Schema):
    id: str
    guid: str
    name: str | None = None
    track: str | None = None
    songs: list[BandMediaOut] = []
    bid_status: str
    federal_state: str | None = None
    are_students: bool
    mean_age_under_27: bool
    is_coverband: bool
    bid_complete: bool
    press_photo: BandMediaFileOut | None = None
    logo: BandMediaFileOut | None = None
    created_at: datetime
    updated_at: datetime


class BandDetailOut(Schema):
    id: str
    guid: str
    slug: str | None = None
    name: str | None = None
    event: str
    track: str | None = None
    bid_status: str
    federal_state: str | None = None
    are_students: bool
    mean_age_under_27: bool
    is_coverband: bool
    has_management: bool
    repeated: bool
    bid_complete: bool
    genre: str | None = None
    cover_letter: str | None = None
    contact: UserOut | None = None
    songs: list[BandMediaOut] = []
    links: list[BandMediaOut] = []
    web_links: list[BandMediaOut] = []
    documents: list[BandMediaOut] = []
    press_photo: BandMediaFileOut | None = None
    logo: BandMediaFileOut | None = None
    created_at: datetime
    updated_at: datetime


class BandPatchIn(Schema):
    name: str | None = None
    genre: str | None = None
    federal_state: str | None = None
    cover_letter: str | None = None
    are_students: bool | None = None
    has_management: bool | None = None
    mean_age_under_27: bool | None = None
    is_coverband: bool | None = None
    track: str | None = None
    bid_status: str | None = None


class BandPatchOut(Schema):
    id: str
    track: str | None = None
    bid_status: str
    bid_complete: bool
    updated_at: datetime
