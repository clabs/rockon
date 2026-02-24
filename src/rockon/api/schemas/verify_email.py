from __future__ import annotations

from ninja import Schema


class VerifyEmailIn(Schema):
    token: str


class VerifyEmailOut(Schema):
    status: str
    next: str = ''
