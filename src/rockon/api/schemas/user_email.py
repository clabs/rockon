from __future__ import annotations

from ninja import Schema


class UpdateEmailIn(Schema):
    changeEmailNew: str
    changeEmailRepeat: str
