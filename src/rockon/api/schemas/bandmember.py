from __future__ import annotations

from ninja import Schema


class PersonIn(Schema):
    first_name: str
    last_name: str
    email: str
    address: str
    housenumber: str
    zip_code: str
    place: str
    nutrition: str
    position: str


class BandMemberSignupIn(Schema):
    band: str
    persons: list[PersonIn]
