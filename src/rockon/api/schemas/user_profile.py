from __future__ import annotations

from typing import Optional

from ninja import Schema


class UserProfileIn(Schema):
    first_name: str
    last_name: str
    nick_name: str = ''
    phone: str = ''
    address: str = ''
    address_extension: str = ''
    address_housenumber: str = ''
    zip_code: str = ''
    place: str = ''
    user_birthday: Optional[str] = None
