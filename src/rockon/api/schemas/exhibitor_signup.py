from __future__ import annotations

from uuid import UUID
from typing import List, Optional

from ninja import Schema


class AttendanceItem(Schema):
    id: UUID
    count: int


class AssetItem(Schema):
    id: UUID
    count: int = 1


class ExhibitorSignupIn(Schema):
    org_id: Optional[UUID] = None
    organisation_name: Optional[str] = None
    organisation_address: Optional[str] = None
    organisation_address_housenumber: Optional[str] = None
    organisation_address_extension: Optional[str] = None
    organisation_zip: Optional[str] = None
    organisation_place: Optional[str] = None
    attendances: List[AttendanceItem]
    assets: List[AssetItem] = []
    offer_note: Optional[str] = None
    general_note: Optional[str] = None
    website: Optional[str] = None
    allow_contact: bool = False
    read_privacy: bool = False


class ExhibitorSignupOut(Schema):
    status: str
    message: str
