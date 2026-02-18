from __future__ import annotations

from ninja import Schema


class BandVoteIn(Schema):
    band: str
    vote: int


class BandVoteOut(Schema):
    band: str
    user: int
    vote: int
