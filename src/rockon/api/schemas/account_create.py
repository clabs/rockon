from ninja import Schema


class AccountCreateIn(Schema):
    email: str
    account_context: str = 'crew'


class AccountCreateOut(Schema):
    status: str
    message: str
