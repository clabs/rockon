from __future__ import annotations

from django.contrib.auth.models import User
from django.db import transaction
from ninja import Router

from rockon.api.schemas import AccountCreateIn, AccountCreateOut
from rockon.base.models import EmailVerification
from rockon.base.services import assign_account_context_group

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

    with transaction.atomic():
        user = User.objects.create_user(
            username=email,
            email=email,
            password=None,
        )

        assign_account_context_group(user, data.account_context)

        EmailVerification.create_and_send(user=user)

    return 201, {'status': 'created', 'message': 'User created'}
