from __future__ import annotations

from uuid import UUID

from ninja import Schema


class AttendanceItem(Schema):
    id: UUID
    count: int


class AssetItem(Schema):
    id: UUID
    count: int = 1


class ExhibitorSignupIn(Schema):
    org_id: UUID | None = None
    organisation_name: str | None = None
    organisation_address: str | None = None
    organisation_address_housenumber: str | None = None
    organisation_address_extension: str | None = None
    organisation_zip: str | None = None
    organisation_place: str | None = None
    attendances: list[AttendanceItem]
    assets: list[AssetItem] = []
    offer_note: str | None = None
    general_note: str | None = None
    website: str | None = None
    allow_contact: bool = False
    read_privacy: bool = False


class ExhibitorSignupOut(Schema):
    status: str
    message: str
