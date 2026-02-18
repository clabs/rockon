from __future__ import annotations

from django.contrib.auth.models import Group, User
from ninja import Router

from rockon.api.schemas import AccountCreateIn, AccountCreateOut
from rockon.base.models import EmailVerification

accountCreate = Router()


@accountCreate.post(
    '',
    response={201: AccountCreateOut, 400: AccountCreateOut},
    url_name='account_create',
)
def create_account(request, data: AccountCreateIn):
    email = data.email.strip().lower()

    if not email:
        return 400, {'status': 'error', 'message': 'Email is required'}

    if User.objects.filter(email=email).exists():
        return 400, {'status': 'exists', 'message': 'User already exists'}

    user = User.objects.create_user(
        username=email,
        email=email,
        password=None,
    )

    if data.account_context in ('crew', 'bands', 'exhibitors'):
        group = Group.objects.get(name=data.account_context)
        user.groups.add(group)

    EmailVerification.create_and_send(user=user)

    return 201, {'status': 'created', 'message': 'User created'}
