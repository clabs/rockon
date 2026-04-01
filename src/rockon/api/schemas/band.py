from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from ninja import Schema


class BandMediaFileOut(Schema):
    file: Optional[str] = None
    encoded_file: Optional[str] = None


class BandMediaOut(Schema):
    id: str
    media_type: str
    url: Optional[str] = None
    file: Optional[str] = None
    encoded_file: Optional[str] = None
    file_name_original: Optional[str] = None
    thumbnail: Optional[str] = None
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
    name: Optional[str] = None
    track: Optional[str] = None
    songs: List[BandMediaOut] = []
    bid_status: str
    federal_state: Optional[str] = None
    are_students: bool
    mean_age_under_27: bool
    is_coverband: bool
    bid_complete: bool
    press_photo: Optional[BandMediaFileOut] = None
    logo: Optional[BandMediaFileOut] = None
    created_at: datetime
    updated_at: datetime


class BandDetailOut(Schema):
    id: str
    guid: str
    slug: Optional[str] = None
    name: Optional[str] = None
    event: str
    track: Optional[str] = None
    bid_status: str
    federal_state: Optional[str] = None
    are_students: bool
    mean_age_under_27: bool
    is_coverband: bool
    has_management: bool
    repeated: bool
    bid_complete: bool
    genre: Optional[str] = None
    cover_letter: Optional[str] = None
    contact: Optional[UserOut] = None
    songs: List[BandMediaOut] = []
    links: List[BandMediaOut] = []
    web_links: List[BandMediaOut] = []
    documents: List[BandMediaOut] = []
    press_photo: Optional[BandMediaFileOut] = None
    logo: Optional[BandMediaFileOut] = None
    created_at: datetime
    updated_at: datetime


class BandPatchIn(Schema):
    name: Optional[str] = None
    genre: Optional[str] = None
    federal_state: Optional[str] = None
    cover_letter: Optional[str] = None
    are_students: Optional[bool] = None
    has_management: Optional[bool] = None
    mean_age_under_27: Optional[bool] = None
    is_coverband: Optional[bool] = None
    track: Optional[str] = None
    bid_status: Optional[str] = None


class BandPatchOut(Schema):
    id: str
    track: Optional[str] = None
    bid_status: str
    bid_complete: bool
    updated_at: datetime
