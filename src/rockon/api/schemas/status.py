from __future__ import annotations

from ninja import Schema


class StatusOut(Schema):
    status: str
    message: str = ''
