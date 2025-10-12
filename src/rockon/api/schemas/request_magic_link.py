from ninja import Schema


class RequestMagicLinkIn(Schema):
    email: str


class RequestMagicLinkOut(Schema):
    status: str
    message: str
