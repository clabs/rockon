from __future__ import annotations

import json

from django.contrib.auth.models import User
from django.http import JsonResponse

from rockon.base.models import AccountContext, EmailVerification


def account_create(request):
    # FIXME: refactor to Django forms to validate input
    body_list = json.loads(request.body)
    body = {}
    for item in body_list:
        body[item["name"]] = item["value"]

    try:
        user = User.objects.get(email=body["user_email"])
        return JsonResponse(
            {"status": "exists", "message": "User already exists"}, status=400
        )
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=body["user_email"],
            email=body["user_email"],
            password=None,
        )
        user.save()
        account_context = AccountContext.objects.get(slug=body["account_context"])
        user.profile.account_context.add(account_context)
        user.profile.save()
        EmailVerification.create_and_send(user=user)

        return JsonResponse(
            {"status": "created", "message": "User created"}, status=201
        )
