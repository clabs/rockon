from __future__ import annotations

from typing import Any

from ninja import Schema


class PasskeyRegisterCompleteIn(Schema):
    name: str = ''
    credential: dict[str, Any]


class PasskeyAuthCompleteIn(Schema):
    credential: dict[str, Any]


class PasskeyOut(Schema):
    id: str
    name: str
    device_info: str
    created_at: str
    last_used_at: str | None


class PasskeyListOut(Schema):
    passkeys: list[PasskeyOut]


class PasskeyRenameIn(Schema):
    name: str
